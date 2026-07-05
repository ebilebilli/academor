(function () {
  "use strict";

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"));
    return match ? decodeURIComponent(match.pop()) : "";
  }

  function getCsrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input && input.value) {
      return input.value;
    }
    return getCookie("csrftoken");
  }

  function pad2(value) {
    return String(value).padStart(2, "0");
  }

  function formatDuration(seconds) {
    var mins = Math.floor(seconds / 60);
    var secs = seconds % 60;
    return pad2(mins) + ":" + pad2(secs);
  }

  function initQuizSpeakingTake(root) {
    if (!root || root.dataset.quizSpeakingBound === "true") {
      return;
    }
    root.dataset.quizSpeakingBound = "true";

    var submitUrl = root.getAttribute("data-submit-url");
    var timeLimitSec = parseInt(root.getAttribute("data-time-limit-sec") || "0", 10) || 0;
    var msgSubmitting = root.getAttribute("data-msg-submitting") || "Submitting…";
    var msgError = root.getAttribute("data-msg-error") || "Could not submit.";
    var msgPrep = root.getAttribute("data-msg-prep") || "Preparation time";
    var msgRecording = root.getAttribute("data-msg-recording") || "Recording";
    var msgSpeakNow = root.getAttribute("data-msg-speak-now") || "Speak now";
    var msgPrepare = root.getAttribute("data-msg-prepare") || "Prepare your answer";
    var msgMicDenied = root.getAttribute("data-msg-mic-denied") || "Microphone access is required.";
    var msgStartTask = root.getAttribute("data-msg-start-task") || "Start task";
    var msgNextTask = root.getAttribute("data-msg-next-task") || "Next task";
    var msgStartNow = root.getAttribute("data-msg-start-now") || "Start recording now";
    var msgFinishAnswer = root.getAttribute("data-msg-finish-answer") || "Finish answer";
    var msgFinishTest = root.getAttribute("data-msg-finish-test") || "Finish test";
    var msgTaskComplete = root.getAttribute("data-msg-task-complete") || "Task complete";
    var msgPartComplete = root.getAttribute("data-msg-part-complete") || "Part complete";
    var msgNextQuestion = root.getAttribute("data-msg-next-question") || "Next question";
    var msgStartingPart = root.getAttribute("data-msg-starting-part") || "Starting";
    var msgAllComplete = root.getAttribute("data-msg-all-complete") || "All speaking tasks are complete.";

    var stage = root.querySelector("[data-speaking-stage]");
    var phaseLabel = root.querySelector("[data-speaking-phase-label]");
    var phaseTimer = root.querySelector("[data-speaking-phase-timer]");
    var recorderWrap = root.querySelector("[data-speaking-recorder]");
    var recPulse = root.querySelector("[data-speaking-rec-pulse]");
    var taskBtn = root.querySelector("[data-speaking-task-btn]");
    var taskBtnLabel = root.querySelector("[data-speaking-task-btn-label]");
    var progressWrap = root.querySelector("[data-speaking-progress]");
    var progressText = root.querySelector("[data-speaking-progress-text]");
    var progressFill = root.querySelector("[data-speaking-progress-fill]");
    var finishBtn = root.querySelector("[data-speaking-finish-btn]");
    var finishHint = root.querySelector("[data-speaking-finish-hint]");
    var resultPanel = root.querySelector("[data-speaking-result]");
    var stageContext = root.querySelector("[data-speaking-stage-context]");
    var questionNodes = Array.prototype.slice.call(root.querySelectorAll("[data-speaking-question]"));
    var expectedQuestionTotal = questionNodes.length;
    try {
      var expectedIds = JSON.parse(root.getAttribute("data-question-ids") || "[]");
      if (expectedIds.length) {
        expectedQuestionTotal = expectedIds.length;
      }
    } catch (error) {
      /* ignore */
    }

    var startedAt = Date.now();
    var submitting = false;
    var submitted = false;
    var quizTimerId = null;
    var phaseTimerId = null;
    var transitionTimerId = null;
    var mediaRecorder = null;
    var mediaStream = null;
    var currentIndex = 0;
    var currentPhase = "idle";
    var recordings = {};
    var recordingDurations = {};
    var phaseRemaining = 0;

    function bindTaskButton(handler, label) {
      if (!taskBtn) {
        return;
      }
      taskBtn.hidden = false;
      if (taskBtnLabel && label) {
        taskBtnLabel.textContent = label;
      }
      taskBtn.onclick = function () {
        if (handler) {
          handler();
        }
      };
    }

    function hideTaskButton() {
      if (!taskBtn) {
        return;
      }
      taskBtn.hidden = true;
      taskBtn.onclick = null;
    }

    function getCurrentQuestionNode() {
      return questionNodes[currentIndex] || null;
    }

    function updateProgress() {
      var total = expectedQuestionTotal || questionNodes.length;
      var done = Object.keys(recordings).length;
      if (progressText) {
        progressText.textContent = Math.min(done + (currentPhase === "idle" ? 1 : 0), total) + " / " + total;
      }
      if (progressFill && total) {
        progressFill.style.width = String(Math.round((done / total) * 100)) + "%";
      }
      if (finishBtn) {
        finishBtn.disabled = done < total || submitting || submitted;
      }
      if (finishHint) {
        finishHint.textContent =
          done >= total
            ? msgFinishTest
            : (root.getAttribute("data-msg-finish-hint") || "Complete every speaking task to finish the test.");
      }
    }

    function partHeadingForNode(node) {
      var section = node ? node.closest("[data-speaking-section]") : null;
      if (!section) {
        return "";
      }
      var title = section.querySelector(".portal-speaking-section__title");
      return title ? title.textContent.trim() : "";
    }

    function questionLabelForNode(node) {
      if (!node) {
        return "";
      }
      if (node.getAttribute("data-part-type") === "part_2") {
        var section = node.closest("[data-speaking-section]");
        var topic = section ? section.querySelector(".portal-speaking-cue-card__topic") : null;
        return topic ? topic.textContent.replace(/\s+/g, " ").trim() : "";
      }
      var numberEl = node.querySelector(".portal-speaking-question-item__number");
      var textEl = node.querySelector(".portal-speaking-question-item__text");
      if (numberEl && textEl) {
        return (numberEl.textContent + " " + textEl.textContent).replace(/\s+/g, " ").trim();
      }
      return "";
    }

    function highlightActiveQuestion(activeNode) {
      questionNodes.forEach(function (item) {
        item.classList.remove("is-speaking-active");
      });
      if (activeNode) {
        activeNode.classList.add("is-speaking-active");
        if (typeof activeNode.scrollIntoView === "function") {
          activeNode.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }
    }

    function updateStageContext(node) {
      if (!stageContext || !node) {
        return;
      }
      var heading = partHeadingForNode(node);
      var label = questionLabelForNode(node);
      stageContext.textContent = label ? heading + " — " + label : heading;
    }

    function markQuestionComplete(node) {
      node.classList.remove("is-speaking-active");
      node.classList.add("is-speaking-complete");
      if (node.classList.contains("portal-speaking-question-item")) {
        node.classList.add("portal-speaking-question-item--done");
      } else {
        node.classList.add("portal-speaking-question--done");
      }
    }

    function setPhaseLabel(text) {
      if (phaseLabel) {
        phaseLabel.textContent = text;
      }
    }

    function setPhaseTime(seconds) {
      phaseRemaining = Math.max(0, seconds);
      if (phaseTimer) {
        phaseTimer.textContent = formatDuration(phaseRemaining);
      }
    }

    function clearPhaseTimer() {
      if (phaseTimerId) {
        window.clearInterval(phaseTimerId);
        phaseTimerId = null;
      }
    }

    function startPhaseCountdown(seconds, onComplete) {
      clearPhaseTimer();
      setPhaseTime(seconds);
      phaseTimerId = window.setInterval(function () {
        phaseRemaining -= 1;
        setPhaseTime(phaseRemaining);
        if (phaseRemaining <= 0) {
          clearPhaseTimer();
          onComplete();
        }
      }, 1000);
    }

    function stopMedia() {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        try {
          mediaRecorder.stop();
        } catch (err) {
          /* ignore */
        }
      }
      if (mediaStream) {
        mediaStream.getTracks().forEach(function (track) {
          track.stop();
        });
        mediaStream = null;
      }
    }

    function startRecording(node, answerSeconds, onComplete) {
      currentPhase = "recording";
      setPhaseLabel(msgRecording + " — " + msgSpeakNow);
      if (recorderWrap) {
        recorderWrap.hidden = false;
      }
      if (recPulse) {
        recPulse.classList.remove("is-paused");
      }
      bindTaskButton(function () {
        clearPhaseTimer();
        stopMedia();
      }, msgFinishAnswer);

      var questionId = node.getAttribute("data-question-id");
      var chunks = [];

      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then(function (stream) {
          mediaStream = stream;
          var mimeType = "";
          if (window.MediaRecorder && MediaRecorder.isTypeSupported("audio/webm")) {
            mimeType = "audio/webm";
          } else if (window.MediaRecorder && MediaRecorder.isTypeSupported("audio/mp4")) {
            mimeType = "audio/mp4";
          }
          mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType: mimeType }) : new MediaRecorder(stream);
          var started = Date.now();
          mediaRecorder.ondataavailable = function (event) {
            if (event.data && event.data.size > 0) {
              chunks.push(event.data);
            }
          };
          mediaRecorder.onstop = function () {
            var duration = Math.max(1, Math.round((Date.now() - started) / 1000));
            var blob = new Blob(chunks, { type: mediaRecorder.mimeType || "audio/webm" });
            var ext = (mediaRecorder.mimeType || "").indexOf("mp4") >= 0 ? "m4a" : "webm";
            recordings[questionId] = new File([blob], "speaking-" + questionId + "." + ext, {
              type: blob.type || "audio/webm",
            });
            recordingDurations[questionId] = duration;
            markQuestionComplete(node);
            if (recorderWrap) {
              recorderWrap.hidden = true;
            }
            if (recPulse) {
              recPulse.classList.add("is-paused");
            }
            hideTaskButton();
            updateProgress();
            onComplete();
          };
          mediaRecorder.start();
          startPhaseCountdown(answerSeconds, function () {
            stopMedia();
          });
        })
        .catch(function () {
          window.alert(msgMicDenied);
          currentPhase = "idle";
          showCurrentTaskIntro();
        });
    }

    function runPrepThenRecord(node) {
      var prepSeconds = parseInt(node.getAttribute("data-prep-seconds") || "0", 10) || 0;
      var answerSeconds = parseInt(node.getAttribute("data-answer-seconds") || "30", 10) || 30;
      highlightActiveQuestion(node);
      updateStageContext(node);

      if (prepSeconds > 0) {
        currentPhase = "prep";
        setPhaseLabel(msgPrep + " — " + msgPrepare);
        if (recorderWrap) {
          recorderWrap.hidden = true;
        }
        bindTaskButton(function () {
          clearPhaseTimer();
          startRecording(node, answerSeconds, advanceAfterTask);
        }, msgStartNow);
        startPhaseCountdown(prepSeconds, function () {
          hideTaskButton();
          startRecording(node, answerSeconds, advanceAfterTask);
        });
      } else {
        startRecording(node, answerSeconds, advanceAfterTask);
      }
    }

    function clearTransitionTimer() {
      if (transitionTimerId) {
        window.clearTimeout(transitionTimerId);
        transitionTimerId = null;
      }
    }

    function partSectionForNode(node) {
      return node ? node.closest("[data-speaking-section]") : null;
    }

    function isNewPart(previousNode, nextNode) {
      var previousSection = partSectionForNode(previousNode);
      var nextSection = partSectionForNode(nextNode);
      return Boolean(previousSection && nextSection && previousSection !== nextSection);
    }

    function showTransitionThenRun(nextNode, previousNode) {
      clearTransitionTimer();
      if (!nextNode) {
        return;
      }
      var partChanged = isNewPart(previousNode, nextNode);
      var delayMs = partChanged ? 2800 : 700;

      highlightActiveQuestion(nextNode);
      updateStageContext(nextNode);
      if (recorderWrap) {
        recorderWrap.hidden = true;
      }
      hideTaskButton();

      if (partChanged) {
        var nextHeading = partHeadingForNode(nextNode);
        setPhaseLabel(msgPartComplete + " — " + msgStartingPart + ": " + nextHeading);
        setPhaseTime(0);
      } else {
        setPhaseLabel(msgTaskComplete + " — " + msgNextQuestion);
      }

      transitionTimerId = window.setTimeout(function () {
        transitionTimerId = null;
        runPrepThenRecord(nextNode);
      }, delayMs);
    }

    function advanceAfterTask() {
      var completedNode = getCurrentQuestionNode();
      if (completedNode) {
        completedNode.classList.remove("is-speaking-active");
      }
      clearPhaseTimer();
      currentPhase = "idle";
      currentIndex += 1;
      if (currentIndex >= questionNodes.length) {
        clearTransitionTimer();
        if (stage) {
          stage.hidden = true;
        }
        updateProgress();
        return;
      }
      showTransitionThenRun(getCurrentQuestionNode(), completedNode);
      updateProgress();
    }

    function showCurrentTaskIntro() {
      var node = getCurrentQuestionNode();
      if (!node || !stage) {
        return;
      }
      stage.hidden = false;
      highlightActiveQuestion(node);
      updateStageContext(node);
      setPhaseLabel(msgStartTask);
      setPhaseTime(parseInt(node.getAttribute("data-answer-seconds") || "30", 10) || 30);
      if (recorderWrap) {
        recorderWrap.hidden = true;
      }
      bindTaskButton(function () {
        runPrepThenRecord(node);
      }, currentIndex === 0 ? msgStartTask : msgNextTask);
      updateProgress();
    }

    function beginSpeakingFlow() {
      if (!questionNodes.length && !expectedQuestionTotal) {
        return;
      }
      if (progressWrap) {
        progressWrap.hidden = false;
      }
      if (stage) {
        stage.hidden = false;
      }
      currentIndex = 0;
      showCurrentTaskIntro();
    }

    function syncTimerToolbarSpacer() {
      var toolbar = root.querySelector(".portal-quiz-take-toolbar--timed");
      var spacer = root.querySelector(".portal-quiz-take-toolbar-spacer");
      if (!toolbar || !spacer) {
        return;
      }
      spacer.style.height = toolbar.offsetHeight + "px";
    }

    function startQuizTimer() {
      if (!timeLimitSec) {
        return;
      }
      var timerWrap = root.querySelector("[data-quiz-timer]");
      var timerValue = root.querySelector("[data-quiz-timer-value]");
      var timerBar = root.querySelector("[data-quiz-timer-bar]");
      var timerBarFill = root.querySelector("[data-quiz-timer-bar-fill]");
      var toolbar = root.querySelector(".portal-quiz-take-toolbar--timed");
      var spacer = root.querySelector(".portal-quiz-take-toolbar-spacer");
      if (timerWrap) {
        timerWrap.hidden = false;
      }
      if (timerBar) {
        timerBar.hidden = false;
        timerBar.setAttribute("aria-hidden", "false");
      }
      if (toolbar) {
        toolbar.classList.add("is-timer-visible");
      }
      if (spacer) {
        spacer.classList.add("is-visible");
      }
      syncTimerToolbarSpacer();
      var remaining = timeLimitSec;
      function tick() {
        if (timerValue) {
          timerValue.textContent = formatDuration(remaining);
        }
        if (timerBarFill) {
          timerBarFill.style.width = String(Math.max(0, (remaining / timeLimitSec) * 100)) + "%";
        }
        remaining -= 1;
        if (remaining < 0 && !submitting && !submitted) {
          submitAttempt({ allowEmpty: true, completionTrigger: "time_limit" });
        }
      }
      tick();
      quizTimerId = window.setInterval(tick, 1000);
    }

    function submitAttempt(options) {
      options = options || {};
      if (submitting) {
        return Promise.resolve(false);
      }
      if (submitted) {
        return Promise.resolve(true);
      }
      submitting = true;
      if (!options.silent && finishBtn) {
        finishBtn.disabled = true;
        finishBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>' + msgSubmitting;
      }
      stopMedia();
      clearPhaseTimer();
      clearTransitionTimer();
      if (quizTimerId) {
        window.clearInterval(quizTimerId);
        quizTimerId = null;
      }

      var formData = new FormData();
      formData.append("duration_sec", String(Math.max(0, Math.round((Date.now() - startedAt) / 1000))));
      if (options.allowEmpty) {
        formData.append("allow_empty", "1");
      }
      if (options.completionTrigger) {
        formData.append("completion_trigger", options.completionTrigger);
      }
      var mockId = root.getAttribute("data-mock-id");
      if (mockId) {
        formData.append("mock", mockId);
      }
      Object.keys(recordings).forEach(function (questionId) {
        formData.append("recording_" + questionId, recordings[questionId]);
        formData.append("duration_" + questionId, String(recordingDurations[questionId] || 0));
      });

      return fetch(submitUrl, {
        method: "POST",
        credentials: "same-origin",
        keepalive: Boolean(options.keepalive),
        headers: {
          "X-CSRFToken": getCsrfToken(),
        },
        body: formData,
      })
        .then(function (response) {
          return response.json().then(function (payload) {
            return { ok: response.ok, payload: payload };
          });
        })
        .then(function (result) {
          submitting = false;
          if (!result.ok || !result.payload || !result.payload.success) {
            if (
              window.PortalQuizMockSection
              && window.PortalQuizMockSection.redirectIfNeeded(result.payload)
            ) {
              return false;
            }
            if (!options.silent) {
              if (finishBtn) {
                finishBtn.disabled = false;
                finishBtn.innerHTML = '<i class="bi bi-check2-circle me-1" aria-hidden="true"></i>' + msgFinishTest;
              }
              window.alert((result.payload && result.payload.error) || msgError);
            }
            return false;
          }
          if (result.payload.mock_continue && result.payload.next_url) {
            submitted = true;
            root.setAttribute("data-quiz-finished", "true");
            if (
              window.PortalQuizMockSection
              && window.PortalQuizMockSection.handleSubmitResponse(root, result.payload, function (data) {
                var content = root.querySelector("[data-quiz-take-content]");
                if (content && resultPanel) {
                  Array.prototype.slice.call(content.children).forEach(function (child) {
                    if (child !== resultPanel) {
                      child.hidden = true;
                    }
                  });
                  resultPanel.classList.remove("d-none");
                  resultPanel.hidden = false;
                }
                var dock = root.querySelector("[data-quiz-take-actions]");
                if (dock) {
                  dock.hidden = true;
                }
              })
            ) {
              return true;
            }
          }
          submitted = true;
          root.setAttribute("data-quiz-finished", "true");
          if (!options.silent) {
            var content = root.querySelector("[data-quiz-take-content]");
            if (content && resultPanel) {
              Array.prototype.slice.call(content.children).forEach(function (child) {
                if (child !== resultPanel) {
                  child.hidden = true;
                }
              });
              resultPanel.classList.remove("d-none");
              resultPanel.hidden = false;
            }
            var dock = root.querySelector("[data-quiz-take-actions]");
            if (dock) {
              dock.hidden = true;
            }
          }
          return true;
        })
        .catch(function () {
          submitting = false;
          if (!options.silent) {
            if (finishBtn) {
              finishBtn.disabled = false;
              finishBtn.innerHTML = '<i class="bi bi-check2-circle me-1" aria-hidden="true"></i>' + msgFinishTest;
            }
            window.alert(msgError);
          }
          return false;
        });
    }

    if (finishBtn) {
      finishBtn.addEventListener("click", function () {
        var total = expectedQuestionTotal || questionNodes.length;
        var done = Object.keys(recordings).length;
        if (done < total) {
          window.alert(
            (root.getAttribute("data-msg-finish-hint") || "Complete every speaking task to finish the test.")
          );
          return;
        }
        submitAttempt();
      });
    }

    startedAt = Date.now();
    startQuizTimer();
    beginSpeakingFlow();

    window.addEventListener("resize", syncTimerToolbarSpacer);

    if (window.PortalQuizLeaveGuard && window.PortalQuizLeaveGuard.init) {
      window.PortalQuizLeaveGuard.init({
        root: root,
        submit: function (options) {
          return submitAttempt({
            allowEmpty: true,
            silent: options && options.silent,
            keepalive: options && options.keepalive,
            completionTrigger: (options && options.completionTrigger) || "auto_leave",
          });
        },
        beforeLeave: function () {
          stopMedia();
        },
      });
    }

    updateProgress();
  }

  function bootSpeakingTake() {
    var root = document.querySelector("[data-quiz-speaking-take]");
    if (!root) {
      return;
    }

    function startQuiz() {
      root.setAttribute("data-quiz-started", "true");
      initQuizSpeakingTake(root);
    }

    if (document.querySelector("[data-quiz-start-gate]")) {
      if (root.getAttribute("data-quiz-started") === "true") {
        startQuiz();
        return;
      }
      document.addEventListener("portal-quiz-started", startQuiz, { once: true });
      return;
    }

    startQuiz();
  }

  function scheduleSpeakingBoot() {
    bootSpeakingTake();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleSpeakingBoot);
  } else {
    scheduleSpeakingBoot();
  }
  document.addEventListener("portal:content-loaded", scheduleSpeakingBoot);
})();

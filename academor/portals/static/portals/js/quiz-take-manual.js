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

  function getBootstrapModal(modalEl) {
    if (!modalEl || !window.bootstrap || !window.bootstrap.Modal) {
      return null;
    }
    return window.bootstrap.Modal.getOrCreateInstance(modalEl, {
      backdrop: "static",
      keyboard: false,
    });
  }

  function pad2(value) {
    return String(value).padStart(2, "0");
  }

  function formatDuration(seconds) {
    return pad2(Math.floor(seconds / 60)) + ":" + pad2(seconds % 60);
  }

  function countWords(text) {
    var trimmed = (text || "").trim();
    if (!trimmed) {
      return 0;
    }
    return trimmed.split(/\s+/).filter(Boolean).length;
  }

  function submissionFields(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-manual-submission]"));
  }

  function questionIdsInOrder(root) {
    var raw = root.getAttribute("data-question-ids") || "[]";
    try {
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed.map(String) : [];
    } catch (err) {
      return [];
    }
  }

  function questionAnswerValue(root, questionId) {
    var textField = root.querySelector(
      'textarea[data-question-id="' + questionId + '"][data-manual-submission]'
    );
    if (textField) {
      return (textField.value || "").trim();
    }
    var radio = root.querySelector(
      'input[type="radio"][data-question-id="' + questionId + '"]:checked'
    );
    if (radio) {
      return radio.value;
    }
    return "";
  }

  function hasAnswerValue(value) {
    if (value === null || value === undefined) {
      return false;
    }
    return String(value).trim() !== "";
  }

  function isQuestionAnswered(root, questionId) {
    return hasAnswerValue(questionAnswerValue(root, questionId));
  }

  function answeredFieldCount(root) {
    var ids = questionIdsInOrder(root);
    if (ids.length) {
      return ids.filter(function (id) {
        return isQuestionAnswered(root, id);
      }).length;
    }
    return submissionFields(root).filter(function (field) {
      return hasAnswerValue(field.value);
    }).length;
  }

  function totalFieldCount(root) {
    var ids = questionIdsInOrder(root);
    if (ids.length) {
      return ids.length;
    }
    var fields = submissionFields(root);
    return fields.length || 1;
  }

  function initListeningPlayOnce(root) {
    var msgPlayed = root.getAttribute("data-msg-listening-played") || "This clip has already been played.";
    var msgReplayBlocked =
      root.getAttribute("data-msg-listening-replay-blocked") || "You cannot replay this clip from the beginning.";
    var autoSequence = root.getAttribute("data-listening-auto-sequence") === "true";
    var clips = [];

    root.querySelectorAll("audio[data-listening-play-once]").forEach(function (audio) {
      clips.push(
        setupListeningClip(audio, {
          msgPlayed: msgPlayed,
          msgReplayBlocked: msgReplayBlocked,
          autoSequence: autoSequence,
        })
      );
    });

    if (autoSequence && clips.length) {
      initListeningAutoSequence(root, clips);
    }

    root.portalListeningCleanup = function () {
      clips.forEach(function (clip) {
        clip.setQueueActive(false);
        try {
          clip.audio.pause();
          clip.audio.removeAttribute("src");
          clip.audio.load();
        } catch (error) {
          /* ignore */
        }
      });
    };
    window.portalQuizMediaCleanup = function () {
      if (typeof root.portalListeningCleanup === "function") {
        root.portalListeningCleanup();
      }
      if (typeof root.portalListeningSequenceCleanup === "function") {
        root.portalListeningSequenceCleanup();
      }
    };
  }

  function setupListeningClip(audio, options) {
    var section = audio.closest(".portal-listening-section");
    var msgPlayed = options.msgPlayed;
    var msgReplayBlocked = options.msgReplayBlocked;
    var autoSequence = options.autoSequence;
    var queueActive = false;
    var hasStarted = false;
    var completed = false;
    var endingNaturally = false;
    var allowedTime = 0;
    var clampingSeek = false;
    var playedNotice = null;
    var replayNotice = null;
    var endedCallbacks = [];
    var sectionOverlay = null;
    var liveIndicator = null;

    if (autoSequence) {
      audio.controls = false;
      audio.setAttribute("tabindex", "-1");
      audio.setAttribute("aria-hidden", "true");
    }

    function ensureSectionOverlay() {
      if (!sectionOverlay && section) {
        var player = section.querySelector(".portal-listening-section__player");
        if (!player) {
          return null;
        }
        sectionOverlay = document.createElement("div");
        sectionOverlay.className = "portal-listening-section__lock";
        sectionOverlay.setAttribute("data-listening-lock", "");
        player.appendChild(sectionOverlay);
      }
      return sectionOverlay;
    }

    function ensureLiveIndicator() {
      if (!liveIndicator && section) {
        var player = section.querySelector(".portal-listening-section__player");
        if (!player) {
          return null;
        }
        liveIndicator = document.createElement("div");
        liveIndicator.className = "portal-listening-live";
        liveIndicator.setAttribute("data-listening-live", "");
        liveIndicator.hidden = true;
        liveIndicator.innerHTML =
          '<span class="portal-listening-live__pulse" aria-hidden="true"></span>' +
          '<span class="portal-listening-live__text"></span>';
        player.insertBefore(liveIndicator, player.firstChild);
      }
      return liveIndicator;
    }

    function ensurePlayedNotice() {
      if (!playedNotice && section) {
        playedNotice = document.createElement("p");
        playedNotice.className = "portal-listening-section__played-notice text-muted small mb-0 mt-2";
        playedNotice.hidden = true;
        var player = section.querySelector(".portal-listening-section__player");
        if (player) {
          player.appendChild(playedNotice);
        }
      }
      return playedNotice;
    }

    function showReplayBlocked() {
      if (!section) {
        return;
      }
      if (!replayNotice) {
        replayNotice = document.createElement("p");
        replayNotice.className = "portal-listening-section__replay-notice text-warning small mb-0 mt-2";
        replayNotice.setAttribute("role", "status");
        var player = section.querySelector(".portal-listening-section__player");
        if (player) {
          player.appendChild(replayNotice);
        }
      }
      replayNotice.textContent = msgReplayBlocked;
      replayNotice.hidden = false;
      window.setTimeout(function () {
        if (replayNotice) {
          replayNotice.hidden = true;
        }
      }, 3200);
    }

    function setSectionVisualState(state, label) {
      if (!section) {
        return;
      }
      section.classList.remove(
        "is-listening-section-waiting",
        "is-listening-section-next",
        "is-listening-section-active"
      );
      if (state === "waiting") {
        section.classList.add("is-listening-section-waiting");
      } else if (state === "next") {
        section.classList.add("is-listening-section-next");
      } else if (state === "playing") {
        section.classList.add("is-listening-section-active");
      }

      var overlay = ensureSectionOverlay();
      var live = ensureLiveIndicator();
      if (state === "playing") {
        if (overlay) {
          overlay.hidden = true;
        }
        if (live) {
          live.hidden = false;
          var liveText = live.querySelector(".portal-listening-live__text");
          if (liveText) {
            liveText.textContent = label || "";
          }
        }
      } else {
        if (live) {
          live.hidden = true;
        }
        if (overlay) {
          overlay.hidden = state === "played";
          overlay.textContent = label || "";
        }
      }
    }

    function lockAudio(message) {
      if (completed) {
        return;
      }
      completed = true;
      endingNaturally = true;
      audio.pause();
      audio.controls = false;
      audio.classList.remove("is-listening-active");
      audio.classList.add("is-listening-played");
      audio.removeAttribute("data-listening-queue-active");
      if (section) {
        section.classList.remove("is-listening-section-active", "is-listening-section-next", "is-listening-section-waiting");
        section.classList.add("is-listening-audio-played");
      }
      if (liveIndicator) {
        liveIndicator.hidden = true;
      }
      if (sectionOverlay) {
        sectionOverlay.hidden = true;
      }
      var notice = ensurePlayedNotice();
      if (notice) {
        notice.textContent = message || msgPlayed;
        notice.hidden = false;
      }
      var callbacks = endedCallbacks.slice();
      endedCallbacks = [];
      callbacks.forEach(function (callback) {
        callback();
      });
    }

    function markPlaybackStarted() {
      hasStarted = true;
      audio.classList.add("is-listening-active");
    }

    function syncAllowedTime() {
      if (completed || clampingSeek || audio.seeking) {
        return;
      }
      allowedTime = Math.max(allowedTime, audio.currentTime || 0);
    }

    function clampSeekPosition() {
      if (completed || !hasStarted || clampingSeek) {
        return;
      }
      if (Math.abs(audio.currentTime - allowedTime) > 0.2) {
        clampingSeek = true;
        audio.currentTime = allowedTime;
        clampingSeek = false;
        showReplayBlocked();
      }
    }

    function hasFinishedClip() {
      var duration = audio.duration;
      return duration && !isNaN(duration) && isFinite(duration) && allowedTime >= duration - 0.35;
    }

    function setQueueActive(active) {
      queueActive = active;
      if (completed) {
        return;
      }
      if (active) {
        audio.setAttribute("data-listening-queue-active", "true");
      } else {
        audio.removeAttribute("data-listening-queue-active");
      }
      audio.controls = false;
    }

    audio.addEventListener("timeupdate", syncAllowedTime);

    audio.addEventListener("seeking", function () {
      if (completed) {
        audio.pause();
        return;
      }
      clampSeekPosition();
    });

    audio.addEventListener("seeked", clampSeekPosition);

    audio.addEventListener("ended", function () {
      endingNaturally = true;
      lockAudio(msgPlayed);
    });

    audio.addEventListener("pause", function () {
      if (!autoSequence || !queueActive || completed || endingNaturally) {
        return;
      }
      if (hasFinishedClip()) {
        return;
      }
      window.requestAnimationFrame(function () {
        if (queueActive && !completed && !endingNaturally) {
          audio.play().catch(function () {});
        }
      });
    });

    audio.addEventListener("play", function () {
      if (autoSequence && !queueActive) {
        audio.pause();
        return;
      }
      if (completed) {
        audio.pause();
        return;
      }
      if (hasFinishedClip()) {
        audio.pause();
        lockAudio(msgPlayed);
        return;
      }
      if (hasStarted && allowedTime > 0.5 && audio.currentTime < 0.5) {
        audio.pause();
        audio.currentTime = allowedTime;
        showReplayBlocked();
        return;
      }
      if (!hasStarted) {
        markPlaybackStarted();
      }
    });

    return {
      audio: audio,
      section: section,
      setQueueActive: setQueueActive,
      setSectionVisualState: setSectionVisualState,
      isCompleted: function () {
        return completed;
      },
      onEnded: function (callback) {
        endedCallbacks.push(callback);
      },
      playAuto: function (liveLabel) {
        if (completed) {
          return Promise.resolve(false);
        }
        setQueueActive(true);
        setSectionVisualState("playing", liveLabel || "");
        if (section && section.scrollIntoView) {
          section.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
        return audio.play().then(
          function () {
            return true;
          },
          function () {
            audio.pause();
            return false;
          }
        );
      },
    };
  }

  function initListeningAutoSequence(root, clips) {
    var firstDelay = parseInt(root.getAttribute("data-listening-first-delay-ms") || "5500", 10) || 5500;
    var gapMs = parseInt(root.getAttribute("data-listening-gap-ms") || "30000", 10) || 30000;
    var msgFirstCountdown = root.getAttribute("data-msg-listening-first-countdown") || "First listening clip starts in";
    var msgNextCountdown = root.getAttribute("data-msg-listening-next-countdown") || "Next listening clip starts in";
    var msgSeconds = root.getAttribute("data-msg-listening-seconds") || "seconds";
    var msgPlaying = root.getAttribute("data-msg-listening-playing") || "Listening clip is playing…";
    var msgAllDone = root.getAttribute("data-msg-listening-all-done") || "All listening clips have finished.";
    var msgWaiting = root.getAttribute("data-msg-listening-waiting") || "Waiting — this clip will play automatically in order.";
    var msgUpNext = root.getAttribute("data-msg-listening-up-next") || "Up next — starts after the countdown.";
    var msgLive = root.getAttribute("data-msg-listening-live") || "Now playing";
    var stack = root.querySelector(".portal-listening-stack");
    var countdownId = null;
    var statusEl = document.createElement("div");
    statusEl.className = "portal-listening-sequence-status panel mb-3";
    statusEl.setAttribute("role", "status");
    statusEl.setAttribute("aria-live", "polite");
    if (stack) {
      stack.classList.add("portal-listening-stack--sequenced");
    }
    if (stack && stack.parentNode) {
      stack.parentNode.insertBefore(statusEl, stack);
    } else {
      root.insertBefore(statusEl, root.firstChild);
    }

    function formatCountdown(prefix, seconds) {
      return prefix + " " + seconds + " " + msgSeconds + ".";
    }

    function setStatus(text) {
      statusEl.textContent = text;
      statusEl.hidden = !text;
    }

    function clearCountdown() {
      if (countdownId) {
        window.clearInterval(countdownId);
        countdownId = null;
      }
    }

    function applyWaitingStates(activeIndex, nextIndex) {
      clips.forEach(function (clip, index) {
        if (clip.isCompleted()) {
          clip.setSectionVisualState("played");
          return;
        }
        if (index === activeIndex) {
          return;
        }
        if (typeof nextIndex === "number" && index === nextIndex) {
          clip.setSectionVisualState("next", msgUpNext);
          return;
        }
        clip.setSectionVisualState("waiting", msgWaiting);
      });
    }

    function runCountdown(totalMs, prefix, onDone, nextIndex) {
      clearCountdown();
      applyWaitingStates(-1, nextIndex);
      var remaining = Math.max(1, Math.ceil(totalMs / 1000));
      function tick() {
        setStatus(formatCountdown(prefix, remaining));
        remaining -= 1;
        if (remaining <= 0) {
          clearCountdown();
          onDone();
        }
      }
      tick();
      countdownId = window.setInterval(tick, 1000);
    }

    function playClipAt(index) {
      if (index >= clips.length) {
        setStatus(msgAllDone);
        return;
      }
      var clip = clips[index];
      applyWaitingStates(index);
      setStatus(msgPlaying);
      clip.playAuto(msgLive).then(function (started) {
        if (!started) {
          setStatus("");
        }
      });
      clip.onEnded(function () {
        clip.setQueueActive(false);
        clip.setSectionVisualState("played");
        var nextIndex = index + 1;
        if (nextIndex >= clips.length) {
          setStatus(msgAllDone);
          return;
        }
        runCountdown(gapMs, msgNextCountdown, function () {
          playClipAt(nextIndex);
        }, nextIndex);
      });
    }

    clips.forEach(function (clip) {
      clip.setQueueActive(false);
      clip.setSectionVisualState("waiting", msgWaiting);
    });

    runCountdown(firstDelay, msgFirstCountdown, function () {
      playClipAt(0);
    }, 0);

    root.portalListeningSequenceCleanup = function () {
      clearCountdown();
    };
  }

  function initWritingAreas(root) {
    var msgWords = root.getAttribute("data-msg-words") || "words";
    var fields = root.querySelectorAll(".portal-quiz-writing-area__input");

    fields.forEach(function (field) {
      var area = field.closest(".portal-quiz-writing-area");
      var countEl = area ? area.querySelector("[data-writing-count]") : null;

      function syncField() {
        if (countEl) {
          var words = countWords(field.value);
          countEl.textContent = words + " " + msgWords;
          countEl.classList.toggle("is-active", words > 0);
        }
        field.style.height = "auto";
        field.style.height = Math.max(field.scrollHeight, 152) + "px";
      }

      field.addEventListener("input", function () {
        syncField();
        updateWritingUi(root);
      });
      syncField();
    });

    root.querySelectorAll('input[type="radio"][data-manual-submission]').forEach(function (radio) {
      radio.addEventListener("change", function () {
        updateWritingUi(root);
      });
    });
  }

  function updateWritingUi(root) {
    var submitHints = root.querySelectorAll("[data-manual-submit-hint]");
    var progressWrap = root.querySelector("[data-writing-progress]");
    var progressText = root.querySelector("[data-writing-progress-text]");
    var progressFill = root.querySelector("[data-writing-progress-fill]");
    var answered = answeredFieldCount(root);
    var total = totalFieldCount(root);
    var msgReady = root.getAttribute("data-msg-ready") || "You can complete the quiz whenever you are ready.";

    submitHints.forEach(function (submitHint) {
      submitHint.textContent = msgReady;
      submitHint.classList.add("is-ready");
    });

    if (progressWrap && progressText && progressFill) {
      var pct = total > 0 ? Math.round((answered / total) * 100) : 0;
      progressText.textContent = answered + " / " + total;
      progressFill.style.width = pct + "%";
    }
  }

  function stopQuizMedia(root) {
    if (typeof window.portalQuizMediaCleanup === "function") {
      window.portalQuizMediaCleanup();
    }
    if (root) {
      root.querySelectorAll("audio, video").forEach(function (node) {
        try {
          node.pause();
          node.removeAttribute("src");
          node.load();
        } catch (error) {
          /* ignore */
        }
      });
    }
  }

  function initQuizLeaveGuard(root, submitManual) {
    if (!window.PortalQuizLeaveGuard) {
      return;
    }
    window.PortalQuizLeaveGuard.init({
      root: root,
      submit: function (options) {
        return submitManual({
          keepalive: options.keepalive,
          silent: options.silent,
          allowEmpty: true,
          completionTrigger: options.completionTrigger,
        });
      },
      beforeLeave: function () {
        stopQuizMedia(root);
      },
      afterLeave: function () {
        window.portalQuizMediaCleanup = null;
      },
      shouldIgnoreLink: function (link) {
        return link.hasAttribute("data-manual-submit-btn");
      },
    });
  }

  function initManualQuizTake(root) {
    var submitBtns = Array.prototype.slice.call(root.querySelectorAll("[data-manual-submit-btn]"));
    var resultPanel = root.querySelector("[data-manual-result]");
    var submitUrl = root.getAttribute("data-submit-url");
    var timeLimitSec = parseInt(root.getAttribute("data-time-limit-sec") || "0", 10) || 0;
    var msgSubmitting = root.getAttribute("data-msg-submitting") || "Submitting…";
    var msgError = root.getAttribute("data-msg-error") || "Could not submit.";
    var msgSubmitLabel = root.getAttribute("data-msg-submit-label") || "Complete";
    var submitBtnHtml = submitBtns[0] ? submitBtns[0].innerHTML : "";
    var isListeningQuiz = root.getAttribute("data-quiz-listening") === "true";
    var startedAt = parseInt(root.dataset.manualQuizBootedAt || "", 10) || Date.now();
    var submitting = false;
    var submitted = false;
    var timerId = null;
    var timerValue = root.querySelector("[data-quiz-timer-value]");
    var timerWrap = root.querySelector("[data-quiz-timer]");
    var timerBar = root.querySelector("[data-quiz-timer-bar]");
    var timerBarFill = root.querySelector("[data-quiz-timer-bar-fill]");
    var timerToolbar = root.querySelector(".portal-quiz-take-toolbar--timed");
    var timerSpacer = root.querySelector(".portal-quiz-take-toolbar-spacer");

    initWritingAreas(root);
    initListeningPlayOnce(root);
    updateWritingUi(root);

    function setSubmittingState(active) {
      submitBtns.forEach(function (btn) {
        if (active) {
          btn.setAttribute("data-submitting", "true");
          btn.disabled = true;
          btn.textContent = msgSubmitting;
        } else {
          btn.removeAttribute("data-submitting");
          btn.disabled = false;
          btn.innerHTML = submitBtnHtml || ('<i class="bi bi-check2-circle me-1" aria-hidden="true"></i>' + msgSubmitLabel);
        }
      });
    }

    function syncTimerToolbarSpacer() {
      if (!timerToolbar || !timerSpacer) {
        return;
      }
      timerSpacer.style.height = timerToolbar.offsetHeight + "px";
    }

    function hideTimerToolbar() {
      if (timerToolbar) {
        timerToolbar.classList.add("is-hidden");
      }
      if (timerSpacer) {
        timerSpacer.hidden = true;
      }
    }

    function elapsedSeconds() {
      return Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    }

    function collectSubmissionPayload() {
      var questionIds = questionIdsInOrder(root);
      if (questionIds.length) {
        var answers = {};
        var orderedAnswers = [];
        questionIds.forEach(function (questionId) {
          var value = questionAnswerValue(root, questionId);
          orderedAnswers.push(value);
          answers[questionId] = value;
        });
        return {
          answers: answers,
          ordered_answers: orderedAnswers,
        };
      }

      var fields = submissionFields(root);
      var answers = {};
      var orderedAnswers = [];
      fields.forEach(function (field, index) {
        if (field.type === "radio" && !field.checked) {
          return;
        }
        var value = field.value || "";
        orderedAnswers.push(value);
        var questionId = field.getAttribute("data-question-id") || questionIds[index] || "";
        if (questionId) {
          answers[questionId] = value;
        }
      });

      if (Object.keys(answers).length) {
        return {
          answers: answers,
          ordered_answers: orderedAnswers,
        };
      }

      return { submission: fields[0] ? fields[0].value : "" };
    }

    function showManualResult(data) {
      hideTimerToolbar();
      root.setAttribute("data-quiz-finished", "true");
      root.querySelectorAll(
        ".panel, .portal-quiz-writing-stack, .portal-quiz-writing-card--solo, .portal-listening-stack, [data-quiz-take-actions-inline]"
      ).forEach(function (el) {
        if (!el.hasAttribute("data-manual-result") && !el.hasAttribute("data-quiz-take-actions")) {
          el.classList.add("d-none");
        }
      });
      var gate = document.querySelector("[data-quiz-start-gate]");
      if (gate) gate.classList.add("d-none");
      var leaveGate = document.querySelector("[data-quiz-leave-gate]");
      if (leaveGate) leaveGate.classList.add("d-none");
      root.querySelectorAll("[data-quiz-take-actions]").forEach(function (el) {
        el.classList.add("d-none");
        el.hidden = true;
      });
      if (resultPanel) {
        if (isListeningQuiz && data) {
          renderListeningResult(data);
        }
        resultPanel.classList.remove("d-none");
        resultPanel.hidden = false;
        if (!window.PortalQuizMockSection || !window.PortalQuizMockSection.isMockRoot(root)) {
          resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    }

    function resultPercentValue(data) {
      if (data.percent !== undefined && data.percent !== null) {
        return data.percent;
      }
      if (!data.max_score) {
        return 0;
      }
      return Math.round((100 * data.total_score) / data.max_score * 10) / 10;
    }

    function resultTimeUsedPercent(data) {
      if (!timeLimitSec) {
        return null;
      }
      var used = data.duration_sec;
      if (used === undefined || used === null) {
        used = elapsedSeconds();
      }
      return Math.round((used / timeLimitSec) * 100);
    }

    function renderListeningResult(data) {
      var resultScore = root.querySelector("[data-manual-result-score]");
      var resultPercent = root.querySelector("[data-manual-result-percent]");
      var resultDuration = root.querySelector("[data-manual-result-duration]");
      var durationWrap = root.querySelector("[data-manual-result-duration-wrap]");
      var resultList = root.querySelector("[data-manual-result-list]");
      var labelCorrect = root.getAttribute("data-label-correct") || "Correct";
      var labelIncorrect = root.getAttribute("data-label-incorrect") || "Incorrect";
      var labelUnanswered = root.getAttribute("data-label-unanswered") || "Not answered";

      if (resultScore) {
        resultScore.textContent = data.total_score + "/" + data.max_score;
      }
      if (resultPercent) {
        resultPercent.textContent = resultPercentValue(data) + "%";
      }
      if (resultDuration && durationWrap) {
        var timeUsedPct = resultTimeUsedPercent(data);
        if (timeUsedPct === null) {
          durationWrap.hidden = true;
        } else {
          durationWrap.hidden = false;
          resultDuration.textContent = timeUsedPct + "%";
        }
      }
      var questionRows = data.questions || data.breakdown;
      if (resultList && Array.isArray(questionRows)) {
        resultList.innerHTML = "";
        questionRows.forEach(function (item, index) {
          var row = document.createElement("div");
          row.className = "portal-quiz-take-result__item";
          var status = labelUnanswered;
          var tone = "muted";
          if (item.is_correct === true) {
            status = labelCorrect;
            tone = "success";
          } else if (item.is_correct === false) {
            status = labelIncorrect;
            tone = "danger";
          }
          row.innerHTML =
            '<span class="portal-quiz-take-result__num">' + (index + 1) + "</span>" +
            '<span class="portal-quiz-take-result__status text-' + tone + '">' + status + "</span>";
          resultList.appendChild(row);
        });
      }
    }

    function submitManual(options) {
      options = options || {};
      if (submitting || submitted || !submitUrl) {
        return Promise.resolve(false);
      }

      submitting = true;
      if (!options.silent) {
        setSubmittingState(true);
      }

      var requestBody = Object.assign(
        {
          duration_sec: Math.max(1, elapsedSeconds()),
          allow_empty: Boolean(options.allowEmpty),
          completion_trigger: options.completionTrigger || "manual",
        },
        collectSubmissionPayload()
      );
      var mockId = root.getAttribute("data-mock-id");
      if (mockId) {
        requestBody.mock = parseInt(mockId, 10);
      }

      return fetch(submitUrl, {
        method: "POST",
        credentials: "same-origin",
        keepalive: Boolean(options.keepalive),
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(requestBody),
      })
        .then(function (response) {
          var contentType = (response.headers.get("content-type") || "").toLowerCase();
          if (contentType.indexOf("application/json") === -1) {
            return response.text().then(function (body) {
              var snippet = (body || "").replace(/\s+/g, " ").trim().slice(0, 160);
              if (/portal-login-html|\/portal\/login/i.test(snippet)) {
                throw new Error(
                  (document.querySelector("[data-quiz-start-gate]")
                    && document.querySelector("[data-quiz-start-gate]").getAttribute("data-msg-session-expired"))
                  || "Your session has expired. Please log in again."
                );
              }
              throw new Error(msgError);
            });
          }
          return response.json().then(function (data) {
            return { ok: response.ok, data: data || {} };
          });
        })
        .then(function (payload) {
          if (payload.data && (payload.data.code === "auth_required" || payload.data.code === "stale_session")) {
            window.alert(payload.data.error || "Your session has expired. Please log in again.");
            if (payload.data.login_url) {
              window.location.href = payload.data.login_url;
            }
            submitting = false;
            return false;
          }
          if (!payload.ok || !payload.data.success) {
            if (window.PortalQuizMockSection && window.PortalQuizMockSection.redirectIfNeeded(payload.data)) {
              return false;
            }
            throw new Error((payload.data && payload.data.error) || msgError);
          }
          if (payload.data.mock_continue && payload.data.next_url) {
            submitted = true;
            submitting = false;
            stopQuizMedia(root);
            if (timerId) window.clearInterval(timerId);
            if (
              window.PortalQuizMockSection
              && window.PortalQuizMockSection.handleSubmitResponse(root, payload.data, showManualResult)
            ) {
              return true;
            }
          }
          submitted = true;
          submitting = false;
          stopQuizMedia(root);
          if (timerId) window.clearInterval(timerId);
          if (!options.silent) {
            showManualResult(payload.data);
          } else {
            root.setAttribute("data-quiz-finished", "true");
          }
          return true;
        })
        .catch(function (err) {
          if (!options.silent) {
            window.alert(err.message || msgError);
            submitting = false;
            setSubmittingState(false);
          } else {
            submitting = false;
          }
          return false;
        });
    }

    function updateTimer() {
      if (!timeLimitSec) return;
      var remaining = Math.max(0, timeLimitSec - elapsedSeconds());
      if (timerValue) timerValue.textContent = formatDuration(remaining);
      if (timerBarFill) {
        var pct = Math.max(0, Math.min(100, (remaining / timeLimitSec) * 100));
        timerBarFill.style.width = pct + "%";
        timerBarFill.classList.toggle("is-low", pct <= 25 && pct > 10);
        timerBarFill.classList.toggle("is-critical", pct <= 10);
      }
      if (remaining <= 0) {
        if (timerId) window.clearInterval(timerId);
        submitManual({ allowEmpty: true, completionTrigger: "time_limit" });
      }
    }

    if (timeLimitSec > 0) {
      if (timerWrap) timerWrap.hidden = false;
      if (timerBar) timerBar.hidden = false;
      syncTimerToolbarSpacer();
      window.addEventListener("resize", syncTimerToolbarSpacer);
      updateTimer();
      timerId = window.setInterval(updateTimer, 1000);
    }

    submitBtns.forEach(function (submitBtn) {
      submitBtn.addEventListener("click", function () {
        submitManual({ allowEmpty: true, completionTrigger: "manual" });
      });
    });

    initQuizLeaveGuard(root, submitManual);
  }

  function scheduleManualQuizTake() {
    var root = document.querySelector("[data-quiz-manual-take]");
    if (!root || root.dataset.manualQuizBound === "true") {
      return;
    }
    root.dataset.manualQuizBound = "true";

    function boot() {
      root.setAttribute("data-quiz-started", "true");
      root.dataset.manualQuizBootedAt = String(Date.now());
      initManualQuizTake(root);
    }

    if (document.querySelector("[data-quiz-start-gate]")) {
      document.addEventListener("portal-quiz-started", boot, { once: true });
      return;
    }

    boot();
  }

  document.addEventListener("DOMContentLoaded", scheduleManualQuizTake);
  document.addEventListener("portal:content-loaded", scheduleManualQuizTake);
})();

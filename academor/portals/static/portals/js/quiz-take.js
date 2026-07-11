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

  function initQuizTake(root) {
    var form = root.querySelector("[data-quiz-take-form]");
    var finishBtn = root.querySelector("[data-quiz-finish-btn]");
    var resultPanel = root.querySelector("[data-quiz-result]");
    var resultScore = root.querySelector("[data-quiz-result-score]");
    var resultPercent = root.querySelector("[data-quiz-result-percent]");
    var resultDuration = root.querySelector("[data-quiz-result-duration]");
    var resultList = root.querySelector("[data-quiz-result-list]");
    var submitUrl = root.getAttribute("data-submit-url");
    var timeLimitSec = parseInt(root.getAttribute("data-time-limit-sec") || "0", 10) || 0;
    var labelCorrect = root.getAttribute("data-label-correct") || "Correct";
    var labelIncorrect = root.getAttribute("data-label-incorrect") || "Incorrect";
    var labelUnanswered = root.getAttribute("data-label-unanswered") || "Not answered";
    var msgSubmitting = root.getAttribute("data-msg-submitting") || "Submitting…";
    var msgError = root.getAttribute("data-msg-error") || "Could not submit the test.";

    var startedAt = Date.now();
    var submitting = false;
    var submitted = false;
    var timerId = null;
    var finishBtnHtml = finishBtn ? finishBtn.innerHTML : "";

    var timerWrap = root.querySelector("[data-quiz-timer]");
    var timerValue = root.querySelector("[data-quiz-timer-value]");
    var timerBar = root.querySelector("[data-quiz-timer-bar]");
    var timerBarFill = root.querySelector("[data-quiz-timer-bar-fill]");
    var timerToolbar = root.querySelector(".portal-quiz-take-toolbar--timed");
    var timerSpacer = root.querySelector(".portal-quiz-take-toolbar-spacer");

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

    function collectAnswers() {
      var answers = {};
      root.querySelectorAll("[data-quiz-question-card]").forEach(function (card) {
        var input = card.querySelector(".portal-quiz-play-option__input:checked");
        var name = input ? input.getAttribute("name") : "";
        var match = name && name.match(/quiz-q-(\d+)/);
        if (match) {
          answers[match[1]] = parseInt(input.value, 10);
        }
      });
      return answers;
    }

    function elapsedSeconds() {
      return Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    }

    function setSubmittingState(active) {
      submitting = active;
      if (finishBtn) {
        finishBtn.disabled = active || submitted;
        finishBtn.innerHTML = active ? msgSubmitting : finishBtnHtml;
      }
      root.querySelectorAll(".portal-quiz-play-option__input").forEach(function (input) {
        input.disabled = active || submitted;
      });
    }

    function resultPercentValue(data) {
      if (data.percent !== null && data.percent !== undefined && !isNaN(data.percent)) {
        return Number(data.percent);
      }
      var maxScore = Number(data.max_score);
      var totalScore = Number(data.total_score);
      if (!maxScore || isNaN(totalScore)) {
        return 0;
      }
      return Math.round((100 * totalScore / maxScore) * 10) / 10;
    }

    function resultTimeUsedPercent(data) {
      if (!timeLimitSec) {
        return null;
      }
      var duration = Number(data.duration_sec);
      if (isNaN(duration) || duration < 0) {
        duration = elapsedSeconds();
      }
      return Math.min(100, Math.round((duration / timeLimitSec) * 100));
    }

    function renderResult(data) {
      if (!resultPanel) {
        return;
      }
      if (form) {
        form.classList.add("d-none");
      }
      var notice = document.querySelector("[data-quiz-start-gate]");
      if (notice) {
        notice.classList.add("d-none");
      }
      var leaveGate = document.querySelector("[data-quiz-leave-gate]");
      if (leaveGate) {
        leaveGate.classList.add("d-none");
      }
      if (timerWrap) {
        timerWrap.hidden = true;
      }
      if (timerBar) {
        timerBar.hidden = true;
      }
      hideTimerToolbar();

      if (resultScore) {
        resultScore.textContent = data.total_score + "/" + data.max_score;
      }
      if (resultPercent) {
        resultPercent.textContent = resultPercentValue(data) + "%";
      }
      var durationWrap = root.querySelector("[data-quiz-result-duration-wrap]");
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
          if (item.selected_index === null || item.selected_index === undefined) {
            status = labelUnanswered;
            tone = "muted";
          } else if (item.is_correct) {
            status = labelCorrect;
            tone = "success";
          } else {
            status = labelIncorrect;
            tone = "danger";
          }
          row.innerHTML =
            '<span class="portal-quiz-take-result__num">' + (index + 1) + "</span>" +
            '<span class="portal-quiz-take-result__status text-' + tone + '">' + status + "</span>";
          resultList.appendChild(row);
        });
      }

      resultPanel.classList.remove("d-none");
      resultPanel.hidden = false;
      resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      root.setAttribute("data-quiz-finished", "true");
    }

    function submitQuiz(options) {
      options = options || {};
      if (submitting || submitted || !submitUrl) {
        return Promise.resolve(false);
      }
      submitting = true;
      if (!options.silent) {
        setSubmittingState(true);
      }

      return fetch(submitUrl, {
        method: "POST",
        credentials: "same-origin",
        keepalive: Boolean(options.keepalive),
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          answers: collectAnswers(),
          duration_sec: elapsedSeconds(),
          completion_trigger: options.completionTrigger || "manual",
          mock: root.getAttribute("data-mock-id") || undefined,
        }),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (payload) {
          if (!payload.ok || !payload.data.success) {
            if (window.PortalQuizMockSection && window.PortalQuizMockSection.redirectIfNeeded(payload.data)) {
              return false;
            }
            throw new Error((payload.data && payload.data.error) || msgError);
          }
          if (payload.data.mock_continue && payload.data.next_url) {
            submitted = true;
            submitting = false;
            if (timerId) {
              window.clearInterval(timerId);
            }
            if (
              window.PortalQuizMockSection
              && window.PortalQuizMockSection.handleSubmitResponse(root, payload.data, renderResult)
            ) {
              return true;
            }
          }
          submitted = true;
          submitting = false;
          if (timerId) {
            window.clearInterval(timerId);
          }
          renderResult(payload.data);
          return true;
        })
        .catch(function (err) {
          if (!options.silent) {
            window.alert((err && err.message) || msgError);
            setSubmittingState(false);
          }
          submitting = false;
          return false;
        });
    }

    function updateTimer() {
      if (!timeLimitSec) {
        return;
      }
      var elapsed = elapsedSeconds();
      var remaining = Math.max(0, timeLimitSec - elapsed);
      if (timerValue) {
        timerValue.textContent = formatDuration(remaining);
      }
      if (timerBarFill) {
        var pct = Math.max(0, Math.min(100, (remaining / timeLimitSec) * 100));
        timerBarFill.style.width = pct + "%";
        timerBarFill.classList.toggle("is-low", pct <= 25 && pct > 10);
        timerBarFill.classList.toggle("is-critical", pct <= 10);
      }
      if (remaining <= 0) {
        if (timerId) {
          window.clearInterval(timerId);
        }
        submitQuiz({ completionTrigger: "time_limit" });
      }
    }

    if (timeLimitSec > 0) {
      if (timerWrap) {
        timerWrap.hidden = false;
      }
      if (timerBar) {
        timerBar.hidden = false;
      }
      syncTimerToolbarSpacer();
      window.addEventListener("resize", syncTimerToolbarSpacer);
      updateTimer();
      timerId = window.setInterval(updateTimer, 1000);
    }

    if (finishBtn) {
      finishBtn.addEventListener("click", function () {
        submitQuiz({ completionTrigger: "manual" });
      });
    }

    if (window.PortalQuizLeaveGuard) {
      window.PortalQuizLeaveGuard.init({
        root: root,
        submit: submitQuiz,
        shouldIgnoreLink: function (link) {
          return link.hasAttribute("data-quiz-finish-btn");
        },
      });
    }

    root.querySelectorAll(".portal-quiz-play-option__input").forEach(function (input) {
      input.addEventListener("change", function () {
        var card = input.closest("[data-quiz-question-card]");
        if (!card) {
          return;
        }
        card.querySelectorAll(".portal-quiz-play-option").forEach(function (option) {
          option.classList.toggle(
            "is-selected",
            option.contains(input) && input.checked
          );
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-quiz-take]");
    if (!root) {
      return;
    }

    function boot() {
      root.setAttribute("data-quiz-started", "true");
      initQuizTake(root);
    }

    if (document.querySelector("[data-quiz-start-gate]")) {
      document.addEventListener("portal-quiz-started", boot, { once: true });
      return;
    }

    boot();
  });
})();

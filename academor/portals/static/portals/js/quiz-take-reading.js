(function () {
  "use strict";

  function onReady(fn) {
    if (window.portalOnReady) {
      window.portalOnReady(fn);
      return;
    }
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

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

  function initQuizReadingTake(root) {
    if (!root || root.dataset.quizReadingBound === "true") {
      return;
    }
    root.dataset.quizReadingBound = "true";

    var form = root.querySelector("[data-quiz-take-form]");
    var finishBtn = root.querySelector("[data-quiz-finish-btn]");
    var resultPanel = root.querySelector("[data-quiz-result]");
    var resultScore = root.querySelector("[data-quiz-result-score]");
    var resultPercent = root.querySelector("[data-quiz-result-percent]");
    var resultDuration = root.querySelector("[data-quiz-result-duration]");
    var resultList = root.querySelector("[data-quiz-result-list]");
    var resultStats = root.querySelector("[data-quiz-result-stats]");
    var resultPending = root.querySelector("[data-quiz-result-pending]");
    var resultEyebrow = root.querySelector("[data-quiz-result-eyebrow]");
    var submitUrl = root.getAttribute("data-submit-url");
    var timeLimitSec = parseInt(root.getAttribute("data-time-limit-sec") || "0", 10) || 0;
    var labelCorrect = root.getAttribute("data-label-correct") || "Correct";
    var labelIncorrect = root.getAttribute("data-label-incorrect") || "Incorrect";
    var labelUnanswered = root.getAttribute("data-label-unanswered") || "Not answered";
    var msgSubmitting = root.getAttribute("data-msg-submitting") || "Submitting…";
    var msgError = root.getAttribute("data-msg-error") || "Could not submit the test.";
    var msgSessionExpired =
      root.getAttribute("data-msg-session-expired")
      || (document.querySelector("[data-quiz-start-gate]")
        && document.querySelector("[data-quiz-start-gate]").getAttribute("data-msg-session-expired"))
      || "Your session has expired. Please log in again.";
    var labelPinPassage = root.getAttribute("data-label-pin-passage") || "Pin passage";
    var labelUnpinPassage = root.getAttribute("data-label-unpin-passage") || "Unpin passage";
    var quizId = root.getAttribute("data-quiz-id") || "0";
    var passagePinStorageKey = "portal-reading-passage-pinned:" + quizId;

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
    var readingTabs = root.querySelector("[data-reading-tabs]");
    var readingTabsNav = root.querySelector(".portal-reading-tabs__nav");

    function isPassagePinned() {
      try {
        return window.sessionStorage.getItem(passagePinStorageKey) === "1";
      } catch (error) {
        return false;
      }
    }

    function setPassagePinned(pinned) {
      try {
        if (pinned) {
          window.sessionStorage.setItem(passagePinStorageKey, "1");
        } else {
          window.sessionStorage.removeItem(passagePinStorageKey);
        }
      } catch (error) {
        /* ignore */
      }
      syncPassagePinState();
    }

    function syncPassagePinButton(section, pinned) {
      if (!section) {
        return;
      }
      var btn = section.querySelector("[data-reading-pin-passage]");
      if (!btn) {
        return;
      }
      var label = btn.querySelector("[data-reading-pin-label]");
      var icon = btn.querySelector("[data-reading-pin-icon]");
      btn.setAttribute("aria-pressed", pinned ? "true" : "false");
      btn.classList.toggle("is-active", pinned);
      if (label) {
        label.textContent = pinned ? labelUnpinPassage : labelPinPassage;
      }
      if (icon) {
        icon.classList.toggle("bi-pin-angle", !pinned);
        icon.classList.toggle("bi-pin-angle-fill", pinned);
      }
    }

    function syncPassagePinState() {
      var pinned = isPassagePinned();
      root.querySelectorAll(".portal-reading-section").forEach(function (section) {
        section.classList.toggle("is-passage-pinned", pinned);
        syncPassagePinButton(section, pinned);
      });
      syncReturnButton();
    }

    function getActiveReturnControls() {
      var panel = getActiveReadingPanel();
      if (!panel) {
        return { btn: null, bar: null };
      }
      return {
        btn: panel.querySelector("[data-reading-return-btn]"),
        bar: panel.querySelector("[data-reading-return-bar]"),
      };
    }

    function setReturnVisible(visible) {
      var controls = getActiveReturnControls();
      if (controls.bar) {
        controls.bar.hidden = !visible;
      } else if (controls.btn) {
        controls.btn.hidden = !visible;
      }
    }

    function getActiveReadingPanel() {
      if (readingTabs) {
        var activeTab = readingTabs.querySelector(".tab-pane.active");
        if (activeTab) {
          return activeTab;
        }
        return readingTabs.querySelector(".portal-reading-section");
      }
      return root.querySelector(".portal-reading-section");
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

    function syncReadingTabMetrics() {
      if (!readingTabs || !readingTabsNav) {
        return;
      }
      readingTabs.style.setProperty("--reading-tab-nav-height", readingTabsNav.offsetHeight + "px");
    }

    function scrollToReadingPanel(panel) {
      if (!panel) {
        return;
      }
      var rect = panel.getBoundingClientRect();
      var topOffset = 16;
      if (timerToolbar && !timerToolbar.classList.contains("is-hidden")) {
        topOffset += timerToolbar.offsetHeight;
      }
      if (readingTabsNav) {
        topOffset += readingTabsNav.offsetHeight;
      }
      var targetY = window.scrollY + rect.top - topOffset;
      window.scrollTo({
        top: Math.max(0, targetY),
        behavior: "smooth",
      });
    }

    function getActivePassage() {
      var panel = getActiveReadingPanel();
      return panel ? panel.querySelector(".portal-reading-section__passage") : null;
    }

    function scrollToActivePassage() {
      var passage = getActivePassage();
      if (!passage) {
        return;
      }
      var rect = passage.getBoundingClientRect();
      var topOffset = 16;
      if (timerToolbar && !timerToolbar.classList.contains("is-hidden")) {
        topOffset += timerToolbar.offsetHeight;
      }
      if (readingTabsNav) {
        topOffset += readingTabsNav.offsetHeight;
      }
      window.scrollTo({
        top: Math.max(0, window.scrollY + rect.top - topOffset),
        behavior: "smooth",
      });
    }

    function syncReturnButton() {
      if (isPassagePinned()) {
        root.querySelectorAll("[data-reading-return-bar]").forEach(function (bar) {
          bar.hidden = true;
        });
        return;
      }
      root.querySelectorAll("[data-reading-return-bar]").forEach(function (bar) {
        bar.hidden = true;
      });
      var controls = getActiveReturnControls();
      if (!controls.btn && !controls.bar) {
        return;
      }
      var passage = getActivePassage();
      if (!passage || submitted) {
        setReturnVisible(false);
        return;
      }
      var rect = passage.getBoundingClientRect();
      setReturnVisible(rect.top < -120 || rect.bottom < 120);
    }

    function collectAnswers() {
      var answers = {};
      root.querySelectorAll("[data-reading-answer]").forEach(function (input) {
        var questionId = input.getAttribute("data-question-id");
        if (!questionId) {
          return;
        }
        if (input.type === "radio") {
          if (input.checked) {
            answers[questionId] = parseInt(input.value, 10);
          }
        } else if ((input.value || "").trim()) {
          answers[questionId] = input.value.trim();
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
      root.querySelectorAll("[data-reading-answer]").forEach(function (input) {
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
      setReturnVisible(false);

      if (resultStats) {
        resultStats.classList.toggle("d-none", !!data.pending_review);
      }
      if (resultEyebrow) {
        resultEyebrow.classList.toggle("d-none", !!data.pending_review);
      }
      if (resultPending) {
        resultPending.classList.toggle("d-none", !data.pending_review);
      }

      if (resultScore && !data.pending_review) {
        resultScore.textContent = data.total_score + "/" + data.max_score;
      }
      if (resultPercent && !data.pending_review) {
        resultPercent.textContent = resultPercentValue(data) + "%";
      }
      var durationWrap = root.querySelector("[data-quiz-result-duration-wrap]");
      if (resultDuration && durationWrap) {
        if (data.pending_review) {
          durationWrap.hidden = true;
        } else {
        var timeUsedPct = resultTimeUsedPercent(data);
        if (timeUsedPct === null) {
          durationWrap.hidden = true;
        } else {
          durationWrap.hidden = false;
          resultDuration.textContent = timeUsedPct + "%";
        }
        }
      }
      var questionRows = data.questions || data.breakdown;
      if (resultList && Array.isArray(questionRows) && !data.pending_review) {
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
          } else if (item.student_answer !== undefined && item.student_answer !== null && item.student_answer !== "") {
            status = item.is_correct ? labelCorrect : labelIncorrect;
            tone = item.is_correct ? "success" : "danger";
          }
          var displayNumber = item.number || item.order || (index + 1);
          row.innerHTML =
            '<span class="portal-quiz-take-result__num">' + displayNumber + "</span>" +
            '<span class="portal-quiz-take-result__status text-' + tone + '">' + status + "</span>";
          resultList.appendChild(row);
        });
      } else if (resultList) {
        resultList.innerHTML = "";
      }

      resultPanel.classList.remove("d-none");
      resultPanel.hidden = false;
      if (!window.PortalQuizMockSection || !window.PortalQuizMockSection.isMockRoot(root)) {
        resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      root.setAttribute("data-quiz-finished", "true");
    }

    function parseJsonResponse(response) {
      var contentType = (response.headers.get("content-type") || "").toLowerCase();
      if (contentType.indexOf("application/json") === -1) {
        return response.text().then(function (body) {
          var snippet = (body || "").replace(/\s+/g, " ").trim().slice(0, 160);
          if (/portal-login-html|\/portal\/login/i.test(snippet)) {
            throw new Error(msgSessionExpired);
          }
          throw new Error(
            snippet
              ? msgError + " (" + response.status + ": " + snippet + ")"
              : msgError + " (" + response.status + ")"
          );
        });
      }
      return response.json().then(function (data) {
        return { ok: response.ok, data: data || {} };
      });
    }

    function handleAuthFailure(data) {
      if (!data || (data.code !== "auth_required" && data.code !== "stale_session")) {
        return false;
      }
      window.alert(data.error || msgSessionExpired);
      if (data.login_url) {
        window.location.href = data.login_url;
      }
      return true;
    }

    function submitQuiz(options) {
      options = options || {};
      if (submitting || submitted || !submitUrl) {
        return Promise.resolve({ ok: false });
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
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          answers: collectAnswers(),
          duration_sec: elapsedSeconds(),
          completion_trigger: options.completionTrigger || "manual",
          mock: root.getAttribute("data-mock-id") || undefined,
        }),
      })
        .then(parseJsonResponse)
        .then(function (payload) {
          if (handleAuthFailure(payload.data)) {
            submitting = false;
            return { ok: false };
          }
          if (!payload.ok || !payload.data.success) {
            if (window.PortalQuizMockSection && window.PortalQuizMockSection.redirectIfNeeded(payload.data)) {
              return { ok: false, redirected: true };
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
              return { ok: true };
            }
          }
          submitted = true;
          submitting = false;
          if (timerId) {
            window.clearInterval(timerId);
          }
          renderResult(payload.data);
          return { ok: true };
        })
        .catch(function (err) {
          var errorMessage = (err && err.message) || msgError;
          if (!options.silent) {
            window.alert(errorMessage);
            setSubmittingState(false);
          }
          submitting = false;
          return Promise.resolve({ ok: false, error: errorMessage });
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
      syncReadingTabMetrics();
      window.addEventListener("resize", syncTimerToolbarSpacer);
      window.addEventListener("resize", syncReadingTabMetrics);
      window.addEventListener("resize", syncReturnButton);
      window.addEventListener("scroll", syncReturnButton, { passive: true });
      updateTimer();
      timerId = window.setInterval(updateTimer, 1000);
    } else {
      syncReadingTabMetrics();
      window.addEventListener("resize", syncReadingTabMetrics);
      window.addEventListener("resize", syncReturnButton);
      window.addEventListener("scroll", syncReturnButton, { passive: true });
    }

    if (finishBtn) {
      finishBtn.addEventListener("click", function () {
        submitQuiz({ completionTrigger: "manual" });
      });
    }

    root.addEventListener("click", function (event) {
      var pinBtn = event.target.closest("[data-reading-pin-passage]");
      if (pinBtn && root.contains(pinBtn)) {
        event.preventDefault();
        setPassagePinned(!isPassagePinned());
        return;
      }

      var btn = event.target.closest("[data-reading-return-btn]");
      if (btn && root.contains(btn)) {
        event.preventDefault();
        scrollToActivePassage();
      }
    });

    root.querySelectorAll(".portal-quiz-play-option__input, input[data-reading-answer]").forEach(function (input) {
      input.addEventListener("keydown", function (event) {
        if (
          event.key === "ArrowUp" ||
          event.key === "ArrowDown" ||
          event.key === "ArrowLeft" ||
          event.key === "ArrowRight"
        ) {
          event.preventDefault();
        }
      });
    });

    if (window.PortalQuizLeaveGuard) {
      window.PortalQuizLeaveGuard.init({
        root: root,
        submit: function (options) {
          return submitQuiz(options).then(function (result) {
            if (result && result.ok) {
              return true;
            }
            if (result && result.error && options && options.silent && root) {
              root.setAttribute("data-msg-error", result.error);
            }
            return false;
          });
        },
        shouldIgnoreLink: function (link) {
          return link.hasAttribute("data-quiz-finish-btn");
        },
      });
    }

    if (readingTabs) {
      readingTabs.addEventListener("shown.bs.tab", function (event) {
        var panel = event.target && document.querySelector(event.target.getAttribute("data-bs-target"));
        if (panel) {
          syncReadingTabMetrics();
          window.requestAnimationFrame(function () {
            scrollToReadingPanel(panel);
            syncPassagePinState();
            window.requestAnimationFrame(syncReturnButton);
          });
        }
      });
    }

    syncPassagePinState();
    syncReturnButton();
  }

  onReady(function () {
    var root = document.querySelector("[data-quiz-reading-take]");
    if (!root) {
      return;
    }

    function boot() {
      root.setAttribute("data-quiz-started", "true");
      initQuizReadingTake(root);
    }

    if (document.querySelector("[data-quiz-start-gate]")) {
      document.addEventListener("portal-quiz-started", boot, { once: true });
      return;
    }

    boot();
  });
})();

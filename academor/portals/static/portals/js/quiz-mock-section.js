(function () {
  "use strict";

  function hideDefaultResultActions() {
    document.querySelectorAll("[data-mock-default-actions]").forEach(function (node) {
      node.hidden = true;
      node.classList.add("d-none");
    });
  }

  function scrollMockPageToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function formatRestTime(totalSeconds) {
    var safe = Math.max(0, Math.floor(Number(totalSeconds) || 0));
    var minutes = Math.floor(safe / 60);
    var seconds = safe % 60;
    return String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
  }

  function fillSectionPlaceholder(template, sectionLabel) {
    if (!template) {
      return "";
    }
    return String(template).split("{section}").join(sectionLabel || "");
  }

  function clearRestTimer(panel) {
    var timerId = panel && panel._mockRestTimerId;
    if (timerId) {
      clearInterval(timerId);
      panel._mockRestTimerId = null;
    }
  }

  function startRestCountdown(panel, data) {
    var restSeconds = Number(data && data.mock_rest_seconds);
    if (!panel || !data || !data.next_url || !(restSeconds > 0)) {
      return false;
    }

    clearRestTimer(panel);

    var restBlock = panel.querySelector("[data-mock-section-rest]");
    var warningNode = panel.querySelector("[data-mock-section-rest-warning]");
    var labelNode = panel.querySelector("[data-mock-section-rest-label]");
    var timerNode = panel.querySelector("[data-mock-section-rest-timer]");
    var button = panel.querySelector("[data-mock-section-continue-btn]");
    var sectionLabel = data.mock_next_section_label || "";
    var warningTpl = panel.getAttribute("data-msg-rest-warning") || "";
    var remainingLabel = panel.getAttribute("data-label-rest-remaining") || "";
    var startLabel = panel.getAttribute("data-label-start") || "Start now";
    var remaining = Math.floor(restSeconds);
    var navigated = false;

    if (warningNode) {
      warningNode.textContent = fillSectionPlaceholder(warningTpl, sectionLabel);
    }
    if (labelNode) {
      labelNode.textContent = remainingLabel;
    }
    if (button) {
      button.textContent = startLabel;
    }

    function goNext() {
      if (navigated) {
        return;
      }
      navigated = true;
      clearRestTimer(panel);
      window.location.replace(data.next_url);
    }

    function tick() {
      if (timerNode) {
        timerNode.textContent = formatRestTime(remaining);
      }
      if (remaining <= 0) {
        goNext();
        return;
      }
      remaining -= 1;
    }

    if (button) {
      button.onclick = goNext;
    }

    if (restBlock) {
      restBlock.classList.remove("d-none");
      restBlock.hidden = false;
    }

    tick();
    panel._mockRestTimerId = setInterval(tick, 1000);
    return true;
  }

  function offerContinue(data) {
    var panel = document.querySelector("[data-mock-section-continue]");
    if (!panel || !data || !data.mock_continue || !data.next_url) {
      return false;
    }

    clearRestTimer(panel);

    var messageNode = panel.querySelector("[data-mock-section-continue-message]");
    var titleNode = panel.querySelector("[data-mock-section-continue-title]");
    var button = panel.querySelector("[data-mock-section-continue-btn]");
    var restBlock = panel.querySelector("[data-mock-section-rest]");
    var nextLabel = panel.getAttribute("data-label-next") || "Next section";
    var finishLabel = panel.getAttribute("data-label-finish") || "";
    var sectionDoneMsg = panel.getAttribute("data-msg-section-done") || "";
    var mockDoneMsg = panel.getAttribute("data-msg-mock-done") || "";

    if (restBlock) {
      restBlock.classList.add("d-none");
      restBlock.hidden = true;
    }

    if (messageNode) {
      if (data.mock_completed) {
        messageNode.textContent = mockDoneMsg;
      } else if (data.mock_next_section_label) {
        messageNode.textContent = data.mock_continue_message || sectionDoneMsg;
      } else {
        messageNode.textContent = sectionDoneMsg;
      }
    }

    if (titleNode) {
      titleNode.textContent = data.mock_completed
        ? (panel.getAttribute("data-title-finish") || titleNode.textContent)
        : (panel.getAttribute("data-title-next") || titleNode.textContent);
    }

    if (button) {
      button.textContent = data.mock_completed ? finishLabel : nextLabel;
      button.onclick = function () {
        clearRestTimer(panel);
        window.location.replace(data.next_url);
      };
    }

    if (!data.mock_completed) {
      startRestCountdown(panel, data);
    }

    hideDefaultResultActions();
    panel.classList.remove("d-none");
    panel.hidden = false;
    return true;
  }

  window.PortalQuizMockSection = {
    redirectIfNeeded: function (data) {
      if (data && data.redirect_url) {
        window.location.href = data.redirect_url;
        return true;
      }
      return false;
    },
    offerContinue: offerContinue,
    isMockRoot: function (root) {
      return Boolean(root && root.getAttribute("data-mock-id"));
    },
    handleSubmitResponse: function (root, data, renderResult) {
      if (!this.isMockRoot(root) || !data || !data.mock_continue || !data.next_url) {
        return false;
      }
      if (typeof renderResult === "function") {
        renderResult(data);
      }
      var offered = offerContinue(data);
      if (offered) {
        requestAnimationFrame(function () {
          scrollMockPageToTop();
        });
      }
      return offered;
    },
  };
})();

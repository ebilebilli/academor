(function () {
  "use strict";

  function hideDefaultResultActions() {
    document.querySelectorAll("[data-mock-default-actions]").forEach(function (node) {
      node.hidden = true;
      node.classList.add("d-none");
    });
  }

  function offerContinue(data) {
    var panel = document.querySelector("[data-mock-section-continue]");
    if (!panel || !data || !data.mock_continue || !data.next_url) {
      return false;
    }

    var messageNode = panel.querySelector("[data-mock-section-continue-message]");
    var titleNode = panel.querySelector("[data-mock-section-continue-title]");
    var button = panel.querySelector("[data-mock-section-continue-btn]");
    var nextLabel = panel.getAttribute("data-label-next") || "Next section";
    var finishLabel = panel.getAttribute("data-label-finish") || "View summary";
    var sectionDoneMsg = panel.getAttribute("data-msg-section-done") || "";
    var mockDoneMsg = panel.getAttribute("data-msg-mock-done") || "";

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
        window.location.replace(data.next_url);
      };
    }

    hideDefaultResultActions();
    panel.classList.remove("d-none");
    panel.hidden = false;
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
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
      return offerContinue(data);
    },
  };
})();

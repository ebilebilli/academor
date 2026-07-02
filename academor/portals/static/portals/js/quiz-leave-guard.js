(function () {
  "use strict";

  function getBootstrapModal(modalEl) {
    if (!modalEl || !window.bootstrap || !window.bootstrap.Modal) {
      return null;
    }
    return window.bootstrap.Modal.getOrCreateInstance(modalEl, {
      backdrop: "static",
      keyboard: false,
    });
  }

  function initQuizLeaveGuard(options) {
    var root = options.root;
    var submit = options.submit;
    var beforeLeave = typeof options.beforeLeave === "function" ? options.beforeLeave : function () {};
    var afterLeave = typeof options.afterLeave === "function" ? options.afterLeave : function () {};
    var shouldIgnoreLink =
      typeof options.shouldIgnoreLink === "function"
        ? options.shouldIgnoreLink
        : function () {
            return false;
          };

    var leaveModalEl = document.querySelector("[data-quiz-leave-gate]");
    if (!leaveModalEl || !root || typeof submit !== "function") {
      return;
    }

    var leaveModal = getBootstrapModal(leaveModalEl);
    var confirmBtn = leaveModalEl.querySelector("[data-quiz-leave-confirm-btn]");
    var cancelBtn = leaveModalEl.querySelector("[data-quiz-leave-cancel-btn]");
    var pendingUrl = "";
    var navigationAllowed = false;
    var leaveWarning =
      root.getAttribute("data-msg-leave-warning") ||
      "If you leave this page now, your quiz will be counted as completed.";

    function isQuizActive() {
      return root.getAttribute("data-quiz-started") === "true" && root.getAttribute("data-quiz-finished") !== "true";
    }

    function showLeaveModal(targetUrl) {
      pendingUrl = targetUrl || "";
      if (leaveModal) {
        if (leaveModalEl.parentElement !== document.body) {
          document.body.appendChild(leaveModalEl);
        }
        leaveModalEl.hidden = false;
        leaveModalEl.removeAttribute("hidden");
        leaveModalEl.classList.remove("d-none");
        leaveModal.show();
        document.body.classList.add("portal-quiz-modal-open");
        return;
      }
      if (window.confirm(leaveWarning)) {
        completeAndNavigate(pendingUrl);
      }
    }

    function hideLeaveModal() {
      pendingUrl = "";
      if (leaveModal) {
        leaveModal.hide();
      }
      document.body.classList.remove("portal-quiz-modal-open");
    }

    function completeAndNavigate(targetUrl) {
      beforeLeave();
      submit({ keepalive: false, silent: true, completionTrigger: "auto_leave" }).then(function (ok) {
        if (!ok) {
          return;
        }
        navigationAllowed = true;
        afterLeave();
        root.setAttribute("data-quiz-finished", "true");
        if (targetUrl) {
          window.location.href = targetUrl;
        }
      });
    }

    document.addEventListener("portal:before-navigate", function (event) {
      if (!isQuizActive() || navigationAllowed) {
        return;
      }
      event.preventDefault();
      if (event.detail && event.detail.push === false) {
        window.history.pushState(
          Object.assign({}, window.history.state, { portalAjax: true, url: window.location.href }),
          "",
          window.location.href
        );
      }
      showLeaveModal(event.detail ? event.detail.url : "");
    });

    if (confirmBtn) {
      confirmBtn.addEventListener("click", function () {
        var targetUrl = pendingUrl;
        hideLeaveModal();
        completeAndNavigate(targetUrl);
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener("click", hideLeaveModal);
    }

    document.addEventListener(
      "click",
      function (event) {
        if (!isQuizActive() || navigationAllowed) {
          return;
        }
        var link = event.target.closest("a[href]");
        if (!link || link.hasAttribute("data-quiz-leave-confirm-btn")) {
          return;
        }
        if (shouldIgnoreLink(link)) {
          return;
        }
        if (leaveModalEl.contains(link)) {
          return;
        }
        var href = link.getAttribute("href") || "";
        if (!href || href.charAt(0) === "#" || href.indexOf("javascript:") === 0) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        showLeaveModal(link.href);
      },
      true
    );

    window.addEventListener("beforeunload", function (event) {
      if (!isQuizActive() || navigationAllowed) {
        return;
      }
      event.preventDefault();
      event.returnValue = leaveWarning;
      return leaveWarning;
    });

    root.querySelectorAll("[data-quiz-leave-link]").forEach(function (link) {
      link.addEventListener("click", function (event) {
        if (!isQuizActive() || navigationAllowed) {
          return;
        }
        event.preventDefault();
        showLeaveModal(link.href);
      });
    });

    window.addEventListener("pagehide", function () {
      if (!isQuizActive() || navigationAllowed) {
        return;
      }
      beforeLeave();
      submit({ keepalive: true, silent: true, completionTrigger: "auto_leave" });
    });
  }

  window.PortalQuizLeaveGuard = {
    init: initQuizLeaveGuard,
  };
})();

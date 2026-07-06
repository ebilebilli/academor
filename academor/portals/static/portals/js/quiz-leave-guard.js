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
    var defaultLeaveTitleEl = leaveModalEl.querySelector("#quizLeaveModalTitle");
    var defaultLeaveTextEl = leaveModalEl.querySelector(".portal-quiz-start-modal__text");
    var defaultLeaveTitle = defaultLeaveTitleEl ? defaultLeaveTitleEl.textContent : "";
    var defaultLeaveText = defaultLeaveTextEl ? defaultLeaveTextEl.textContent : "";
    if (confirmBtn) {
      confirmBtn.dataset.defaultHtml = confirmBtn.innerHTML;
    }
    var pendingUrl = "";
    var navigationAllowed = false;
    var leaveWarning =
      root.getAttribute("data-msg-leave-warning") ||
      "If you leave this page now, your quiz will be counted as completed.";
    var mockLeaveWarning =
      root.getAttribute("data-msg-mock-leave-warning") ||
      "Leave the mock test? Your current progress will be lost.";
    var leaveWarningText = root.getAttribute("data-mock-id") ? mockLeaveWarning : leaveWarning;

    function isMockQuiz() {
      return Boolean(root.getAttribute("data-mock-id"));
    }

    function getMockCancelUrl() {
      return root.getAttribute("data-mock-cancel-url") || "";
    }

    function isCancelUrl(url) {
      var cancelUrl = getMockCancelUrl();
      if (!cancelUrl) {
        return false;
      }
      try {
        var target = new URL(url, window.location.origin);
        var cancel = new URL(cancelUrl, window.location.origin);
        return target.pathname === cancel.pathname;
      } catch (e) {
        return url === cancelUrl;
      }
    }

    function navigateAway(targetUrl) {
      navigationAllowed = true;
      afterLeave();
      root.setAttribute("data-quiz-finished", "true");
      var url = targetUrl || getMockCancelUrl();
      if (!url) {
        return;
      }
      // Mock abandon is a state change: the cancel endpoint only acts on
      // POST (CSRF-protected), so send the POST first, then navigate to the
      // "next" destination encoded in the cancel URL.
      if (isMockQuiz() && isCancelUrl(url)) {
        var finalUrl = "";
        try {
          finalUrl = new URL(url, window.location.origin).searchParams.get("next") || "";
        } catch (e) {
          finalUrl = "";
        }
        fetch(url, {
          method: "POST",
          credentials: "same-origin",
          keepalive: true,
          headers: { "X-CSRFToken": getCsrfToken() },
        })
          .catch(function () {})
          .then(function () {
            window.location.href = finalUrl || url;
          });
        return;
      }
      window.location.href = url;
    }

    function isQuizActive() {
      return root.getAttribute("data-quiz-started") === "true" && root.getAttribute("data-quiz-finished") !== "true";
    }

    function showLeaveModal(targetUrl) {
      pendingUrl = targetUrl || "";
      var titleEl = leaveModalEl.querySelector("#quizLeaveModalTitle");
      var textEl = leaveModalEl.querySelector(".portal-quiz-start-modal__text");
      if (titleEl) {
        titleEl.textContent = isMockQuiz()
          ? (root.getAttribute("data-mock-leave-title") || "Leave mock test?")
          : defaultLeaveTitle;
      }
      if (textEl) {
        textEl.textContent = leaveWarningText;
      }
      if (confirmBtn) {
        confirmBtn.innerHTML = isMockQuiz()
          ? '<i class="bi bi-box-arrow-right me-1" aria-hidden="true"></i>' + (root.getAttribute("data-mock-leave-confirm") || "Leave mock test")
          : (confirmBtn.dataset.defaultHtml || confirmBtn.innerHTML);
      }
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
      if (window.confirm(leaveWarningText)) {
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
      if (isMockQuiz()) {
        navigateAway(targetUrl);
        return;
      }
      beforeLeave();
      submit({ keepalive: false, silent: true, completionTrigger: "auto_leave" }).then(function (ok) {
        if (!ok) {
          var msgError =
            root.getAttribute("data-msg-error") ||
            "Could not submit the test. Please try again.";
          window.alert(msgError);
          return;
        }
        navigateAway(targetUrl);
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
      event.returnValue = leaveWarningText;
      return leaveWarningText;
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
      if (!isQuizActive() || navigationAllowed || isMockQuiz()) {
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

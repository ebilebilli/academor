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

  function getBootstrapModal(modalEl) {
    if (!modalEl || !window.bootstrap || !window.bootstrap.Modal) {
      return null;
    }
    return window.bootstrap.Modal.getOrCreateInstance(modalEl, {
      backdrop: "static",
      keyboard: false,
    });
  }

  function hideStartModal(modalEl, modal) {
    if (modal) {
      modal.hide();
    } else if (modalEl) {
      modalEl.classList.remove("show", "d-block");
      modalEl.hidden = true;
      modalEl.classList.add("d-none");
      document.querySelectorAll(".modal-backdrop").forEach(function (node) {
        node.remove();
      });
    }
    document.body.classList.remove("modal-open", "portal-quiz-modal-open");
    document.body.style.removeProperty("overflow");
    document.body.style.removeProperty("padding-right");
  }

  function unlockQuizRoot(root) {
    if (!root) {
      return;
    }
    root.classList.remove("portal-quiz-take--locked");
    var content = root.querySelector("[data-quiz-take-content]");
    if (content) {
      content.hidden = false;
    }
    var actions = root.querySelector("[data-quiz-take-actions]");
    if (actions) {
      actions.hidden = false;
    }
  }

  function dispatchQuizStarted() {
    window.setTimeout(function () {
      document.dispatchEvent(new CustomEvent("portal-quiz-started"));
    }, 0);
  }

  function initQuizStartGate() {
    var modalEl = document.querySelector("[data-quiz-start-gate]");
    var root = document.querySelector("[data-quiz-take], [data-quiz-manual-take], [data-quiz-reading-take], [data-quiz-speaking-take]");
    if (!modalEl || !root) {
      return;
    }
    if (root.dataset.quizStartGateBound === "true") {
      return;
    }
    root.dataset.quizStartGateBound = "true";

    var startBtn = modalEl.querySelector("[data-quiz-start-btn]");
    var startUrl = modalEl.getAttribute("data-start-url");
    var msgError = modalEl.getAttribute("data-msg-start-error") || "Could not start the quiz. Please try again.";
    var modal = getBootstrapModal(modalEl);

    if (!startBtn || !startUrl) {
      window.alert(msgError);
      return;
    }

    root.setAttribute("data-quiz-started", "false");

    if (modalEl.parentElement !== document.body) {
      document.body.appendChild(modalEl);
    }

    root.classList.add("portal-quiz-take--locked");

    if (modal) {
      modal.show();
      document.body.classList.add("portal-quiz-modal-open");
    } else {
      modalEl.classList.add("show", "d-block");
      modalEl.hidden = false;
    }

    startBtn.addEventListener("click", function () {
      if (startBtn.disabled) {
        return;
      }

      var csrfToken = getCsrfToken();
      if (!csrfToken) {
        window.alert(msgError);
        return;
      }

      startBtn.disabled = true;

      fetch(startUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: "{}",
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          }).catch(function () {
            return { ok: false, data: { error: msgError } };
          });
        })
        .then(function (payload) {
          if (payload.data && payload.data.redirect_url) {
            window.location.href = payload.data.redirect_url;
            return;
          }
          if (!payload.ok || !payload.data.success) {
            throw new Error((payload.data && payload.data.error) || msgError);
          }
          root.setAttribute("data-quiz-started", "true");
          hideStartModal(modalEl, modal);
          unlockQuizRoot(root);
          dispatchQuizStarted();
        })
        .catch(function (err) {
          startBtn.disabled = false;
          window.alert(err.message || msgError);
        });
    });
  }

  function scheduleQuizStartGate() {
    initQuizStartGate();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleQuizStartGate);
  } else {
    scheduleQuizStartGate();
  }
  document.addEventListener("portal:content-loaded", scheduleQuizStartGate);
})();

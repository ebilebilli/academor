(function () {
  "use strict";

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[1]) : "";
  }

  function getCsrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input && input.value) {
      return input.value;
    }
    return getCookie("csrftoken");
  }

  function setRowState(row, isActive) {
    if (!row) {
      return;
    }
    row.classList.toggle("is-inactive", !isActive);
  }

  function postToggle(url, isActive) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ is_active: !!isActive }),
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("toggle failed");
      }
      return response.json();
    }).then(function (data) {
      if (!data.ok) {
        throw new Error("toggle rejected");
      }
      return data;
    });
  }

  function bindToggle(toggle) {
    if (!toggle || toggle.dataset.quizAccessBound === "true") {
      return;
    }
    toggle.dataset.quizAccessBound = "true";

    toggle.addEventListener("change", function () {
      var url = toggle.getAttribute("data-toggle-url");
      if (!url) {
        return;
      }

      var row = toggle.closest("[data-quiz-access-row]");
      var previous = !toggle.checked;
      toggle.disabled = true;

      postToggle(url, toggle.checked)
        .then(function (data) {
          toggle.checked = !!data.is_active;
          setRowState(row, toggle.checked);
        })
        .catch(function () {
          toggle.checked = previous;
        })
        .finally(function () {
          toggle.disabled = false;
        });
    });
  }

  function setActiveCategory(root, categoryId) {
    var buttons = root.querySelectorAll("[data-quiz-access-cat]");
    buttons.forEach(function (btn) {
      var isActive = btn.getAttribute("data-quiz-access-cat") === String(categoryId);
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });

    root.querySelectorAll("[data-quiz-access-category]").forEach(function (section) {
      var show =
        categoryId === "all" ||
        section.getAttribute("data-quiz-access-category") === String(categoryId);
      section.hidden = !show;
      section.classList.toggle("is-hidden", !show);
    });
  }

  function bindCategoryTabs(root) {
    var nav = root.querySelector("[data-quiz-access-cats]");
    if (!nav || nav.dataset.quizAccessCatsBound === "true") {
      return;
    }
    nav.dataset.quizAccessCatsBound = "true";

    nav.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-quiz-access-cat]");
      if (!btn || !nav.contains(btn)) {
        return;
      }
      event.preventDefault();
      setActiveCategory(root, btn.getAttribute("data-quiz-access-cat") || "all");
    });

    setActiveCategory(root, "all");
  }

  function bindBulkActions(root) {
    if (root.dataset.quizAccessBulkBound === "true") {
      return;
    }
    root.dataset.quizAccessBulkBound = "true";

    root.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-quiz-access-bulk]");
      if (!btn || !root.contains(btn)) {
        return;
      }
      event.preventDefault();

      var mode = btn.getAttribute("data-quiz-access-bulk");
      var categoryId = btn.getAttribute("data-quiz-access-bulk-category");
      var section = root.querySelector(
        '[data-quiz-access-category="' + categoryId + '"]'
      );
      if (!section) {
        return;
      }

      var wantActive = mode === "on";
      var toggles = Array.prototype.slice.call(
        section.querySelectorAll(".portal-quiz-access-toggle")
      ).filter(function (toggle) {
        return !!toggle.checked !== wantActive;
      });

      if (!toggles.length) {
        return;
      }

      btn.disabled = true;
      var chain = Promise.resolve();
      toggles.forEach(function (toggle) {
        chain = chain.then(function () {
          var url = toggle.getAttribute("data-toggle-url");
          if (!url) {
            return;
          }
          toggle.disabled = true;
          return postToggle(url, wantActive)
            .then(function (data) {
              toggle.checked = !!data.is_active;
              setRowState(toggle.closest("[data-quiz-access-row]"), toggle.checked);
            })
            .catch(function () {
              /* leave previous state */
            })
            .finally(function () {
              toggle.disabled = false;
            });
        });
      });

      chain.finally(function () {
        btn.disabled = false;
      });
    });
  }

  function initQuizAccessPanel(root) {
    if (!root) {
      return;
    }
    root.querySelectorAll(".portal-quiz-access-toggle").forEach(function (toggle) {
      if (toggle.hasAttribute("data-mock-access-toggle")) {
        return;
      }
      setRowState(toggle.closest("[data-quiz-access-row]"), toggle.checked);
      bindToggle(toggle);
    });

    var mockToggle = root.querySelector("[data-mock-access-toggle]");
    if (mockToggle && mockToggle.dataset.quizAccessBound !== "true") {
      mockToggle.dataset.quizAccessBound = "true";
      mockToggle.addEventListener("change", function () {
        var url = mockToggle.getAttribute("data-toggle-url");
        if (!url) {
          return;
        }
        var previous = !mockToggle.checked;
        mockToggle.disabled = true;
        postToggle(url, mockToggle.checked)
          .then(function (data) {
            mockToggle.checked = !!data.is_active;
          })
          .catch(function () {
            mockToggle.checked = previous;
          })
          .finally(function () {
            mockToggle.disabled = false;
          });
      });
    }

    bindCategoryTabs(root);
    bindBulkActions(root);
  }

  window.initTeacherQuizAccessPanel = initQuizAccessPanel;

  if (window.portalOnReady) {
    window.portalOnReady(function () {
      initQuizAccessPanel(document.querySelector("[data-quiz-access-panel]"));
    });
  } else {
    document.addEventListener("DOMContentLoaded", function () {
      initQuizAccessPanel(document.querySelector("[data-quiz-access-panel]"));
    });
  }
})();

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
    row.classList.toggle("is-partial", false);
  }

  function postJson(url, body) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify(body),
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("request failed");
      }
      return response.json();
    }).then(function (data) {
      if (!data.ok) {
        throw new Error("request rejected");
      }
      return data;
    });
  }

  function postToggle(url, isActive) {
    return postJson(url, { is_active: !!isActive });
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

  function applyToggleState(toggle, isActive) {
    toggle.checked = isActive;
    setRowState(toggle.closest("[data-quiz-access-row]"), isActive);
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

      var bulkUrl = root.getAttribute("data-quiz-access-bulk-url");
      var mode = btn.getAttribute("data-quiz-access-bulk");
      var categoryId = btn.getAttribute("data-quiz-access-bulk-category");
      var scope = btn.getAttribute("data-quiz-access-bulk-scope") || "program";
      var section = root.querySelector(
        '[data-quiz-access-category="' + categoryId + '"]'
      );
      if (!bulkUrl || !section) {
        return;
      }

      var wantActive = mode === "on";
      var toggles = Array.prototype.slice.call(
        section.querySelectorAll(".portal-quiz-access-toggle[data-quiz-id]")
      ).filter(function (toggle) {
        return !!toggle.checked !== wantActive;
      });

      if (!toggles.length) {
        return;
      }

      var previous = toggles.map(function (toggle) {
        return toggle.checked;
      });
      btn.disabled = true;
      toggles.forEach(function (toggle) {
        toggle.disabled = true;
        applyToggleState(toggle, wantActive);
      });

      var payload = {
        is_active: wantActive,
        category_id: categoryId,
        quiz_ids: toggles.map(function (toggle) {
          return toggle.getAttribute("data-quiz-id");
        }),
      };
      if (scope === "program") {
        payload.program_flagged_only = true;
      } else if (scope === "general") {
        payload.general_only = true;
      }

      postJson(bulkUrl, payload)
        .then(function (data) {
          var applied = {};
          (data.quiz_ids || []).forEach(function (quizId) {
            applied[String(quizId)] = true;
          });
          toggles.forEach(function (toggle, index) {
            var quizId = toggle.getAttribute("data-quiz-id");
            applyToggleState(
              toggle,
              applied[String(quizId)] ? !!data.is_active : previous[index]
            );
          });
        })
        .catch(function () {
          toggles.forEach(function (toggle, index) {
            applyToggleState(toggle, previous[index]);
          });
        })
        .finally(function () {
          toggles.forEach(function (toggle) {
            toggle.disabled = false;
          });
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

    root.querySelectorAll("[data-mock-access-toggle]").forEach(function (toggle) {
      if (toggle.dataset.quizAccessBound === "true") {
        return;
      }
      toggle.dataset.quizAccessBound = "true";
      toggle.addEventListener("change", function () {
        var url = toggle.getAttribute("data-toggle-url");
        if (!url) {
          return;
        }
        var previous = !toggle.checked;
        toggle.disabled = true;
        postToggle(url, toggle.checked)
          .then(function (data) {
            toggle.checked = !!data.is_active;
          })
          .catch(function () {
            toggle.checked = previous;
          })
          .finally(function () {
            toggle.disabled = false;
          });
      });
    });

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

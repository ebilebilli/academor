(function () {
  "use strict";

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"));
    return match ? decodeURIComponent(match.pop()) : "";
  }

  function clampScore(value) {
    if (value === "" || value == null) {
      return "";
    }
    var num = Number(value);
    if (Number.isNaN(num)) {
      return value;
    }
    if (num < 0) {
      return "0";
    }
    if (num > 10) {
      return "10";
    }
    return String(Math.round(num * 10) / 10);
  }

  function updateRowState(row) {
    var input = row.querySelector("[data-weekly-score-input]");
    var badge = row.querySelector("[data-weekly-score-badge]");
    if (!input || !badge) {
      return;
    }
    var hasScore = String(input.value || "").trim() !== "";
    row.classList.toggle("is-scored", hasScore);
    badge.textContent = hasScore
      ? badge.dataset.scoredLabel || badge.textContent
      : badge.dataset.pendingLabel || badge.textContent;
    badge.classList.toggle("ds-badge--success", hasScore);
  }

  function initForm(panel) {
    var form = panel.querySelector("[data-weekly-scores-form]");
    if (!form || form.dataset.bound === "true") {
      return form;
    }
    form.dataset.bound = "true";

    panel.querySelectorAll("[data-weekly-score-row]").forEach(function (row) {
      var input = row.querySelector("[data-weekly-score-input]");
      if (!input) {
        return;
      }
      input.addEventListener("input", function () {
        input.classList.remove("is-invalid");
        updateRowState(row);
      });
      input.addEventListener("blur", function () {
        input.value = clampScore(input.value);
        updateRowState(row);
      });
    });

    return form;
  }

  function initSearch(panel) {
    var search = panel.querySelector("[data-weekly-search]");
    if (!search || search.dataset.bound === "true") {
      return;
    }
    search.dataset.bound = "true";
    search.addEventListener("input", function () {
      var query = String(search.value || "").trim().toLowerCase();
      panel.querySelectorAll("[data-weekly-score-row]").forEach(function (row) {
        var name = row.getAttribute("data-student-name") || "";
        row.classList.toggle("is-hidden", query && name.indexOf(query) === -1);
      });
    });
  }

  function showFlash(panel, message, level) {
    var existing = panel.querySelector("[data-weekly-scores-flash]");
    if (existing) {
      existing.remove();
    }
    if (!message) {
      return;
    }
    var flash = document.createElement("div");
    flash.className = "weekly-scores-flash weekly-scores-flash--" + (level || "success");
    flash.setAttribute("role", "status");
    flash.setAttribute("data-weekly-scores-flash", "");
    flash.innerHTML = '<i class="ti ti-check" aria-hidden="true"></i> ' + message;
    panel.prepend(flash);
    window.setTimeout(function () {
      if (flash.parentNode) {
        flash.remove();
      }
    }, 4200);
  }

  function buildPanelUrl(baseUrl, params) {
    var url = new URL(baseUrl, window.location.origin);
    Object.keys(params).forEach(function (key) {
      if (params[key] === null || params[key] === undefined || params[key] === "") {
        url.searchParams.delete(key);
      } else {
        url.searchParams.set(key, params[key]);
      }
    });
    return url.pathname + url.search;
  }

  function readStateFromPanel(panel) {
    var groupField = panel.querySelector("[data-weekly-group-field]");
    return {
      group: groupField ? groupField.value : "all",
    };
  }

  function initWeeklyScoresApp(app) {
    if (!app) {
      return null;
    }
    if (app.__weeklyScoresController) {
      return app.__weeklyScoresController;
    }

    var mount = app.querySelector("[data-weekly-scores-mount]");
    var panelUrl = app.getAttribute("data-panel-url") || window.location.pathname;
    if (!mount) {
      return null;
    }
    app.dataset.bound = "true";

    function setLoading(isLoading) {
      mount.setAttribute("aria-busy", isLoading ? "true" : "false");
      var panel = mount.querySelector("[data-weekly-scores-panel]");
      if (panel) {
        panel.classList.toggle("is-loading", isLoading);
      }
    }

    function replacePanel(html) {
      mount.innerHTML = html;
      var panel = mount.querySelector("[data-weekly-scores-panel]");
      if (panel) {
        initForm(panel);
        initSearch(panel);
      }
    }

    function pushUrl(params) {
      var next = buildPanelUrl(panelUrl, params);
      window.history.pushState(
        Object.assign({}, window.history.state, { weeklyScores: true, params: params }),
        "",
        next
      );
    }

    function loadPanel(params, options) {
      options = options || {};
      setLoading(true);
      var url = buildPanelUrl(panelUrl, params);
      return fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          Accept: "text/html",
        },
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("load failed");
          }
          return response.text();
        })
        .then(function (html) {
          replacePanel(html);
          if (options.pushState !== false) {
            pushUrl(params);
          }
        })
        .catch(function () {
          showFlash(
            mount.querySelector("[data-weekly-scores-panel]") || mount,
            "Yükləmə alınmadı.",
            "error"
          );
        })
        .finally(function () {
          setLoading(false);
        });
    }

    function submitForm(form) {
      var panel = form.closest("[data-weekly-scores-panel]");
      var saveBtn = form.querySelector("[data-weekly-save-btn]");
      var invalid = false;

      form.querySelectorAll("[data-weekly-score-input]").forEach(function (input) {
        var raw = String(input.value || "").trim();
        if (!raw) {
          input.classList.remove("is-invalid");
          return;
        }
        var num = Number(raw);
        if (Number.isNaN(num) || num < 0 || num > 10) {
          input.classList.add("is-invalid");
          invalid = true;
        } else {
          input.value = clampScore(raw);
          input.classList.remove("is-invalid");
        }
      });

      if (invalid) {
        showFlash(panel, "Bal 0 ilə 10 arasında olmalıdır.", "error");
        return Promise.resolve();
      }

      if (saveBtn) {
        saveBtn.disabled = true;
      }
      setLoading(true);

      var formData = new FormData(form);
      return fetch(panelUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
          Accept: "application/json",
        },
        body: formData,
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok) {
            showFlash(panel, result.data.message || "Xəta baş verdi.", "error");
            return;
          }
          replacePanel(result.data.html || "");
          var newPanel = mount.querySelector("[data-weekly-scores-panel]");
          var flashLevel = result.data.level || (result.data.ok ? "success" : "info");
          showFlash(newPanel, result.data.message, flashLevel);
          var state = readStateFromPanel(newPanel);
          pushUrl(state);
        })
        .catch(function () {
          showFlash(panel, "Yadda saxlama alınmadı.", "error");
        })
        .finally(function () {
          setLoading(false);
          if (saveBtn) {
            saveBtn.disabled = false;
          }
        });
    }

    app.addEventListener("submit", function (event) {
      var form = event.target.closest("[data-weekly-scores-form]");
      if (!form || !app.contains(form)) {
        return;
      }
      event.preventDefault();
      submitForm(form);
    });

    window.addEventListener("popstate", function () {
      if (!document.body.contains(app)) {
        return;
      }
      var params = (window.history.state && window.history.state.params) || {};
      var search = new URLSearchParams(window.location.search);
      loadPanel(
        {
          group: params.group || search.get("group") || "all",
        },
        { pushState: false }
      );
    });

    var initialPanel = mount.querySelector("[data-weekly-scores-panel]");
    if (initialPanel) {
      initForm(initialPanel);
      initSearch(initialPanel);
    }

    var controller = { loadPanel: loadPanel };
    app.__weeklyScoresController = controller;
    return controller;
  }

  function setWeeklyGroupActive(groupBtn) {
    var nav = groupBtn.closest(".weekly-scores-groups");
    if (!nav) {
      return;
    }
    nav.querySelectorAll("[data-weekly-group]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn === groupBtn);
    });
  }

  function handleWeeklyGroupClick(event) {
    var groupBtn = event.target.closest("[data-weekly-group]");
    if (!groupBtn) {
      return;
    }
    var app = groupBtn.closest("[data-weekly-scores-app]");
    if (!app) {
      return;
    }
    event.preventDefault();
    setWeeklyGroupActive(groupBtn);
    var controller = app.__weeklyScoresController || initWeeklyScoresApp(app);
    if (controller && typeof controller.loadPanel === "function") {
      controller.loadPanel({
        group: groupBtn.getAttribute("data-weekly-group") || "all",
      });
    }
  }

  function bootWeeklyScores() {
    document.querySelectorAll("[data-weekly-scores-app]").forEach(function (app) {
      initWeeklyScoresApp(app);
    });
  }

  document.addEventListener("click", handleWeeklyGroupClick);
  document.addEventListener("portal:content-loaded", bootWeeklyScores);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootWeeklyScores);
  } else {
    bootWeeklyScores();
  }
})();

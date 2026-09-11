(function () {
  "use strict";

  var fieldMap = {
    student_count: "[data-portal-stat='student_count']",
    group_count: "[data-portal-stat='group_count']",
    lesson_count: "[data-portal-stat='lesson_count']",
    quiz_result_count: "[data-portal-stat='quiz_result_count']",
    weekly_score_count: "[data-portal-stat='weekly_score_count']",
  };

  var activeRequest = 0;

  function applyStats(root, payload) {
    if (!root || !payload) {
      return;
    }
    Object.keys(fieldMap).forEach(function (key) {
      if (payload[key] == null) {
        return;
      }
      root.querySelectorAll(fieldMap[key]).forEach(function (node) {
        node.textContent = String(payload[key]);
      });
    });
    root.classList.remove("is-loading");
  }

  function loadStats() {
    var root = document.querySelector("[data-portal-dashboard-stats]");
    if (!root) {
      return;
    }

    var statsUrl = root.getAttribute("data-portal-dashboard-stats");
    if (!statsUrl) {
      return;
    }

    var requestId = ++activeRequest;

    fetch(statsUrl, {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("dashboard stats failed");
        }
        return response.json();
      })
      .then(function (payload) {
        if (requestId !== activeRequest) {
          return;
        }
        var current = document.querySelector("[data-portal-dashboard-stats]");
        if (!current || current.getAttribute("data-portal-dashboard-stats") !== statsUrl) {
          return;
        }
        applyStats(current, payload);
      })
      .catch(function () {
        if (requestId !== activeRequest) {
          return;
        }
        var current = document.querySelector("[data-portal-dashboard-stats]");
        if (current) {
          current.classList.remove("is-loading");
        }
      });
  }

  document.addEventListener("portal:content-loaded", loadStats);
})();

(function () {
  "use strict";

  var root = document.querySelector("[data-portal-dashboard-stats]");
  if (!root) {
    return;
  }

  var statsUrl = root.getAttribute("data-portal-dashboard-stats");
  if (!statsUrl) {
    return;
  }

  var fieldMap = {
    student_count: "[data-portal-stat='student_count']",
    group_count: "[data-portal-stat='group_count']",
    lesson_count: "[data-portal-stat='lesson_count']",
    quiz_result_count: "[data-portal-stat='quiz_result_count']",
    weekly_score_count: "[data-portal-stat='weekly_score_count']",
  };

  function applyStats(payload) {
    if (!payload) {
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
      .then(applyStats)
      .catch(function () {
        root.classList.remove("is-loading");
      });
  }

  document.addEventListener("DOMContentLoaded", loadStats);
})();

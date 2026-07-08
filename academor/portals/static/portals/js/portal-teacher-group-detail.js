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

  function initGroupDetail() {
    var root = document.getElementById("portal-teacher-group-detail");
    if (!root || root.dataset.portalGroupDetailBound === "true") {
      return;
    }
    root.dataset.portalGroupDetailBound = "true";

    function filterStudents() {
      var input = document.getElementById("student-search");
      var search = (input && input.value ? input.value : "").toLowerCase();
      root.querySelectorAll(".portal-student-item").forEach(function (item) {
        var name = item.dataset.name || "";
        item.style.display = name.indexOf(search) !== -1 ? "" : "none";
      });
    }

    root.addEventListener("input", function (event) {
      if (event.target && event.target.id === "student-search") {
        filterStudents();
      }
    });

    root.addEventListener("click", function (event) {
      if (event.target.closest("[data-portal-print]")) {
        event.preventDefault();
        window.print();
      }
    });
  }

  onReady(initGroupDetail);
  document.addEventListener("portal:content-loaded", initGroupDetail);
})();

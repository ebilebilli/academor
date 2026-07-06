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

  function initTeacherGroups() {
    var root = document.getElementById("portal-teacher-groups");
    if (!root || root.dataset.portalTeacherGroupsBound === "true") {
      return;
    }
    root.dataset.portalTeacherGroupsBound = "true";

    var totalGroups = parseInt(root.dataset.totalGroups, 10) || 0;
    var labelShowing = root.dataset.labelShowing || "Showing";
    var labelOf = root.dataset.labelOf || "of";

    function visibleCards() {
      return Array.prototype.filter.call(
        root.querySelectorAll(".group-card-item"),
        function (card) {
          return card.style.display !== "none";
        }
      );
    }

    function updateStats() {
      var cards = visibleCards();
      var active = 0;
      var totalStudents = 0;

      cards.forEach(function (card) {
        if (card.dataset.status === "active") {
          active += 1;
        }
        totalStudents += parseInt(card.dataset.students, 10) || 0;
      });

      var activeEl = document.getElementById("active-groups");
      var studentsEl = document.getElementById("total-students");
      var groupsEl = document.getElementById("total-groups");
      var showingEl = document.getElementById("showing-text");

      if (activeEl) {
        activeEl.textContent = String(active);
      }
      if (studentsEl) {
        studentsEl.textContent = String(totalStudents);
      }
      if (groupsEl) {
        groupsEl.textContent = String(cards.length);
      }
      if (showingEl) {
        showingEl.textContent = labelShowing + " " + cards.length + " " + labelOf + " " + totalGroups;
      }
    }

    function applyFilter(filter) {
      root.querySelectorAll(".group-card-item").forEach(function (card) {
        var show = filter === "all" || card.dataset.status === filter;
        card.style.display = show ? "" : "none";
      });
      updateStats();
    }

    function filterByCourse(course) {
      root.querySelectorAll(".group-card-item").forEach(function (card) {
        var show = course === "all" || card.dataset.course === course;
        card.style.display = show ? "" : "none";
      });
      updateStats();
    }

    function populateCourseFilter() {
      var menu = document.getElementById("course-filter-menu");
      if (!menu || menu.dataset.populated === "true") {
        return;
      }
      menu.dataset.populated = "true";

      var courses = {};
      root.querySelectorAll(".group-card-item").forEach(function (card) {
        if (card.dataset.course) {
          courses[card.dataset.course] = true;
        }
      });

      Object.keys(courses).forEach(function (course) {
        var li = document.createElement("li");
        var link = document.createElement("a");
        link.className = "dropdown-item";
        link.href = "#";
        link.dataset.portalGroupsCourse = course;
        link.textContent = course;
        li.appendChild(link);
        menu.appendChild(li);
      });
    }

    function filterGroups() {
      var input = document.getElementById("group-search");
      var search = (input && input.value ? input.value : "").toLowerCase();

      root.querySelectorAll(".group-card-item").forEach(function (card) {
        var name = card.dataset.name || "";
        card.style.display = name.indexOf(search) !== -1 ? "" : "none";
      });
      updateStats();
    }

    function sortGroups(column) {
      var container = document.getElementById("groups-cards-view");
      if (!container) {
        return;
      }

      var cards = Array.prototype.slice.call(container.querySelectorAll(".group-card-item"));
      var ascending = container.dataset.sortDir !== column;
      container.dataset.sortDir = ascending ? column : "";

      cards.sort(function (a, b) {
        var valA = a.dataset[column] || "";
        var valB = b.dataset[column] || "";

        if (column === "students") {
          valA = parseInt(valA, 10) || 0;
          valB = parseInt(valB, 10) || 0;
        }

        if (valA < valB) {
          return ascending ? -1 : 1;
        }
        if (valA > valB) {
          return ascending ? 1 : -1;
        }
        return 0;
      });

      cards.forEach(function (card) {
        container.appendChild(card);
      });
    }

    root.addEventListener("input", function (event) {
      if (event.target && event.target.id === "group-search") {
        filterGroups();
      }
    });

    root.addEventListener("click", function (event) {
      var target = event.target.closest("[data-portal-groups-filter], [data-portal-groups-sort], [data-portal-groups-course]");
      if (!target) {
        return;
      }
      event.preventDefault();

      if (target.dataset.portalGroupsFilter) {
        applyFilter(target.dataset.portalGroupsFilter);
      } else if (target.dataset.portalGroupsSort) {
        sortGroups(target.dataset.portalGroupsSort);
      } else if (target.dataset.portalGroupsCourse) {
        filterByCourse(target.dataset.portalGroupsCourse);
      }
    });

    populateCourseFilter();
    updateStats();
  }

  onReady(initTeacherGroups);
  document.addEventListener("portal:content-loaded", initTeacherGroups);
})();

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
    var sortDirection = {};

    function visibleRows() {
      return Array.prototype.filter.call(
        root.querySelectorAll(".group-row"),
        function (row) {
          return row.style.display !== "none";
        }
      );
    }

    function updateStats() {
      var rows = visibleRows();
      var active = 0;
      var totalStudents = 0;

      rows.forEach(function (row) {
        if (row.dataset.status === "active") {
          active += 1;
        }
        totalStudents += parseInt(row.dataset.students, 10) || 0;
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
        groupsEl.textContent = String(rows.length);
      }
      if (showingEl) {
        showingEl.textContent = labelShowing + " " + rows.length + " " + labelOf + " " + totalGroups;
      }
    }

    function setRowVisible(selector, name, show) {
      root.querySelectorAll(selector).forEach(function (el) {
        el.style.display = show ? "" : "none";
      });
    }

    function applyFilter(filter) {
      root.querySelectorAll(".group-row").forEach(function (row) {
        var show = filter === "all" || row.dataset.status === filter;
        row.style.display = show ? "" : "none";
      });
      root.querySelectorAll(".group-card-item").forEach(function (card) {
        var show = filter === "all" || card.dataset.status === filter;
        card.style.display = show ? "" : "none";
      });
      updateStats();
    }

    function filterByCourse(course) {
      if (course === "all") {
        setRowVisible(".group-row, .group-card-item", null, true);
      } else {
        root.querySelectorAll(".group-row").forEach(function (row) {
          row.style.display = row.dataset.course === course ? "" : "none";
        });
        root.querySelectorAll(".group-card-item").forEach(function (card) {
          card.style.display = card.dataset.course === course ? "" : "none";
        });
      }
      updateStats();
    }

    function populateCourseFilter() {
      var menu = document.getElementById("course-filter-menu");
      if (!menu || menu.dataset.populated === "true") {
        return;
      }
      menu.dataset.populated = "true";

      var courses = {};
      root.querySelectorAll(".group-row").forEach(function (row) {
        if (row.dataset.course) {
          courses[row.dataset.course] = true;
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

      root.querySelectorAll(".group-row").forEach(function (row) {
        var name = row.dataset.name || "";
        row.style.display = name.indexOf(search) !== -1 ? "" : "none";
      });
      root.querySelectorAll(".group-card-item").forEach(function (card) {
        var name = card.dataset.name || "";
        card.style.display = name.indexOf(search) !== -1 ? "" : "none";
      });
      updateStats();
    }

    function setView(view) {
      var tableBtn = document.getElementById("view-table");
      var cardsBtn = document.getElementById("view-cards");
      var tableView = document.getElementById("groups-table-view");
      var cardsView = document.getElementById("groups-cards-view");

      if (tableBtn) {
        tableBtn.classList.toggle("active", view === "table");
      }
      if (cardsBtn) {
        cardsBtn.classList.toggle("active", view === "cards");
      }
      if (tableView) {
        tableView.style.display = view === "table" ? "" : "none";
      }
      if (cardsView) {
        cardsView.style.display = view === "cards" ? "" : "none";
      }
    }

    function sortGroups(column) {
      var table = document.getElementById("groups-table");
      if (!table) {
        return;
      }
      var tbody = table.querySelector("tbody");
      if (!tbody) {
        return;
      }

      var rows = Array.prototype.slice.call(tbody.querySelectorAll(".group-row"));
      sortDirection[column] = !sortDirection[column];

      rows.sort(function (a, b) {
        var valA = a.dataset[column] || "";
        var valB = b.dataset[column] || "";

        if (column === "students") {
          valA = parseInt(valA, 10) || 0;
          valB = parseInt(valB, 10) || 0;
        }

        if (valA < valB) {
          return sortDirection[column] ? -1 : 1;
        }
        if (valA > valB) {
          return sortDirection[column] ? 1 : -1;
        }
        return 0;
      });

      rows.forEach(function (row) {
        tbody.appendChild(row);
      });
    }

    root.addEventListener("input", function (event) {
      if (event.target && event.target.id === "group-search") {
        filterGroups();
      }
    });

    root.addEventListener("click", function (event) {
      var target = event.target.closest("[data-portal-groups-filter], [data-portal-groups-sort], [data-portal-groups-course], [data-portal-groups-view]");
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
      } else if (target.dataset.portalGroupsView) {
        setView(target.dataset.portalGroupsView);
      }
    });

    populateCourseFilter();
    updateStats();
  }

  onReady(initTeacherGroups);
  document.addEventListener("portal:content-loaded", initTeacherGroups);
})();

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

  function readJson(id, fallback) {
    var node = document.getElementById(id);
    if (!node) {
      return fallback;
    }
    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      return fallback;
    }
  }

  function parseGroupIds(raw) {
    return (raw || "")
      .split(",")
      .map(function (part) { return part.trim(); })
      .filter(Boolean);
  }

  function summaryForScope(student, groupKey) {
    var summaries = student.summary_by_group || {};
    return summaries[groupKey] || summaries.all || { present: 0, absent: 0, late: 0, marked: 0 };
  }

  function attendanceRate(summary) {
    var marked = summary.marked || 0;
    if (!marked) {
      return null;
    }
    return Math.round((100 * summary.present / marked) * 10) / 10;
  }

  function rateClass(rate) {
    if (rate === null || rate === undefined) {
      return " is-empty";
    }
    if (rate >= 85) {
      return " is-good";
    }
    if (rate >= 70) {
      return " is-fair";
    }
    return " is-low";
  }

  function initAttendanceHub() {
    var panel = document.querySelector(".portal-attendance-hub-panel");
    if (!panel || panel.dataset.portalAttendanceHubBound === "true") {
      return;
    }

    var groupChips = panel.querySelectorAll(".portal-attendance-hub-group-chip[data-attendance-group]");
    var cardItems = panel.querySelectorAll(".portal-attendance-hub-item");
    var tableRows = panel.querySelectorAll(".portal-attendance-hub-row");

    if (!groupChips.length && !cardItems.length && !tableRows.length) {
      return;
    }

    panel.dataset.portalAttendanceHubBound = "true";

    var statsData = readJson("attendance-hub-stats-data", {});
    var studentsData = readJson("attendance-hub-students-data", []);
    var studentsById = {};
    studentsData.forEach(function (student) {
      studentsById[String(student.id)] = student;
    });

    var searchInput = document.getElementById("attendance-student-search");
    var cardsView = document.getElementById("attendance-cards-view");
    var tableView = document.getElementById("attendance-table-view");
    var emptyState = document.getElementById("attendance-search-empty");
    var countEl = document.getElementById("attendance-visible-count");
    var attentionBtn = document.getElementById("attendance-filter-attention");
    var clearFiltersBtn = document.getElementById("attendance-clear-filters");
    var statsRoot = document.getElementById("attendance-hub-stats");
    var cardsBtn = document.getElementById("attendance-view-cards");
    var tableBtn = document.getElementById("attendance-view-table");

    var state = {
      query: "",
      group: "all",
      filter: "all",
      sort: "name",
    };

    function setActiveInList(items, activeItem) {
      items.forEach(function (item) {
        item.classList.toggle("active", item === activeItem);
      });
    }

    function syncGroupSelection(groupKey) {
      state.group = groupKey;
      panel.querySelectorAll(".portal-attendance-hub-group-chip[data-attendance-group]").forEach(function (button) {
        button.classList.toggle("active", button.getAttribute("data-attendance-group") === groupKey);
      });
    }

    function syncAttentionButton() {
      if (!attentionBtn) {
        return;
      }
      var active = state.filter === "attention";
      attentionBtn.classList.toggle("active", active);
      attentionBtn.setAttribute("aria-pressed", active ? "true" : "false");
    }

    function updateHubStats() {
      if (!statsRoot) {
        return;
      }
      var stats = statsData[state.group] || statsData.all || {};
      statsRoot.querySelectorAll("[data-stat]").forEach(function (node) {
        var key = node.getAttribute("data-stat");
        var value = stats[key];
        if (key === "attendance_rate") {
          node.textContent = value === null || value === undefined ? "—" : value + "%";
        } else {
          node.textContent = value === null || value === undefined ? "0" : value;
        }
      });
    }

    function setMetricValue(node, value) {
      if (!node) {
        return;
      }
      var strong = node.querySelector("strong");
      if (strong) {
        strong.textContent = value;
      } else {
        node.textContent = value;
      }
    }

    function updateCard(item, student) {
      if (!student) {
        return;
      }

      var summary = summaryForScope(student, state.group);
      var rate = attendanceRate(summary);
      var card = item.querySelector("[data-attendance-card]");
      if (!card) {
        return;
      }

      card.classList.toggle("has-attention", summary.absent > 0);

      var rateNode = card.querySelector("[data-card-rate]");
      if (rateNode) {
        rateNode.className = "portal-attendance-hub-card__rate" + rateClass(rate);
        var rateValue = rateNode.querySelector(".portal-attendance-hub-card__rate-value");
        if (rateValue) {
          rateValue.textContent = rate === null ? "—" : rate + "%";
        }
      }

      setMetricValue(card.querySelector("[data-card-present]"), summary.present);
      setMetricValue(card.querySelector("[data-card-absent]"), summary.absent);
      setMetricValue(card.querySelector("[data-card-late]"), summary.late);
    }

    function updateRow(row, student) {
      if (!student) {
        return;
      }

      var summary = summaryForScope(student, state.group);
      var rate = attendanceRate(summary);

      row.classList.toggle("has-attention", summary.absent > 0);

      var presentNode = row.querySelector("[data-row-present]");
      if (presentNode) presentNode.textContent = summary.present;
      var absentNode = row.querySelector("[data-row-absent]");
      if (absentNode) absentNode.textContent = summary.absent;
      var lateNode = row.querySelector("[data-row-late]");
      if (lateNode) lateNode.textContent = summary.late;
      var rateNode = row.querySelector("[data-row-rate]");
      if (rateNode) {
        rateNode.textContent = rate === null ? "—" : rate + "%";
        rateNode.className = "portal-attendance-hub-rate-badge" + rateClass(rate);
      }
    }

    function matchesGroup(item) {
      if (state.group === "all") {
        return true;
      }
      return parseGroupIds(item.getAttribute("data-group-ids")).indexOf(String(state.group)) !== -1;
    }

    function matchesSearch(item) {
      if (!state.query) {
        return true;
      }
      return (item.getAttribute("data-name") || "").includes(state.query);
    }

    function matchesAttention(student, item) {
      if (state.filter !== "attention") {
        return true;
      }
      if (student) {
        return summaryForScope(student, state.group).absent > 0;
      }
      if (item.classList.contains("has-attention")) {
        return true;
      }
      return !!item.querySelector(".has-attention");
    }

    function sortValue(student) {
      if (!student) {
        return "";
      }
      var summary = summaryForScope(student, state.group);
      var rate = attendanceRate(summary);
      if (state.sort === "rate-desc") {
        return rate === null ? -1 : rate;
      }
      if (state.sort === "rate-asc") {
        return rate === null ? 101 : rate;
      }
      if (state.sort === "absent-desc") {
        return summary.absent;
      }
      return (student.full_name || "").toLowerCase();
    }

    function compareStudents(a, b) {
      var av = sortValue(a);
      var bv = sortValue(b);
      if (state.sort === "rate-desc" || state.sort === "absent-desc") {
        return bv - av || String((a && a.full_name) || "").localeCompare(String((b && b.full_name) || ""));
      }
      if (state.sort === "rate-asc") {
        return av - bv || String((a && a.full_name) || "").localeCompare(String((b && b.full_name) || ""));
      }
      return String(av).localeCompare(String(bv));
    }

    function reorderDom(parent, items) {
      if (!parent) {
        return;
      }
      items.forEach(function (item) {
        parent.appendChild(item);
      });
    }

    function currentCardItems() {
      return Array.prototype.slice.call(panel.querySelectorAll(".portal-attendance-hub-item"));
    }

    function currentTableRows() {
      return Array.prototype.slice.call(panel.querySelectorAll(".portal-attendance-hub-row"));
    }

    function applyFilters() {
      var visible = 0;
      var visibleStudents = [];
      var items = currentCardItems();
      var rows = currentTableRows();

      items.forEach(function (item) {
        var student = studentsById[item.getAttribute("data-student-id")];
        var show = matchesSearch(item) && matchesGroup(item) && matchesAttention(student, item);
        item.hidden = !show;
        if (show) {
          updateCard(item, student);
          visibleStudents.push({ item: item, student: student });
          visible += 1;
        }
      });

      rows.forEach(function (row) {
        var student = studentsById[row.getAttribute("data-student-id")];
        var show = matchesSearch(row) && matchesGroup(row) && matchesAttention(student, row);
        row.hidden = !show;
        if (show) {
          updateRow(row, student);
        }
      });

      visibleStudents.sort(function (a, b) {
        return compareStudents(a.student, b.student);
      });

      reorderDom(cardsView, visibleStudents.map(function (entry) { return entry.item; }));

      var sortedRows = rows.filter(function (row) {
        return !row.hidden;
      }).sort(function (rowA, rowB) {
        return compareStudents(
          studentsById[rowA.getAttribute("data-student-id")],
          studentsById[rowB.getAttribute("data-student-id")]
        );
      });
      reorderDom(document.getElementById("attendance-table-body"), sortedRows);

      if (emptyState) {
        emptyState.classList.toggle("d-none", visible > 0 || items.length === 0);
      }

      var tableMode = tableBtn && tableBtn.classList.contains("active");
      if (cardsView) {
        cardsView.classList.toggle("d-none", tableMode || (visible === 0 && items.length > 0));
      }
      if (tableView) {
        tableView.classList.toggle("d-none", !tableMode || (visible === 0 && items.length > 0));
      }

      if (countEl) {
        var countValue = countEl.querySelector("[data-attendance-count]");
        if (countValue) {
          countValue.textContent = visible;
        }
      }

      updateHubStats();
    }

    function clearFilters() {
      state.query = "";
      state.group = "all";
      state.filter = "all";
      state.sort = "name";
      if (searchInput) {
        searchInput.value = "";
      }
      syncGroupSelection("all");
      syncAttentionButton();
      panel.querySelectorAll("[data-attendance-sort]").forEach(function (button) {
        button.classList.toggle("active", button.getAttribute("data-attendance-sort") === "name");
      });
      applyFilters();
    }

    panel.addEventListener("click", function (event) {
      var groupChip = event.target.closest(".portal-attendance-hub-group-chip[data-attendance-group]");
      if (groupChip && panel.contains(groupChip)) {
        syncGroupSelection(groupChip.getAttribute("data-attendance-group") || "all");
        applyFilters();
        return;
      }

      var sortButton = event.target.closest("[data-attendance-sort]");
      if (sortButton && panel.contains(sortButton)) {
        state.sort = sortButton.getAttribute("data-attendance-sort") || "name";
        setActiveInList(panel.querySelectorAll("[data-attendance-sort]"), sortButton);
        applyFilters();
        return;
      }

      if (attentionBtn && event.target.closest("#attendance-filter-attention")) {
        state.filter = state.filter === "attention" ? "all" : "attention";
        syncAttentionButton();
        applyFilters();
        return;
      }

      if (clearFiltersBtn && event.target.closest("#attendance-clear-filters")) {
        clearFilters();
        return;
      }

      if (cardsBtn && event.target.closest("#attendance-view-cards")) {
        cardsBtn.classList.add("active");
        if (tableBtn) tableBtn.classList.remove("active");
        if (cardsView) cardsView.classList.remove("d-none");
        if (tableView && currentCardItems().some(function (item) { return !item.hidden; })) {
          tableView.classList.add("d-none");
        }
        return;
      }

      if (tableBtn && event.target.closest("#attendance-view-table")) {
        tableBtn.classList.add("active");
        if (cardsBtn) cardsBtn.classList.remove("active");
        if (tableView) tableView.classList.remove("d-none");
        if (cardsView) cardsView.classList.add("d-none");
      }
    });

    if (searchInput && searchInput.dataset.portalAttendanceSearchBound !== "true") {
      searchInput.dataset.portalAttendanceSearchBound = "true";
      var searchTimer = null;
      searchInput.addEventListener("input", function () {
        if (searchTimer) {
          window.clearTimeout(searchTimer);
        }
        searchTimer = window.setTimeout(function () {
          state.query = (searchInput.value || "").trim().toLowerCase();
          applyFilters();
        }, 180);
      });
    }

    currentCardItems().forEach(function (item) {
      updateCard(item, studentsById[item.getAttribute("data-student-id")]);
    });

    currentTableRows().forEach(function (row) {
      updateRow(row, studentsById[row.getAttribute("data-student-id")]);
    });

    applyFilters();
  }

  onReady(initAttendanceHub);
})();

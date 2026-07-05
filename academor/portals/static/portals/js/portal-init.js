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

  function bindContentLoaded(fn) {
    onReady(fn);
  }

  /* ── Service tabs (classrooms, quiz categories) ── */
  function initServiceTabs(root) {
    if (root.dataset.portalServiceTabsBound === "true") {
      return;
    }
    var tablist = root.querySelector("[data-portal-service-tablist]");
    if (!tablist) {
      return;
    }
    var tableSelector = root.dataset.portalServiceTable || "table";
    var table = root.querySelector(tableSelector);
    if (!table) {
      return;
    }
    var tabs = tablist.querySelectorAll(".nav-link[data-service], .s-filter-tab[data-service]");
    if (!tabs.length) {
      return;
    }
    var matchMode = root.dataset.portalServiceMatch || "single";
    var rowSelector = matchMode === "csv" ? "tbody tr[data-services]" : "tbody tr[data-service]";
    var rows = table.querySelectorAll(rowSelector);
    var emptyRow = root.dataset.portalServiceEmptyRow
      ? root.querySelector(root.dataset.portalServiceEmptyRow)
      : null;
    var filterEmpty = root.dataset.portalServiceFilterEmpty
      ? root.querySelector(root.dataset.portalServiceFilterEmpty)
      : null;
    root.dataset.portalServiceTabsBound = "true";

    function applyFilter(service) {
      var visible = 0;
      rows.forEach(function (row) {
        var show;
        if (matchMode === "csv") {
          var codes = (row.getAttribute("data-services") || "").split(",").filter(Boolean);
          show = service === "all" || codes.indexOf(service) !== -1;
        } else {
          show = service === "all" || row.getAttribute("data-service") === service;
        }
        row.classList.toggle("d-none", !show);
        if (show) {
          visible += 1;
        }
      });
      if (emptyRow) {
        emptyRow.classList.add("d-none");
      }
      if (filterEmpty) {
        filterEmpty.classList.toggle("d-none", visible > 0 || rows.length === 0);
      }
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (item) {
          item.classList.remove("active", "is-active");
          item.setAttribute("aria-selected", "false");
        });
        tab.classList.add(tab.classList.contains("s-filter-tab") ? "is-active" : "active");
        tab.setAttribute("aria-selected", "true");
        applyFilter(tab.getAttribute("data-service"));
      });
    });
  }

  /* ── Status tabs (attendance) ── */
  function initStatusTabs(root) {
    if (root.dataset.portalStatusTabsBound === "true") {
      return;
    }
    var tablist = root.querySelector("[data-portal-status-tablist]") || root.querySelector(".portal-attendance-tabs") || root.querySelector(".s-filter-tabs");
    if (!tablist) {
      return;
    }
    var table = root.querySelector(root.dataset.portalStatusTable || "table");
    if (!table) {
      return;
    }
    var tabs = tablist.querySelectorAll(".nav-link[data-status], .s-filter-tab[data-status]");
    var rows = table.querySelectorAll("tbody tr[data-status]");
    if (!tabs.length) {
      return;
    }
    var emptyRow = root.dataset.portalStatusEmptyRow
      ? root.querySelector(root.dataset.portalStatusEmptyRow)
      : root.querySelector(".attendance-empty-row");
    var filterEmpty = root.dataset.portalStatusFilterEmpty
      ? root.querySelector(root.dataset.portalStatusFilterEmpty)
      : root.querySelector("#attendance-filter-empty");
    root.dataset.portalStatusTabsBound = "true";

    function applyFilter(status) {
      var visible = 0;
      rows.forEach(function (row) {
        var show = status === "all" || row.getAttribute("data-status") === status;
        row.hidden = !show;
        if (show) {
          visible += 1;
        }
      });
      if (emptyRow) {
        emptyRow.hidden = true;
      }
      if (filterEmpty) {
        filterEmpty.classList.toggle("d-none", visible > 0 || rows.length === 0);
      }
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (item) {
          item.classList.remove("active", "is-active");
          item.setAttribute("aria-selected", "false");
        });
        tab.classList.add(tab.classList.contains("s-filter-tab") ? "is-active" : "active");
        tab.setAttribute("aria-selected", "true");
        applyFilter(tab.getAttribute("data-status"));
      });
    });
  }

  /* ── Parent child switcher ── */
  function initSwitcher(root) {
    if (root.dataset.portalChildSwitcherBound === "true") {
      return;
    }
    var pills = root.querySelectorAll("[data-child-idx]");
    var blocks = root.querySelectorAll("[data-child-block]");
    if (!pills.length || !blocks.length) {
      return;
    }
    root.dataset.portalChildSwitcherBound = "true";
    pills.forEach(function (pill) {
      pill.addEventListener("click", function () {
        var idx = pill.dataset.childIdx;
        pills.forEach(function (item) {
          item.classList.remove("is-active");
          item.setAttribute("aria-pressed", "false");
        });
        blocks.forEach(function (block) {
          block.classList.add("d-none");
        });
        pill.classList.add("is-active");
        pill.setAttribute("aria-pressed", "true");
        var activeBlock = root.querySelector('[data-child-block="' + idx + '"]');
        if (activeBlock) {
          activeBlock.classList.remove("d-none");
        }
      });
    });
  }

  /* ── Lessons filter ── */
  function tabButtons(tablist, attr) {
    return tablist
      ? Array.prototype.slice.call(tablist.querySelectorAll("[" + attr + "]"))
      : [];
  }

  function activeClassFor(tablist) {
    if (!tablist) {
      return "active";
    }
    return tablist.querySelector(".s-filter-tab, .s-pill") ? "is-active" : "active";
  }

  function readActiveValue(tablist, attr, fallback) {
    if (!tablist) {
      return fallback;
    }
    var activeClass = activeClassFor(tablist);
    var active = tablist.querySelector("." + activeClass + "[" + attr + "]")
      || tablist.querySelector("[" + attr + "]." + activeClass);
    return active ? (active.getAttribute(attr) || fallback) : fallback;
  }

  function setActiveTab(tablist, tab, attr) {
    var activeClass = activeClassFor(tablist);
    tabButtons(tablist, attr).forEach(function (item) {
      item.classList.remove(activeClass, "active", "is-active");
      item.setAttribute("aria-selected", "false");
    });
    tab.classList.add(activeClass);
    if (activeClass === "active") {
      tab.classList.add("active");
    }
    tab.setAttribute("aria-selected", "true");
  }

  function setItemVisible(item, show, hideMode) {
    if (hideMode === "class") {
      item.classList.toggle("d-none", !show);
    } else {
      item.hidden = !show;
    }
  }

  function initLessonsFilter(root) {
    if (root.dataset.portalLessonsFilterBound === "true") {
      return;
    }
    var subjectTabsSel = root.dataset.portalLessonsSubjectTabs || "#lessonSubjectTabs";
    var categoryTabsSel = root.dataset.portalLessonsCategoryTabs || "#lessonCategoryTabs";
    var periodTabsSel = root.dataset.portalLessonsPeriodTabs || "[data-portal-lessons-period-tabs]";
    var itemsSel = root.dataset.portalLessonsItems;
    var emptyRowSel = root.dataset.portalLessonsEmptyRow || ".lessons-empty-row";
    var filterEmptySel = root.dataset.portalLessonsEmpty || "#lessons-filter-empty";
    var hideMode = root.dataset.portalLessonsHide || "hidden";
    var subjectTablist = root.querySelector(subjectTabsSel);
    var categoryTablist = root.querySelector(categoryTabsSel);
    var periodTablist = root.querySelector(periodTabsSel);

    if (!itemsSel) {
      if (root.querySelector("#teacher-lessons-table")) {
        itemsSel = "#teacher-lessons-table tbody tr[data-subject]";
        hideMode = "hidden";
      } else if (root.querySelector("#student-lessons-table")) {
        itemsSel = "#student-lessons-table .s-lesson-card[data-subject]";
        hideMode = "class";
      }
    }
    if (!itemsSel || (!subjectTablist && !categoryTablist && !periodTablist)) {
      return;
    }

    root.dataset.portalLessonsFilterBound = "true";
    var activeSubject = readActiveValue(subjectTablist, "data-subject", "all");
    var activeCategory = readActiveValue(categoryTablist, "data-category", "all");
    var activePeriod = readActiveValue(periodTablist, "data-period", "all");

    function parseLocalDate(value) {
      if (!value) {
        return null;
      }
      var parts = value.split("-");
      if (parts.length !== 3) {
        return null;
      }
      return new Date(
        parseInt(parts[0], 10),
        parseInt(parts[1], 10) - 1,
        parseInt(parts[2], 10)
      );
    }

    function itemMatchesPeriod(item) {
      if (activePeriod === "all") {
        return true;
      }
      var lessonDate = parseLocalDate(item.getAttribute("data-lesson-date"));
      if (!lessonDate) {
        return false;
      }
      var today = new Date();
      today.setHours(0, 0, 0, 0);
      var start = new Date(today);
      if (activePeriod === "week") {
        start.setDate(start.getDate() - 7);
      } else if (activePeriod === "month") {
        start.setDate(start.getDate() - 30);
      } else if (activePeriod === "year") {
        start.setDate(start.getDate() - 365);
      } else {
        return true;
      }
      return lessonDate >= start;
    }

    function rowMatchesCategory(item) {
      if (activeCategory === "all") {
        return true;
      }
      var rowCategory = item.getAttribute("data-category") || "";
      if (activeCategory === "none") {
        return !rowCategory;
      }
      return rowCategory === String(activeCategory);
    }

    function applyFilters() {
      var items = root.querySelectorAll(itemsSel);
      var visible = 0;
      items.forEach(function (item) {
        var showSubject = activeSubject === "all"
          || item.getAttribute("data-subject") === activeSubject;
        var show = showSubject && rowMatchesCategory(item) && itemMatchesPeriod(item);
        setItemVisible(item, show, hideMode);
        if (show) {
          visible += 1;
        }
      });
      var emptyRow = root.querySelector(emptyRowSel);
      if (emptyRow) {
        emptyRow.hidden = true;
      }
      var filterEmpty = root.querySelector(filterEmptySel)
        || document.querySelector(filterEmptySel);
      if (filterEmpty) {
        filterEmpty.classList.toggle("d-none", visible > 0 || items.length === 0);
      }
    }

    root.addEventListener("click", function (event) {
      var subjectTab = null;
      var categoryTab = null;
      var periodTab = null;
      if (subjectTablist) {
        subjectTab = event.target.closest("[data-subject]");
        if (subjectTab && !subjectTablist.contains(subjectTab)) {
          subjectTab = null;
        }
      }
      if (categoryTablist) {
        categoryTab = event.target.closest("[data-category]");
        if (categoryTab && !categoryTablist.contains(categoryTab)) {
          categoryTab = null;
        }
      }
      if (periodTablist) {
        periodTab = event.target.closest("[data-period]");
        if (periodTab && !periodTablist.contains(periodTab)) {
          periodTab = null;
        }
      }
      if (!subjectTab && !categoryTab && !periodTab) {
        return;
      }
      if (subjectTab) {
        setActiveTab(subjectTablist, subjectTab, "data-subject");
        activeSubject = subjectTab.getAttribute("data-subject") || "all";
      }
      if (categoryTab) {
        setActiveTab(categoryTablist, categoryTab, "data-category");
        activeCategory = categoryTab.getAttribute("data-category") || "all";
      }
      if (periodTab) {
        setActiveTab(periodTablist, periodTab, "data-period");
        activePeriod = periodTab.getAttribute("data-period") || "all";
      }
      applyFilters();
    });

    applyFilters();
  }

  /* ── Score shell (quiz / lesson score toggle) ── */
  function initScoreShell(root) {
    if (root.dataset.portalScoreBound === "true") {
      return;
    }
    var tabs = root.querySelectorAll("[data-score-tab]");
    var panels = root.querySelectorAll("[data-score-panel]");
    if (!tabs.length || !panels.length) {
      return;
    }
    root.dataset.portalScoreBound = "true";

    function countFor(name) {
      var tab = root.querySelector('[data-score-tab="' + name + '"]');
      if (!tab) {
        return 0;
      }
      var badge = tab.querySelector(".portal-score-segment__count, .s-filter-tab__badge");
      return badge ? parseInt(badge.textContent, 10) || 0 : 0;
    }

    function activate(name) {
      tabs.forEach(function (tab) {
        var active = tab.getAttribute("data-score-tab") === name;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
      panels.forEach(function (panel) {
        var active = panel.getAttribute("data-score-panel") === name;
        panel.classList.toggle("is-active", active);
        panel.hidden = !active;
      });
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        activate(tab.getAttribute("data-score-tab"));
      });
    });

    var initial = new URLSearchParams(window.location.search).get("view");
    if (initial !== "quiz" && initial !== "weekly" && initial !== "lesson") {
      initial = countFor("quiz") === 0 && countFor("weekly") > 0 ? "weekly" : "quiz";
    }
    if (initial === "lesson") {
      initial = "weekly";
    }
    activate(initial);
  }

  /* ── Scores period filter ── */
  function parseScoreDate(value) {
    if (!value) {
      return null;
    }
    var parts = value.split("-");
    if (parts.length !== 3) {
      return null;
    }
    return new Date(
      parseInt(parts[0], 10),
      parseInt(parts[1], 10) - 1,
      parseInt(parts[2], 10)
    );
  }

  function scoreMatchesPeriod(item, activePeriod) {
    if (activePeriod === "all") {
      return true;
    }
    var scoreDate = parseScoreDate(item.getAttribute("data-score-date") || item.getAttribute("data-score-day"));
    if (!scoreDate) {
      return false;
    }
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    var start = new Date(today);
    if (activePeriod === "week") {
      start.setDate(start.getDate() - 7);
    } else if (activePeriod === "month") {
      start.setDate(start.getDate() - 30);
    } else if (activePeriod === "year") {
      start.setDate(start.getDate() - 365);
    } else {
      return true;
    }
    return scoreDate >= start;
  }

  function updateScoreTabCounts(root) {
    root.querySelectorAll("[data-score-tab]").forEach(function (tab) {
      var name = tab.getAttribute("data-score-tab");
      var panel = root.querySelector('[data-score-panel="' + name + '"]');
      if (!panel) {
        return;
      }
      var visible = panel.querySelectorAll("tr[data-score-date]:not([hidden])").length;
      var badge = tab.querySelector(".portal-score-segment__count, .s-filter-tab__badge");
      if (badge) {
        badge.textContent = visible;
      }
    });
  }

  function scoreMatchesGroup(item, activeGroup) {
    if (activeGroup === "all") {
      return true;
    }
    var ids = item.getAttribute("data-group-ids") || "";
    if (!ids) {
      return false;
    }
    return ids.split(",").indexOf(String(activeGroup)) !== -1;
  }

  function updateGroupChipCounts(root, activePeriod) {
    var groupNav = root.querySelector("[data-score-group-filter]");
    if (!groupNav) {
      return;
    }
    groupNav.querySelectorAll("[data-score-group]").forEach(function (btn) {
      var groupId = btn.getAttribute("data-score-group") || "all";
      var count = 0;
      root.querySelectorAll("tr[data-score-date]").forEach(function (row) {
        if (!scoreMatchesPeriod(row, activePeriod)) {
          return;
        }
        if (groupId === "all" || scoreMatchesGroup(row, groupId)) {
          count += 1;
        }
      });
      var meta = btn.querySelector("[data-score-group-count]");
      if (meta) {
        meta.textContent = count;
      }
    });
  }

  function syncScoreGroupUrl(activeGroup) {
    var url = new URL(window.location.href);
    if (activeGroup === "all") {
      url.searchParams.delete("group");
    } else {
      url.searchParams.set("group", activeGroup);
    }
    var next = url.pathname + url.search;
    if (next !== window.location.pathname + window.location.search) {
      window.history.replaceState(
        Object.assign({}, window.history.state, { scoreGroup: activeGroup }),
        "",
        next
      );
    }
  }

  function initScoresPeriodFilter(root) {
    if (root.__scoreFilterController) {
      return root.__scoreFilterController;
    }
    var periodTablist = root.querySelector("[data-portal-scores-period-tabs]");
    var groupNav = root.querySelector("[data-score-group-filter]");
    if (!periodTablist && !groupNav) {
      return null;
    }

    root.dataset.portalScoresFilterBound = "true";
    var activePeriod = periodTablist
      ? readActiveValue(periodTablist, "data-period", "all")
      : "all";
    var activeGroup = new URLSearchParams(window.location.search).get("group") || "all";
    if (groupNav) {
      var validGroups = {};
      groupNav.querySelectorAll("[data-score-group]").forEach(function (btn) {
        var groupId = btn.getAttribute("data-score-group");
        if (groupId && groupId !== "all") {
          validGroups[groupId] = true;
        }
      });
      if (activeGroup !== "all" && !validGroups[activeGroup]) {
        activeGroup = "all";
      }
      setScoreGroupActive(groupNav, activeGroup);
    }

    function applyFilters() {
      var tableRows = root.querySelectorAll("tr[data-score-date]");
      var dayCards = root.querySelectorAll("[data-score-day]");
      var visibleRows = 0;

      tableRows.forEach(function (row) {
        var show = scoreMatchesPeriod(row, activePeriod) && scoreMatchesGroup(row, activeGroup);
        row.hidden = !show;
        if (show) {
          visibleRows += 1;
        }
      });

      var visibleDays = 0;
      dayCards.forEach(function (card) {
        var show = scoreMatchesPeriod(card, activePeriod) && scoreMatchesGroup(card, activeGroup);
        card.hidden = !show;
        if (show) {
          visibleDays += 1;
        }
      });

      root.querySelectorAll("[data-score-panel]").forEach(function (panel) {
        var dataRows = panel.querySelectorAll("tr[data-score-date]");
        var anyData = dataRows.length > 0;
        var anyVisible = Array.prototype.some.call(dataRows, function (row) {
          return !row.hidden;
        });
        panel.querySelectorAll("tbody tr:not([data-score-date])").forEach(function (row) {
          row.hidden = anyData && !anyVisible;
        });
      });

      updateScoreTabCounts(root);
      updateGroupChipCounts(root, activePeriod);

      var filterEmpty = root.querySelector("#scores-filter-empty");
      var hasItems = tableRows.length > 0 || dayCards.length > 0;
      var visibleCount = visibleRows + visibleDays;
      if (filterEmpty) {
        filterEmpty.classList.toggle("d-none", visibleCount > 0 || !hasItems);
      }
    }

    var controller = {
      setPeriod: function (period) {
        activePeriod = period || "all";
        applyFilters();
      },
      setGroup: function (group) {
        activeGroup = group || "all";
        applyFilters();
      },
      applyFilters: applyFilters,
    };
    root.__scoreFilterController = controller;

    if (periodTablist) {
      periodTablist.addEventListener("click", function (event) {
        var periodTab = event.target.closest("[data-period]");
        if (!periodTab || !periodTablist.contains(periodTab)) {
          return;
        }
        setActiveTab(periodTablist, periodTab, "data-period");
        controller.setPeriod(periodTab.getAttribute("data-period") || "all");
      });
    }

    window.requestAnimationFrame(applyFilters);
    return controller;
  }

  function setScoreGroupActive(groupNav, groupId) {
    if (!groupNav) {
      return;
    }
    var activeChip = groupNav.querySelector('[data-score-group="' + groupId + '"]');
    if (!activeChip) {
      return;
    }
    groupNav.querySelectorAll("[data-score-group]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn === activeChip);
    });
  }

  function handleScoreGroupClick(event) {
    var groupBtn = event.target.closest("[data-score-group]");
    if (!groupBtn) {
      return;
    }
    var root = groupBtn.closest("[data-portal-scores-filter]");
    if (!root) {
      return;
    }
    event.preventDefault();
    var groupNav = root.querySelector("[data-score-group-filter]");
    setScoreGroupActive(groupNav, groupBtn.getAttribute("data-score-group") || "all");
    var controller = initScoresPeriodFilter(root);
    if (!controller) {
      return;
    }
    var group = groupBtn.getAttribute("data-score-group") || "all";
    syncScoreGroupUrl(group);
    controller.setGroup(group);
  }

  function initAll() {
    document.querySelectorAll("[data-portal-service-tabs]").forEach(initServiceTabs);
    document.querySelectorAll("[data-portal-status-tabs]").forEach(initStatusTabs);
    document.querySelectorAll("[data-portal-child-switcher]").forEach(initSwitcher);
    document.querySelectorAll("[data-portal-lessons-filter]").forEach(initLessonsFilter);
    document.querySelectorAll("[data-portal-scores-filter]").forEach(initScoresPeriodFilter);
    document.querySelectorAll("[data-score-shell]").forEach(initScoreShell);
  }

  function scheduleInitAll() {
    window.requestAnimationFrame(initAll);
  }

  document.addEventListener("click", handleScoreGroupClick);
  document.addEventListener("portal:content-loaded", scheduleInitAll);
  bindContentLoaded(scheduleInitAll);
})();

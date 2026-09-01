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

  /* ── Quiz categories: service tabs + category tabs ── */
  function initQuizCategoryFilters(root) {
    if (root.dataset.portalQuizCategoryFiltersBound === "true") {
      return;
    }
    var table = root.querySelector(root.dataset.portalQuizTable || "#quiz-categories-table");
    if (!table) {
      return;
    }
    var serviceTablist = root.querySelector("[data-portal-quiz-service-tablist]");
    var categoryTablist = root.querySelector("[data-portal-quiz-category-tablist]");
    var categoryFilterRow = root.querySelector("[data-portal-quiz-category-filter-row]");
    if (!serviceTablist && !categoryTablist) {
      return;
    }
    var rows = table.querySelectorAll("tbody tr[data-category]");
    var emptyRow = root.dataset.portalQuizEmptyRow
      ? root.querySelector(root.dataset.portalQuizEmptyRow)
      : null;
    var filterEmpty = root.dataset.portalQuizFilterEmpty
      ? root.querySelector(root.dataset.portalQuizFilterEmpty)
      : null;
    var serviceTabs = serviceTablist
      ? serviceTablist.querySelectorAll(".s-filter-tab[data-service], .nav-link[data-service]")
      : [];
    var categoryTabs = categoryTablist
      ? categoryTablist.querySelectorAll(".s-pill[data-category], .s-filter-tab[data-category]")
      : [];
    var allCategoryTab = categoryTablist
      ? categoryTablist.querySelector('[data-category="all"]')
      : null;
    var activeService = "all";
    var activeCategory = "all";
    root.dataset.portalQuizCategoryFiltersBound = "true";

    function setActiveTabs(tabs, attr, value, activeClass) {
      tabs.forEach(function (tab) {
        var isActive = tab.getAttribute(attr) === value;
        tab.classList.toggle(activeClass, isActive);
        tab.classList.toggle("active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }

    function syncCategoryTabs() {
      if (!categoryTablist) {
        return;
      }
      var visibleSpecific = 0;
      var activeStillVisible = activeCategory === "all";
      categoryTabs.forEach(function (tab) {
        var cat = tab.getAttribute("data-category");
        if (cat === "all") {
          tab.classList.remove("d-none");
          return;
        }
        var show = activeService === "all" || tab.getAttribute("data-service") === activeService;
        tab.classList.toggle("d-none", !show);
        if (show) {
          visibleSpecific += 1;
          if (cat === activeCategory) {
            activeStillVisible = true;
          }
        }
      });
      if (allCategoryTab) {
        var allCount = 0;
        rows.forEach(function (row) {
          if (activeService === "all" || row.getAttribute("data-service") === activeService) {
            allCount += 1;
          }
        });
        var badge = allCategoryTab.querySelector(".s-pill__count, .s-filter-tab__badge");
        if (badge) {
          badge.textContent = String(allCount);
        }
      }
      if (categoryFilterRow) {
        categoryFilterRow.classList.toggle("d-none", visibleSpecific <= 1);
      }
      if (!activeStillVisible || visibleSpecific <= 1) {
        activeCategory = "all";
        setActiveTabs(categoryTabs, "data-category", "all", "is-active");
      }
    }

    function applyFilters() {
      var visible = 0;
      rows.forEach(function (row) {
        var serviceOk = activeService === "all" || row.getAttribute("data-service") === activeService;
        var categoryOk = activeCategory === "all" || row.getAttribute("data-category") === activeCategory;
        var show = serviceOk && categoryOk;
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

    serviceTabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        activeService = tab.getAttribute("data-service") || "all";
        activeCategory = "all";
        setActiveTabs(serviceTabs, "data-service", activeService, "is-active");
        setActiveTabs(categoryTabs, "data-category", "all", "is-active");
        syncCategoryTabs();
        applyFilters();
      });
    });

    categoryTabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        if (tab.classList.contains("d-none")) {
          return;
        }
        activeCategory = tab.getAttribute("data-category") || "all";
        setActiveTabs(categoryTabs, "data-category", activeCategory, "is-active");
        applyFilters();
      });
    });

    if (serviceTabs.length) {
      var activeServiceTab = serviceTablist.querySelector(".s-filter-tab.is-active, .nav-link.active, .nav-link.is-active");
      if (activeServiceTab) {
        activeService = activeServiceTab.getAttribute("data-service") || "all";
      }
    }
    syncCategoryTabs();
    applyFilters();
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

    function readActiveGroup() {
      var groupNav = root.closest("[data-portal-scores-filter]")
        ? root.closest("[data-portal-scores-filter]").querySelector("[data-score-group-filter]")
        : null;
      if (!groupNav) {
        return null;
      }
      return readGroupFilterValue(groupNav);
    }

    function updateStatusBadges(activeGroup) {
      tabs.forEach(function (tab) {
        var status = tab.getAttribute("data-status");
        var badge = tab.querySelector(".s-filter-tab__badge, .nav-link__badge");
        if (!badge) {
          return;
        }
        var count = 0;
        rows.forEach(function (row) {
          if (!scoreMatchesGroup(row, activeGroup)) {
            return;
          }
          if (status === "all" || row.getAttribute("data-status") === status) {
            count += 1;
          }
        });
        badge.textContent = count;
      });
    }

    function applyFilter(status) {
      var activeGroup = readActiveGroup();
      var visible = 0;
      rows.forEach(function (row) {
        var showStatus = status === "all" || row.getAttribute("data-status") === status;
        var showGroup = scoreMatchesGroup(row, activeGroup);
        var show = showStatus && showGroup;
        row.hidden = !show;
        if (show) {
          visible += 1;
        }
      });
      updateStatusBadges(activeGroup);
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

    root.__statusFilterApply = function () {
      var active = tablist.querySelector(".is-active[data-status], .active[data-status]")
        || tabs[0];
      if (active) {
        applyFilter(active.getAttribute("data-status") || "all");
      }
    };
    root.__statusFilterApply();
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

  function readGroupFilterValue(groupNav) {
    if (!groupNav) {
      return null;
    }
    var select = groupNav.querySelector("[data-score-group-select]");
    if (select) {
      return select.value || null;
    }
    return readActiveValue(groupNav, "data-score-group", null);
  }

  function getGroupFilterElement(groupNav, groupId) {
    if (!groupNav || !groupId) {
      return null;
    }
    var select = groupNav.querySelector("[data-score-group-select]");
    if (select) {
      return select.querySelector('option[data-score-group="' + groupId + '"]')
        || Array.prototype.find.call(select.options, function (option) {
          return option.value === String(groupId);
        });
    }
    return groupNav.querySelector('[data-score-group="' + groupId + '"]');
  }

  function readCategoryFilterValue(categoryTablist) {
    if (!categoryTablist) {
      return "all";
    }
    var select = categoryTablist.querySelector("[data-category-select]");
    if (select) {
      return select.value || "all";
    }
    return readActiveValue(categoryTablist, "data-category", "all");
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
    var periodItemsSel = root.dataset.portalLessonsPeriodItems || "";
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
    if (!itemsSel || (!subjectTablist && !categoryTablist && !periodTablist && !root.querySelector("[data-score-group-filter]"))) {
      return;
    }

    root.dataset.portalLessonsFilterBound = "true";
    var activeSubject = readActiveValue(subjectTablist, "data-subject", "all");
    var activeCategory = readCategoryFilterValue(categoryTablist);
    var activePeriod = periodTablist
      ? readActiveValue(periodTablist, "data-period", "week")
      : "all";
    var groupNav = root.querySelector("[data-score-group-filter]");

    function readActiveGroup() {
      if (!groupNav) {
        return null;
      }
      return readGroupFilterValue(groupNav);
    }

    function itemMatchesGroup(item) {
      return scoreMatchesGroup(item, readActiveGroup());
    }

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

    function itemMatchesPeriod(item, periodCode) {
      var period = periodCode == null ? activePeriod : periodCode;
      if (period === "all") {
        return true;
      }
      var lessonDate = parseLocalDate(item.getAttribute("data-lesson-date"));
      if (!lessonDate) {
        return false;
      }
      var today = new Date();
      today.setHours(0, 0, 0, 0);
      var start = new Date(today);
      if (period === "week") {
        start.setDate(start.getDate() - 7);
      } else if (period === "month") {
        start.setDate(start.getDate() - 30);
      } else if (period === "year") {
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

    function itemMatchesSubject(item) {
      return activeSubject === "all"
        || item.getAttribute("data-subject") === activeSubject;
    }

    function updateSubjectTabCounts() {
      if (!subjectTablist) {
        return;
      }
      var items = root.querySelectorAll(itemsSel);
      var counts = { all: 0 };
      items.forEach(function (item) {
        if (!itemMatchesGroup(item) || !itemMatchesPeriod(item)) {
          return;
        }
        counts.all += 1;
        var subject = item.getAttribute("data-subject") || "";
        if (subject) {
          counts[subject] = (counts[subject] || 0) + 1;
        }
      });
      subjectTablist.querySelectorAll("[data-subject]").forEach(function (tab) {
        var code = tab.getAttribute("data-subject");
        var badge = tab.querySelector(".s-filter-tab__badge");
        if (!badge) {
          return;
        }
        badge.textContent = code === "all" ? counts.all : (counts[code] || 0);
      });
    }

    function updatePeriodTabCounts() {
      if (!periodTablist) {
        return;
      }
      var items = root.querySelectorAll(itemsSel);
      var counts = { all: 0, week: 0, month: 0, year: 0 };
      items.forEach(function (item) {
        if (!itemMatchesGroup(item) || !itemMatchesSubject(item) || !rowMatchesCategory(item)) {
          return;
        }
        counts.all += 1;
        if (itemMatchesPeriod(item, "week")) {
          counts.week += 1;
        }
        if (itemMatchesPeriod(item, "month")) {
          counts.month += 1;
        }
        if (itemMatchesPeriod(item, "year")) {
          counts.year += 1;
        }
      });
      periodTablist.querySelectorAll("[data-period]").forEach(function (tab) {
        var code = tab.getAttribute("data-period");
        var badge = tab.querySelector(".s-filter-tab__badge");
        if (!badge || !code) {
          return;
        }
        badge.textContent = counts[code] || 0;
      });
    }

    function syncSubjectTabsToGroup() {
      if (!subjectTablist || !groupNav) {
        return;
      }
      var activeGroup = readActiveGroup();
      if (!activeGroup) {
        return;
      }
      var groupBtn = getGroupFilterElement(groupNav, activeGroup);
      if (!groupBtn) {
        return;
      }
      var servicesRaw = groupBtn.getAttribute("data-group-services") || "";
      var services = servicesRaw
        ? servicesRaw.split(",").map(function (value) { return value.trim(); }).filter(Boolean)
        : [];
      var needReset = false;
      subjectTablist.querySelectorAll("[data-subject]").forEach(function (tab) {
        var code = tab.getAttribute("data-subject");
        if (code === "all") {
          tab.hidden = false;
          return;
        }
        var show = !services.length || services.indexOf(code) !== -1;
        tab.hidden = !show;
        if (!show && tab.classList.contains("is-active")) {
          needReset = true;
        }
      });
      if (needReset) {
        var allTab = subjectTablist.querySelector('[data-subject="all"]');
        if (allTab) {
          setActiveTab(subjectTablist, allTab, "data-subject");
          activeSubject = "all";
        }
      }
    }

    function applyFilters() {
      syncSubjectTabsToGroup();
      var items = root.querySelectorAll(itemsSel);
      var visible = 0;
      items.forEach(function (item) {
        var show = itemMatchesSubject(item)
          && rowMatchesCategory(item)
          && itemMatchesPeriod(item)
          && itemMatchesGroup(item);
        setItemVisible(item, show, hideMode);
        if (show) {
          visible += 1;
        }
      });
      root.querySelectorAll("[data-portal-video-records] .s-lesson-card[data-group-ids]").forEach(function (item) {
        var show = itemMatchesGroup(item);
        setItemVisible(item, show, "class");
      });
      if (periodItemsSel) {
        root.querySelectorAll(periodItemsSel).forEach(function (item) {
          var show = itemMatchesPeriod(item) && itemMatchesGroup(item);
          if (item.hasAttribute("data-subject") && !itemMatchesSubject(item)) {
            show = false;
          }
          if (item.hasAttribute("data-category") && !rowMatchesCategory(item)) {
            show = false;
          }
          setItemVisible(item, show, "class");
        });
        root.querySelectorAll("[data-portal-student-homeworks]").forEach(function (section) {
          var cards = section.querySelectorAll(".s-homework-summary-card");
          if (!cards.length) {
            return;
          }
          var anyVisible = false;
          cards.forEach(function (card) {
            if (!card.classList.contains("d-none") && !card.hidden) {
              anyVisible = true;
            }
          });
          section.classList.toggle("d-none", !anyVisible);
        });
      }
      var emptyRow = root.querySelector(emptyRowSel);
      if (emptyRow) {
        emptyRow.hidden = true;
      }
      var filterEmpty = root.querySelector(filterEmptySel)
        || document.querySelector(filterEmptySel);
      if (filterEmpty) {
        filterEmpty.classList.toggle("d-none", visible > 0 || items.length === 0);
      }
      updateSubjectTabCounts();
      updatePeriodTabCounts();
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

    var categorySelect = categoryTablist && categoryTablist.querySelector("[data-category-select]");
    if (categorySelect) {
      categorySelect.addEventListener("change", function () {
        activeCategory = categorySelect.value || "all";
        applyFilters();
      });
    }

    root.__lessonsFilterApply = applyFilters;
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
    if (initial !== "quiz" && initial !== "weekly" && initial !== "mock" && initial !== "lesson") {
      initial = countFor("quiz") === 0 && countFor("weekly") > 0 ? "weekly" : "quiz";
    }
    if (initial === "lesson") {
      initial = "weekly";
    }
    if (initial === "mock" && !root.querySelector('[data-score-tab="mock"]')) {
      initial = countFor("quiz") === 0 && countFor("weekly") > 0 ? "weekly" : "quiz";
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
      var badge = tab.querySelector(".portal-score-segment__count, .s-filter-tab__badge");
      if (!badge) {
        return;
      }
      var dataRows = panel.querySelectorAll("tr[data-score-date]");
      if (!dataRows.length && badge.hasAttribute("data-score-tab-total")) {
        badge.textContent = badge.getAttribute("data-score-tab-total") || "0";
        return;
      }
      var visible = panel.querySelectorAll("tr[data-score-date]:not([hidden])").length;
      badge.textContent = visible;
    });
  }

  function scoreMatchesGroup(item, activeGroup) {
    if (!activeGroup) {
      return true;
    }
    var ids = item.getAttribute("data-group-ids") || item.getAttribute("data-group-id") || "";
    if (!ids) {
      return false;
    }
    return ids.split(",").map(function (value) {
      return value.trim();
    }).indexOf(String(activeGroup)) !== -1;
  }

  function findFilterRoot(root, selector) {
    if (!root) {
      return null;
    }
    if (root.matches && root.matches(selector)) {
      return root;
    }
    return root.querySelector(selector);
  }

  function collectGroupCountableItems(root) {
    var seen = [];
    var pushUnique = function (node) {
      if (!node || seen.indexOf(node) !== -1) {
        return;
      }
      seen.push(node);
    };
    root.querySelectorAll("tr[data-score-date]").forEach(pushUnique);
    root.querySelectorAll("[data-score-day]").forEach(pushUnique);
    root.querySelectorAll("tr[data-group-ids]").forEach(pushUnique);
    root.querySelectorAll(".s-lesson-card[data-group-ids]").forEach(pushUnique);
    root.querySelectorAll(".s-schedule-lesson[data-group-ids]").forEach(pushUnique);
    root.querySelectorAll("#classrooms-table tbody tr[data-group-ids]").forEach(pushUnique);
    return seen;
  }

  function itemMatchesPeriodForGroupCount(item, activePeriod) {
    if (item.hasAttribute("data-score-date") || item.hasAttribute("data-score-day")) {
      return scoreMatchesPeriod(item, activePeriod);
    }
    return true;
  }

  function updateGroupChipCounts(root, activePeriod) {
    var groupNav = root.querySelector("[data-score-group-filter]");
    if (!groupNav) {
      return;
    }
    var items = collectGroupCountableItems(root);
    var select = groupNav.querySelector("[data-score-group-select]");
    var activeGroup = readGroupFilterValue(groupNav);

    function countForGroup(groupId) {
      var count = 0;
      items.forEach(function (item) {
        if (!itemMatchesPeriodForGroupCount(item, activePeriod)) {
          return;
        }
        if (scoreMatchesGroup(item, groupId)) {
          count += 1;
        }
      });
      return count;
    }

    if (select) {
      var selectBadge = groupNav.querySelector("[data-score-group-count]");
      if (selectBadge && activeGroup) {
        selectBadge.textContent = countForGroup(activeGroup);
      }
      return;
    }

    groupNav.querySelectorAll("button[data-score-group]").forEach(function (btn) {
      var groupId = btn.getAttribute("data-score-group");
      if (!groupId) {
        return;
      }
      var meta = btn.querySelector("[data-score-group-count]");
      if (meta) {
        meta.textContent = countForGroup(groupId);
      }
    });
  }

  function syncScoreGroupUrl(activeGroup) {
    if (!activeGroup) {
      return;
    }
    var url = new URL(window.location.href);
    url.searchParams.set("group", activeGroup);
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
      ? readActiveValue(periodTablist, "data-period", "week")
      : "all";
    var activeGroup = null;
    if (groupNav) {
      var validGroups = {};
      var defaultGroup = null;
      groupNav.querySelectorAll("[data-score-group]").forEach(function (btn) {
        var groupId = btn.getAttribute("data-score-group");
        if (!groupId) {
          return;
        }
        validGroups[groupId] = true;
        if (!defaultGroup) {
          defaultGroup = groupId;
        }
      });
      activeGroup = new URLSearchParams(window.location.search).get("group");
      if (!activeGroup || !validGroups[activeGroup]) {
        activeGroup = defaultGroup;
      }
      if (activeGroup) {
        setScoreGroupActive(groupNav, activeGroup);
        syncScoreGroupUrl(activeGroup);
      }
    }

    function syncDependentFilters() {
      var lessonsRoot = findFilterRoot(root, "[data-portal-lessons-filter]");
      if (lessonsRoot && typeof lessonsRoot.__lessonsFilterApply === "function") {
        lessonsRoot.__lessonsFilterApply();
      }
      var statusRoot = findFilterRoot(root, "[data-portal-status-tabs]");
      if (statusRoot && typeof statusRoot.__statusFilterApply === "function") {
        statusRoot.__statusFilterApply();
      }
    }

    function applyFilters() {
      var tableRows = root.querySelectorAll("tr[data-score-date]");
      var dayCards = root.querySelectorAll("[data-score-day]");
      var groupRows = root.querySelectorAll("tr[data-group-ids]:not([data-score-date])");
      var scheduleItems = root.querySelectorAll(".s-schedule-lesson[data-group-ids]");
      var lessonCards = root.querySelectorAll(".s-lesson-card[data-group-ids], .s-lesson-card[data-group-id]");
      var visibleRows = 0;

      tableRows.forEach(function (row) {
        var show = scoreMatchesPeriod(row, activePeriod) && scoreMatchesGroup(row, activeGroup);
        row.hidden = !show;
        if (show) {
          visibleRows += 1;
        }
      });

      groupRows.forEach(function (row) {
        var show = scoreMatchesGroup(row, activeGroup);
        row.hidden = !show;
        row.classList.toggle("d-none", !show);
        if (show) {
          visibleRows += 1;
        }
      });

      scheduleItems.forEach(function (item) {
        var show = scoreMatchesGroup(item, activeGroup);
        item.classList.toggle("d-none", !show);
        if (show) {
          visibleRows += 1;
        }
      });

      lessonCards.forEach(function (item) {
        var show = scoreMatchesGroup(item, activeGroup);
        setItemVisible(item, show, "class");
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
      syncDependentFilters();

      var filterEmpty = root.querySelector("#scores-filter-empty")
        || root.querySelector("#lessons-filter-empty")
        || root.querySelector("#attendance-filter-empty")
        || root.querySelector("#classrooms-filter-empty");
      var countableItems = tableRows.length + dayCards.length + groupRows.length
        + lessonCards.length + scheduleItems.length;
      var visibleCount = visibleRows + visibleDays;
      if (filterEmpty) {
        filterEmpty.classList.toggle("d-none", visibleCount > 0 || countableItems === 0);
      }
    }

    var controller = {
      setPeriod: function (period) {
        activePeriod = period || "all";
        applyFilters();
      },
      setGroup: function (group) {
        activeGroup = group || null;
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

    var groupSelect = groupNav && groupNav.querySelector("[data-score-group-select]");
    if (groupSelect && groupSelect.dataset.scoreGroupSelectBound !== "true") {
      groupSelect.dataset.scoreGroupSelectBound = "true";
      groupSelect.addEventListener("change", function () {
        var group = groupSelect.value;
        if (!group) {
          return;
        }
        syncScoreGroupUrl(group);
        controller.setGroup(group);
      });
    }

    window.requestAnimationFrame(applyFilters);
    return controller;
  }

  function setScoreGroupActive(groupNav, groupId) {
    if (!groupNav) {
      return;
    }
    var select = groupNav.querySelector("[data-score-group-select]");
    if (select) {
      if (groupId) {
        select.value = String(groupId);
      }
      return;
    }
    var activeChip = groupNav.querySelector('[data-score-group="' + groupId + '"]')
      || groupNav.querySelector("[data-score-group]");
    if (!activeChip) {
      return;
    }
    setActiveTab(groupNav, activeChip, "data-score-group");
  }

  function applyQuizHubService(hub, service) {
    var activeService = service || "all";
    hub.querySelectorAll("[data-portal-quiz-service-tablist] .qhub__service-btn").forEach(function (btn) {
      var active = btn.getAttribute("data-service") === activeService;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", active ? "true" : "false");
    });
    hub.querySelectorAll("[data-portal-quiz-category-tablist] .qhub__nav-item").forEach(function (item) {
      var cat = item.getAttribute("data-category");
      if (cat === "all") {
        item.style.display = "";
        item.classList.add("is-active");
        item.setAttribute("aria-selected", "true");
        return;
      }
      var show = activeService === "all" || item.getAttribute("data-service") === activeService;
      item.style.display = show ? "" : "none";
      item.classList.remove("is-active");
    });
    var visible = 0;
    hub.querySelectorAll(".qhub__card").forEach(function (card) {
      var show = activeService === "all" || card.getAttribute("data-service") === activeService;
      card.style.display = show ? "" : "none";
      if (show) {
        visible += 1;
      }
    });
    var emptyMsg = hub.querySelector("#quiz-categories-filter-empty");
    if (emptyMsg) {
      emptyMsg.classList.toggle("d-none", visible > 0);
    }
  }

  function handleQuizHubClick(event) {
    var hub = event.target.closest("[data-quiz-hub]");
    if (!hub) {
      return;
    }
    var svcBtn = event.target.closest("[data-portal-quiz-service-tablist] .qhub__service-btn");
    if (svcBtn && hub.contains(svcBtn)) {
      event.preventDefault();
      applyQuizHubService(hub, svcBtn.getAttribute("data-service") || "all");
      return;
    }
    var allBtn = event.target.closest('[data-portal-quiz-category-tablist] [data-category="all"]');
    if (allBtn && hub.contains(allBtn)) {
      event.preventDefault();
      var activeSvc = hub.querySelector("[data-portal-quiz-service-tablist] .qhub__service-btn.is-active");
      applyQuizHubService(hub, activeSvc ? activeSvc.getAttribute("data-service") : "all");
    }
  }

  function handleScoreGroupClick(event) {
    if (event.target.closest("[data-score-group-select]")) {
      return;
    }
    var groupBtn = event.target.closest("button[data-score-group]");
    if (!groupBtn) {
      return;
    }
    var root = groupBtn.closest("[data-portal-scores-filter]");
    if (!root) {
      return;
    }
    event.preventDefault();
    var groupNav = root.querySelector("[data-score-group-filter]");
    setScoreGroupActive(groupNav, groupBtn.getAttribute("data-score-group"));
    var controller = initScoresPeriodFilter(root);
    if (!controller) {
      return;
    }
    var group = groupBtn.getAttribute("data-score-group");
    if (!group) {
      return;
    }
    syncScoreGroupUrl(group);
    controller.setGroup(group);
  }

  function initAll() {
    document.querySelectorAll("[data-portal-service-tabs]").forEach(initServiceTabs);
    document.querySelectorAll("[data-portal-quiz-category-filters]").forEach(initQuizCategoryFilters);
    document.querySelectorAll("[data-portal-status-tabs]").forEach(initStatusTabs);
    document.querySelectorAll("[data-portal-child-switcher]").forEach(initSwitcher);
    document.querySelectorAll("[data-portal-lessons-filter]").forEach(initLessonsFilter);
    document.querySelectorAll("[data-portal-scores-filter]").forEach(initScoresPeriodFilter);
    document.querySelectorAll("[data-score-shell]").forEach(initScoreShell);
  }

  function scheduleInitAll() {
    window.requestAnimationFrame(initAll);
  }

  document.addEventListener("click", handleQuizHubClick);
  document.addEventListener("click", handleScoreGroupClick);
  document.addEventListener("portal:content-loaded", scheduleInitAll);
  bindContentLoaded(scheduleInitAll);
})();

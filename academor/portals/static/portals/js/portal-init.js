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
    document.addEventListener("portal:content-loaded", fn);
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

  /* ── Dashboard date ── */
  function updateDates() {
    var text = new Date().toLocaleDateString("az-AZ", {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
    document.querySelectorAll("[data-portal-today-date]").forEach(function (el) {
      el.textContent = text;
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
    var itemsSel = root.dataset.portalLessonsItems;
    var emptyRowSel = root.dataset.portalLessonsEmptyRow || ".lessons-empty-row";
    var filterEmptySel = root.dataset.portalLessonsEmpty || "#lessons-filter-empty";
    var hideMode = root.dataset.portalLessonsHide || "hidden";
    var subjectTablist = root.querySelector(subjectTabsSel);
    var categoryTablist = root.querySelector(categoryTabsSel);

    if (!itemsSel) {
      if (root.querySelector("#teacher-lessons-table")) {
        itemsSel = "#teacher-lessons-table tbody tr[data-subject]";
        hideMode = "hidden";
      } else if (root.querySelector("#student-lessons-table")) {
        itemsSel = "#student-lessons-table .s-lesson-card[data-subject]";
        hideMode = "class";
      }
    }
    if (!itemsSel || (!subjectTablist && !categoryTablist)) {
      return;
    }

    root.dataset.portalLessonsFilterBound = "true";
    var activeSubject = readActiveValue(subjectTablist, "data-subject", "all");
    var activeCategory = readActiveValue(categoryTablist, "data-category", "all");

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
        var show = showSubject && rowMatchesCategory(item);
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
      if (!subjectTab && !categoryTab) {
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
    if (initial !== "quiz" && initial !== "lesson") {
      initial = countFor("quiz") === 0 && countFor("lesson") > 0 ? "lesson" : "quiz";
    }
    activate(initial);
  }

  function initAll() {
    document.querySelectorAll("[data-portal-service-tabs]").forEach(initServiceTabs);
    document.querySelectorAll("[data-portal-status-tabs]").forEach(initStatusTabs);
    document.querySelectorAll("[data-portal-child-switcher]").forEach(initSwitcher);
    document.querySelectorAll("[data-portal-lessons-filter]").forEach(initLessonsFilter);
    document.querySelectorAll("[data-score-shell]").forEach(initScoreShell);
    updateDates();
  }

  bindContentLoaded(initAll);
})();

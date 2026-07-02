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

  function tabButtons(tablist, attr) {
    if (!tablist) {
      return [];
    }
    return Array.prototype.slice.call(tablist.querySelectorAll("[" + attr + "]"));
  }

  function activeClassFor(tablist) {
    if (!tablist) {
      return "active";
    }
    if (tablist.querySelector(".s-filter-tab, .s-pill")) {
      return "is-active";
    }
    return "active";
  }

  function readActiveValue(tablist, attr, fallback) {
    if (!tablist) {
      return fallback;
    }
    var activeClass = activeClassFor(tablist);
    var active = tablist.querySelector("." + activeClass + "[" + attr + "]")
      || tablist.querySelector("[" + attr + "]." + activeClass);
    if (!active) {
      return fallback;
    }
    return active.getAttribute(attr) || fallback;
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
      return;
    }
    item.hidden = !show;
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

    if (!itemsSel) {
      return;
    }

    if (!subjectTablist && !categoryTablist) {
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
        subjectTab = event.target.closest("[" + "data-subject" + "]");
        if (subjectTab && !subjectTablist.contains(subjectTab)) {
          subjectTab = null;
        }
      }

      if (categoryTablist) {
        categoryTab = event.target.closest("[" + "data-category" + "]");
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

  function initAll() {
    document.querySelectorAll("[data-portal-lessons-filter]").forEach(initLessonsFilter);
  }

  onReady(initAll);
  document.addEventListener("portal:content-loaded", initAll);
})();

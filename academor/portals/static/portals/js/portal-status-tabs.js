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

  function initAll() {
    document.querySelectorAll("[data-portal-status-tabs]").forEach(initStatusTabs);
  }

  onReady(initAll);
  document.addEventListener("portal:content-loaded", initAll);
})();

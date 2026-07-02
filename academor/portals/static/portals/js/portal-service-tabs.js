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

  function initAll() {
    document.querySelectorAll("[data-portal-service-tabs]").forEach(initServiceTabs);
  }

  onReady(initAll);
  document.addEventListener("portal:content-loaded", initAll);
})();

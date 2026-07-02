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

  function readExportConfig() {
    var node = document.getElementById("portal-group-detail-export");
    if (!node) {
      return null;
    }
    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      return null;
    }
  }

  function csvEscape(value) {
    var text = String(value || "");
    if (/[",\n]/.test(text)) {
      return '"' + text.replace(/"/g, '""') + '"';
    }
    return text;
  }

  function initGroupDetail() {
    var root = document.getElementById("portal-teacher-group-detail");
    if (!root || root.dataset.portalGroupDetailBound === "true") {
      return;
    }
    root.dataset.portalGroupDetailBound = "true";

    var exportConfig = readExportConfig();

    function filterStudents() {
      var input = document.getElementById("student-search");
      var search = (input && input.value ? input.value : "").toLowerCase();
      root.querySelectorAll(".portal-student-item").forEach(function (item) {
        var name = item.dataset.name || "";
        item.style.display = name.indexOf(search) !== -1 ? "" : "none";
      });
    }

    function exportStudents(format) {
      if (format !== "csv" || !exportConfig) {
        return;
      }

      var rows = [exportConfig.headers || []];
      root.querySelectorAll(".portal-student-item[data-full-name]").forEach(function (item) {
        rows.push([
          item.getAttribute("data-full-name") || "",
          item.getAttribute("data-username") || "",
          item.getAttribute("data-phone") || "",
        ]);
      });

      if (rows.length <= 1) {
        return;
      }

      var csv = rows.map(function (row) {
        return row.map(csvEscape).join(",");
      }).join("\n");
      var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      var link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = exportConfig.filename || "students.csv";
      link.click();
      URL.revokeObjectURL(link.href);
    }

    root.addEventListener("input", function (event) {
      if (event.target && event.target.id === "student-search") {
        filterStudents();
      }
    });

    root.addEventListener("click", function (event) {
      var exportBtn = event.target.closest("[data-portal-export-students]");
      if (exportBtn) {
        event.preventDefault();
        exportStudents(exportBtn.dataset.portalExportStudents);
      }
    });
  }

  onReady(initGroupDetail);
  document.addEventListener("portal:content-loaded", initGroupDetail);
})();

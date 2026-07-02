(function () {
  "use strict";

  function boot() {
    var form = document.querySelector("[data-attendance-session-form]");
    if (!form || form.dataset.portalAttendanceBound === "true") {
      return;
    }
    form.dataset.portalAttendanceBound = "true";

    var rows = Array.prototype.slice.call(form.querySelectorAll("[data-student-row]"));
    var selectAll = form.querySelector("#select-all-checkbox");
    var countEl = form.querySelector("[data-selected-count]");
    var saveBtn = form.querySelector("#save-btn");
    var selectOneMsg = form.getAttribute("data-select-one-msg") || "Select at least one student.";
    var counts = {
      present: form.querySelector("#count-present"),
      absent: form.querySelector("#count-absent"),
      late: form.querySelector("#count-late"),
    };

    function rowCheckbox(row) {
      return row.querySelector(".student-checkbox");
    }

    function rowRadios(row) {
      return Array.prototype.slice.call(row.querySelectorAll('input[type="radio"]'));
    }

    function rowStatus(row) {
      var checked = row.querySelector('input[type="radio"]:checked');
      return checked ? checked.value : "";
    }

    function syncRowActiveState(row) {
      var status = rowStatus(row);
      row.setAttribute("data-current-status", status);
      rowRadios(row).forEach(function (radio) {
        var label = radio.closest(".portal-status-btn");
        if (label) {
          label.classList.toggle("active", radio.checked);
        }
      });
    }

    function setRowStatus(row, status) {
      rowRadios(row).forEach(function (radio) {
        radio.checked = radio.value === status;
      });
      syncRowActiveState(row);
    }

    function selectedRows() {
      return rows.filter(function (row) {
        var checkbox = rowCheckbox(row);
        return checkbox && checkbox.checked;
      });
    }

    function updateSelectedCount() {
      var selected = selectedRows();
      if (countEl) {
        countEl.textContent = selected.length + " / " + rows.length;
      }
      if (selectAll) {
        selectAll.checked = rows.length > 0 && selected.length === rows.length;
        selectAll.indeterminate = selected.length > 0 && selected.length < rows.length;
      }
      if (saveBtn) {
        saveBtn.disabled = selected.length === 0;
      }
    }

    function updateStatusCounts() {
      var tallies = { present: 0, absent: 0, late: 0 };
      selectedRows().forEach(function (row) {
        var status = rowStatus(row);
        if (Object.prototype.hasOwnProperty.call(tallies, status)) {
          tallies[status] += 1;
        }
      });
      if (counts.present) {
        counts.present.textContent = String(tallies.present);
      }
      if (counts.absent) {
        counts.absent.textContent = String(tallies.absent);
      }
      if (counts.late) {
        counts.late.textContent = String(tallies.late);
      }
    }

    function refresh() {
      updateSelectedCount();
      updateStatusCounts();
    }

    rows.forEach(function (row) {
      syncRowActiveState(row);
      var checkbox = rowCheckbox(row);
      if (checkbox) {
        checkbox.addEventListener("change", refresh);
      }
      rowRadios(row).forEach(function (radio) {
        radio.addEventListener("change", function () {
          syncRowActiveState(row);
          updateStatusCounts();
        });
      });
    });

    if (selectAll) {
      selectAll.addEventListener("change", function () {
        var checked = selectAll.checked;
        rows.forEach(function (row) {
          var checkbox = rowCheckbox(row);
          if (checkbox) {
            checkbox.checked = checked;
          }
        });
        refresh();
      });
    }

    form.querySelectorAll("[data-bulk-status]").forEach(function (button) {
      button.addEventListener("click", function () {
        var status = button.getAttribute("data-bulk-status");
        selectedRows().forEach(function (row) {
          setRowStatus(row, status);
        });
        refresh();
      });
    });

    form.addEventListener("submit", function (event) {
      if (selectedRows().length === 0) {
        event.preventDefault();
        window.alert(selectOneMsg);
        return;
      }

      rows.forEach(function (row) {
        var checkbox = rowCheckbox(row);
        var isSelected = checkbox && checkbox.checked;
        rowRadios(row).forEach(function (radio) {
          radio.disabled = !isSelected;
        });
        if (checkbox && !isSelected) {
          checkbox.disabled = true;
        }
      });
    });

    refresh();
  }

  if (window.portalOnReady) {
    window.portalOnReady(boot);
  } else {
    document.addEventListener("DOMContentLoaded", boot);
  }
})();

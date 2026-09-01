(function () {
  "use strict";

  function reindexRows(container, countInput) {
    var rows = container.querySelectorAll(".portal-schedule-slot-row");
    rows.forEach(function (row, index) {
      row.dataset.slotIndex = String(index);
      var weekday = row.querySelector("[data-slot-weekday], select[name*='-weekday']");
      var startTime = row.querySelector("[data-slot-start-time], input[name*='-start_time']");
      var duration = row.querySelector("[data-slot-duration], input[name*='-duration_min']");
      if (weekday) {
        weekday.name = "slots-" + index + "-weekday";
        weekday.id = "slots-" + index + "-weekday";
      }
      if (startTime) {
        startTime.name = "slots-" + index + "-start_time";
        startTime.id = "slots-" + index + "-start_time";
      }
      if (duration) {
        duration.name = "slots-" + index + "-duration_min";
        duration.id = "slots-" + index + "-duration_min";
      }
      var removeBtn = row.querySelector(".portal-schedule-slot-remove");
      if (removeBtn) {
        removeBtn.hidden = rows.length <= 1;
      }
    });
    if (countInput) {
      countInput.value = String(rows.length);
    }
  }

  function bindRemove(row, container, countInput) {
    var removeBtn = row.querySelector(".portal-schedule-slot-remove");
    if (!removeBtn || removeBtn.dataset.bound === "true") {
      return;
    }
    removeBtn.dataset.bound = "true";
    removeBtn.addEventListener("click", function () {
      row.remove();
      reindexRows(container, countInput);
    });
  }

  function init() {
    var form = document.getElementById("portal-teacher-schedule-bulk-form");
    if (!form) {
      return;
    }
    var container = document.getElementById("schedule-slot-rows");
    var countInput = document.getElementById("schedule-slot-count");
    var addBtn = document.getElementById("schedule-slot-add");
    var template = document.getElementById("schedule-slot-row-template");
    if (!container || !countInput || !addBtn || !template) {
      return;
    }

    container.querySelectorAll(".portal-schedule-slot-row").forEach(function (row) {
      bindRemove(row, container, countInput);
    });

    addBtn.addEventListener("click", function () {
      var index = container.querySelectorAll(".portal-schedule-slot-row").length;
      var html = template.innerHTML.replace(/__INDEX__/g, String(index));
      var wrapper = document.createElement("div");
      wrapper.innerHTML = html.trim();
      var row = wrapper.firstElementChild;
      container.appendChild(row);
      bindRemove(row, container, countInput);
      reindexRows(container, countInput);
      if (typeof window.portalInitTime24Inputs === "function") {
        window.portalInitTime24Inputs(row);
      }
      var focusTarget = row.querySelector("[data-slot-weekday], select");
      if (focusTarget) {
        focusTarget.focus();
      }
    });

    reindexRows(container, countInput);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

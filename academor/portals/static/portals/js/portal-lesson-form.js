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

  function initLessonForm() {
    var form = document.querySelector("[data-lesson-form]");
    if (!form || form.dataset.portalLessonFormBound === "true") {
      return;
    }
    form.dataset.portalLessonFormBound = "true";

    /* Group select-all */
    var selectAll = form.querySelector("[data-lesson-select-all-groups]");
    var groupInputs = Array.prototype.slice.call(
      form.querySelectorAll(".portal-lesson-group-input, [name='groups']")
    );
    var groupCountEl = form.querySelector("[data-lesson-group-count]");

    function updateGroupCount() {
      if (!groupCountEl || !groupInputs.length) {
        return;
      }
      var selected = groupInputs.filter(function (input) {
        return input.checked;
      }).length;
      groupCountEl.textContent = selected + " / " + groupInputs.length;
      if (selectAll) {
        selectAll.checked = selected === groupInputs.length;
        selectAll.indeterminate = selected > 0 && selected < groupInputs.length;
      }
    }

    if (selectAll && groupInputs.length) {
      selectAll.addEventListener("change", function () {
        var checked = selectAll.checked;
        groupInputs.forEach(function (input) {
          input.checked = checked;
        });
        updateGroupCount();
      });
    }

    groupInputs.forEach(function (input) {
      input.addEventListener("change", updateGroupCount);
    });
    updateGroupCount();

    /* Material tabs */
    var tabs = form.querySelectorAll("[data-material-tab]");
    var panels = form.querySelectorAll("[data-material-panel]");

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        var target = tab.getAttribute("data-material-tab");
        tabs.forEach(function (item) {
          var active = item === tab;
          item.classList.toggle("is-active", active);
          item.setAttribute("aria-selected", active ? "true" : "false");
        });
        panels.forEach(function (panel) {
          var show = panel.getAttribute("data-material-panel") === target;
          panel.classList.toggle("is-active", show);
          if (show) {
            panel.removeAttribute("hidden");
          } else {
            panel.setAttribute("hidden", "hidden");
          }
        });
      });
    });

    /* File dropzones */
    form.querySelectorAll("[data-lesson-dropzone]").forEach(function (zone) {
      var target = zone.getAttribute("data-target");
      var fileInput = zone.querySelector('input[type="file"]');
      var filenameEl = form.querySelector('[data-lesson-filename="' + target + '"]');

      if (!fileInput) {
        return;
      }

      function showFilename() {
        var name = fileInput.files && fileInput.files[0] ? fileInput.files[0].name : "";
        if (filenameEl) {
          filenameEl.textContent = name;
        }
        zone.classList.toggle("has-file", Boolean(name));
      }

      function assignFiles(files) {
        if (!files || !files.length) {
          return;
        }
        try {
          var dt = new DataTransfer();
          dt.items.add(files[0]);
          fileInput.files = dt.files;
        } catch (err) {
          return;
        }
        showFilename();
      }

      fileInput.addEventListener("change", showFilename);
      showFilename();

      zone.addEventListener("dragover", function (event) {
        event.preventDefault();
        zone.classList.add("is-dragover");
      });

      zone.addEventListener("dragleave", function () {
        zone.classList.remove("is-dragover");
      });

      zone.addEventListener("drop", function (event) {
        event.preventDefault();
        zone.classList.remove("is-dragover");
        assignFiles(event.dataTransfer.files);
      });
    });

    /* Submit feedback */
    var submitBtn = form.querySelector("[data-lesson-submit]");
    form.addEventListener("submit", function () {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add("disabled");
      }
    });
  }

  onReady(initLessonForm);
})();

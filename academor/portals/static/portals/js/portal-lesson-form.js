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

  function resetLessonFormSubmitButtons() {
    document.querySelectorAll("[data-lesson-form] [data-lesson-submit]").forEach(function (btn) {
      btn.disabled = false;
      btn.classList.remove("disabled", "is-submitting");
      btn.removeAttribute("aria-busy");
    });
  }

  if (!window.__portalLessonFormPageshowBound) {
    window.__portalLessonFormPageshowBound = true;
    window.addEventListener("pageshow", function (event) {
      if (event.persisted) {
        resetLessonFormSubmitButtons();
      }
    });
  }

  function initLessonForm() {
    document.querySelectorAll("[data-lesson-form]").forEach(function (form) {
      if (form.dataset.portalLessonFormBound === "true") {
        return;
      }
      form.dataset.portalLessonFormBound = "true";
      bindLessonForm(form);
    });
  }

  function bindLessonForm(form) {
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
      var allowMultiple = zone.getAttribute("data-multiple") === "true";

      if (!fileInput) {
        return;
      }

      if (allowMultiple && fileInput.multiple !== true) {
        fileInput.setAttribute("multiple", "multiple");
      }

      function showFilename() {
        var files = fileInput.files ? Array.prototype.slice.call(fileInput.files) : [];
        var label = "";
        if (files.length === 1) {
          label = files[0].name;
        } else if (files.length > 1) {
          label = files.length + " files";
        }
        if (filenameEl) {
          filenameEl.textContent = label;
        }
        zone.classList.toggle("has-file", files.length > 0);
      }

      function assignFiles(files) {
        if (!files || !files.length) {
          return;
        }
        try {
          var dt = new DataTransfer();
          Array.prototype.forEach.call(files, function (file) {
            dt.items.add(file);
          });
          fileInput.files = dt.files;
        } catch (err) {
          return;
        }
        showFilename();
      }

      function applySelectedFiles(files) {
        var selected = files ? Array.prototype.slice.call(files) : [];
        if (!selected.length) {
          showFilename();
          return;
        }
        if (target !== "image" || typeof window.portalCompressImageFiles !== "function") {
          assignFiles(selected);
          return;
        }
        zone.classList.add("is-compressing");
        window
          .portalCompressImageFiles(selected, {
            maxWidth: 1920,
            maxHeight: 1080,
            quality: 0.82,
          })
          .then(function (compressed) {
            assignFiles(compressed);
          })
          .catch(function () {
            assignFiles(selected);
          })
          .finally(function () {
            zone.classList.remove("is-compressing");
          });
      }

      fileInput.addEventListener("change", function () {
        applySelectedFiles(fileInput.files);
      });
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
        applySelectedFiles(event.dataTransfer.files);
      });
    });

    function initExistingMaterialRemoval() {
      form.querySelectorAll("[data-lesson-remove-toggle]").forEach(function (button) {
        button.addEventListener("click", function () {
          var item = button.closest("[data-lesson-existing-item]");
          var input = item ? item.querySelector("[data-lesson-remove-input]") : null;
          if (!input) {
            return;
          }
          var marked = !input.checked;
          input.checked = marked;
          item.classList.toggle("is-marked-for-removal", marked);
          button.setAttribute("aria-pressed", marked ? "true" : "false");
          button.innerHTML =
            '<i class="bi bi-' +
            (marked ? "arrow-counterclockwise" : "trash") +
            '" aria-hidden="true"></i> ' +
            (marked ? button.getAttribute("data-label-undo") : button.getAttribute("data-label-delete"));
        });
      });
    }

    function syncVideoLinkRemoveButtons(list) {
      var rows = list.querySelectorAll("[data-lesson-video-link-row]");
      rows.forEach(function (row, index) {
        var removeBtn = row.querySelector("[data-lesson-video-link-remove]");
        if (!removeBtn) {
          return;
        }
        removeBtn.hidden = rows.length === 1 && index === 0;
      });
    }

    function appendFileRow(list, root) {
      var template = root.querySelector("[data-lesson-file-row-template]");
      var row;
      if (template && template.content && template.content.firstElementChild) {
        row = template.content.firstElementChild.cloneNode(true);
      } else {
        var sample = list.querySelector("[data-lesson-file-row]");
        if (!sample) {
          return;
        }
        row = sample.cloneNode(true);
        var input = row.querySelector('input[type="file"]');
        if (input) {
          input.value = "";
        }
      }
      list.appendChild(row);
    }

    function syncFileRowRemoveButtons(list) {
      var rows = list.querySelectorAll("[data-lesson-file-row]");
      rows.forEach(function (row, index) {
        var removeBtn = row.querySelector("[data-lesson-file-row-remove]");
        if (!removeBtn) {
          return;
        }
        removeBtn.hidden = rows.length === 1 && index === 0;
      });
    }

    function compressImageInput(input) {
      if (!input || !input.files || !input.files.length) {
        return;
      }
      if (typeof window.portalCompressImageFiles !== "function") {
        return;
      }
      var row = input.closest("[data-lesson-file-row]");
      if (row) {
        row.classList.add("is-compressing");
      }
      window
        .portalCompressImageFiles([input.files[0]], {
          maxWidth: 1920,
          maxHeight: 1080,
          quality: 0.82,
        })
        .then(function (compressed) {
          if (!compressed.length) {
            return;
          }
          try {
            var dt = new DataTransfer();
            dt.items.add(compressed[0]);
            input.files = dt.files;
          } catch (err) {
            /* keep original */
          }
        })
        .finally(function () {
          if (row) {
            row.classList.remove("is-compressing");
          }
        });
    }

    function initFileRows(root) {
      var list = root.querySelector("[data-lesson-file-rows-list]");
      var addBtn = root.querySelector("[data-lesson-file-row-add]");
      var fieldName = root.getAttribute("data-lesson-file-rows") || "";
      if (!list || !addBtn) {
        return;
      }

      syncFileRowRemoveButtons(list);

      addBtn.addEventListener("click", function () {
        appendFileRow(list, root);
        syncFileRowRemoveButtons(list);
      });

      list.addEventListener("click", function (event) {
        var removeBtn = event.target.closest("[data-lesson-file-row-remove]");
        if (!removeBtn) {
          return;
        }
        var row = removeBtn.closest("[data-lesson-file-row]");
        var rows = list.querySelectorAll("[data-lesson-file-row]");
        if (!row) {
          return;
        }
        if (rows.length <= 1) {
          var input = row.querySelector('input[type="file"]');
          if (input) {
            input.value = "";
          }
          return;
        }
        row.remove();
        syncFileRowRemoveButtons(list);
      });

      if (fieldName === "image_files") {
        list.addEventListener("change", function (event) {
          var input = event.target.closest('input[type="file"]');
          if (input) {
            compressImageInput(input);
          }
        });
      }
    }

    function appendVideoLinkRow(list, root) {
      var template = root.querySelector("[data-lesson-video-link-template]");
      var row;
      if (template && template.content && template.content.firstElementChild) {
        row = template.content.firstElementChild.cloneNode(true);
      } else {
        var sample = list.querySelector("[data-lesson-video-link-row]");
        if (!sample) {
          return;
        }
        row = sample.cloneNode(true);
        row.querySelectorAll("input").forEach(function (input) {
          input.value = "";
        });
      }
      list.appendChild(row);
    }

    function initVideoLinkRows() {
      var root = form.querySelector("[data-lesson-video-links]");
      if (!root) {
        return;
      }
      var list = root.querySelector("[data-lesson-video-links-list]");
      var addBtn = root.querySelector("[data-lesson-video-link-add]");
      if (!list || !addBtn) {
        return;
      }

      syncVideoLinkRemoveButtons(list);

      addBtn.addEventListener("click", function () {
        appendVideoLinkRow(list, root);
        syncVideoLinkRemoveButtons(list);
      });

      list.addEventListener("click", function (event) {
        var removeBtn = event.target.closest("[data-lesson-video-link-remove]");
        if (!removeBtn) {
          return;
        }
        var row = removeBtn.closest("[data-lesson-video-link-row]");
        var rows = list.querySelectorAll("[data-lesson-video-link-row]");
        if (!row) {
          return;
        }
        if (rows.length <= 1) {
          var input = row.querySelector('input[type="url"]');
          if (input) {
            input.value = "";
          }
          return;
        }
        row.remove();
        syncVideoLinkRemoveButtons(list);
      });
    }

    initExistingMaterialRemoval();
    form.querySelectorAll("[data-lesson-file-rows]").forEach(initFileRows);
    initVideoLinkRows();

    /* Submit feedback — visual busy state only; never leave the button disabled */
    var submitBtn = form.querySelector("[data-lesson-submit]");
    var submitting = false;

    function setSubmitBusy(active) {
      if (!submitBtn) {
        return;
      }
      submitting = active;
      submitBtn.disabled = false;
      submitBtn.classList.remove("disabled");
      submitBtn.classList.toggle("is-submitting", active);
      if (active) {
        submitBtn.setAttribute("aria-busy", "true");
      } else {
        submitBtn.removeAttribute("aria-busy");
      }
    }

    form.addEventListener("input", function () {
      setSubmitBusy(false);
    });

    form.addEventListener("change", function () {
      setSubmitBusy(false);
    });

    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        setSubmitBusy(false);
        return;
      }
      if (submitting) {
        event.preventDefault();
        return;
      }
      setSubmitBusy(true);
    });
  }

  onReady(initLessonForm);
  document.addEventListener("portal:content-loaded", initLessonForm);
  window.portalInitLessonForm = initLessonForm;
})();

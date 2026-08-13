(function () {
  "use strict";

  function adminForm(root) {
    return root.querySelector("#listeningaudio_form") || root.querySelector("form");
  }

  function groupOptionsUrl(form) {
    var configured = form && form.getAttribute("data-listening-group-options-url");
    if (configured) {
      return configured;
    }
    var path = window.location.pathname.replace(/\/$/, "");
    if (/\/add$/.test(path) || /\/change$/.test(path)) {
      return path.replace(/\/(add|change)$/, "/group-options/").replace(/\/\/+/g, "/");
    }
    return path + "/group-options/";
  }

  function csrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function audioId(form) {
    var idInput = form.querySelector('input[name="id"]');
    if (idInput && idInput.value) {
      return idInput.value;
    }
    return "";
  }

  function collectInlineGroups(form) {
    var groups = [];
    var seen = {};

    form.querySelectorAll('input[name$="-title"]').forEach(function (titleInput) {
      var match = titleInput.name.match(/^(.+)-(\d+)-title$/);
      if (!match) {
        return;
      }
      var prefix = match[1];
      var index = match[2];
      var rowKey = prefix + "-" + index;
      if (seen[rowKey]) {
        return;
      }
      if (!form.querySelector('[name="' + prefix + "-" + index + '-option_pool_text"]')) {
        return;
      }
      if (isDeletedRow(prefix, index, form)) {
        return;
      }
      seen[rowKey] = true;
      groups.push({
        ref: "idx:" + index,
        title: (titleInput.value || "").trim(),
        order: readInlineOrder(form, prefix, index),
      });
    });

    return groups.sort(function (a, b) {
      return a.order - b.order || a.ref.localeCompare(b.ref);
    });
  }

  function isDeletedRow(prefix, index, form) {
    var deleteInput = form.querySelector('[name="' + prefix + "-" + index + '-DELETE"]');
    return Boolean(deleteInput && deleteInput.checked);
  }

  function readInlineOrder(form, prefix, index) {
    var orderInput = form.querySelector('[name="' + prefix + "-" + index + '-order"]');
    var value = orderInput ? parseInt(orderInput.value, 10) : 0;
    return Number.isFinite(value) ? value : 0;
  }

  function renderGroupOptions(select, groups) {
    var current = select.value;
    select.innerHTML = "";
    var empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "---------";
    select.appendChild(empty);

    groups.forEach(function (group) {
      var option = document.createElement("option");
      option.value = group.ref || ("id:" + group.id);
      var label = group.title || ("Group " + (group.order || ""));
      option.textContent = label;
      select.appendChild(option);
    });

    if (current) {
      select.value = current;
    }
  }

  function fetchSavedGroups(form) {
    var pk = audioId(form);
    if (!pk) {
      return Promise.resolve([]);
    }
    var url = groupOptionsUrl(form) + "?audio_id=" + encodeURIComponent(pk);
    return fetch(url, {
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        if (!response.ok) {
          return [];
        }
        return response.json();
      })
      .then(function (payload) {
        return (payload && payload.groups) || [];
      })
      .catch(function () {
        return [];
      });
  }

  function mergeSavedGroups(inlineGroups, savedGroups) {
    var merged = savedGroups.map(function (group) {
      return {
        id: group.id,
        ref: "id:" + group.id,
        title: group.title,
        order: group.order,
      };
    });
    inlineGroups.forEach(function (group) {
      merged.push(group);
    });
    return merged.sort(function (a, b) {
      return (a.order || 0) - (b.order || 0);
    });
  }

  function syncGroupSelects(form) {
    var inlineGroups = collectInlineGroups(form);
    return fetchSavedGroups(form).then(function (savedGroups) {
      var groups = mergeSavedGroups(inlineGroups, savedGroups);
      form
        .querySelectorAll("select.listening-question-group-ref, select[name$='-group_ref']")
        .forEach(function (select) {
          renderGroupOptions(select, groups);
        });
    });
  }

  function bindForm(form) {
    if (!form || form.dataset.listeningGroupSyncBound === "1") {
      return;
    }
    form.dataset.listeningGroupSyncBound = "1";
    form.setAttribute("data-listening-group-options-url", groupOptionsUrl(form));

    var scheduleSync = function () {
      window.clearTimeout(form._listeningGroupSyncTimer);
      form._listeningGroupSyncTimer = window.setTimeout(function () {
        syncGroupSelects(form);
      }, 120);
    };

    form.addEventListener("input", function (event) {
      var target = event.target;
      if (!target || !target.name) {
        return;
      }
      if (target.name.indexOf("-title") !== -1 || target.name.indexOf("-order") !== -1) {
        scheduleSync();
      }
    });

    document.addEventListener("click", function (event) {
      var target = event.target;
      if (!target) {
        return;
      }
      if (target.closest(".add-row") || target.closest("[id$='-add']")) {
        window.setTimeout(function () {
          syncGroupSelects(form);
        }, 0);
      }
    });

    if (typeof django !== "undefined" && django.jQuery) {
      django.jQuery(document).on("formset:added", function () {
        syncGroupSelects(form);
      });
    }

    syncGroupSelects(form);
  }

  function init() {
    var form = adminForm(document);
    if (!form) {
      return;
    }
    bindForm(form);
  }

  document.addEventListener("DOMContentLoaded", init);
})();

(function () {
  "use strict";

  var QUESTION_TOGGLE_FIELDS = [
    "group_ref",
    "answer_options",
    "question_config",
    "word_limit",
    "case_insensitive",
    "accept_alternatives_text",
    "question",
    "correct_answer",
  ];

  var FALLBACK_HELP = {
    question:
      "Prompt, table, flow-chart, or diagram context. Leave blank for a numbered answer line only when appropriate.",
    correct_answer: "Exact text for gap-fill tasks or the matching option label.",
    answer_options:
      "JSON list for multiple choice only. Leave empty for fixed or group options.",
    question_config:
      "Advanced JSON only. Prefer word limit and alternative answer fields.",
    word_limit: "Maximum words accepted from the student.",
    case_insensitive: "Ignore letter case when auto-scoring text answers.",
    accept_alternatives_text:
      "One acceptable answer per line (e.g. mechanized for mechanised).",
    group_ref:
      "Choose a matching group. New groups appear here as soon as you enter a title below.",
  };

  var MATCHING_TYPES = {
    matching_headings: true,
    matching_info: true,
    matching_features: true,
    matching_sentence_endings: true,
  };

  var TEXT_TYPES = {
    sentence_completion: true,
    summary_completion: true,
    note_completion: true,
    table_completion: true,
    flowchart_completion: true,
    diagram_label: true,
    short_answer: true,
  };

  function adminForm(root) {
    return (
      root.querySelector("#readingpassage_form") ||
      root.querySelector("form#readingquestiongroup_form") ||
      root.querySelector("form")
    );
  }

  function adminCustomUrl(form, attrName, suffix) {
    var configured = form && form.getAttribute(attrName);
    if (configured) {
      return configured;
    }
    var path = window.location.pathname.replace(/\/$/, "");
    if (/\/add$/.test(path) || /\/change$/.test(path)) {
      return path.replace(/\/(add|change)$/, suffix).replace(/\/\/+/g, "/");
    }
    return path + suffix;
  }

  function groupOptionsUrl(form) {
    return adminCustomUrl(form, "data-reading-group-options-url", "/group-options/");
  }

  function questionTypeFieldsUrl(form) {
    return adminCustomUrl(
      form,
      "data-reading-question-type-fields-url",
      "/question-type-fields/"
    );
  }

  function csrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function passageId(form) {
    var idInput = form.querySelector('input[name="id"]');
    if (idInput && idInput.value) {
      return idInput.value;
    }
    return "";
  }

  function isDeletedRow(prefix, index, form) {
    var deleteInput = form.querySelector('[name="' + prefix + "-" + index + '-DELETE"]');
    return Boolean(deleteInput && deleteInput.checked);
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
      if (!form.querySelector('[name="' + prefix + "-" + index + '-option_pool"]')) {
        return;
      }
      if (isDeletedRow(prefix, index, form)) {
        return;
      }
      seen[rowKey] = true;

      var idInput = form.querySelector('[name="' + prefix + "-" + index + '-id"]');
      var orderInput = form.querySelector('[name="' + prefix + "-" + index + '-order"]');
      var typeInput = form.querySelector('[name="' + prefix + "-" + index + '-question_type"]');
      var orderValue = orderInput ? parseInt(orderInput.value, 10) : parseInt(index, 10);
      groups.push({
        prefix: prefix,
        index: index,
        pk: idInput && idInput.value ? idInput.value : "",
        title: (titleInput.value || "").trim(),
        order: isNaN(orderValue) ? parseInt(index, 10) : orderValue,
        question_type: typeInput ? typeInput.value : "",
      });
    });

    groups.sort(function (a, b) {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return parseInt(a.index, 10) - parseInt(b.index, 10);
    });

    return groups;
  }

  function groupLabel(group, displayIndex) {
    if (group.title) {
      return group.title;
    }
    if (group.pk) {
      return "Group #" + group.pk;
    }
    return "New group " + (displayIndex + 1);
  }

  function groupValue(group, displayIndex) {
    if (group.pk) {
      return "id:" + group.pk;
    }
    return "idx:" + displayIndex;
  }

  function mergeSavedGroups(inlineGroups, savedGroups) {
    var merged = inlineGroups.slice();
    var knownIds = {};
    merged.forEach(function (group) {
      if (group.pk) {
        knownIds[group.pk] = true;
      }
    });
    savedGroups.forEach(function (saved) {
      if (!knownIds[String(saved.id)]) {
        merged.push({
          pk: String(saved.id),
          title: saved.title || "",
          order: saved.order || 0,
          question_type: saved.question_type || "",
          index: "",
          prefix: "",
        });
      }
    });
    merged.sort(function (a, b) {
      if (a.order !== b.order) {
        return a.order - b.order;
      }
      return String(a.pk).localeCompare(String(b.pk));
    });
    return merged;
  }

  function renderGroupOptions(select, groups, filterType) {
    var previous = select.value;
    select.innerHTML = "";

    var emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "---------";
    select.appendChild(emptyOption);

    groups.forEach(function (group, displayIndex) {
      if (filterType && group.question_type && group.question_type !== filterType) {
        return;
      }
      var option = document.createElement("option");
      option.value = groupValue(group, displayIndex);
      option.textContent = groupLabel(group, displayIndex);
      select.appendChild(option);
    });

    if (
      previous &&
      Array.from(select.options).some(function (option) {
        return option.value === previous;
      })
    ) {
      select.value = previous;
    } else {
      select.value = "";
    }
  }

  function questionTypeSelect(block) {
    return block.querySelector("select[name$='-question_type']");
  }

  function questionFieldRow(block, name) {
    return block.querySelector(".field-" + name);
  }

  function fieldHelp(row) {
    if (!row) {
      return null;
    }
    return row.querySelector(".help") || row.querySelector("p.help");
  }

  function clearQuestionField(block, name) {
    var row = questionFieldRow(block, name);
    if (!row) {
      return;
    }
    var input = row.querySelector("input, textarea, select");
    if (!input) {
      return;
    }
    if (name === "answer_options") {
      input.value = "[]";
    } else if (name === "question_config") {
      input.value = "{}";
    } else if (input.tagName === "SELECT") {
      input.value = "";
    } else {
      input.value = "";
    }
  }

  function fallbackQuestionFieldConfig(questionType) {
    var type = questionType || "mcq";
    var showSet = { question: true, correct_answer: true };
    var clearFields = [];

    if (MATCHING_TYPES[type]) {
      showSet.group_ref = true;
    } else {
      clearFields.push("group_ref");
    }

    if (type === "mcq") {
      showSet.answer_options = true;
    } else {
      clearFields.push("answer_options");
    }

    if (TEXT_TYPES[type]) {
      showSet.question_config = true;
      showSet.word_limit = true;
      showSet.case_insensitive = true;
      showSet.accept_alternatives_text = true;
    } else {
      clearFields.push("question_config", "word_limit", "case_insensitive", "accept_alternatives_text");
    }

    var fieldHelp = {
      question: FALLBACK_HELP.question,
      correct_answer: FALLBACK_HELP.correct_answer,
      answer_options: FALLBACK_HELP.answer_options,
      question_config: FALLBACK_HELP.question_config,
      group_ref: FALLBACK_HELP.group_ref,
    };

    if (type === "mcq") {
      fieldHelp.correct_answer = "Must exactly match one of the answer options.";
    } else if (type === "tfng") {
      fieldHelp.correct_answer = "Enter one of: True, False, Not Given.";
    } else if (type === "ynng") {
      fieldHelp.correct_answer = "Enter one of: Yes, No, Not Given.";
    } else if (MATCHING_TYPES[type]) {
      fieldHelp.correct_answer =
        "Must exactly match one option from the selected group pool.";
    } else if (TEXT_TYPES[type]) {
      fieldHelp.correct_answer = "Primary expected answer for auto-scoring and feedback.";
      fieldHelp.accept_alternatives_text =
        "Other answers that should also count as correct (one per line).";
      fieldHelp.question_config = "Advanced JSON only.";
    }

    return {
      question_type: type,
      show_fields: Object.keys(showSet),
      clear_fields: clearFields,
      field_help: fieldHelp,
    };
  }

  function applyQuestionFieldConfig(block, config) {
    if (!config) {
      return;
    }

    var showSet = {};
    (config.show_fields || []).forEach(function (name) {
      showSet[name] = true;
    });

    QUESTION_TOGGLE_FIELDS.forEach(function (name) {
      var row = questionFieldRow(block, name);
      if (!row) {
        return;
      }
      row.classList.toggle("quiz-admin-hidden-field", !showSet[name]);
    });

    (config.clear_fields || []).forEach(function (name) {
      clearQuestionField(block, name);
    });

    var helpMap = config.field_help || {};
    Object.keys(helpMap).forEach(function (name) {
      var help = fieldHelp(questionFieldRow(block, name));
      if (help) {
        help.textContent = helpMap[name];
      }
    });
  }

  var questionTypeRequestIds = new WeakMap();

  function syncQuestionBlockFields(block, form) {
    var select = questionTypeSelect(block);
    if (!select) {
      return Promise.resolve();
    }

    var questionType = select.value || "mcq";
    applyQuestionFieldConfig(block, fallbackQuestionFieldConfig(questionType));

    var url = questionTypeFieldsUrl(form);
    if (!url) {
      applyQuestionFieldConfig(block, fallbackQuestionFieldConfig(questionType));
      return Promise.resolve();
    }

    var nextRequestId = (questionTypeRequestIds.get(block) || 0) + 1;
    questionTypeRequestIds.set(block, nextRequestId);

    var body = new FormData();
    body.append("question_type", questionType);
    body.append("csrfmiddlewaretoken", csrfToken());

    return fetch(url, {
      method: "POST",
      body: body,
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("question type request failed");
        }
        return response.json();
      })
      .then(function (config) {
        if (questionTypeRequestIds.get(block) !== nextRequestId) {
          return;
        }
        applyQuestionFieldConfig(block, config);
      })
      .catch(function () {
        if (questionTypeRequestIds.get(block) !== nextRequestId) {
          return;
        }
        applyQuestionFieldConfig(block, fallbackQuestionFieldConfig(questionType));
      });
  }

  function refreshGroupSelects(form, groups) {
    form
      .querySelectorAll("select.reading-question-group-ref, select[name$='-group_ref']")
      .forEach(function (select) {
        var block = select.closest(".inline-related");
        var filterType = "";
        if (block) {
          var typeSelect = questionTypeSelect(block);
          filterType = typeSelect ? typeSelect.value : "";
        }
        renderGroupOptions(select, groups, filterType);
      });
  }

  function fetchSavedGroups(form) {
    var pk = passageId(form);
    if (!pk) {
      return Promise.resolve([]);
    }
    var url = groupOptionsUrl(form) + "?passage_id=" + encodeURIComponent(pk);
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

  function syncGroupSelects(form) {
    var inlineGroups = collectInlineGroups(form);
    return fetchSavedGroups(form).then(function (savedGroups) {
      var groups = mergeSavedGroups(inlineGroups, savedGroups);
      refreshGroupSelects(form, groups);
    });
  }

  function isQuestionInlineBlock(block) {
    return Boolean(block.querySelector("[name$='-correct_answer']"));
  }

  function collectQuestionBlocks(root) {
    var blocks = [];
    root.querySelectorAll(".inline-related").forEach(function (block) {
      if (isQuestionInlineBlock(block) && questionTypeSelect(block)) {
        blocks.push(block);
      }
    });
    return blocks;
  }

  function bindQuestionBlock(block, form) {
    if (block.dataset.readingQuestionTypeBound === "1") {
      return;
    }

    var select = questionTypeSelect(block);
    if (!select) {
      return;
    }

    select.addEventListener("change", function () {
      syncQuestionBlockFields(block, form).then(function () {
        syncGroupSelects(form);
      });
    });

    block.dataset.readingQuestionTypeBound = "1";
    syncQuestionBlockFields(block, form);
  }

  function bindQuestionBlocks(root, form) {
    collectQuestionBlocks(root).forEach(function (block) {
      bindQuestionBlock(block, form);
    });
  }

  function debounce(fn, delay) {
    var timer = null;
    return function () {
      var args = arguments;
      var context = this;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () {
        fn.apply(context, args);
      }, delay);
    };
  }

  function bindForm(form) {
    if (!form || form.dataset.readingGroupSyncBound === "1") {
      return;
    }
    form.dataset.readingGroupSyncBound = "1";
    form.setAttribute("data-reading-group-options-url", groupOptionsUrl(form));
    form.setAttribute(
      "data-reading-question-type-fields-url",
      questionTypeFieldsUrl(form)
    );

    var scheduleSync = debounce(function () {
      syncGroupSelects(form);
    }, 120);

    form.addEventListener("input", function (event) {
      var target = event.target;
      if (!target || !target.name) {
        return;
      }
      if (
        target.name.indexOf("-title") !== -1 ||
        target.name.indexOf("-order") !== -1 ||
        target.name.indexOf("-option_pool") !== -1
      ) {
        scheduleSync();
      }
    });

    form.addEventListener("change", function (event) {
      var target = event.target;
      if (!target || !target.name) {
        return;
      }
      if (target.name.indexOf("-DELETE") !== -1) {
        scheduleSync();
      }
    });

    document.addEventListener("click", function (event) {
      var target = event.target;
      if (!target) {
        return;
      }
      if (
        target.closest(".add-row") ||
        target.matches(".add-row a") ||
        target.closest("[id$='-add']")
      ) {
        window.setTimeout(function () {
          initRoot(document, form);
        }, 0);
      }
    });

    if (typeof django !== "undefined" && django.jQuery) {
      django.jQuery(document).on("formset:added", function (_event, row) {
        initRoot(row, form);
      });
    }

    bindQuestionBlocks(form, form);
    syncGroupSelects(form);
  }

  function initRoot(root, form) {
    var resolvedForm = form || adminForm(root) || adminForm(document);
    if (!resolvedForm) {
      return;
    }
    bindQuestionBlocks(root, resolvedForm);
    root.querySelectorAll(".inline-related").forEach(function (block) {
      if (isQuestionInlineBlock(block)) {
        bindQuestionBlock(block, resolvedForm);
      }
    });
  }

  function init() {
    var form = adminForm(document);
    if (!form) {
      return;
    }
    bindForm(form);
    initRoot(document, form);
  }

  document.addEventListener("DOMContentLoaded", init);
})();

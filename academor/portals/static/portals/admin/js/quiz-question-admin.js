(function () {
  "use strict";

  var ANSWER_FIELDS = ["answer_options", "correct_option_number", "correct_answer", "correct_option_index"];
  var RESPONSE_FIELD = "student_response_preview";
  var GRADING_INPUTS = ["is_essay", "is_listening", "is_speaking", "is_reading", "is_math"];

  var PROMPT_TYPES = {
    text: {
      badge: "Text",
      questionLabel: "Question text",
      questionHelp: "Write the full question shown to the student.",
      mediaFileLabel: "Media file",
      mediaUrlLabel: "Media URL",
      mediaUrlHelp: "Optional external link instead of an uploaded file.",
      accept: "",
      showMedia: false,
    },
    image: {
      badge: "Image",
      questionLabel: "Caption (optional)",
      questionHelp: "Short text shown below the image.",
      mediaFileLabel: "Image file",
      mediaUrlLabel: "Image URL",
      mediaUrlHelp: "Direct link to an image (PNG, JPG, WebP, …).",
      accept: "image/*",
      showMedia: true,
    },
    video: {
      badge: "Video",
      questionLabel: "Caption (optional)",
      questionHelp: "Short text shown with the video.",
      mediaFileLabel: "Video file",
      mediaUrlLabel: "Video URL",
      mediaUrlHelp: "Direct video link or embed URL (e.g. YouTube).",
      accept: "video/*",
      showMedia: true,
    },
    audio: {
      badge: "Audio",
      questionLabel: "Caption (optional)",
      questionHelp: "Short text shown with the audio clip.",
      mediaFileLabel: "Audio file",
      mediaUrlLabel: "Audio URL",
      mediaUrlHelp: "Direct link to an audio file (MP3, WAV, …).",
      accept: "audio/*",
      showMedia: true,
    },
  };

  function quizForm() {
    return (
      document.querySelector("#quiz_form") ||
      document.querySelector("form#quiz_form") ||
      document.querySelector("form[action*='quiz']")
    );
  }

  function gradingModeAjaxUrl() {
    var parts = window.location.pathname.split("/");
    var quizIdx = parts.indexOf("quiz");
    if (quizIdx === -1) {
      return null;
    }
    return parts.slice(0, quizIdx + 1).join("/") + "/grading-mode-fields/";
  }

  function satSectionConfigUrl() {
    var parts = window.location.pathname.split("/");
    var quizIdx = parts.indexOf("quiz");
    if (quizIdx === -1) {
      return null;
    }
    return parts.slice(0, quizIdx + 1).join("/") + "/sat-section-config/";
  }

  function csrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function gradingModeFromQuizForm() {
    var form = quizForm();
    if (!form) {
      return "variant";
    }
    if (form.querySelector("#id_is_essay:checked")) {
      return "essay";
    }
    if (form.querySelector("#id_is_listening:checked")) {
      return "listening";
    }
    if (form.querySelector("#id_is_speaking:checked")) {
      return "speaking";
    }
    if (form.querySelector("#id_is_reading:checked")) {
      return "reading";
    }
    if (form.querySelector("#id_is_math:checked")) {
      return "math";
    }
    return "variant";
  }

  function fallbackGradingConfig(mode) {
    if (mode === "essay") {
      return {
        grading_mode: mode,
        show_fields: [RESPONSE_FIELD],
        hide_fields: ANSWER_FIELDS.slice(),
        clear_fields: ANSWER_FIELDS.slice(),
      };
    }
    if (mode === "variant") {
      return {
        grading_mode: mode,
        show_fields: ["answer_options", "correct_option_number"],
        hide_fields: [RESPONSE_FIELD, "correct_answer", "correct_option_index"],
        clear_fields: [],
      };
    }
    if (mode === "reading" || mode === "math") {
      return {
        grading_mode: mode,
        show_fields: [],
        hide_fields: ANSWER_FIELDS.concat([RESPONSE_FIELD]),
        // Do not clear answer_options — SAT MCQ data lives there.
        clear_fields: [],
      };
    }
    return {
      grading_mode: mode,
      show_fields: [],
      hide_fields: ANSWER_FIELDS.concat([RESPONSE_FIELD]),
      clear_fields: ANSWER_FIELDS.slice(),
      hide_time_limit: mode === "speaking",
    };
  }

  function timeLimitFieldset() {
    var field = document.querySelector("#quiz_form .field-is_time_limited");
    return field ? field.closest("fieldset") : null;
  }

  function clearTimeLimitFields() {
    var timeLimited = document.querySelector("#id_is_time_limited");
    var minutes = document.querySelector("#id_time_limit_minutes");
    if (timeLimited) {
      timeLimited.checked = false;
    }
    if (minutes) {
      minutes.value = "";
    }
  }

  function applyTimeLimitVisibility(hide) {
    var fieldset = timeLimitFieldset();
    if (fieldset) {
      fieldset.classList.toggle("quiz-admin-hidden-fieldset", !!hide);
    }
    if (hide) {
      clearTimeLimitFields();
    }
  }

  function clearFieldValue(block, name) {
    var row = fieldRow(block, name);
    if (!row) {
      return;
    }
    if (name === "answer_options") {
      // Only clear the hidden JSON payload — never the CKEditor source textareas.
      var hidden = row.querySelector("textarea.answer-options-hidden");
      if (hidden) {
        hidden.value = "[]";
      }
      return;
    }
    var input = row.querySelector("input, textarea");
    if (!input) {
      return;
    }
    input.value = "";
  }

  function applyGradingConfig(block, config) {
    if (!config) {
      return;
    }

    // Never wipe answer options on an existing quiz-question edit page.
    // Those fields are the source of truth for SAT MCQ/SPR questions.
    var isQuestionEdit =
      !!(block.closest && block.closest("#quizquestion_form")) ||
      !!(document.querySelector("#quizquestion_form"));
    if (isQuestionEdit) {
      config = Object.assign({}, config, { clear_fields: [] });
    }

    var allFields = ANSWER_FIELDS.concat([RESPONSE_FIELD]);
    var showSet = {};
    (config.show_fields || []).forEach(function (name) {
      showSet[name] = true;
    });

    allFields.forEach(function (name) {
      var row = fieldRow(block, name);
      if (!row) {
        return;
      }
      // On quiz-question change form, keep MCQ option fields visible.
      if (isQuestionEdit && (name === "answer_options" || name === "correct_option_number")) {
        row.classList.remove("quiz-admin-hidden-field");
        return;
      }
      if (isQuestionEdit && (name === "correct_answer" || name === "correct_option_index")) {
        row.classList.add("quiz-admin-hidden-field");
        return;
      }
      row.classList.toggle("quiz-admin-hidden-field", !showSet[name]);
    });

    (config.clear_fields || []).forEach(function (name) {
      clearFieldValue(block, name);
    });

    if (showSet[RESPONSE_FIELD]) {
      clearFieldValue(block, RESPONSE_FIELD);
    }
  }

  function applyGradingConfigToAll(config) {
    collectBlocks(document).forEach(function (block) {
      applyGradingConfig(block, config);
      var select = promptSelect(block);
      if (select) {
        syncAudioListeningNotice(block, select.value || "text");
      }
    });
    applyTimeLimitVisibility(!!(config && config.hide_time_limit));
    applyQuizInlineMode(config && config.grading_mode);
    syncSharedPassageFieldVisibility();
  }

  function applyQuizInlineMode(mode) {
    var form = quizForm();
    if (!form) {
      return;
    }
    var variantInline = form.querySelector(".inline-group.portal-quiz-inline");
    var speakingInline = form.querySelector(".inline-group .speakingpart");
    var hideVariant = mode === "speaking" || mode === "listening" || mode === "reading" || mode === "math";
    if (variantInline) {
      variantInline.classList.toggle("quiz-admin-hidden-fieldset", hideVariant);
    }
    var notice = form.querySelector("[data-quiz-speaking-inline-notice]");
    if (mode === "speaking" && !speakingInline && !form.querySelector("#quiz_form input[name='id']")) {
      if (!notice) {
        notice = document.createElement("div");
        notice.className = "help quiz-speaking-inline-notice";
        notice.setAttribute("data-quiz-speaking-inline-notice", "");
        notice.textContent =
          "Save this quiz first with Speaking enabled, then edit it to add speaking parts — or add parts under Speaking parts in the admin menu.";
        var target = variantInline || form.querySelector(".inline-group");
        if (target && target.parentNode) {
          target.parentNode.insertBefore(notice, target);
        }
      }
      notice.hidden = false;
    } else if (notice) {
      notice.hidden = true;
    }
  }

  var gradingRequestId = 0;

  function syncGradingModeViaAjax() {
    var url = gradingModeAjaxUrl();
    var form = quizForm();
    if (!url || !form) {
      applyGradingConfigToAll(fallbackGradingConfig(gradingModeFromQuizForm()));
      return;
    }

    var requestId = ++gradingRequestId;
    var body = new FormData();
    GRADING_INPUTS.forEach(function (name) {
      var input = form.querySelector("#id_" + name);
      if (input && input.checked) {
        body.append(name, "on");
      }
    });
    body.append("csrfmiddlewaretoken", csrfToken());

    fetch(url, {
      method: "POST",
      body: body,
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("grading mode request failed");
        }
        return response.json();
      })
      .then(function (config) {
        if (requestId !== gradingRequestId) {
          return;
        }
        applyGradingConfigToAll(config);
      })
      .catch(function () {
        if (requestId !== gradingRequestId) {
          return;
        }
        applyGradingConfigToAll(fallbackGradingConfig(gradingModeFromQuizForm()));
      });
  }

  function syncMathFieldVisibility() {
    var form = quizForm();
    if (!form) {
      return;
    }
    var mathRow = form.querySelector(".field-is_math");
    var mathInput = form.querySelector("#id_is_math");
    if (mathRow) {
      mathRow.classList.add("quiz-admin-hidden-field");
    }
    if (mathInput) {
      mathInput.checked = false;
    }
  }

  function syncSharedPassageFieldVisibility() {
    var form = quizForm();
    if (!form) {
      return;
    }
    var fieldset = form.querySelector(".quiz-shared-passage-fieldset");
    if (!fieldset) {
      return;
    }
    var isVariant = gradingModeFromQuizForm() === "variant";
    fieldset.classList.toggle("quiz-admin-hidden-fieldset", !isVariant);

    var flagInput = form.querySelector("#id_has_shared_passage");
    var sharedContentRows = [
      form.querySelector(".field-shared_passage"),
      form.querySelector(".field-shared_audio_file"),
      form.querySelector(".field-shared_youtube_url")
    ];
    if (!isVariant) {
      if (flagInput) {
        flagInput.checked = false;
      }
      sharedContentRows.forEach(function (row) {
        if (row) {
          row.classList.add("quiz-admin-hidden-field");
        }
      });
      return;
    }
    var enabled = !!(flagInput && flagInput.checked);
    sharedContentRows.forEach(function (row) {
      if (row) {
        row.classList.toggle("quiz-admin-hidden-field", !enabled);
      }
    });
  }

  function selectedSatSection() {
    var form = quizForm();
    if (!form) {
      return "";
    }
    var checked = form.querySelector('input[name="sat_section"]:checked');
    return checked ? checked.value : "";
  }

  function applySatSectionFlags(flags) {
    var form = quizForm();
    if (!form || !flags) {
      return;
    }
    GRADING_INPUTS.forEach(function (name) {
      var input = form.querySelector("#id_" + name);
      if (!input) {
        return;
      }
      input.checked = !!flags[name];
    });
  }

  function syncSatSectionFieldVisibility() {
    var form = quizForm();
    if (!form) {
      return;
    }
    var satInput = form.querySelector("#id_is_sat");
    var satEnabled = !!(satInput && satInput.checked);
    var satFieldset = form.querySelector(".sat-section-fieldset");
    var gradingFieldset = form.querySelector(".quiz-grading-fieldset");
    var ieltsRow = form.querySelector(".field-is_ielts");

    if (satFieldset) {
      satFieldset.classList.toggle("quiz-admin-hidden-fieldset", !satEnabled);
    }
    if (gradingFieldset) {
      gradingFieldset.classList.toggle("quiz-admin-hidden-fieldset", satEnabled);
    }
    if (ieltsRow) {
      ieltsRow.classList.toggle("quiz-admin-hidden-field", satEnabled);
    }
    syncMathFieldVisibility();
    syncSharedPassageFieldVisibility();
  }

  var satSectionRequestId = 0;

  function syncSatSectionViaAjax() {
    var url = satSectionConfigUrl();
    var form = quizForm();
    if (!url || !form) {
      syncSatSectionFieldVisibility();
      syncGradingModeViaAjax();
      return;
    }

    syncSatSectionFieldVisibility();

    var satInput = form.querySelector("#id_is_sat");
    if (!satInput || !satInput.checked) {
      syncGradingModeViaAjax();
      return;
    }

    var requestId = ++satSectionRequestId;
    var body = new FormData();
    body.append("is_sat", "on");
    body.append("sat_section", selectedSatSection());
    body.append("csrfmiddlewaretoken", csrfToken());

    fetch(url, {
      method: "POST",
      body: body,
      credentials: "same-origin",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("sat-section-config failed");
        }
        return response.json();
      })
      .then(function (config) {
        if (requestId !== satSectionRequestId) {
          return;
        }
        applySatSectionFlags(config.flags || {});
        if (config.grading_mode) {
          applyGradingConfigToAll(fallbackGradingConfig(config.grading_mode));
          applyQuizInlineMode(config.grading_mode);
        }
        syncGradingModeViaAjax();
      })
      .catch(function () {
        if (requestId !== satSectionRequestId) {
          return;
        }
        syncGradingModeViaAjax();
      });
  }

  function bindGradingModeOnQuizForm() {
    var form = quizForm();
    if (!form || form.dataset.quizGradingBound === "1") {
      return;
    }

    GRADING_INPUTS.forEach(function (name) {
      var input = form.querySelector("#id_" + name);
      if (!input) {
        return;
      }
      input.addEventListener("change", syncGradingModeViaAjax);
    });

    var sharedPassageInput = form.querySelector("#id_has_shared_passage");
    if (sharedPassageInput) {
      sharedPassageInput.addEventListener("change", syncSharedPassageFieldVisibility);
    }

    var satInput = form.querySelector("#id_is_sat");
    if (satInput) {
      satInput.addEventListener("change", function () {
        if (satInput.checked) {
          var ieltsInput = form.querySelector("#id_is_ielts");
          if (ieltsInput) {
            ieltsInput.checked = false;
          }
        }
        syncSatSectionViaAjax();
      });
    }

    form.querySelectorAll('input[name="sat_section"]').forEach(function (input) {
      input.addEventListener("change", syncSatSectionViaAjax);
    });

    form.dataset.quizGradingBound = "1";
    syncSatSectionFieldVisibility();
    syncSharedPassageFieldVisibility();
    syncSatSectionViaAjax();
  }

  function fieldRow(block, name) {
    return block.querySelector(".field-" + name);
  }

  function fieldLabel(row) {
    return row ? row.querySelector("label") : null;
  }

  function fieldHelp(row) {
    if (!row) {
      return null;
    }
    return row.querySelector(".help") || row.querySelector("p.help");
  }

  function fileInput(block) {
    return (
      block.querySelector("[data-quiz-field='media_file']") ||
      block.querySelector("input[type='file'][name*='media_file']")
    );
  }

  function urlInput(block) {
    return (
      block.querySelector("[data-quiz-field='media_url']") ||
      block.querySelector("input[name*='media_url']")
    );
  }

  function promptSelect(block) {
    return block.querySelector(".quiz-prompt-type");
  }

  function existingMediaUrl(block) {
    var row = fieldRow(block, "media_file");
    if (!row) {
      return "";
    }
    var link = row.querySelector("a[href]");
    return link ? link.getAttribute("href") : "";
  }

  function ensurePanel(block) {
    if (block.dataset.quizPromptReady === "1") {
      return block.querySelector("[data-quiz-prompt-panel]");
    }

    var promptRow = fieldRow(block, "prompt_type");
    var questionRow = fieldRow(block, "question");
    var mediaFileRow = fieldRow(block, "media_file");
    var mediaUrlRow = fieldRow(block, "media_url");
    if (!promptRow || !questionRow) {
      return null;
    }

    var panel = document.createElement("div");
    panel.className = "quiz-prompt-panel";
    panel.setAttribute("data-quiz-prompt-panel", "");
    panel.innerHTML =
      '<div class="quiz-prompt-panel__head">' +
      '<span class="quiz-prompt-panel__badge" data-quiz-prompt-badge>Text</span>' +
      '<p class="quiz-prompt-panel__hint" data-quiz-prompt-hint></p>' +
      "</div>" +
      '<div class="quiz-prompt-panel__body" data-quiz-prompt-body></div>' +
      '<div class="quiz-prompt-panel__preview" data-quiz-prompt-preview hidden></div>';

    var body = panel.querySelector("[data-quiz-prompt-body]");
    var anchor = promptRow.parentNode;
    anchor.insertBefore(panel, promptRow);
    body.appendChild(promptRow);
    body.appendChild(questionRow);
    if (mediaFileRow) {
      body.appendChild(mediaFileRow);
    }
    if (mediaUrlRow) {
      body.appendChild(mediaUrlRow);
    }

    block.dataset.quizPromptReady = "1";
    return panel;
  }

  function renderPreview(previewEl, type, source) {
    if (!previewEl || !source) {
      if (previewEl) {
        previewEl.hidden = true;
        previewEl.innerHTML = "";
      }
      return;
    }

    previewEl.hidden = false;
    if (type === "image") {
      previewEl.innerHTML = '<img src="' + source + '" alt="">';
      return;
    }
    if (type === "video") {
      previewEl.innerHTML =
        '<video controls preload="metadata" src="' + source + '"></video>';
      return;
    }
    if (type === "audio") {
      previewEl.innerHTML =
        '<audio controls preload="metadata" src="' + source + '"></audio>';
    }
  }

  function updatePreview(block, type) {
    var panel = block.querySelector("[data-quiz-prompt-panel]");
    if (!panel) {
      return;
    }
    var previewEl = panel.querySelector("[data-quiz-prompt-preview]");
    var input = fileInput(block);
    var url = urlInput(block);

    if (input && input.files && input.files[0]) {
      if (block._quizPreviewObjectUrl) {
        URL.revokeObjectURL(block._quizPreviewObjectUrl);
      }
      block._quizPreviewObjectUrl = URL.createObjectURL(input.files[0]);
      renderPreview(previewEl, type, block._quizPreviewObjectUrl);
      return;
    }

    var urlValue = url && url.value ? url.value.trim() : "";
    if (urlValue) {
      renderPreview(previewEl, type, urlValue);
      return;
    }

    var existing = existingMediaUrl(block);
    if (existing && type !== "text") {
      renderPreview(previewEl, type, existing);
      return;
    }

    renderPreview(previewEl, type, "");
  }

  function applyPromptType(block, type) {
    var config = PROMPT_TYPES[type] || PROMPT_TYPES.text;
    var panel = ensurePanel(block);
    if (!panel) {
      return;
    }

    panel.setAttribute("data-quiz-active-type", type);

    var badge = panel.querySelector("[data-quiz-prompt-badge]");
    var hint = panel.querySelector("[data-quiz-prompt-hint]");
    if (badge) {
      badge.textContent = config.badge;
    }
    if (hint) {
      hint.textContent = config.showMedia
        ? "Upload a file or paste a URL — preview updates instantly."
        : "Write the question text shown to students.";
    }

    var questionRow = fieldRow(block, "question");
    var mediaFileRow = fieldRow(block, "media_file");
    var mediaUrlRow = fieldRow(block, "media_url");

    var qLabel = fieldLabel(questionRow);
    var qHelp = fieldHelp(questionRow);
    if (qLabel) {
      qLabel.textContent = config.questionLabel;
    }
    if (qHelp) {
      qHelp.textContent = config.questionHelp;
    }

    if (mediaFileRow) {
      mediaFileRow.classList.toggle("quiz-admin-hidden-field", !config.showMedia);
      var mfLabel = fieldLabel(mediaFileRow);
      if (mfLabel) {
        mfLabel.textContent = config.mediaFileLabel;
      }
    }

    if (mediaUrlRow) {
      mediaUrlRow.classList.toggle("quiz-admin-hidden-field", !config.showMedia);
      var muLabel = fieldLabel(mediaUrlRow);
      var muHelp = fieldHelp(mediaUrlRow);
      if (muLabel) {
        muLabel.textContent = config.mediaUrlLabel;
      }
      if (muHelp) {
        muHelp.textContent = config.mediaUrlHelp;
      }
    }

    var input = fileInput(block);
    if (input) {
      if (config.accept) {
        input.setAttribute("accept", config.accept);
      } else {
        input.removeAttribute("accept");
      }
    }

    updatePreview(block, type);
    syncAudioListeningNotice(block, type);
  }

  function syncAudioListeningNotice(block, type) {
    var panel = block.querySelector("[data-quiz-prompt-panel]");
    if (!panel) {
      return;
    }
    var existing = panel.querySelector("[data-quiz-audio-listening-notice]");
    var isListening = gradingModeFromQuizForm() === "listening";
    if (type !== "audio" || !isListening) {
      if (existing) {
        existing.remove();
      }
      return;
    }
    if (existing) {
      return;
    }
    var notice = document.createElement("p");
    notice.className = "quiz-audio-listening-notice";
    notice.setAttribute("data-quiz-audio-listening-notice", "");
    notice.textContent =
      "Listening mode: add audio and questions in the Listening audio sections below, not here.";
    panel.appendChild(notice);
  }

  function bindBlock(block) {
    if (block.dataset.quizPromptBound === "1") {
      return;
    }

    var select = promptSelect(block);
    if (!select) {
      return;
    }

    ensurePanel(block);

    function sync() {
      applyPromptType(block, select.value || "text");
    }

    select.addEventListener("change", sync);

    var file = fileInput(block);
    if (file) {
      file.addEventListener("change", sync);
    }

    var url = urlInput(block);
    if (url) {
      url.addEventListener("input", sync);
    }

    sync();
    block.dataset.quizPromptBound = "1";
  }

  function collectBlocks(root) {
    var blocks = [];

    root.querySelectorAll(".inline-related").forEach(function (node) {
      if (promptSelect(node)) {
        blocks.push(node);
      }
    });

    var standalone = root.querySelector("#quizquestion_form") || root.querySelector("form");
    if (
      standalone &&
      promptSelect(standalone) &&
      blocks.indexOf(standalone) === -1
    ) {
      blocks.push(standalone);
    }

    if (!blocks.length && root.matches && root.matches(".inline-related") && promptSelect(root)) {
      blocks.push(root);
    }

    return blocks;
  }

  function initRoot(root) {
    bindGradingModeOnQuizForm();
    collectBlocks(root).forEach(bindBlock);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initRoot(document);

    document.body.addEventListener("click", function (event) {
      if (event.target.closest(".add-row")) {
        window.setTimeout(function () {
          initRoot(document);
          syncGradingModeViaAjax();
        }, 0);
      }
    });

    if (window.django && django.jQuery) {
      django.jQuery(document).on("formset:added", function (_event, row) {
        initRoot(row);
        syncGradingModeViaAjax();
      });
    }
  });
})();

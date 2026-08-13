(function ($) {
  'use strict';

  function optionCount(form) {
    var hidden = form.find('textarea.answer-options-hidden').first();
    if (hidden.length) {
      try {
        var parsed = JSON.parse(hidden.val() || '[]');
        if (Array.isArray(parsed)) {
          var fromWidget = parsed.filter(function (item) {
            return item && String(item).trim();
          }).length;
          if (fromWidget >= 2) {
            return fromWidget;
          }
        }
      } catch (err) {
        /* fall through */
      }
    }
    var rawOptions = form.find("[name$='-answer_options']").first();
    if (rawOptions.length) {
      try {
        var fallback = JSON.parse(rawOptions.val() || '[]');
        if (Array.isArray(fallback)) {
          return fallback.filter(function (item) {
            return item && String(item).trim();
          }).length;
        }
      } catch (err2) {
        return 0;
      }
    }
    return 0;
  }

  function hasLabelGroup(form) {
    var select = form.find("select[name$='-group_ref']").first();
    return Boolean(select.length && String(select.val() || '').trim());
  }

  function syncListeningAnswerMode(form) {
    if (!form || !form.length) {
      return;
    }
    var isMcq = optionCount(form) >= 2 || hasLabelGroup(form);
    form.find('.field-correct_option_number').toggle(isMcq);
    form.find('.field-correct_answer, .field-correct_option_index').hide();
    form.find('.field-answer_options').toggle(!hasLabelGroup(form));
    form.find('.field-spr_correct_answers, .field-spr_max_length').toggle(!isMcq);
  }

  function bindForm(form) {
    if (!form.length || form.data('listeningSprToggleBound')) {
      return;
    }
    form.data('listeningSprToggleBound', true);
    syncListeningAnswerMode(form);
    form.on('input change', 'textarea.answer-options-hidden, .answer-options-container, select[name$="-group_ref"]', function () {
      syncListeningAnswerMode(form);
    });
    // Answer-options widget may rewrite the hidden JSON after CKEditor sync.
    var observerTarget = form.find('.answer-options-container').get(0);
    if (observerTarget && window.MutationObserver) {
      var observer = new MutationObserver(function () {
        syncListeningAnswerMode(form);
      });
      observer.observe(observerTarget, { childList: true, subtree: true });
    }
  }

  function initAll() {
    $('.inline-group .inline-related, #listeningquestion_form').each(function () {
      bindForm($(this));
    });
  }

  $(function () {
    initAll();
    $(document).on('formset:added', function (event, row) {
      bindForm($(row));
    });
  });
})(django.jQuery);

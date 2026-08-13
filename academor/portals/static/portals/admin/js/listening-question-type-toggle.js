(function ($) {
  'use strict';

  function optionCount(form) {
    var hidden = form.find('textarea.answer-options-hidden').first();
    if (!hidden.length) {
      return 0;
    }
    try {
      var parsed = JSON.parse(hidden.val() || '[]');
      if (!Array.isArray(parsed)) {
        return 0;
      }
      return parsed.filter(function (item) {
        return item && String(item).trim();
      }).length;
    } catch (err) {
      return 0;
    }
  }

  function syncListeningAnswerMode(form) {
    if (!form || !form.length) {
      return;
    }
    var isMcq = optionCount(form) >= 2;
    form.find('.field-correct_option_number, .field-correct_answer, .field-correct_option_index').toggle(isMcq);
    form.find('.field-spr_correct_answers, .field-spr_max_length').toggle(!isMcq);
  }

  function bindForm(form) {
    if (!form.length || form.data('listeningSprToggleBound')) {
      return;
    }
    form.data('listeningSprToggleBound', true);
    syncListeningAnswerMode(form);
    form.on('input change', 'textarea.answer-options-hidden, .answer-options-container', function () {
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

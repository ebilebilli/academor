(function($) {
    'use strict';

    $(document).ready(function() {
        initializeQuestionTypeToggle();
        revealValidationErrors();
    });

    function initializeQuestionTypeToggle() {
        $(document).on('change', 'select[name="question_type"], select[data-quiz-question-type]', function() {
            toggleQuestionTypeFields($(this));
        });

        $('select[name="question_type"], select[data-quiz-question-type"]').each(function() {
            toggleQuestionTypeFields($(this));
        });

        if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(document).on('formset:added', function(event, row) {
                row.find('select[name="question_type"], select[data-quiz-question-type"]').each(function() {
                    toggleQuestionTypeFields($(this));
                });
            });
        }
    }

    function toggleQuestionTypeFields(selectElement) {
        var questionType = selectElement.val();
        var form = selectElement.closest('form');

        if (!form.length) {
            form = selectElement.closest('.inline-related, .module');
        }

        if (questionType === 'spr') {
            hideMCQFields(form);
            showSPRFields(form);
        } else {
            showMCQFields(form);
            hideSPRFields(form);
        }
    }

    function hideMCQFields(form) {
        form.find('.quiz-mcq-answers-fieldset').hide();
        form.find('.field-answer_options, .field-correct_answer').hide();
    }

    function showMCQFields(form) {
        form.find('.quiz-mcq-answers-fieldset').show();
        form.find('.field-answer_options, .field-correct_answer').show();
    }

    function hideSPRFields(form) {
        form.find('.quiz-spr-answers-fieldset').hide();
        form.find('.field-spr_correct_answers, .field-spr_max_length').hide();
    }

    function showSPRFields(form) {
        form.find('.quiz-spr-answers-fieldset').show();
        form.find('.field-spr_correct_answers, .field-spr_max_length').show();
    }

    function revealValidationErrors() {
        var $errors = $('.form-row.errors, .errors').filter(function() {
            return $(this).find('.errorlist').length || $(this).hasClass('errors');
        });
        if (!$errors.length) {
            return;
        }

        $errors.each(function() {
            var $row = $(this);
            $row.show().css({display: 'block', visibility: 'visible'});
            $row.removeClass('quiz-admin-hidden-field');
            $row.closest('fieldset').show().removeClass('collapsed quiz-admin-hidden-fieldset');
        });

        var summary = [];
        $('.errorlist li').each(function() {
            var text = ($(this).text() || '').trim();
            if (text) {
                summary.push(text);
            }
        });
        if (!summary.length) {
            return;
        }

        var $banner = $('#quiz-question-error-banner');
        if (!$banner.length) {
            $banner = $('<div id="quiz-question-error-banner" class="errornote"></div>');
            var $target = $('ul.messagelist').first();
            if ($target.length) {
                $target.after($banner);
            } else {
                $('.errornote').first().after($banner);
                if (!$('.errornote').length) {
                    $('#content-main').prepend($banner);
                }
            }
        }
        $banner.html(
            '<strong>Save failed — fix these:</strong><ul style="margin:0.4rem 0 0 1.2rem;">' +
            summary.map(function(item) {
                return '<li>' + $('<div>').text(item).html() + '</li>';
            }).join('') +
            '</ul>'
        );
        if ($banner[0] && $banner[0].scrollIntoView) {
            $banner[0].scrollIntoView({behavior: 'smooth', block: 'start'});
        }
    }

})(django.jQuery || jQuery);

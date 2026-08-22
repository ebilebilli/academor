(function($) {
    'use strict';

    $(document).ready(function() {
        initializeQuestionTypeToggle();
        revealValidationErrors();
    });

    function initializeQuestionTypeToggle() {
        $(document).on('change', 'select[name="question_type"], select[name$="-question_type"], select[data-quiz-question-type]', function() {
            toggleQuestionTypeFields($(this));
        });

        $('select[name="question_type"], select[name$="-question_type"], select[data-quiz-question-type]').each(function() {
            toggleQuestionTypeFields($(this));
        });

        if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(document).on('formset:added', function(event, row) {
                row.find('select[name="question_type"], select[name$="-question_type"], select[data-quiz-question-type]').each(function() {
                    toggleQuestionTypeFields($(this));
                });
            });
        }
    }

    function fieldScope(selectElement) {
        // Prefer the inline row so one question's type does not hide siblings.
        var scope = selectElement.closest('.inline-related');
        if (scope.length) {
            return scope;
        }
        scope = selectElement.closest('form');
        if (scope.length) {
            return scope;
        }
        return selectElement.closest('.module');
    }

    function toggleQuestionTypeFields(selectElement) {
        var questionType = selectElement.val();
        var scope = fieldScope(selectElement);
        if (!scope.length) {
            return;
        }

        if (questionType === 'spr') {
            hideMCQFields(scope);
            showSPRFields(scope);
        } else {
            showMCQFields(scope);
            hideSPRFields(scope);
        }
    }

    function hideMCQFields(scope) {
        scope.find('.quiz-mcq-answers-fieldset').addClass('quiz-admin-hidden-fieldset');
        scope.find(
            '.field-answer_options, .field-correct_answer, .field-correct_option_number, .field-correct_option_index, .field-is_dropdown',
        ).addClass('quiz-admin-hidden-field');
    }

    function showMCQFields(scope) {
        scope.find('.quiz-mcq-answers-fieldset').removeClass('quiz-admin-hidden-fieldset');
        scope.find('.field-answer_options, .field-correct_option_number, .field-is_dropdown')
            .removeClass('quiz-admin-hidden-field')
            .show();
        // Hidden inputs stay in DOM but their rows stay visually quiet.
        scope.find('.field-correct_answer, .field-correct_option_index')
            .addClass('quiz-admin-hidden-field');
    }

    function hideSPRFields(scope) {
        scope.find('.quiz-spr-answers-fieldset').addClass('quiz-admin-hidden-fieldset');
        scope.find('.field-spr_correct_answers, .field-spr_max_length')
            .addClass('quiz-admin-hidden-field');
    }

    function showSPRFields(scope) {
        scope.find('.quiz-spr-answers-fieldset').removeClass('quiz-admin-hidden-fieldset');
        scope.find('.field-spr_correct_answers, .field-spr_max_length')
            .removeClass('quiz-admin-hidden-field')
            .show();
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

    // Expose so grading-mode sync can re-apply after it touches field visibility.
    window.quizQuestionTypeToggleSync = function(root) {
        var $root = root ? $(root) : $(document);
        $root.find('select[name="question_type"], select[name$="-question_type"], select[data-quiz-question-type]').each(function() {
            toggleQuestionTypeFields($(this));
        });
    };

})(django.jQuery || jQuery);

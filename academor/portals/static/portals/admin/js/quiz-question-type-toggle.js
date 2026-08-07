(function($) {
    'use strict';
    
    // Initialize when document is ready
    $(document).ready(function() {
        initializeQuestionTypeToggle();
    });
    
    function initializeQuestionTypeToggle() {
        // Handle question type change
        $(document).on('change', 'select[name="question_type"], select[data-quiz-question-type]', function() {
            toggleQuestionTypeFields($(this));
        });
        
        // Initialize on page load
        $('select[name="question_type"], select[data-quiz-question-type"]').each(function() {
            toggleQuestionTypeFields($(this));
        });
        
        // Also handle inline formsets
        if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(document).on('formset:added', function(event, row) {
                row.find('select[name="question_type"], select[data-quiz-question-type]').each(function() {
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
            // Hide MCQ fields, show SPR fields
            hideMCQFields(form);
            showSPRFields(form);
        } else if (questionType === 'mcq') {
            // Show MCQ fields, hide SPR fields
            showMCQFields(form);
            hideSPRFields(form);
        } else {
            // Default: show MCQ, hide SPR
            showMCQFields(form);
            hideSPRFields(form);
        }
    }
    
    function hideMCQFields(form) {
        // Hide MCQ fieldset only (do not match "SPR Answers")
        form.find('fieldset').each(function() {
            var fieldset = $(this);
            var legendText = fieldset.find('legend, h2').first().text() || '';
            if (legendText.includes('MCQ Answers')) {
                fieldset.hide();
            }
        });

        form.find('.field-answer_options, .field-correct_answer').hide();
    }

    function showMCQFields(form) {
        form.find('fieldset').each(function() {
            var fieldset = $(this);
            var legendText = fieldset.find('legend, h2').first().text() || '';
            if (legendText.includes('MCQ Answers')) {
                fieldset.show();
            }
        });

        form.find('.field-answer_options, .field-correct_answer').show();
    }
    
    function hideSPRFields(form) {
        // Hide SPR fieldset
        form.find('fieldset').each(function() {
            var fieldset = $(this);
            var legendText = fieldset.find('legend, h2').text();
            if (legendText.includes('SPR Answers')) {
                fieldset.hide();
            }
        });
        
        // Also hide individual field rows for inline forms
        form.find('.field-spr_correct_answers, .field-spr_max_length').hide();
    }
    
    function showSPRFields(form) {
        // Show SPR fieldset
        form.find('fieldset').each(function() {
            var fieldset = $(this);
            var legendText = fieldset.find('legend, h2').text();
            if (legendText.includes('SPR Answers')) {
                fieldset.show();
            }
        });
        
        // Also show individual field rows for inline forms
        form.find('.field-spr_correct_answers, .field-spr_max_length').show();
    }
    
})(django.jQuery || jQuery);
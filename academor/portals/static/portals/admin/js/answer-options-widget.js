(function($) {
    'use strict';
    
    // Initialize when document is ready
    $(document).ready(function() {
        initializeAnswerOptionsWidget();
    });
    
    function initializeAnswerOptionsWidget() {
        // Handle add option button
        $(document).on('click', '.answer-option-add-btn', function(e) {
            e.preventDefault();
            addAnswerOption($(this).closest('.answer-options-container'));
        });
        
        // Handle remove option button
        $(document).on('click', '.answer-option-remove-btn', function(e) {
            e.preventDefault();
            removeAnswerOption($(this).closest('.answer-option-item'));
        });
        
        // Initialize CKEditor for existing textareas
        initializeCKEditors();
        
        // Update hidden field when options change
        $(document).on('change', '.answer-option-textarea', function() {
            updateHiddenField($(this).closest('.answer-options-container'));
        });
    }
    
    function itemLabelFor(container) {
        return container.attr('data-item-label') || 'Option';
    }

    function addAnswerOption(container) {
        var list = container.find('.answer-options-list');
        var itemCount = list.find('.answer-option-item').length;
        var newIndex = itemCount;
        var itemLabel = itemLabelFor(container);

        var optionHtml = `
            <div class="answer-option-item" data-index="${newIndex}">
                <div class="answer-option-header">
                    <span class="answer-option-label">${itemLabel} ${newIndex + 1}</span>
                    <button type="button" class="answer-option-remove-btn" title="Remove">×</button>
                </div>
                <textarea class="answer-option-textarea ckeditor-enabled" rows="2" data-index="${newIndex}"></textarea>
            </div>
        `;

        list.append(optionHtml);

        // Initialize CKEditor for the new textarea
        var newTextarea = list.find('.answer-option-item').last().find('.answer-option-textarea');
        initializeCKEditorForTextarea(newTextarea);

        // Update labels
        updateOptionLabels(container);

        // Update hidden field
        updateHiddenField(container);
    }
    
    function removeAnswerOption(optionItem) {
        var container = optionItem.closest('.answer-options-container');
        
        // Destroy CKEditor instance if exists
        var textarea = optionItem.find('.answer-option-textarea');
        var editorId = textarea.attr('id');
        if (editorId && window.CKEDITOR && window.CKEDITOR.instances[editorId]) {
            window.CKEDITOR.instances[editorId].destroy();
        }
        
        optionItem.remove();
        
        // Update labels
        updateOptionLabels(container);
        
        // Update hidden field
        updateHiddenField(container);
    }
    
    function updateOptionLabels(container) {
        var itemLabel = itemLabelFor(container);
        container.find('.answer-option-item').each(function(index) {
            $(this).attr('data-index', index);
            $(this).find('.answer-option-label').text(itemLabel + ' ' + (index + 1));
            $(this).find('.answer-option-textarea').attr('data-index', index);
        });
    }
    
    function updateHiddenField(container) {
        var options = [];
        container.find('.answer-option-textarea').each(function() {
            var textarea = $(this);
            var value = textarea.val();
            
            // Get value from CKEditor if it's initialized
            var editorId = textarea.attr('id');
            if (editorId && window.CKEDITOR && window.CKEDITOR.instances[editorId]) {
                value = window.CKEDITOR.instances[editorId].getData();
            }
            
            options.push(value);
        });
        
        container.find('.answer-options-hidden').val(JSON.stringify(options));
    }
    
    function initializeCKEditors() {
        $('.answer-option-textarea.ckeditor-enabled').each(function() {
            initializeCKEditorForTextarea($(this));
        });
    }
    
    function initializeCKEditorForTextarea(textarea) {
        // Check if CKEditor is available
        if (typeof window.CKEDITOR === 'undefined') {
            return;
        }
        
        // Ensure the textarea has a unique ID
        if (!textarea.attr('id')) {
            var uniqueId = 'answer-option-textarea-' + Math.random().toString(36).substr(2, 9);
            textarea.attr('id', uniqueId);
        }
        
        // Destroy existing instance if any
        var editorId = textarea.attr('id');
        if (window.CKEDITOR.instances[editorId]) {
            window.CKEDITOR.instances[editorId].destroy();
        }
        
        // Initialize CKEditor with image paste/upload + drag-resize (image2)
        window.CKEDITOR.replace(editorId, {
            toolbar: [
                ['Bold', 'Italic', 'Underline'],
                ['NumberedList', 'BulletedList'],
                ['Link', 'Unlink'],
                ['Image'],
                ['RemoveFormat']
            ],
            height: 60,
            width: '100%',
            extraPlugins: 'image2',
            removePlugins: 'image,elementspath',
            resize_enabled: false,
            image2_disableResizer: false,
            filebrowserUploadUrl: '/ckeditor/upload/',
            filebrowserBrowseUrl: '/ckeditor/browse/'
        });
        
        // Update hidden field when CKEditor content changes
        window.CKEDITOR.instances[editorId].on('change', function() {
            updateHiddenField(textarea.closest('.answer-options-container'));
        });
    }
    
    // Also initialize when Django's formsets are added
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function(event, row) {
            initializeCKEditors();
        });
    }
    
})(django.jQuery || jQuery);
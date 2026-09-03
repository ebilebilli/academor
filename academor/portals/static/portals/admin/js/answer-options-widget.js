(function($) {
    'use strict';

    function initializeAnswerOptionsWidget() {
        $(document).on('click', '.answer-option-add-btn', function(e) {
            e.preventDefault();
            addAnswerOption($(this).closest('.answer-options-container'));
        });

        $(document).on('click', '.answer-option-remove-btn', function(e) {
            e.preventDefault();
            removeAnswerOption($(this).closest('.answer-option-item'));
        });

        initializeCKEditors();

        $(document).on('change', '.answer-option-textarea', function() {
            updateHiddenField($(this).closest('.answer-options-container'));
        });

        // Critical: sync CKEditor → hidden JSON before Django admin save.
        $(document).on('submit', 'form', function() {
            if (window.CKEDITOR) {
                Object.keys(window.CKEDITOR.instances || {}).forEach(function(id) {
                    try {
                        window.CKEDITOR.instances[id].updateElement();
                    } catch (err) {
                        // ignore destroyed instances
                    }
                });
            }
            syncAllAnswerOptionContainers($(this));
        });
    }

    function syncAllAnswerOptionContainers(scope) {
        var $scope = scope && scope.length ? scope : $(document);
        $scope.find('.answer-options-container').each(function() {
            updateHiddenField($(this), {force: true});
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

        var fieldName = container.attr('data-field-name') || '';
        var optionHtml = `
            <div class="answer-option-item" data-index="${newIndex}">
                <div class="answer-option-header">
                    <span class="answer-option-label">${itemLabel} ${newIndex + 1}</span>
                    <button type="button" class="answer-option-remove-btn" title="Remove">×</button>
                </div>
                <textarea class="answer-option-textarea ckeditor-enabled" name="${fieldName}_item_${newIndex}" rows="2" data-index="${newIndex}"></textarea>
            </div>
        `;

        list.append(optionHtml);

        var newTextarea = list.find('.answer-option-item').last().find('.answer-option-textarea');
        initializeCKEditorForTextarea(newTextarea);
        updateOptionLabels(container);
        updateHiddenField(container, {force: true});
    }

    function removeAnswerOption(optionItem) {
        var container = optionItem.closest('.answer-options-container');
        var textarea = optionItem.find('.answer-option-textarea');
        var editorId = textarea.attr('id');
        if (editorId && window.CKEDITOR && window.CKEDITOR.instances[editorId]) {
            window.CKEDITOR.instances[editorId].destroy();
        }

        optionItem.remove();
        updateOptionLabels(container);
        updateHiddenField(container, {force: true});
    }

    function updateOptionLabels(container) {
        var itemLabel = itemLabelFor(container);
        var fieldName = container.attr('data-field-name') || '';
        container.find('.answer-option-item').each(function(index) {
            $(this).attr('data-index', index);
            $(this).find('.answer-option-label').text(itemLabel + ' ' + (index + 1));
            $(this).find('.answer-option-textarea')
                .attr('data-index', index)
                .attr('name', fieldName + '_item_' + index);
        });
    }

    function readOptionValue(textarea) {
        var value = textarea.val() || '';
        var editorId = textarea.attr('id');
        if (editorId && window.CKEDITOR && window.CKEDITOR.instances[editorId]) {
            var editor = window.CKEDITOR.instances[editorId];
            // Avoid wiping saved options while the editor is still booting.
            if (editor.status === 'ready' || editor.status === 'loaded') {
                value = editor.getData();
            }
        }
        return value;
    }

    function updateHiddenField(container, opts) {
        opts = opts || {};
        var options = [];
        var hasReadyEditor = false;
        var allEmpty = true;

        container.find('.answer-option-textarea').each(function() {
            var textarea = $(this);
            var editorId = textarea.attr('id');
            if (editorId && window.CKEDITOR && window.CKEDITOR.instances[editorId]) {
                var editor = window.CKEDITOR.instances[editorId];
                if (editor.status === 'ready' || editor.status === 'loaded') {
                    hasReadyEditor = true;
                }
            }
            var value = readOptionValue(textarea);
            if (value && String(value).trim()) {
                allEmpty = false;
            }
            options.push(value);
        });

        var hidden = container.find('.answer-options-hidden');
        var previous = hidden.val() || '[]';

        // Never wipe saved options with empty values (CKEditor boot/submit race),
        // even when force=true on form submit.
        if (allEmpty && previous && previous !== '[]') {
            try {
                var prevList = JSON.parse(previous);
                if (Array.isArray(prevList) && prevList.some(function(item) {
                    return item && String(item).trim();
                })) {
                    return;
                }
            } catch (e) {
                // fall through and write
            }
        }

        // If some editors are still booting, keep previous payload.
        if (!hasReadyEditor && previous && previous !== '[]' && !opts.force) {
            return;
        }

        hidden.val(JSON.stringify(options));
    }

    function initializeCKEditors() {
        $('.answer-option-textarea.ckeditor-enabled').each(function() {
            initializeCKEditorForTextarea($(this));
        });
    }

    function initializeCKEditorForTextarea(textarea) {
        if (typeof window.CKEDITOR === 'undefined') {
            return;
        }

        if (!textarea.attr('id')) {
            var uniqueId = 'answer-option-textarea-' + Math.random().toString(36).substr(2, 9);
            textarea.attr('id', uniqueId);
        }

        var editorId = textarea.attr('id');
        if (window.CKEDITOR.instances[editorId]) {
            window.CKEDITOR.instances[editorId].destroy(true);
        }

        window.CKEDITOR.replace(editorId, {
            toolbar: [
                ['Bold', 'Italic', 'Underline', 'Subscript', 'Superscript'],
                ['NumberedList', 'BulletedList'],
                ['Link', 'Unlink'],
                ['Image'],
                ['SpecialChar', 'RemoveFormat']
            ],
            height: 60,
            width: '100%',
            extraPlugins: 'image2',
            removePlugins: 'image,elementspath',
            resize_enabled: false,
            image2_disableResizer: false,
            // Keep pasted math / unicode / Word markup as-is.
            allowedContent: true,
            pasteFilter: null,
            forcePasteAsPlainText: false,
            pasteFromWordRemoveFontStyles: false,
            pasteFromWordRemoveStyles: false,
            pasteFromWordPromptCleanup: false,
            entities: false,
            basicEntities: true,
            entities_latin: false,
            entities_greek: false,
            entities_processNumerical: false,
            filebrowserUploadUrl: '/ckeditor/upload/',
            filebrowserBrowseUrl: '/ckeditor/browse/'
        });

        var editor = window.CKEDITOR.instances[editorId];
        editor.on('instanceReady', function() {
            updateHiddenField(textarea.closest('.answer-options-container'));
        });
        editor.on('change', function() {
            updateHiddenField(textarea.closest('.answer-options-container'), {force: true});
        });
    }

    $(document).ready(function() {
        initializeAnswerOptionsWidget();
    });

    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            initializeCKEditors();
        });
    }

})(django.jQuery || jQuery);

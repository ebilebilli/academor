(function (global) {
    var LESSON_FIELD_NAMES = ['months', 'lesson_count', 'lesson_minutes'];

    function fieldRows(root, fieldName) {
        return root.querySelectorAll('.field-' + fieldName + ', .form-row.field-' + fieldName);
    }

    function rowInputs(row) {
        return row.querySelectorAll('input, select, textarea');
    }

    function clearInput(input) {
        if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = false;
            return;
        }
        input.value = '';
    }

    function toggleLessonFields(root, hide) {
        LESSON_FIELD_NAMES.forEach(function (name) {
            fieldRows(root, name).forEach(function (row) {
                row.style.display = hide ? 'none' : '';
                rowInputs(row).forEach(function (input) {
                    if (hide) {
                        clearInput(input);
                        input.disabled = true;
                        input.removeAttribute('required');
                    } else {
                        input.disabled = false;
                    }
                });
            });
        });
    }

    function toggleCreditsField(root, show) {
        fieldRows(root, 'credits').forEach(function (row) {
            row.style.display = show ? '' : 'none';
            rowInputs(row).forEach(function (input) {
                input.disabled = !show;
                if (show) {
                    input.setAttribute('required', 'required');
                } else {
                    clearInput(input);
                    input.removeAttribute('required');
                }
            });
        });
    }

    global.academorApplyMockPricePackageFields = function (isMock, root) {
        root = root || document;
        toggleLessonFields(root, isMock);
        toggleCreditsField(root, isMock);
    };
})(window);

(function () {
    var BULLET_FIELD_NAMES = ['bullet_list_az', 'bullet_list_en', 'bullet_list_ru'];

    function readFlag(id) {
        var el = document.getElementById(id);
        return !!(el && el.checked);
    }

    function mockFlagsActive() {
        return readFlag('id_ielts_mock_test') || readFlag('id_sat_mock_test');
    }

    function fieldRows(fieldName) {
        return document.querySelectorAll(
            '.field-' + fieldName + ', .form-row.field-' + fieldName
        );
    }

    function toggleBulletListFields() {
        var active = mockFlagsActive();
        BULLET_FIELD_NAMES.forEach(function (name) {
            fieldRows(name).forEach(function (row) {
                row.style.display = active ? '' : 'none';
            });
        });
    }

    function bindExclusive() {
        var ielts = document.getElementById('id_ielts_mock_test');
        var sat = document.getElementById('id_sat_mock_test');
        if (!ielts || !sat) {
            return;
        }
        ielts.addEventListener('change', toggleBulletListFields);
        sat.addEventListener('change', toggleBulletListFields);
    }

    function bind() {
        bindExclusive();
        toggleBulletListFields();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bind);
    } else {
        bind();
    }
})();

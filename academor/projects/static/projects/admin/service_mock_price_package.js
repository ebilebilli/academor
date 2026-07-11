(function () {
    function readFlag(id) {
        var el = document.getElementById(id);
        return !!(el && el.checked);
    }

    function mockFlagsActive() {
        return readFlag('id_ielts_mock_test') || readFlag('id_sat_mock_test');
    }

    function toggleMockPriceFields() {
        var active = mockFlagsActive();
        document.querySelectorAll('.course-price-package-inline').forEach(function (inline) {
            window.academorApplyMockPricePackageFields(active, inline);
        });
    }

    function bindExclusive() {
        var ielts = document.getElementById('id_ielts_mock_test');
        var sat = document.getElementById('id_sat_mock_test');
        if (!ielts || !sat) {
            return;
        }
        ielts.addEventListener('change', function () {
            if (ielts.checked) {
                sat.checked = false;
            }
            toggleMockPriceFields();
        });
        sat.addEventListener('change', function () {
            if (sat.checked) {
                ielts.checked = false;
            }
            toggleMockPriceFields();
        });
    }

    function bind() {
        bindExclusive();
        toggleMockPriceFields();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bind);
    } else {
        bind();
    }

    document.addEventListener('formset:added', function () {
        toggleMockPriceFields();
    });
})();

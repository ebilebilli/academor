(function () {
    function courseSelect() {
        return document.getElementById('id_course');
    }

    function flagsUrl() {
        var match = window.location.pathname.match(/^(.*\/coursepricepackage)\//);
        return match ? match[1] + '/service-mock-flags/' : '';
    }

    function applyMockFields(isMock) {
        window.academorApplyMockPricePackageFields(isMock, document);
    }

    function checkCourse() {
        var select = courseSelect();
        var courseId = select && select.value;
        if (!courseId) {
            applyMockFields(false);
            return;
        }
        var url = flagsUrl();
        if (!url) {
            applyMockFields(false);
            return;
        }
        fetch(url + '?course_id=' + encodeURIComponent(courseId), { credentials: 'same-origin' })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                applyMockFields(!!data.is_mock_test);
            })
            .catch(function () {
                applyMockFields(false);
            });
    }

    function bind() {
        var select = courseSelect();
        if (select) {
            select.addEventListener('change', checkCourse);
            if (window.django && django.jQuery) {
                django.jQuery(select).on('select2:select select2:clear', checkCourse);
            }
        }
        checkCourse();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bind);
    } else {
        bind();
    }
})();

(function () {
  var originalTeacherAutocompleteUrl = null;

  function selectedCourseIds() {
    var select = document.getElementById('id_courses_to');
    if (!select) {
      return [];
    }
    return Array.prototype.map.call(select.options, function (option) {
      return option.value;
    }).filter(Boolean);
  }

  function teacherSelect() {
    return document.getElementById('id_teacher');
  }

  function baseTeacherAutocompleteUrl(select) {
    return (
      select.getAttribute('data-ajax--url')
      || select.dataset.ajaxUrl
      || ''
    );
  }

  function buildTeacherAutocompleteUrl(baseUrl, courseIds) {
    if (!baseUrl) {
      return '';
    }
    var url = new URL(baseUrl, window.location.origin);
    url.searchParams.delete('group_courses');
    if (courseIds.length) {
      url.searchParams.set('group_courses', courseIds.join(','));
    }
    return url.pathname + url.search;
  }

  function reinitTeacherAutocomplete(select, url) {
    if (!window.django || !django.jQuery) {
      return;
    }
    var $ = django.jQuery;
    var $select = $(select);
    if (!$select.length) {
      return;
    }
    select.setAttribute('data-ajax--url', url);
    if ($select.data('select2')) {
      $select.select2('destroy');
    }
    if (typeof $select.djangoAdminSelect2 === 'function') {
      $select.djangoAdminSelect2();
    }
  }

  function syncTeacherAutocomplete() {
    var select = teacherSelect();
    if (!select) {
      return;
    }
    if (!originalTeacherAutocompleteUrl) {
      originalTeacherAutocompleteUrl = baseTeacherAutocompleteUrl(select);
    }
    var baseUrl = originalTeacherAutocompleteUrl;
    if (!baseUrl) {
      return;
    }
    var courseIds = selectedCourseIds();
    var nextUrl = buildTeacherAutocompleteUrl(baseUrl, courseIds);
    reinitTeacherAutocomplete(select, nextUrl);
  }

  function bindCourseSelector() {
    ['id_courses_from', 'id_courses_to'].forEach(function (id) {
      var element = document.getElementById(id);
      if (element) {
        element.addEventListener('change', syncTeacherAutocomplete);
      }
    });
    document.querySelectorAll(
      '.field-courses .selector-chooseall,'
      + ' .field-courses .selector-clearall,'
      + ' .field-courses .selector-add,'
      + ' .field-courses .selector-remove'
    ).forEach(function (button) {
      button.addEventListener('click', function () {
        window.setTimeout(syncTeacherAutocomplete, 0);
      });
    });
  }

  function bind() {
    bindCourseSelector();
    syncTeacherAutocomplete();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();

(function () {
  'use strict';

  var nav = document.querySelector('[data-score-qnav]');
  if (!nav) {
    return;
  }

  function syncScrollMargin() {
    var height = Math.ceil(nav.getBoundingClientRect().height) + 12;
    document.documentElement.style.setProperty('--score-qnav-offset', height + 'px');
  }

  function scrollToQuestion(id) {
    var target = document.getElementById(id);
    if (!target) {
      return;
    }
    syncScrollMargin();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('[data-score-qnav-target]');
    if (!link || !nav.contains(link)) {
      return;
    }
    var id = link.getAttribute('data-score-qnav-target');
    if (!id) {
      return;
    }
    event.preventDefault();
    scrollToQuestion(id);
  });

  syncScrollMargin();
  window.addEventListener('resize', syncScrollMargin);
})();

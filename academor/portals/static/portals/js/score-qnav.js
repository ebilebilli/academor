(function () {
  'use strict';

  var slot = document.querySelector('[data-score-qnav-slot]');
  var nav = document.querySelector('[data-score-qnav]');
  if (!slot || !nav) {
    return;
  }

  function topbarOffset() {
    var topbar = document.querySelector('.admin-navbar');
    if (!topbar) {
      return 0;
    }
    var styles = window.getComputedStyle(topbar);
    if (styles.position === 'fixed' || styles.position === 'sticky') {
      return Math.ceil(topbar.getBoundingClientRect().height);
    }
    return 0;
  }

  function syncScrollMargin() {
    var height = Math.ceil(nav.getBoundingClientRect().height) + topbarOffset() + 12;
    document.documentElement.style.setProperty('--score-qnav-offset', height + 'px');
  }

  function unpin() {
    nav.classList.remove('is-fixed');
    nav.style.top = '';
    nav.style.left = '';
    nav.style.width = '';
    slot.style.height = '';
  }

  function pin() {
    var rect = slot.getBoundingClientRect();
    var offset = topbarOffset();
    slot.style.height = nav.offsetHeight + 'px';
    nav.classList.add('is-fixed');
    nav.style.top = offset + 'px';
    nav.style.left = rect.left + 'px';
    nav.style.width = rect.width + 'px';
  }

  function updatePin() {
    var offset = topbarOffset();
    var rect = slot.getBoundingClientRect();
    if (rect.top <= offset) {
      pin();
    } else {
      unpin();
    }
    syncScrollMargin();
  }

  function scrollToQuestion(id) {
    var target = document.getElementById(id);
    if (!target) {
      return;
    }
    updatePin();
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

  window.addEventListener('scroll', updatePin, { passive: true });
  window.addEventListener('resize', function () {
    if (nav.classList.contains('is-fixed')) {
      pin();
    }
    syncScrollMargin();
  });

  updatePin();
})();

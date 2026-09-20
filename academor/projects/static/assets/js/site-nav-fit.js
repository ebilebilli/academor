/**
 * Fit desktop navbar horizontally without shrinking bar height.
 * Items must be flex-shrink:0 (CSS) so overflow raises scrollWidth
 * and --nav-scale binary search can actually run.
 *
 * Wide / 4K viewports keep scale 1: Contact is flush-right, so comparing
 * its edge to innerWidth falsely looks like overflow and crushed type/logo.
 */
(function () {
  "use strict";

  var rafId = 0;
  var resizeTimer = 0;
  var fitting = false;
  var MIN_SCALE = 0.78;
  var MAX_SCALE = 1;
  var WIDE_NO_SHRINK = 2000;
  var OVERFLOW_SLACK = 4;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function clearNavVars(nav) {
    [
      "--nav-scale",
      "--nav-fs",
      "--nav-gap",
      "--nav-pad-y",
      "--nav-bar-h",
      "--nav-btn-fs",
      "--nav-btn-pad-x",
      "--nav-logo-max",
      "--nav-brand-pad-x",
    ].forEach(function (prop) {
      nav.style.removeProperty(prop);
    });
  }

  function setScale(nav, scale) {
    nav.style.setProperty("--nav-scale", String(scale));
  }

  function isOverflowing(nav) {
    if (nav.scrollWidth > nav.clientWidth + OVERFLOW_SLACK) return true;

    var collapse = qs(".navbar-collapse", nav);
    if (collapse && collapse.scrollWidth > collapse.clientWidth + OVERFLOW_SLACK) {
      return true;
    }

    var navRight = nav.getBoundingClientRect().right;
    var login = qs(".nav-login-btn, .nav-portal-btn", nav);
    var contact = qs(".nav-contact-btn", nav);
    var edge = Math.max(
      login ? login.getBoundingClientRect().right : 0,
      contact ? contact.getBoundingClientRect().right : 0
    );
    return edge > navRight + OVERFLOW_SLACK;
  }

  function fitSiteNavbar() {
    if (fitting) return;
    var nav = qs("nav.navbar.navbar-light");
    if (!nav || window.matchMedia("(max-width: 991.98px)").matches) {
      if (nav) clearNavVars(nav);
      return;
    }

    fitting = true;
    try {
      clearNavVars(nav);
      if (!qs(".navbar-nav .nav-link", nav)) return;
      /* 4K / 2560 CSS px: plenty of width — do not shrink logo/type/buttons */
      if (window.innerWidth >= WIDE_NO_SHRINK) return;
      if (!isOverflowing(nav)) return;

      var lo = MIN_SCALE;
      var hi = MAX_SCALE;
      var best = MIN_SCALE;
      var i;

      for (i = 0; i < 16; i++) {
        var mid = Math.round(((lo + hi) / 2) * 1000) / 1000;
        setScale(nav, mid);
        if (isOverflowing(nav)) {
          hi = mid;
        } else {
          best = mid;
          lo = mid;
        }
      }

      setScale(nav, best);
    } finally {
      fitting = false;
    }
  }

  function scheduleFit() {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(function () {
      rafId = 0;
      fitSiteNavbar();
    });
  }

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  onReady(function () {
    scheduleFit();
    window.addEventListener("load", scheduleFit);
    window.addEventListener(
      "resize",
      function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(scheduleFit, 60);
      },
      { passive: true }
    );
    window.addEventListener("orientationchange", scheduleFit);
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(scheduleFit).catch(function () {});
    }
  });

  window.fitSiteNavbar = scheduleFit;
})();

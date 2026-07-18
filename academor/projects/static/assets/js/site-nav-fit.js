/**
 * Scale site navbar type/spacing until links + auth buttons fit the viewport.
 * Wide screens keep larger type; tight widths / long AZ·RU labels shrink.
 */
(function () {
  "use strict";

  var rafId = 0;
  var resizeTimer = 0;

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function clearNavVars(nav) {
    [
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

  function isOverflowing(nav) {
    if (nav.scrollWidth > nav.clientWidth + 1) return true;
    var login = qs(".nav-login-btn, .nav-portal-btn", nav);
    var contact = qs(".navbar-collapse > a.btn.nav-contact-btn, .navbar-collapse > a.btn.btn-primary", nav);
    var edge = Math.max(
      login ? login.getBoundingClientRect().right : 0,
      contact ? contact.getBoundingClientRect().right : 0
    );
    return edge > window.innerWidth - 2;
  }

  function fitSiteNavbar() {
    var nav = qs("nav.navbar.navbar-light");
    if (!nav || window.matchMedia("(max-width: 991.98px)").matches) {
      if (nav) clearNavVars(nav);
      return;
    }

    clearNavVars(nav);

    var link = qs(".navbar-nav .nav-link", nav);
    var brand = qs(".navbar-brand", nav);
    var logo = qs(".site-logo", brand);
    var login = qs(".nav-login-btn, .nav-portal-btn", nav);
    if (!link) return;

    var size = parseFloat(window.getComputedStyle(link).fontSize) || 16;
    var gap = parseFloat(window.getComputedStyle(link).marginRight) || 8;
    var barH = brand ? parseFloat(window.getComputedStyle(brand).height) || 72 : 72;
    var btnPad = login ? parseFloat(window.getComputedStyle(login).paddingLeft) || 16 : 16;
    var logoMax = logo ? logo.getBoundingClientRect().width || 200 : 200;
    var brandPad = brand ? parseFloat(window.getComputedStyle(brand).paddingLeft) || 12 : 12;

    var minSize = 10.5;
    var minGap = 3;
    var minBar = 48;
    var minBtnPad = 8;
    var minLogo = 110;
    var minBrandPad = 6;
    var guard = 36;

    while (guard-- > 0 && isOverflowing(nav)) {
      if (size > minSize) {
        size -= 0.5;
        nav.style.setProperty("--nav-fs", size + "px");
        nav.style.setProperty("--nav-btn-fs", Math.max(minSize, size - 0.5) + "px");
      } else if (gap > minGap) {
        gap -= 0.5;
        nav.style.setProperty("--nav-gap", gap + "px");
      } else if (btnPad > minBtnPad) {
        btnPad -= 1;
        nav.style.setProperty("--nav-btn-pad-x", btnPad + "px");
      } else if (logoMax > minLogo) {
        logoMax -= 8;
        nav.style.setProperty("--nav-logo-max", logoMax + "px");
      } else if (brandPad > minBrandPad) {
        brandPad -= 1;
        nav.style.setProperty("--nav-brand-pad-x", brandPad + "px");
      } else if (barH > minBar) {
        barH -= 2;
        nav.style.setProperty("--nav-bar-h", barH + "px");
      } else {
        break;
      }
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
        resizeTimer = setTimeout(scheduleFit, 80);
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

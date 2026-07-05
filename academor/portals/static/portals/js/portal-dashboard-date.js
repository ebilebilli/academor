(function () {
  "use strict";

  /**
   * Dashboard dates are rendered server-side via {% portal_today_long %}.
   * This file is kept for portal:content-loaded hooks if needed later.
   */
  function onReady(fn) {
    if (window.portalOnReady) {
      window.portalOnReady(fn);
      return;
    }
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  onReady(function () {});
  document.addEventListener("portal:content-loaded", function () {});
})();

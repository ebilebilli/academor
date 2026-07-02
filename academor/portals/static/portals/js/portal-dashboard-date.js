(function () {
  "use strict";

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

  function formatToday() {
    return new Date().toLocaleDateString("az-AZ", {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
  }

  function updateDates() {
    var text = formatToday();
    document.querySelectorAll("[data-portal-today-date]").forEach(function (el) {
      el.textContent = text;
    });
  }

  onReady(updateDates);
  document.addEventListener("portal:content-loaded", updateDates);
})();

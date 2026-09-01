(function () {
  "use strict";

  function formatDigits(value) {
    var digits = String(value || "").replace(/\D/g, "").slice(0, 4);
    if (digits.length <= 2) {
      return digits;
    }
    return digits.slice(0, 2) + ":" + digits.slice(2);
  }

  function normalizeTime(value) {
    var match = /^(\d{1,2}):(\d{2})$/.exec(String(value || "").trim());
    if (!match) {
      return "";
    }
    var hours = Math.min(parseInt(match[1], 10), 23);
    var minutes = Math.min(parseInt(match[2], 10), 59);
    return String(hours).padStart(2, "0") + ":" + String(minutes).padStart(2, "0");
  }

  function bindInput(input) {
    if (!input || input.dataset.portalTime24Bound === "true") {
      return;
    }
    input.dataset.portalTime24Bound = "true";
    input.setAttribute("autocomplete", "off");
    input.setAttribute("inputmode", "numeric");
    input.setAttribute("maxlength", "5");

    input.addEventListener("input", function () {
      input.value = formatDigits(input.value);
    });

    input.addEventListener("blur", function () {
      if (!input.value) {
        return;
      }
      input.value = normalizeTime(input.value);
    });
  }

  function init(root) {
    var scope = root || document;
    scope.querySelectorAll(".portal-time-24h").forEach(bindInput);
  }

  window.portalBindTime24Input = bindInput;
  window.portalInitTime24Inputs = init;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      init();
    });
  } else {
    init();
  }
})();

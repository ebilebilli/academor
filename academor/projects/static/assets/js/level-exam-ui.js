/* Score report (templates/level-exam-result.html): numbers count up once, in step with the scale. */
(function () {
  "use strict";

  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-lx-count"));
    var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
    if (isNaN(target)) {
      return;
    }
    var duration = 1300;
    var start = null;
    function frame(now) {
      if (start === null) {
        start = now;
      }
      var t = Math.min(1, (now - start) / duration);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (t < 1) {
        window.requestAnimationFrame(frame);
      }
    }
    el.textContent = (0).toFixed(decimals);
    window.setTimeout(function () {
      window.requestAnimationFrame(frame);
    }, 350);
  }

  function init() {
    document.querySelectorAll("[data-lx-count]").forEach(countUp);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

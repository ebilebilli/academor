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

  function initSwitcher(root) {
    if (root.dataset.portalChildSwitcherBound === "true") {
      return;
    }

    var pills = root.querySelectorAll("[data-child-idx]");
    var blocks = root.querySelectorAll("[data-child-block]");
    if (!pills.length || !blocks.length) {
      return;
    }

    root.dataset.portalChildSwitcherBound = "true";

    pills.forEach(function (pill) {
      pill.addEventListener("click", function () {
        var idx = pill.dataset.childIdx;
        pills.forEach(function (item) {
          item.classList.remove("is-active");
          item.setAttribute("aria-pressed", "false");
        });
        blocks.forEach(function (block) {
          block.classList.add("d-none");
        });
        pill.classList.add("is-active");
        pill.setAttribute("aria-pressed", "true");
        var activeBlock = root.querySelector('[data-child-block="' + idx + '"]');
        if (activeBlock) {
          activeBlock.classList.remove("d-none");
        }
      });
    });
  }

  function initAll() {
    document.querySelectorAll("[data-portal-child-switcher]").forEach(initSwitcher);
  }

  onReady(initAll);
  document.addEventListener("portal:content-loaded", initAll);
})();

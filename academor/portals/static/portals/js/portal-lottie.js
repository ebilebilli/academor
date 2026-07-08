(function () {
  "use strict";

  var PLAYER_SRC =
    "https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs";
  var loadPromise = null;
  var readyBound = false;

  function loadPlayer() {
    if (customElements.get("dotlottie-player")) {
      return Promise.resolve();
    }
    if (!loadPromise) {
      loadPromise = import(PLAYER_SRC).catch(function () {
        loadPromise = null;
      });
    }
    return loadPromise;
  }

  function configurePlayer(player) {
    if (!player) {
      return;
    }
    player.background = "transparent";
    if (typeof player.setBackground === "function") {
      player.setBackground("transparent");
    }
    if (typeof player.setRenderConfig === "function") {
      player.setRenderConfig({ clearCanvas: true });
    }
  }

  function bindPlayer(player) {
    configurePlayer(player);
    player.addEventListener("ready", function () {
      configurePlayer(player);
    });
  }

  function initLottie(root) {
    var scope = root || document;
    var blocks = scope.querySelectorAll("[data-portal-lottie]");
    if (!blocks.length) {
      return;
    }
    loadPlayer().then(function () {
      blocks.forEach(function (block) {
        bindPlayer(block.querySelector("dotlottie-player"));
      });
    });
  }

  function onReady(fn) {
    if (readyBound) {
      return;
    }
    readyBound = true;

    var called = false;
    function callOnce(detail) {
      if (called) {
        return;
      }
      called = true;
      try {
        fn(detail);
      } catch (error) {
        console.error(error);
      }
    }

    // Prefer portal lifecycle, but do not miss initialization if the event fired early.
    if (window.portalOnReady) {
      window.portalOnReady(function (detail) {
        callOnce(detail);
      });
    }

    // Fallback for full page loads or race conditions.
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        callOnce(null);
      });
    } else {
      window.setTimeout(function () {
        callOnce(null);
      }, 0);
    }
  }

  onReady(function () {
    initLottie(document);
  });
  document.addEventListener("portal:content-loaded", function (event) {
    initLottie(event.detail && event.detail.root ? event.detail.root : document);
  });
})();

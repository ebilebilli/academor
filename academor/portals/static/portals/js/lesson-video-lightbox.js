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

  function initLessonVideoLightbox() {
    var root = document.querySelector("[data-lesson-video-lightbox]");
    if (!root || root.dataset.lessonVideoLightboxBound === "true") {
      return;
    }
    root.dataset.lessonVideoLightboxBound = "true";

    var embedUrl = root.getAttribute("data-embed-url") || "";
    var autoOpen = root.getAttribute("data-auto-open") === "true";
    var iframe = root.querySelector("[data-lesson-video-iframe]");
    var openButtons = document.querySelectorAll("[data-lesson-video-open]");
    var closeButtons = root.querySelectorAll("[data-lesson-video-close]");

    if (!embedUrl || !iframe) {
      return;
    }

    function buildEmbedSrc(baseUrl) {
      try {
        var url = new URL(baseUrl);
        url.searchParams.set("autoplay", "1");
        url.searchParams.set("origin", window.location.origin);
        url.searchParams.set("rel", "0");
        return url.toString();
      } catch (err) {
        var sep = baseUrl.indexOf("?") >= 0 ? "&" : "?";
        return (
          baseUrl +
          sep +
          "autoplay=1&origin=" +
          encodeURIComponent(window.location.origin)
        );
      }
    }

    function openLightbox() {
      iframe.src = buildEmbedSrc(embedUrl);
      root.hidden = false;
      document.body.classList.add("s-video-lightbox-open");
      var closeBtn = root.querySelector(".s-video-lightbox__close");
      if (closeBtn) {
        closeBtn.focus();
      }
    }

    function closeLightbox() {
      iframe.src = "";
      root.hidden = true;
      document.body.classList.remove("s-video-lightbox-open");
    }

    openButtons.forEach(function (button) {
      button.addEventListener("click", openLightbox);
    });

    closeButtons.forEach(function (button) {
      button.addEventListener("click", closeLightbox);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !root.hidden) {
        closeLightbox();
      }
    });

    if (autoOpen) {
      openLightbox();
    }
  }

  onReady(initLessonVideoLightbox);
})();

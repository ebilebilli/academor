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

  function initLessonImageLightbox() {
    var root = document.querySelector("[data-lesson-image-lightbox]");
    if (!root || root.dataset.lessonImageLightboxBound === "true") {
      return;
    }
    root.dataset.lessonImageLightboxBound = "true";

    var img = root.querySelector("[data-lesson-image-lightbox-img]");
    var openButtons = document.querySelectorAll("[data-lesson-image-open]");
    var closeButtons = root.querySelectorAll("[data-lesson-image-close]");

    if (!img || !openButtons.length) {
      return;
    }

    function openLightbox(url, alt) {
      if (!url) {
        return;
      }
      img.src = url;
      img.alt = alt || "";
      root.hidden = false;
      document.body.classList.add("s-image-lightbox-open");
      var closeBtn = root.querySelector(".s-image-lightbox__close");
      if (closeBtn) {
        closeBtn.focus();
      }
    }

    function closeLightbox() {
      img.removeAttribute("src");
      img.alt = "";
      root.hidden = true;
      document.body.classList.remove("s-image-lightbox-open");
    }

    openButtons.forEach(function (button) {
      button.addEventListener("click", function (event) {
        event.preventDefault();
        openLightbox(
          button.getAttribute("data-image-url") || "",
          button.getAttribute("data-image-alt") || ""
        );
      });
    });

    closeButtons.forEach(function (button) {
      button.addEventListener("click", closeLightbox);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !root.hidden) {
        closeLightbox();
      }
    });
  }

  onReady(initLessonImageLightbox);
})();

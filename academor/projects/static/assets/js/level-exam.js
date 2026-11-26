/* Public SAT / IELTS level test (templates/level-exam-base.html).
   The section page reuses the portal exam scripts. They hand a submit response that carries
   `next_url` to window.PortalQuizMockSection; here that simply moves on to the next section
   (or the result page) without drawing the portal's per-question answer review. */
(function () {
  "use strict";

  window.PortalQuizMockSection = {
    redirectIfNeeded: function (data) {
      if (data && data.redirect_url) {
        window.location.href = data.redirect_url;
        return true;
      }
      return false;
    },
    isMockRoot: function () {
      return false;
    },
    offerContinue: function () {
      return false;
    },
    handleSubmitResponse: function (root, data) {
      if (!data || !data.next_url) {
        return false;
      }
      if (root) {
        root.setAttribute("data-quiz-finished", "true");
      }
      document.body.classList.add("is-leaving");
      window.location.replace(data.next_url);
      return true;
    }
  };
})();

/* The exam name sits in the page, right under the (fixed) timer toolbar, so the toolbar
   never covers it: move it below the toolbar's spacer once the page is ready. */
(function () {
  "use strict";

  function placeHead() {
    var head = document.querySelector(".lx-head");
    var spacer = document.querySelector(".portal-quiz-take-toolbar-spacer");
    if (head && spacer && spacer.parentNode && head.previousElementSibling !== spacer) {
      spacer.parentNode.insertBefore(head, spacer.nextSibling);
    }
  }

  /* The fixed timer toolbar grows once the timer starts (and wraps on phones); keep the
     spacer under it at least as tall, so the heading and first question are never covered. */
  function keepSpacer() {
    var toolbar = document.querySelector(".portal-quiz-take-toolbar");
    var spacer = document.querySelector(".portal-quiz-take-toolbar-spacer");
    if (!toolbar || !spacer || !("ResizeObserver" in window)) {
      return;
    }
    function sync() {
      if (getComputedStyle(toolbar).position !== "fixed" || spacer.hidden) {
        spacer.style.minHeight = "";
        return;
      }
      spacer.style.minHeight = "0px";
      var need = toolbar.getBoundingClientRect().bottom - spacer.getBoundingClientRect().top;
      spacer.style.minHeight = Math.max(0, Math.ceil(need)) + "px";
    }
    new ResizeObserver(sync).observe(toolbar);
    window.addEventListener("resize", sync);
    document.addEventListener("portal-quiz-started", function () {
      window.setTimeout(sync, 50);
    });
  }

  function init() {
    placeHead();
    keepSpacer();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

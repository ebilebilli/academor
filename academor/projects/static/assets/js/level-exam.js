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

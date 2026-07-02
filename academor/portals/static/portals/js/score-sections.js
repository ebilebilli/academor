(function () {
  "use strict";

  function boot() {
    var shell = document.querySelector("[data-score-shell]");
    if (!shell || shell.dataset.portalScoreBound === "true") {
      return;
    }
    shell.dataset.portalScoreBound = "true";

    var tabs = shell.querySelectorAll("[data-score-tab]");
    var panels = shell.querySelectorAll("[data-score-panel]");

    function countFor(name) {
      var tab = shell.querySelector('[data-score-tab="' + name + '"]');
      if (!tab) {
        return 0;
      }
      var badge = tab.querySelector(".portal-score-segment__count");
      return badge ? parseInt(badge.textContent, 10) || 0 : 0;
    }

    function activate(name) {
      tabs.forEach(function (tab) {
        var active = tab.getAttribute("data-score-tab") === name;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
      panels.forEach(function (panel) {
        var active = panel.getAttribute("data-score-panel") === name;
        panel.classList.toggle("is-active", active);
        panel.hidden = !active;
      });

      try {
        var url = new URL(window.location.href);
        url.searchParams.set("view", name);
        window.history.replaceState(
          Object.assign({}, window.history.state, { portalAjax: true, url: url.href, view: name }),
          "",
          url
        );
      } catch (err) {
        /* ignore */
      }
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        activate(tab.getAttribute("data-score-tab"));
      });
    });

    var params = new URLSearchParams(window.location.search);
    var initial = params.get("view");
    if (initial !== "quiz" && initial !== "lesson") {
      initial = countFor("quiz") === 0 && countFor("lesson") > 0 ? "lesson" : "quiz";
    }
    activate(initial);
  }

  if (window.portalOnReady) {
    window.portalOnReady(boot);
  } else {
    document.addEventListener("DOMContentLoaded", boot);
  }
})();

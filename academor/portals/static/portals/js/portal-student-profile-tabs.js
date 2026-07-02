(function () {
  "use strict";

  function tabFromUrl() {
    var params = new URLSearchParams(window.location.search);
    return params.get("tab") || "quiz-results";
  }

  function setActiveTab(nav, tab) {
    nav.querySelectorAll("[data-tab]").forEach(function (link) {
      var isActive = link.getAttribute("data-tab") === tab;
      link.classList.toggle("is-active", isActive);
      if (isActive) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  function afterPanelLoaded(panel, tab) {
    if (tab === "duration" && typeof window.initStudentDurationPanel === "function") {
      window.initStudentDurationPanel(panel.querySelector("[data-duration-panel]"));
    }
    panel.removeAttribute("aria-busy");
    panel.classList.remove("is-loading");
  }

  function loadTab(shell, tab, pushState) {
    var nav = shell.querySelector("[data-student-profile-tab-nav]");
    var panel = shell.querySelector("[data-student-profile-tab-panel]");
    if (!nav || !panel) {
      return Promise.resolve();
    }

    var activeLink = nav.querySelector('[data-tab="' + tab + '"]');
    if (!activeLink) {
      return Promise.resolve();
    }

    if (activeLink.classList.contains("is-active") && !pushState) {
      return Promise.resolve();
    }

    panel.setAttribute("aria-busy", "true");
    panel.classList.add("is-loading");

    var url = activeLink.getAttribute("href");
    if (url.charAt(0) === "?") {
      url = window.location.pathname + url;
    }

    return fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        Accept: "text/html",
      },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("tab load failed");
        }
        return response.text();
      })
      .then(function (html) {
        panel.innerHTML = html;
        setActiveTab(nav, tab);
        if (pushState !== false) {
          window.history.pushState(
            Object.assign({}, window.history.state, {
              portalAjax: true,
              url: url,
              studentProfileTab: tab,
            }),
            "",
            url
          );
        }
        afterPanelLoaded(panel, tab);
      })
      .catch(function () {
        window.location.href = url;
      });
  }

  function onProfilePopstate(event) {
    var shell = document.querySelector("[data-student-profile-tabs]");
    if (!shell) {
      return;
    }
    var tab = (event.state && event.state.studentProfileTab) || tabFromUrl();
    loadTab(shell, tab, false);
  }

  function boot() {
    var shell = document.querySelector("[data-student-profile-tabs]");
    if (!shell || shell.dataset.portalProfileTabsBound === "true") {
      return;
    }
    shell.dataset.portalProfileTabsBound = "true";

    var nav = shell.querySelector("[data-student-profile-tab-nav]");
    if (!nav) {
      return;
    }

    nav.addEventListener("click", function (event) {
      var link = event.target.closest("[data-tab]");
      if (!link || !nav.contains(link)) {
        return;
      }
      event.preventDefault();
      var tab = link.getAttribute("data-tab");
      if (!tab) {
        return;
      }
      loadTab(shell, tab, true);
    });

    var initialTab = tabFromUrl();
    var activeLink = nav.querySelector(".portal-student-segment.is-active");
    var activeTab = activeLink ? activeLink.getAttribute("data-tab") : null;
    if (initialTab && initialTab !== activeTab) {
      loadTab(shell, initialTab, false);
    }

    if (!window.__portalProfileTabsPopstateBound) {
      window.__portalProfileTabsPopstateBound = true;
      window.addEventListener("popstate", onProfilePopstate);
    }
  }

  if (window.portalOnReady) {
    window.portalOnReady(boot);
  } else {
    document.addEventListener("DOMContentLoaded", boot);
  }
})();

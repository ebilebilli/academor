(function () {
  "use strict";

  var profileClickBound = false;
  var tabCache = {};
  var cacheTimestamps = {};
  var CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

  function tabFromUrl() {
    var params = new URLSearchParams(window.location.search);
    return params.get("tab") || "quiz-results";
  }

  function profilePageRoot() {
    return document.querySelector("[data-student-profile-page]");
  }

  function profileTabShell() {
    return document.querySelector("[data-student-profile-tabs]");
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

  function buildProfileUrl(shell, tab, groupId) {
    var params = new URLSearchParams(window.location.search);
    params.set("tab", tab);
    var activeGroup = groupId || (shell && shell.getAttribute("data-profile-from-group"));
    if (activeGroup) {
      params.set("from_group", activeGroup);
    } else {
      params.delete("from_group");
    }
    return window.location.pathname + "?" + params.toString();
  }

  function isCacheValid(cacheKey) {
    if (!cacheTimestamps[cacheKey]) {
      return false;
    }
    var now = Date.now();
    return (now - cacheTimestamps[cacheKey]) < CACHE_TTL;
  }

  function afterPanelLoaded(panel, tab) {
    if (tab === "duration" && typeof window.initStudentDurationPanel === "function") {
      window.initStudentDurationPanel(panel.querySelector("[data-duration-panel]"));
    }
    if (tab === "quiz-access" && typeof window.initTeacherQuizAccessPanel === "function") {
      window.initTeacherQuizAccessPanel(panel.querySelector("[data-quiz-access-panel]"));
    }
    panel.removeAttribute("aria-busy");
    panel.classList.remove("is-loading");
  }

  function loadTab(shell, tab, pushState, options) {
    options = options || {};
    var nav = shell.querySelector("[data-student-profile-tab-nav]");
    var panel = shell.querySelector("[data-student-profile-tab-panel]");
    if (!nav || !panel) {
      return Promise.resolve();
    }

    var activeLink = nav.querySelector('[data-tab="' + tab + '"]');
    if (!activeLink) {
      return Promise.resolve();
    }

    if (
      activeLink.classList.contains("is-active")
      && !pushState
      && !options.forceReload
    ) {
      return Promise.resolve();
    }

    setActiveTab(nav, tab);
    panel.setAttribute("aria-busy", "true");
    panel.classList.add("is-loading");

    var url = buildProfileUrl(shell, tab);
    var cacheKey = url;

    if (tabCache[cacheKey] && isCacheValid(cacheKey) && !options.forceReload) {
      panel.innerHTML = tabCache[cacheKey];
      if (pushState !== false) {
        window.history.pushState(
          {
            studentProfileTab: tab,
            url: url,
          },
          "",
          url
        );
      }
      afterPanelLoaded(panel, tab);
      return Promise.resolve();
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
        tabCache[cacheKey] = html;
        cacheTimestamps[cacheKey] = Date.now();
        panel.innerHTML = html;
        if (pushState !== false) {
          window.history.pushState(
            {
              studentProfileTab: tab,
              url: url,
            },
            "",
            url
          );
        }
        afterPanelLoaded(panel, tab);
      })
      .catch(function () {
        panel.classList.remove("is-loading");
        panel.removeAttribute("aria-busy");
        setActiveTab(nav, tabFromUrl());
        window.location.href = url;
      });
  }

  function loadProfilePage(groupId) {
    var page = profilePageRoot();
    var shell = profileTabShell();
    if (!page) {
      return Promise.resolve();
    }

    tabCache = {};
    var tab = tabFromUrl();
    var url = buildProfileUrl(shell, tab, groupId);
    page.setAttribute("aria-busy", "true");
    page.classList.add("is-loading");

    return fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-Profile-Fragment": "page",
        Accept: "text/html",
      },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("profile page load failed");
        }
        return response.text();
      })
      .then(function (html) {
        page.innerHTML = html;
        page.classList.remove("is-loading");
        page.removeAttribute("aria-busy");
        window.history.pushState(
          {
            studentProfileTab: tab,
            url: url,
          },
          "",
          url
        );
        var panel = profileTabShell();
        if (panel) {
          var activeTab = tabFromUrl();
          afterPanelLoaded(
            panel.querySelector("[data-student-profile-tab-panel]"),
            activeTab
          );
        }
      })
      .catch(function () {
        page.classList.remove("is-loading");
        page.removeAttribute("aria-busy");
        window.location.href = url;
      });
  }

  function onProfilePopstate(event) {
    var page = profilePageRoot();
    var shell = profileTabShell();
    if (!page || !shell) {
      return;
    }
    var tab = (event.state && event.state.studentProfileTab) || tabFromUrl();
    var params = new URLSearchParams(window.location.search);
    var urlGroup = params.get("from_group") || "";
    var shellGroup = shell.getAttribute("data-profile-from-group") || "";
    if (urlGroup !== shellGroup) {
      if (urlGroup) {
        loadProfilePage(urlGroup);
      } else {
        window.location.reload();
      }
      return;
    }
    loadTab(shell, tab, false);
  }

  function bindProfileInteractions() {
    if (profileClickBound) {
      return;
    }
    profileClickBound = true;

    document.addEventListener("click", function (event) {
      var groupBtn = event.target.closest("[data-profile-group]");
      if (groupBtn && groupBtn.closest("[data-student-profile-page]")) {
        event.preventDefault();
        event.stopPropagation();
        if (groupBtn.classList.contains("is-active")) {
          return;
        }
        var groupId = groupBtn.getAttribute("data-profile-group");
        if (!groupId) {
          return;
        }
        loadProfilePage(groupId);
        return;
      }

      var shell = profileTabShell();
      if (!shell) {
        return;
      }
      var nav = shell.querySelector("[data-student-profile-tab-nav]");
      if (!nav) {
        return;
      }
      var link = event.target.closest("[data-tab]");
      if (!link || !nav.contains(link)) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      var tab = link.getAttribute("data-tab");
      if (!tab) {
        return;
      }
      loadTab(shell, tab, true);
    });

    if (!window.__portalProfileTabsPopstateBound) {
      window.__portalProfileTabsPopstateBound = true;
      window.addEventListener("popstate", onProfilePopstate);
    }
  }

  function boot() {
    if (!profilePageRoot()) {
      return;
    }
    bindProfileInteractions();

    var shell = profileTabShell();
    if (!shell) {
      return;
    }

    var nav = shell.querySelector("[data-student-profile-tab-nav]");
    if (!nav) {
      return;
    }

    var initialTab = tabFromUrl();
    var activeLink = nav.querySelector(".portal-student-segment.is-active");
    var activeTab = activeLink ? activeLink.getAttribute("data-tab") : null;
    if (initialTab && initialTab !== activeTab) {
      loadTab(shell, initialTab, false);
    }
  }

  if (window.portalOnReady) {
    window.portalOnReady(boot);
  } else {
    document.addEventListener("DOMContentLoaded", boot);
  }
  document.addEventListener("portal:content-loaded", boot);
})();

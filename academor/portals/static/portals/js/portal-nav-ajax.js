(function () {
  "use strict";

  window.portalOnReady = function (callback) {
    document.addEventListener("portal:content-loaded", function () {
      try {
        callback();
      } catch (error) {
        console.error(error);
      }
    });
  };

  function dispatchPortalContentLoaded(url, initial) {
    document.dispatchEvent(new CustomEvent("portal:content-loaded", {
      detail: { url: url || window.location.href, initial: !!initial },
    }));
  }

  var SKIP_PATH_RE = /\/portal\/(login|logout)\/?$|\/portal\/student\/quizzes\/\d+\/(take|manual|reading|speaking)\/?$|\/portal\/student\/ielts-mock(\/|$)/i;
  var PREFETCH_SKIP_PATH_RE = /\/portal\/student\/(scores|notifications)(\/|$)|\/portal\/student\/quizzes(\/category\/|\/|$)|\/portal\/parent\/(scores|notifications)(\/|$)/i;
  var CORE_SCRIPTS = /bootstrap\.bundle|\/main\.js|portal-nav-ajax\.js|portal-init\.js/i;
  var FRAGMENT_HEADERS = {
    Accept: "text/html",
    "X-Requested-With": "XMLHttpRequest",
    "X-Portal-Fragment": "1",
  };
  var prefetchedHtml = new Map();
  var prefetchInFlight = new Map();
  var PREFETCH_MAX = 10;
  var prefetchHoverTimer = null;
  var prefetchHoverUrl = "";

  function isModifiedClick(event) {
    return event.defaultPrevented
      || event.button !== 0
      || event.metaKey
      || event.ctrlKey
      || event.shiftKey
      || event.altKey;
  }

  function shouldHandleLink(link) {
    if (!link || !link.href) {
      return false;
    }

    var rawHref = link.getAttribute("href") || "";
    if (!rawHref || rawHref.charAt(0) === "#") {
      return false;
    }

    if (link.hasAttribute("download")
      || link.hasAttribute("onclick")
      || link.target === "_blank"
      || link.getAttribute("data-no-ajax") === "true"
      || link.getAttribute("data-bs-toggle") === "modal"
      || link.getAttribute("role") === "button") {
      return false;
    }

    var url;
    try {
      url = new URL(link.href, window.location.origin);
    } catch (error) {
      return false;
    }

    if (url.origin !== window.location.origin || !url.pathname.startsWith("/portal/")) {
      return false;
    }

    if (SKIP_PATH_RE.test(url.pathname)) {
      return false;
    }

    return true;
  }

  function shouldPrefetchLink(link) {
    if (!shouldHandleLink(link)) {
      return false;
    }
    try {
      var url = new URL(link.href, window.location.origin);
      if (PREFETCH_SKIP_PATH_RE.test(url.pathname)) {
        return false;
      }
    } catch (error) {
      return false;
    }
    return true;
  }

  function clearPrefetchCache() {
    prefetchedHtml.clear();
    prefetchInFlight.forEach(function (controller) {
      try {
        controller.abort();
      } catch (error) {
        /* ignore */
      }
    });
    prefetchInFlight.clear();
    prefetchHoverUrl = "";
    if (prefetchHoverTimer) {
      clearTimeout(prefetchHoverTimer);
      prefetchHoverTimer = null;
    }
  }

  function findNavLink(target) {
    return target.closest("#adminSidebar .nav-link, .mobile-bottom-nav .mobile-nav-item, #adminSidebar .brand-mark");
  }

  function findPortalLink(target) {
    var link = target.closest("a[href]");
    if (!link) {
      return null;
    }
    if (link.closest("[data-portal-content-root]")
      || link.closest("#adminSidebar")
      || link.closest(".mobile-bottom-nav")
      || link.classList.contains("brand-mark")) {
      return link;
    }
    return null;
  }

  function parseHtml(html) {
    return new DOMParser().parseFromString(html, "text/html");
  }

  function ensureStyles(doc) {
    var promises = [];
    doc.querySelectorAll('head link[rel="stylesheet"]').forEach(function (link) {
      var href = link.getAttribute("href");
      if (!href || href.indexOf("/portals/") === -1) {
        return;
      }

      var exists = document.querySelector('link[rel="stylesheet"][href="' + href + '"]');
      if (exists) {
        return;
      }

      promises.push(new Promise(function (resolve) {
        var node = document.createElement("link");
        node.rel = "stylesheet";
        node.href = href;
        node.onload = resolve;
        node.onerror = resolve;
        document.head.appendChild(node);
      }));
    });

    return Promise.all(promises);
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = src;
      script.async = false;
      script.setAttribute("data-portal-page-script", "true");
      script.onload = resolve;
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  function loadPageScripts(doc) {
    var scripts = Array.prototype.slice.call(doc.body.querySelectorAll("script[src]"));
    var loads = [];

    scripts.forEach(function (script) {
      var src = script.getAttribute("src");
      if (!src || CORE_SCRIPTS.test(src)) {
        return;
      }

      if (document.querySelector('script[data-portal-page-script][src="' + src + '"]')) {
        return;
      }

      loads.push(loadScript(src));
    });

    return Promise.all(loads);
  }

  function normalizePath(href) {
    try {
      var path = new URL(href, window.location.origin).pathname;
      return path.length > 1 ? path.replace(/\/$/, "") : path;
    } catch (error) {
      return href;
    }
  }

  function getNavRoot(doc, selector) {
    if (!doc) {
      return null;
    }
    if (selector === "#adminSidebar") {
      return doc.querySelector("#portal-nav-snapshot #adminSidebar")
        || doc.querySelector("#adminSidebar");
    }
    if (selector === ".mobile-bottom-nav") {
      return doc.querySelector("#portal-nav-snapshot .mobile-bottom-nav")
        || doc.querySelector(".mobile-bottom-nav");
    }
    return doc.querySelector(selector);
  }

  function syncLinkStates(selector, doc) {
    var currentRoot = document.querySelector(selector);
    var nextRoot = getNavRoot(doc, selector);
    if (!currentRoot || !nextRoot) {
      return;
    }

    var nextByPath = {};
    nextRoot.querySelectorAll("a[href]").forEach(function (link) {
      nextByPath[normalizePath(link.getAttribute("href"))] = link;
    });

    currentRoot.querySelectorAll("a[href]").forEach(function (link) {
      var nextLink = nextByPath[normalizePath(link.getAttribute("href"))];
      if (!nextLink) {
        link.classList.remove("active");
        link.removeAttribute("aria-current");
        return;
      }

      link.classList.toggle("active", nextLink.classList.contains("active"));
      if (nextLink.classList.contains("active")) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }

      var nextBadge = nextLink.querySelector(".nav-badge, .mobile-nav-badge");
      var currentBadge = link.querySelector(".nav-badge, .mobile-nav-badge");
      if (nextBadge && currentBadge) {
        currentBadge.textContent = nextBadge.textContent;
        currentBadge.hidden = nextBadge.hidden;
        currentBadge.classList.toggle("d-none", nextBadge.classList.contains("d-none"));
      }
    });
  }

  function isMockTestNavContext(url) {
    try {
      var parsed = new URL(url, window.location.origin);
      if (parsed.pathname.indexOf("/portal/student/ielts-mock") === 0) {
        return true;
      }
      if (
        parsed.searchParams.has("mock")
        && /\/portal\/student\/quizzes\/\d+\/(take|manual|reading|speaking)\/?$/i.test(parsed.pathname)
      ) {
        return true;
      }
    } catch (error) {
      return false;
    }
    return false;
  }

  function syncActiveNavFromUrl(url) {
    if (isMockTestNavContext(url)) {
      document.querySelectorAll("#adminSidebar .nav-link, .mobile-bottom-nav .mobile-nav-item").forEach(function (link) {
        var isMock = link.hasAttribute("data-nav-mock-test");
        link.classList.toggle("active", isMock);
        if (isMock) {
          link.setAttribute("aria-current", "page");
        } else {
          link.removeAttribute("aria-current");
        }
      });
      return;
    }

    var current = normalizePath(url);
    var bestMatch = null;
    var bestScore = -1;

    document.querySelectorAll(
      "#adminSidebar .nav-link[href], .mobile-bottom-nav .mobile-nav-item[href]"
    ).forEach(function (link) {
      if (link.classList.contains("brand-mark")) {
        return;
      }
      var path = normalizePath(link.getAttribute("href"));
      if (!path) {
        return;
      }
      var score = -1;
      if (current === path) {
        score = 1000 + path.length;
      } else if (path !== "/portal" && current.indexOf(path + "/") === 0) {
        score = path.length;
      }
      if (score > bestScore) {
        bestMatch = link;
        bestScore = score;
      }
    });

    document.querySelectorAll("#adminSidebar .nav-link, .mobile-bottom-nav .mobile-nav-item").forEach(function (link) {
      var active = link === bestMatch;
      link.classList.toggle("active", active);
      if (active) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  function trimPrefetchCache() {
    while (prefetchedHtml.size > PREFETCH_MAX) {
      var firstKey = prefetchedHtml.keys().next().value;
      prefetchedHtml.delete(firstKey);
    }
  }

  function prefetchPage(url) {
    if (prefetchedHtml.has(url) || prefetchInFlight.has(url)) {
      return;
    }

    var controller = new AbortController();
    prefetchInFlight.set(url, controller);

    fetch(url, {
      method: "GET",
      credentials: "same-origin",
      signal: controller.signal,
      headers: FRAGMENT_HEADERS,
    })
      .then(function (response) {
        if (!response.ok || response.redirected) {
          return "";
        }
        return response.text();
      })
      .then(function (html) {
        if (html && html.indexOf("data-portal-content-root") !== -1) {
          prefetchedHtml.set(url, html);
          trimPrefetchCache();
        }
      })
      .catch(function () {})
      .finally(function () {
        prefetchInFlight.delete(url);
      });
  }

  function schedulePrefetch(url) {
    if (!url || prefetchHoverUrl === url) {
      return;
    }
    prefetchHoverUrl = url;
    if (prefetchHoverTimer) {
      clearTimeout(prefetchHoverTimer);
    }
    prefetchHoverTimer = setTimeout(function () {
      prefetchPage(url);
    }, 60);
  }

  function fetchPageHtml(url, signal) {
    if (prefetchedHtml.has(url)) {
      var cached = prefetchedHtml.get(url);
      prefetchedHtml.delete(url);
      return Promise.resolve(cached);
    }

    return fetch(url, {
      method: "GET",
      credentials: "same-origin",
      signal: signal,
      headers: FRAGMENT_HEADERS,
    })
      .then(function (response) {
        if (response.redirected) {
          window.location.href = response.url;
          return null;
        }

        if (!response.ok) {
          throw new Error("HTTP " + response.status);
        }

        return response.text();
      });
  }

  function applyNavigationHtml(html, url, push) {
    if (!html) {
      return Promise.resolve();
    }

    stopAllPageMedia();

    var doc = parseHtml(html);
    var nextContent = doc.querySelector("[data-portal-content-root]");
    if (!nextContent) {
      window.location.href = url;
      return Promise.resolve();
    }

    document.title = doc.title || document.title;
    window.__portalNavPending = true;

    var root = document.querySelector("[data-portal-content-root]");
    if (root) {
      root.classList.add("is-ajax-swapped");
    }

    mountContent(nextContent.innerHTML, nextContent);
    syncLinkStates("#adminSidebar", doc);
    syncLinkStates(".mobile-bottom-nav", doc);
    syncActiveNavFromUrl(url);
    syncBadgesFromSnapshot(doc);
    syncTopbarBadges(doc);
    setLoading(false);

    if (push !== false) {
      window.history.pushState(
        Object.assign({}, window.history.state, { portalAjax: true, url: url }),
        "",
        url
      );
    }

    window.__portalNavPending = false;

    return Promise.all([ensureStyles(doc), loadPageScripts(doc)]).then(function () {
      dispatchPortalContentLoaded(url, false);
      if (window.AcademorPortal && typeof window.AcademorPortal.initPageContent === "function") {
        window.AcademorPortal.initPageContent();
      }
    }).then(function () {
      window.scrollTo(0, 0);

      if (root) {
        window.requestAnimationFrame(function () {
          root.classList.remove("is-ajax-swapped");
        });
      }
    });
  }

  function syncBadgesFromSnapshot(doc) {
    var snapshot = doc
      ? doc.querySelector("#portal-badge-snapshot")
      : document.querySelector("[data-portal-content-root] #portal-badge-snapshot");
    if (!snapshot) {
      return;
    }

    var count = Math.max(0, parseInt(snapshot.getAttribute("data-unread-notifications"), 10) || 0);
    document.querySelectorAll("[data-portal-unread-badge]").forEach(function (badge) {
      if (count > 0) {
        badge.textContent = count;
        badge.hidden = false;
        badge.classList.remove("d-none");
      } else {
        badge.hidden = true;
        badge.classList.add("d-none");
      }
    });
  }

  function syncTopbarBadges(doc) {
    var nextTopbar = doc.querySelector(".admin-navbar");
    if (!nextTopbar) {
      return;
    }

    document.querySelectorAll("[data-portal-unread-badge]").forEach(function (badge) {
      var parent = badge.closest("a, .dropdown-item");
      if (!parent) {
        return;
      }

      var href = parent.getAttribute("href");
      var selector = href
        ? '.admin-navbar a[href="' + href.replace(/"/g, '\\"') + '"] [data-portal-unread-badge]'
        : null;
      var nextBadge = selector ? nextTopbar.querySelector(selector) : null;
      if (!nextBadge) {
        return;
      }

      badge.textContent = nextBadge.textContent;
      badge.hidden = nextBadge.hidden;
      badge.classList.toggle("d-none", nextBadge.classList.contains("d-none"));
    });
  }

  var loadingTimer = null;

  function setLoading(isLoading) {
    if (isLoading) {
      if (!loadingTimer) {
        loadingTimer = setTimeout(function () {
          var root = document.querySelector("[data-portal-content-root]");
          if (root) {
            root.classList.add("is-nav-loading");
          }
          loadingTimer = null;
        }, 80);
      }
    } else {
      if (loadingTimer) {
        clearTimeout(loadingTimer);
        loadingTimer = null;
      }
      var root = document.querySelector("[data-portal-content-root]");
      if (root) {
        root.classList.remove("is-nav-loading");
      }
    }
  }

  function stripInertPageScripts(root) {
    if (!root) {
      return;
    }
    root.querySelectorAll('script[src]:not([type="application/json"])').forEach(function (node) {
      node.remove();
    });
  }

  function runInlineScripts(root) {
    if (!root) {
      return;
    }

    root.querySelectorAll("script:not([src])").forEach(function (oldScript) {
      if ((oldScript.getAttribute("type") || "").toLowerCase() === "application/json") {
        return;
      }

      var script = document.createElement("script");
      Array.prototype.forEach.call(oldScript.attributes, function (attr) {
        script.setAttribute(attr.name, attr.value);
      });
      script.textContent = oldScript.textContent;
      oldScript.parentNode.replaceChild(script, oldScript);
    });
  }

  function mountContent(html, sourceRoot) {
    var root = document.querySelector("[data-portal-content-root]");
    if (!root) {
      return;
    }

    var range = document.createRange();
    range.selectNodeContents(root);
    range.deleteContents();

    var fragment = range.createContextualFragment(html);
    root.appendChild(fragment);

    stripInertPageScripts(root);
    syncJsonScripts(sourceRoot, root);
    runInlineScripts(root);
  }

  function syncJsonScripts(sourceRoot, targetRoot) {
    if (!sourceRoot || !targetRoot) {
      return;
    }

    sourceRoot.querySelectorAll('script[type="application/json"]').forEach(function (node) {
      var id = node.id;
      if (!id) {
        return;
      }

      var existing = document.getElementById(id);
      if (existing) {
        existing.remove();
      }

      targetRoot.appendChild(node.cloneNode(true));
    });
  }

  var activeController = null;

  function stopAllPageMedia() {
    if (typeof window.portalQuizMediaCleanup === "function") {
      try {
        window.portalQuizMediaCleanup();
      } catch (error) {
        /* ignore */
      }
    }
    document.querySelectorAll("audio, video").forEach(function (node) {
      try {
        node.pause();
        node.removeAttribute("src");
        node.load();
      } catch (error) {
        /* ignore */
      }
    });
  }

  function requestPortalNavigation(url, push) {
    var event = new CustomEvent("portal:before-navigate", {
      cancelable: true,
      detail: { url: url, push: push },
    });
    return document.dispatchEvent(event);
  }

  function navigate(url, push) {
    if (!requestPortalNavigation(url, push)) {
      return Promise.resolve();
    }

    stopAllPageMedia();

    if (activeController) {
      activeController.abort();
    }

    activeController = new AbortController();
    setLoading(true);

    return fetchPageHtml(url, activeController.signal)
      .then(function (html) {
        return applyNavigationHtml(html, url, push);
      })
      .catch(function (error) {
        if (error && error.name === "AbortError") {
          return;
        }
        window.location.href = url;
      })
      .finally(function () {
        setLoading(false);
        activeController = null;
      });
  }

  document.addEventListener("mouseover", function (event) {
    var link = findPortalLink(event.target);
    if (!link || !shouldPrefetchLink(link)) {
      return;
    }
    schedulePrefetch(link.href);
  }, true);

  document.addEventListener("focusin", function (event) {
    var link = findPortalLink(event.target);
    if (!link || !shouldPrefetchLink(link)) {
      return;
    }
    schedulePrefetch(link.href);
  });

  document.addEventListener("touchstart", function (event) {
    var link = findPortalLink(event.target);
    if (!link || !shouldPrefetchLink(link)) {
      return;
    }
    prefetchPage(link.href);
  }, { passive: true, capture: true });

  document.addEventListener("click", function (event) {
    if (isModifiedClick(event)) {
      return;
    }

    var link = findPortalLink(event.target);
    if (!link || !shouldHandleLink(link)) {
      return;
    }

    event.preventDefault();
    navigate(link.href, true);

    if (findNavLink(event.target)
      && window.AcademorPortal
      && typeof window.AcademorPortal.closeMobileSidebar === "function") {
      window.AcademorPortal.closeMobileSidebar();
    }
  });

  window.addEventListener("popstate", function (event) {
    if (event.state && event.state.portalAjax && event.state.url) {
      navigate(event.state.url, false);
      return;
    }

    if (event.state && event.state.studentProfileTab) {
      navigate(window.location.href, false);
      return;
    }

    if (new URLSearchParams(window.location.search).has("view")) {
      navigate(window.location.href, false);
      return;
    }

    window.location.reload();
  });

  if (!window.history.state || !window.history.state.portalAjax) {
    window.history.replaceState(
      Object.assign({}, window.history.state, {
        portalAjax: true,
        url: window.location.href,
      }),
      "",
      window.location.href
    );
  }

  function scheduleInitialPortalReady() {
    window.setTimeout(function () {
      dispatchPortalContentLoaded(window.location.href, true);
    }, 0);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleInitialPortalReady);
  } else {
    scheduleInitialPortalReady();
  }

  document.addEventListener("portal:content-loaded", function (event) {
    var url = (event.detail && event.detail.url) || window.location.href;
    syncActiveNavFromUrl(url);
  });

  window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
      clearPrefetchCache();
    }
  });

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") {
      clearPrefetchCache();
    }
  });
})();

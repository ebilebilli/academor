/* Result page answer review: the sticky number strip and the answer map jump to a question,
   and the strip marks the question being read. */
(function () {
  "use strict";

  var section = document.querySelector(".lxa");
  var jump = document.querySelector("[data-lxa-jump]");
  if (!section || !jump) {
    return;
  }
  var track = jump.querySelector("[data-lxa-jump-track]");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // the strip sits right under the site's sticky bar
  function siteBarHeight() {
    var bar = document.querySelector(".navbar.sticky-top, .sticky-top");
    if (!bar) {
      return 0;
    }
    // the bar's bottom edge, so anything pinned above it (a notice, a progress line) counts too
    var rect = bar.getBoundingClientRect();
    return rect.bottom > 0 ? Math.round(rect.bottom) : 0;
  }

  var sentinel = null;

  function layout() {
    var top = siteBarHeight();
    section.style.setProperty("--lxa-jump-top", top + "px");
    section.style.setProperty("--lxa-scroll-offset", top + jump.offsetHeight + 16 + "px");
    if (sentinel) {
      jump.classList.toggle("is-stuck", sentinel.getBoundingClientRect().top < top);
    }
  }

  layout();
  window.addEventListener("resize", layout);
  window.addEventListener("load", layout);
  // the site bar can move once the page scrolls (a notice appears above it), so follow it
  var queued = false;
  window.addEventListener("scroll", function () {
    if (queued) {
      return;
    }
    queued = true;
    requestAnimationFrame(function () {
      queued = false;
      layout();
    });
  }, { passive: true });

  // a shadow once the strip is pinned (checked on scroll: an instant jump crosses no observer threshold)
  sentinel = document.createElement("div");
  sentinel.setAttribute("aria-hidden", "true");
  jump.parentNode.insertBefore(sentinel, jump);

  var links = Array.prototype.slice.call(jump.querySelectorAll("[data-lxa-jump-link]"));
  var byId = {};
  links.forEach(function (link) {
    byId[link.getAttribute("href").slice(1)] = link;
  });

  function keepInStrip(link) {
    if (!track || !link) {
      return;
    }
    var left = link.offsetLeft - track.clientWidth / 2 + link.offsetWidth / 2;
    track.scrollTo({ left: Math.max(0, left), behavior: reduceMotion ? "auto" : "smooth" });
  }

  function markCurrent(id) {
    links.forEach(function (link) {
      link.classList.toggle("is-current", link.getAttribute("href") === "#" + id);
    });
    keepInStrip(byId[id]);
  }

  var jumping = null;  // while a jump scrolls, the reading marker must not follow the passing items

  function goTo(id) {
    var item = document.getElementById(id);
    if (!item) {
      return;
    }
    // a correct answer hidden by "Mistakes only" needs the full list back first
    if (item.offsetParent === null) {
      var all = document.getElementById("lxa-all");
      if (all) {
        all.checked = true;
      }
    }
    layout();
    // a long way is jumped at once: a smooth scroll across dozens of answers only gets in the way
    // ("instant", not "auto": the page sets scroll-behavior: smooth, which "auto" would follow)
    var far = Math.abs(item.getBoundingClientRect().top) > window.innerHeight * 3;
    var done = function () {
      clearTimeout(jumping);
      jumping = null;
      window.removeEventListener("scrollend", done);
      markCurrent(id);
    };
    clearTimeout(jumping);
    jumping = setTimeout(done, 1600);
    if ("onscrollend" in window) {
      window.addEventListener("scrollend", done);
    }
    item.scrollIntoView({ behavior: far || reduceMotion ? "instant" : "smooth", block: "start" });
    item.classList.remove("is-flash");
    void item.offsetWidth;
    item.classList.add("is-flash");
    markCurrent(id);
    if (history.replaceState) {
      history.replaceState(null, "", "#" + id);
    }
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("[data-lxa-jump-link]");
    if (!link) {
      return;
    }
    event.preventDefault();
    goTo(link.getAttribute("href").slice(1));
  });

  // follow the reading position
  if ("IntersectionObserver" in window) {
    var visible = {};
    var watcher = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting ? entry.boundingClientRect.top : undefined;
      });
      if (jumping) {
        return;
      }
      var first = null;
      Object.keys(visible).forEach(function (id) {
        if (visible[id] !== undefined && (first === null || visible[id] < visible[first])) {
          first = id;
        }
      });
      if (first) {
        markCurrent(first);
      }
    }, { rootMargin: "-" + (siteBarHeight() + jump.offsetHeight + 8) + "px 0px -60% 0px" });
    document.querySelectorAll(".lxa-item[id]").forEach(function (item) {
      watcher.observe(item);
    });
  }

  if (location.hash && /^#lxa-q-/.test(location.hash)) {
    window.addEventListener("load", function () {
      goTo(location.hash.slice(1));
    });
  }
})();

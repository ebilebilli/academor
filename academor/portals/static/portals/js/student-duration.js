(function () {
  "use strict";

  function parseEntry(el) {
    return {
      el: el,
      date: parseInt(el.getAttribute("data-date-ts") || "0", 10) || 0,
      duration: parseInt(el.getAttribute("data-duration-sec") || "0", 10) || 0,
    };
  }

  function sortEntries(list, mode) {
    var items = Array.prototype.slice.call(list.querySelectorAll("[data-duration-entry]"));
    if (!items.length) {
      return;
    }
    var parsed = items.map(parseEntry);
    if (mode === "longest") {
      parsed.sort(function (a, b) {
        return b.duration - a.duration || b.date - a.date;
      });
    } else {
      parsed.sort(function (a, b) {
        return b.date - a.date;
      });
    }
    parsed.forEach(function (item) {
      list.appendChild(item.el);
    });
  }

  function animateMeters(root) {
    var fills = root.querySelectorAll(".portal-duration-meter__fill[data-target-width]");
    if (!fills.length || !("IntersectionObserver" in window)) {
      fills.forEach(function (fill) {
        fill.style.width = fill.getAttribute("data-target-width") || "0%";
      });
      return;
    }
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) {
            return;
          }
          var fill = entry.target;
          fill.style.width = fill.getAttribute("data-target-width") || "0%";
          observer.unobserve(fill);
        });
      },
      { threshold: 0.2, rootMargin: "0px 0px -10% 0px" }
    );
    fills.forEach(function (fill) {
      observer.observe(fill);
    });
  }

  function initDurationPanel(panel) {
    if (!panel) {
      return;
    }

    var list = panel.querySelector("[data-duration-list]");
    var sortBtns = panel.querySelectorAll("[data-duration-sort]");
    var activeSort = "newest";

    sortBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var mode = btn.getAttribute("data-duration-sort") || "newest";
        if (mode === activeSort) {
          return;
        }
        activeSort = mode;
        sortBtns.forEach(function (other) {
          other.classList.toggle("is-active", other === btn);
          other.setAttribute("aria-pressed", other === btn ? "true" : "false");
        });
        if (list) {
          sortEntries(list, mode);
        }
      });
    });

    animateMeters(panel);
  }

  window.initStudentDurationPanel = initDurationPanel;

  function boot() {
    initDurationPanel(document.querySelector("[data-duration-panel]"));
  }

  if (window.portalOnReady) {
    window.portalOnReady(boot);
  } else {
    document.addEventListener("DOMContentLoaded", boot);
  }
})();

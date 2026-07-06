(function () {
  "use strict";

  function syncScoreFilters(root) {
    if (!root) {
      return;
    }
    if (root.__scoreFilterController && typeof root.__scoreFilterController.applyFilters === "function") {
      root.__scoreFilterController.applyFilters();
      return;
    }
    document.dispatchEvent(new CustomEvent("portal:content-loaded"));
  }

  function initQuizHistoryLazy(root) {
    if (!root || root.dataset.quizHistoryBound === "true") {
      return;
    }
    var url = root.getAttribute("data-quiz-history-url");
    var sentinel = root.querySelector("[data-quiz-history-sentinel]");
    var tbody = root.querySelector("[data-quiz-history-body]");
    var loading = root.querySelector("[data-quiz-history-loading]");
    if (!url || !sentinel || !tbody) {
      return;
    }

    root.dataset.quizHistoryBound = "true";
    var offset = parseInt(root.getAttribute("data-quiz-history-offset") || "0", 10) || 0;
    var total = parseInt(root.getAttribute("data-quiz-history-total") || "0", 10) || 0;
    var loadingMore = false;
    var hasMore = offset < total;

    function setLoading(active) {
      loadingMore = active;
      if (loading) {
        loading.classList.toggle("d-none", !active);
      }
    }

    function appendRows(html) {
      if (!html) {
        return;
      }
      var emptyRow = tbody.querySelector("[data-quiz-history-empty]");
      if (emptyRow) {
        emptyRow.remove();
      }
      tbody.insertAdjacentHTML("beforeend", html);
      syncScoreFilters(root.closest("[data-portal-scores-filter]"));
    }

    function loadMore() {
      if (!hasMore || loadingMore) {
        return;
      }
      setLoading(true);
      var requestUrl = new URL(url, window.location.origin);
      requestUrl.searchParams.set("offset", String(offset));

      fetch(requestUrl.toString(), {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("load failed");
          }
          return response.json();
        })
        .then(function (payload) {
          appendRows(payload.html || "");
          offset = payload.next_offset || offset;
          hasMore = !!payload.has_more;
          root.setAttribute("data-quiz-history-offset", String(offset));
          if (!hasMore) {
            observer.disconnect();
            sentinel.hidden = true;
          }
        })
        .catch(function () {
          hasMore = false;
          observer.disconnect();
          sentinel.hidden = true;
        })
        .finally(function () {
          setLoading(false);
        });
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            loadMore();
          }
        });
      },
      { root: null, rootMargin: "240px 0px", threshold: 0.01 }
    );

    if (hasMore) {
      sentinel.hidden = false;
      observer.observe(sentinel);
    }
  }

  function initAll() {
    document.querySelectorAll("[data-quiz-history-lazy]").forEach(initQuizHistoryLazy);
  }

  document.addEventListener("portal:content-loaded", initAll);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})();

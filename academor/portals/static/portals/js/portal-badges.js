(function () {
  "use strict";

  var POLL_MS = 20000;
  var badgesUrl = document.body.getAttribute("data-portal-badges-url");
  if (!badgesUrl) {
    return;
  }

  function applyBadgeCount(nodes, count) {
    var value = Math.max(0, parseInt(count, 10) || 0);
    nodes.forEach(function (badge) {
      if (value > 0) {
        badge.textContent = String(value);
        badge.hidden = false;
        badge.classList.remove("d-none");
      } else {
        badge.hidden = true;
        badge.classList.add("d-none");
      }
    });
  }

  function syncBadges(payload) {
    if (!payload) {
      return;
    }
    applyBadgeCount(
      document.querySelectorAll("[data-portal-unread-badge]"),
      payload.unread
    );
    applyBadgeCount(
      document.querySelectorAll("[data-portal-pending-review-badge]"),
      payload.pending_reviews
    );
    var snapshot = document.getElementById("portal-badge-snapshot");
    if (snapshot && payload.unread != null) {
      snapshot.setAttribute("data-unread-notifications", String(payload.unread || 0));
    }
    if (snapshot && payload.pending_reviews != null) {
      snapshot.setAttribute("data-pending-reviews", String(payload.pending_reviews || 0));
    }
  }

  function pollBadges() {
    if (document.visibilityState !== "visible") {
      return;
    }
    fetch(badgesUrl, {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("badge poll failed");
        }
        return response.json();
      })
      .then(syncBadges)
      .catch(function () {});
  }

  document.addEventListener("DOMContentLoaded", function () {
    pollBadges();
    window.setInterval(pollBadges, POLL_MS);
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") {
        pollBadges();
      }
    });
  });

  window.portalSyncBadges = syncBadges;
})();

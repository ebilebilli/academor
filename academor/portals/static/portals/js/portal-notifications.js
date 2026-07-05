(function () {
  "use strict";

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"));
    return match ? decodeURIComponent(match.pop()) : "";
  }

  function postAction(url) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
        Accept: "application/json",
      },
    }).then(function (response) {
      return response.json().then(function (data) {
        return { ok: response.ok, data: data };
      });
    });
  }

  function updateUnreadBadges(count) {
    var value = Math.max(0, parseInt(count, 10) || 0);
    document.querySelectorAll("[data-portal-unread-badge]").forEach(function (node) {
      if (value > 0) {
        node.textContent = value;
        node.hidden = false;
        node.classList.remove("d-none");
      } else {
        node.hidden = true;
        node.classList.add("d-none");
      }
    });

    var markAllWrap = document.querySelector("[data-notification-mark-all-wrap]");
    if (markAllWrap) {
      markAllWrap.hidden = value <= 0;
      markAllWrap.classList.toggle("d-none", value <= 0);
    }
  }

  function showEmptyState(list) {
    if (!list || list.querySelector("[data-notification-item]")) {
      return;
    }
    var empty = list.querySelector("[data-notification-empty]");
    if (empty) {
      empty.hidden = false;
      empty.classList.remove("d-none");
    }
  }

  function removeItem(item) {
    var list = item.closest("[data-notification-list]");
    item.classList.add("is-removing");
    window.setTimeout(function () {
      item.remove();
      showEmptyState(list);
    }, 180);
  }

  function markItemRead(item) {
    item.classList.remove("is-unread");
    var dot = item.querySelector(".notif-item__dot, .portal-notification-unread-dot");
    if (dot) {
      dot.remove();
    }
    var readBtn = item.querySelector("[data-notification-mark-read]");
    if (readBtn) {
      readBtn.remove();
    }
  }

  function initNotifications() {
    var list = document.querySelector("[data-notification-list]");
    if (!list || list.dataset.portalNotificationsBound === "true") {
      return;
    }

    list.dataset.portalNotificationsBound = "true";

    list.addEventListener("click", function (event) {
      var deleteBtn = event.target.closest("[data-notification-delete]");
      if (deleteBtn) {
        event.preventDefault();
        if (deleteBtn.disabled) {
          return;
        }
        var item = deleteBtn.closest("[data-notification-item]");
        var url = deleteBtn.getAttribute("data-delete-url");
        if (!item || !url) {
          return;
        }
        deleteBtn.disabled = true;
        removeItem(item);
        postAction(url)
          .then(function (payload) {
            if (!payload.ok || !payload.data.success) {
              throw new Error("delete failed");
            }
            updateUnreadBadges(payload.data.unread_count);
          })
          .catch(function () {
            window.location.reload();
          });
        return;
      }

      var readBtn = event.target.closest("[data-notification-mark-read]");
      if (readBtn) {
        event.preventDefault();
        if (readBtn.disabled) {
          return;
        }
        var readItem = readBtn.closest("[data-notification-item]");
        var readUrl = readBtn.getAttribute("data-mark-read-url");
        if (!readItem || !readUrl) {
          return;
        }
        readBtn.disabled = true;
        markItemRead(readItem);
        postAction(readUrl)
          .then(function (payload) {
            if (!payload.ok || !payload.data.success) {
              throw new Error("read failed");
            }
            updateUnreadBadges(payload.data.unread_count);
          })
          .catch(function () {
            window.location.reload();
          });
      }
    });

    var markAllBtn = document.querySelector("[data-notification-mark-all]");
    if (markAllBtn) {
      markAllBtn.addEventListener("click", function () {
        if (markAllBtn.disabled) {
          return;
        }
        var url = markAllBtn.getAttribute("data-mark-all-url");
        if (!url) {
          return;
        }
        markAllBtn.disabled = true;
        list.querySelectorAll("[data-notification-item].is-unread").forEach(markItemRead);
        updateUnreadBadges(0);
        postAction(url)
          .then(function (payload) {
            if (!payload.ok || !payload.data.success) {
              throw new Error("mark all failed");
            }
            updateUnreadBadges(payload.data.unread_count);
          })
          .catch(function () {
            window.location.reload();
          })
          .finally(function () {
            markAllBtn.disabled = false;
          });
      });
    }
  }

  function bootNotifications() {
    initNotifications();
  }

  if (window.portalOnReady) {
    window.portalOnReady(bootNotifications);
  } else {
    document.addEventListener("DOMContentLoaded", bootNotifications);
  }

  // AJAX nav loads this script after content swap; portal:content-loaded already fired.
  bootNotifications();
})();

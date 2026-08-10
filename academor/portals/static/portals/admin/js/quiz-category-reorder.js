/**
 * Drag-and-drop reorder for QuizCategory admin changelist.
 * Saves order via POST; portal lists sort by the same order field.
 */
(function () {
  "use strict";

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()[\]\\/+^])/g, "\\$1") + "=([^;]*)"));
    return match ? decodeURIComponent(match[1]) : "";
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var configEl = document.getElementById("quiz-category-reorder-config");
    var table = document.getElementById("result_list");
    if (!configEl || !table) {
      return;
    }
    var reorderUrl = configEl.getAttribute("data-reorder-url");
    if (!reorderUrl) {
      return;
    }
    var tbody = table.tBodies[0];
    if (!tbody) {
      return;
    }

    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
    if (rows.length < 2) {
      return;
    }

    var dragRow = null;
    var statusEl = document.getElementById("quiz-category-reorder-status");

    function setStatus(message, isError) {
      if (!statusEl) {
        return;
      }
      statusEl.textContent = message || "";
      statusEl.classList.toggle("is-error", !!isError);
      statusEl.classList.toggle("is-ok", !!message && !isError);
    }

    function rowId(row) {
      var checkbox = row.querySelector('input.action-select[name="_selected_action"]');
      return checkbox ? checkbox.value : "";
    }

    function syncOrderCells() {
      Array.prototype.forEach.call(tbody.querySelectorAll("tr"), function (row, index) {
        var cell = row.querySelector(".field-order");
        if (cell) {
          cell.textContent = String(index);
        }
      });
    }

    function collectIds() {
      return Array.prototype.map
        .call(tbody.querySelectorAll("tr"), rowId)
        .filter(Boolean);
    }

    function saveOrder() {
      var ids = collectIds();
      if (!ids.length) {
        return;
      }
      setStatus("Saving…", false);
      fetch(reorderUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ ids: ids }),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { ok: response.ok, data: data };
          });
        })
        .then(function (result) {
          if (!result.ok) {
            setStatus((result.data && result.data.error) || "Could not save order.", true);
            return;
          }
          syncOrderCells();
          setStatus("Order saved — portal will use this order.", false);
        })
        .catch(function () {
          setStatus("Could not save order.", true);
        });
    }

    rows.forEach(function (row) {
      row.classList.add("quiz-cat-sortable-row");
      row.setAttribute("draggable", "true");

      row.addEventListener("dragstart", function (event) {
        dragRow = row;
        row.classList.add("is-dragging");
        event.dataTransfer.effectAllowed = "move";
        try {
          event.dataTransfer.setData("text/plain", rowId(row));
        } catch (err) {
          /* IE / older browsers */
        }
      });

      row.addEventListener("dragend", function () {
        row.classList.remove("is-dragging");
        Array.prototype.forEach.call(tbody.querySelectorAll("tr"), function (r) {
          r.classList.remove("drag-over");
        });
        dragRow = null;
      });

      row.addEventListener("dragover", function (event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
        if (!dragRow || dragRow === row) {
          return;
        }
        row.classList.add("drag-over");
        var rect = row.getBoundingClientRect();
        var before = event.clientY < rect.top + rect.height / 2;
        if (before) {
          tbody.insertBefore(dragRow, row);
        } else {
          tbody.insertBefore(dragRow, row.nextSibling);
        }
      });

      row.addEventListener("dragleave", function () {
        row.classList.remove("drag-over");
      });

      row.addEventListener("drop", function (event) {
        event.preventDefault();
        row.classList.remove("drag-over");
        saveOrder();
      });
    });
  });
})();

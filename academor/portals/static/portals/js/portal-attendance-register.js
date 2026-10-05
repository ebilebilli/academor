(function () {
  "use strict";

  var STATUS_MARK = {
    "": "",
    present: "+",
    absent: "–",
    late: "G",
  };

  function csrfToken(root) {
    var input = root.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function applyMark(button, status) {
    button.setAttribute("data-status", status || "");
    button.textContent = STATUS_MARK[status] || "";
    button.classList.remove("is-present", "is-absent", "is-late");
    var cell = button.closest("td");
    if (cell) {
      cell.classList.remove("is-present", "is-absent", "is-late");
      if (status) {
        cell.classList.add("is-" + status);
        button.classList.add("is-" + status);
      }
    }
  }

  function csvEscape(value) {
    var text = value == null ? "" : String(value);
    if (/[",;\n]/.test(text)) {
      return '"' + text.replace(/"/g, '""') + '"';
    }
    return text;
  }

  function downloadCsv(root) {
    var table = root.querySelector("[data-register-table]");
    if (!table) {
      return;
    }
    var month = root.getAttribute("data-month") || "";
    var teacher = root.getAttribute("data-teacher") || "";
    var groupName = root.getAttribute("data-group-name") || "";
    var lines = [];
    lines.push(["Qrup", groupName].map(csvEscape).join(";"));
    lines.push(["Müəllim", teacher].map(csvEscape).join(";"));
    lines.push(["Ay", month].map(csvEscape).join(";"));
    lines.push("");

    Array.prototype.forEach.call(table.querySelectorAll("tr"), function (row) {
      if (row.getAttribute("data-register-empty-row") !== null) {
        return;
      }
      var cells = row.querySelectorAll("th, td");
      var values = Array.prototype.map.call(cells, function (cell) {
        var button = cell.querySelector("[data-register-cell]");
        if (button) {
          var status = button.getAttribute("data-status") || "";
          return STATUS_MARK[status] || "";
        }
        var nameText = cell.querySelector(".portal-register-table__name-text");
        if (nameText) {
          return nameText.innerText.replace(/\s+/g, " ").trim();
        }
        return cell.innerText.replace(/\s+/g, " ").trim();
      });
      lines.push(values.map(csvEscape).join(";"));
    });

    var blob = new Blob(["\uFEFF" + lines.join("\r\n")], {
      type: "text/csv;charset=utf-8;",
    });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    var safeGroup = (groupName || "qrup").replace(/[\\/:*?"<>|]+/g, "_");
    link.href = url;
    link.download = "davamiyyet_" + safeGroup + "_" + month + ".csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function initRegister() {
    var root = document.querySelector("[data-attendance-register]");
    if (!root || root.dataset.bound === "true") {
      return;
    }
    root.dataset.bound = "true";

    var markUrl = root.getAttribute("data-mark-url");
    var guestUrl = root.getAttribute("data-guest-url");
    var groupUrl = root.getAttribute("data-group-url");
    var pageUrl = root.getAttribute("data-page-url") || "";
    var groupId = root.getAttribute("data-group-id");
    var month = root.getAttribute("data-month") || "";
    var savedMsg = root.getAttribute("data-saved-msg") || "";
    var errorMsg = root.getAttribute("data-error-msg") || "";
    var guestAddedMsg = root.getAttribute("data-guest-added-msg") || "";
    var guestRemovedMsg = root.getAttribute("data-guest-removed-msg") || "";
    var guestEmptyMsg = root.getAttribute("data-guest-empty-msg") || "";
    var groupAddedMsg = root.getAttribute("data-group-added-msg") || "";
    var groupRemovedMsg = root.getAttribute("data-group-removed-msg") || "";
    var groupEmptyMsg = root.getAttribute("data-group-empty-msg") || "";
    var statusEl = root.querySelector("[data-register-status]");
    var exportBtn = root.querySelector("[data-register-export]");
    var addForm = root.querySelector("[data-register-add-form]");
    var addGroupForm = root.querySelector("[data-register-add-group-form]");
    var body = root.querySelector("[data-register-body]");
    var rowTemplate = root.querySelector("[data-register-row-template]");
    var mode = "present";

    function registerPageUrl(nextGroupId) {
      var params = ["tab=mark"];
      if (month) {
        params.push("month=" + encodeURIComponent(month));
      }
      if (nextGroupId) {
        params.push("group=" + encodeURIComponent(nextGroupId));
      }
      return pageUrl + "?" + params.join("&");
    }

    function setStatus(message, isError) {
      if (!statusEl) {
        return;
      }
      statusEl.textContent = message || "";
      statusEl.classList.toggle("is-error", Boolean(isError));
    }

    function syncModeButtons() {
      root.querySelectorAll("[data-register-mode]").forEach(function (button) {
        var value = button.getAttribute("data-register-mode") || "";
        var active = value === mode;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });
    }

    function updateRowCounts(row, payload) {
      var absent = row.querySelector("[data-count-absent]");
      var attended = row.querySelector("[data-count-attended]");
      if (absent) {
        absent.textContent = payload.absent == null ? absent.textContent : payload.absent;
      }
      if (attended) {
        attended.textContent = payload.attended == null ? attended.textContent : payload.attended;
      }
    }

    function renumberRows() {
      if (!body) {
        return;
      }
      Array.prototype.forEach.call(body.querySelectorAll("tr[data-student-name]"), function (row, index) {
        var num = row.querySelector("[data-row-num]");
        if (num) {
          num.textContent = String(index + 1);
        }
      });
    }

    function removeEmptyRow() {
      if (!body) {
        return;
      }
      var empty = body.querySelector("[data-register-empty-row]");
      if (empty) {
        empty.remove();
      }
      var scroll = root.querySelector(".portal-register__scroll");
      if (scroll) {
        scroll.classList.remove("is-empty");
      }
    }

    function jsonFetch(url, options) {
      return fetch(url, options).then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok && data && data.ok, data: data, status: response.status };
        });
      });
    }

    function saveCell(button, nextStatus) {
      var row = button.closest("tr");
      var studentId = row && row.getAttribute("data-student-id");
      var guestId = row && row.getAttribute("data-guest-id");
      var iso = button.getAttribute("data-date");
      var previous = button.getAttribute("data-status") || "";
      var next = previous === nextStatus ? "" : nextStatus;
      applyMark(button, next);
      button.classList.add("is-pending");
      setStatus(savedMsg, false);

      var payload = {
        group_id: groupId,
        date: iso,
        status: next,
      };
      if (guestId) {
        payload.guest_id = guestId;
      } else {
        payload.student_id = studentId;
      }

      jsonFetch(markUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-CSRFToken": csrfToken(root),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(payload),
      })
        .then(function (result) {
          if (!result.ok) {
            throw new Error("save-failed");
          }
          applyMark(button, result.data.status || "");
          if (row) {
            updateRowCounts(row, result.data);
          }
          setStatus(savedMsg, false);
        })
        .catch(function () {
          applyMark(button, previous);
          setStatus(errorMsg, true);
        })
        .then(function () {
          button.classList.remove("is-pending");
        });
    }

    function appendGuestRow(guest) {
      if (!body || !rowTemplate) {
        window.location.reload();
        return;
      }
      removeEmptyRow();
      var node = rowTemplate.content.firstElementChild.cloneNode(true);
      node.setAttribute("data-guest-id", String(guest.id));
      node.setAttribute("data-student-id", "");
      node.setAttribute("data-student-name", guest.name);
      var nameText = node.querySelector(".portal-register-table__name-text");
      if (nameText) {
        nameText.textContent = guest.name;
      }
      node.querySelectorAll("[data-register-cell]").forEach(function (button) {
        button.setAttribute("aria-label", guest.name + ", " + (button.getAttribute("data-date") || ""));
      });
      body.appendChild(node);
      renumberRows();
    }

    root.addEventListener("click", function (event) {
      var modeBtn = event.target.closest("[data-register-mode]");
      if (modeBtn && root.contains(modeBtn)) {
        mode = modeBtn.getAttribute("data-register-mode") || "";
        syncModeButtons();
        return;
      }

      var removeGroupBtn = event.target.closest("[data-register-remove-group]");
      if (removeGroupBtn && root.contains(removeGroupBtn)) {
        event.preventDefault();
        var removeGroupId = removeGroupBtn.getAttribute("data-group-id");
        if (!removeGroupId || !groupUrl) {
          return;
        }
        jsonFetch(groupUrl, {
          method: "DELETE",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": csrfToken(root),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ group_id: removeGroupId }),
        })
          .then(function (result) {
            if (!result.ok) {
              throw new Error("remove-group-failed");
            }
            setStatus(groupRemovedMsg, false);
            var fallbackId = groupId === removeGroupId ? "" : groupId;
            window.location.href = registerPageUrl(fallbackId);
          })
          .catch(function () {
            setStatus(errorMsg, true);
          });
        return;
      }

      var removeBtn = event.target.closest("[data-register-remove-guest]");
      if (removeBtn && root.contains(removeBtn)) {
        event.preventDefault();
        var row = removeBtn.closest("tr");
        var guestId = row && row.getAttribute("data-guest-id");
        if (!guestId || !guestUrl) {
          return;
        }
        jsonFetch(guestUrl, {
          method: "DELETE",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": csrfToken(root),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ group_id: groupId, guest_id: guestId }),
        })
          .then(function (result) {
            if (!result.ok) {
              throw new Error("remove-failed");
            }
            if (row) {
              row.remove();
            }
            renumberRows();
            setStatus(guestRemovedMsg, false);
          })
          .catch(function () {
            setStatus(errorMsg, true);
          });
        return;
      }

      var button = event.target.closest("[data-register-cell]");
      if (!button || !root.contains(button) || button.classList.contains("is-pending")) {
        return;
      }
      event.preventDefault();
      var chosen = event.shiftKey ? "late" : mode;
      saveCell(button, chosen);
    });

    root.addEventListener("contextmenu", function (event) {
      var button = event.target.closest("[data-register-cell]");
      if (!button || !root.contains(button) || button.classList.contains("is-pending")) {
        return;
      }
      event.preventDefault();
      saveCell(button, "absent");
    });

    if (addGroupForm) {
      addGroupForm.addEventListener("submit", function (event) {
        event.preventDefault();
        var input = addGroupForm.querySelector("[name=group_name]");
        var name = input ? String(input.value || "").trim() : "";
        if (!name) {
          setStatus(groupEmptyMsg, true);
          if (input) {
            input.focus();
          }
          return;
        }
        jsonFetch(groupUrl, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": csrfToken(root),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ name: name }),
        })
          .then(function (result) {
            if (!result.ok) {
              throw new Error("add-group-failed");
            }
            setStatus(groupAddedMsg, false);
            window.location.href = registerPageUrl(result.data.group.id);
          })
          .catch(function () {
            setStatus(errorMsg, true);
          });
      });
    }

    if (addForm) {
      addForm.addEventListener("submit", function (event) {
        event.preventDefault();
        var input = addForm.querySelector("[name=guest_name]");
        var name = input ? String(input.value || "").trim() : "";
        if (!name) {
          setStatus(guestEmptyMsg, true);
          if (input) {
            input.focus();
          }
          return;
        }
        jsonFetch(guestUrl, {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": csrfToken(root),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ group_id: groupId, name: name }),
        })
          .then(function (result) {
            if (!result.ok) {
              throw new Error("add-failed");
            }
            if (input) {
              input.value = "";
              input.focus();
            }
            appendGuestRow(result.data.guest);
            setStatus(guestAddedMsg, false);
          })
          .catch(function () {
            setStatus(errorMsg, true);
          });
      });
    }

    if (exportBtn) {
      exportBtn.addEventListener("click", function () {
        downloadCsv(root);
      });
    }

    syncModeButtons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRegister);
  } else {
    initRegister();
  }
})();

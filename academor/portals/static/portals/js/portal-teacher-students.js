(function () {
  "use strict";

  function getCsrfToken() {
    var input = document.querySelector("[name=csrfmiddlewaretoken]");
    if (input && input.value) {
      return input.value;
    }
    var match = document.cookie.match(/(^|;)\s*csrftoken\s*=\s*([^;]+)/);
    return match ? decodeURIComponent(match.pop()) : "";
  }

  function renderGroupChips(cell, names, emptyLabel) {
    cell.textContent = "";
    if (!names.length) {
      var empty = document.createElement("span");
      empty.className = "text-muted small";
      empty.textContent = emptyLabel;
      cell.appendChild(empty);
      return;
    }
    names.forEach(function (name) {
      var chip = document.createElement("span");
      chip.className = "portal-students__chip portal-students__chip--group";
      chip.textContent = name;
      cell.appendChild(chip);
    });
  }

  function bindGroupMenu(menu, emptyLabel) {
    if (menu.dataset.bound === "true") {
      return;
    }
    menu.dataset.bound = "true";
    var row = menu.closest("[data-student-row]");
    var cell = row ? row.querySelector("[data-student-groups-cell]") : null;
    var boxes = Array.prototype.slice.call(menu.querySelectorAll("input[type=checkbox]"));
    var pick = menu.querySelector("[data-pick]");

    function syncPick() {
      if (pick && window.PortalPick) {
        window.PortalPick.sync(pick);
      }
    }
    boxes.forEach(function (box) {
      box.addEventListener("change", function () {
        var previous = boxes.map(function (item) {
          return item === box ? !item.checked : item.checked;
        });
        boxes.forEach(function (item) {
          item.disabled = true;
        });
        fetch(menu.getAttribute("data-url"), {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({
            group_ids: boxes.filter(function (item) { return item.checked; }).map(function (item) { return item.value; }),
          }),
        })
          .then(function (response) {
            return response.json().then(function (data) {
              if (!response.ok || !data.ok) {
                throw new Error("failed");
              }
              return data;
            });
          })
          .then(function (data) {
            var active = {};
            (data.group_ids || []).forEach(function (id) {
              active[String(id)] = true;
            });
            var names = [];
            boxes.forEach(function (item) {
              item.checked = !!active[item.value];
              if (item.checked) {
                names.push(item.getAttribute("data-group-name"));
              }
            });
            if (cell) {
              renderGroupChips(cell, names, emptyLabel);
            }
            syncPick();
          })
          .catch(function () {
            boxes.forEach(function (item, index) {
              item.checked = previous[index];
            });
            syncPick();
          })
          .finally(function () {
            boxes.forEach(function (item) {
              item.disabled = false;
            });
          });
      });
    });
  }

  function init() {
    var root = document.querySelector("[data-teacher-students]");
    if (!root) {
      return;
    }
    var emptyLabel = root.getAttribute("data-label-no-group") || "—";
    root.querySelectorAll("[data-student-groups]").forEach(function (menu) {
      bindGroupMenu(menu, emptyLabel);
    });

    var search = root.querySelector("[data-students-search]");
    if (search && search.dataset.bound !== "true") {
      search.dataset.bound = "true";
      var rows = Array.prototype.slice.call(root.querySelectorAll("[data-student-row]"));
      var noMatch = root.querySelector("[data-students-no-match]");
      search.addEventListener("input", function () {
        var term = search.value.trim().toLowerCase();
        var shown = 0;
        rows.forEach(function (row) {
          var match = !term || (row.getAttribute("data-student-name") || "").indexOf(term) !== -1;
          row.hidden = !match;
          if (match) {
            shown += 1;
          }
        });
        if (noMatch) {
          noMatch.classList.toggle("d-none", shown > 0);
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  document.addEventListener("portal:content-loaded", init);
})();

/* Multi-select pick lists (templates/portals/includes/pick_list.html):
   search, "N selected", select all (visible) / clear, and the checked-row class for
   browsers without :has(). Re-runs after portal AJAX navigation. */
(function () {
  "use strict";

  function options(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-pick-option]"));
  }

  function inputOf(option) {
    return option.querySelector('input[type="checkbox"]');
  }

  function sync(root) {
    var selected = 0;
    options(root).forEach(function (option) {
      var input = inputOf(option);
      var checked = !!(input && input.checked);
      option.classList.toggle("is-checked", checked);
      if (checked) {
        selected += 1;
      }
    });
    var count = root.querySelector("[data-pick-count]");
    if (count) {
      count.textContent = selected + " " + (count.getAttribute("data-suffix") || "");
      count.classList.toggle("has-selection", selected > 0);
    }
  }

  function filter(root, term) {
    var query = (term || "").trim().toLowerCase();
    var shown = 0;
    options(root).forEach(function (option) {
      var input = inputOf(option);
      var match = !query || option.textContent.toLowerCase().indexOf(query) !== -1;
      // ticked options always stay in view, so a search never hides a choice
      var visible = match || !!(input && input.checked);
      option.hidden = !visible;
      if (visible) {
        shown += 1;
      }
    });
    root.querySelectorAll("[data-pick-group]").forEach(function (group) {
      group.hidden = !group.querySelector("[data-pick-option]:not([hidden])");
    });
    var none = root.querySelector("[data-pick-no-match]");
    if (none) {
      none.hidden = shown > 0;
    }
  }

  function setAll(root, checked) {
    options(root).forEach(function (option) {
      var input = inputOf(option);
      if (!input || input.disabled || option.hidden) {
        return;
      }
      if (input.checked !== checked) {
        input.checked = checked;
        input.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
    sync(root);
  }

  function bind(root) {
    if (root.dataset.pickBound === "true") {
      return;
    }
    root.dataset.pickBound = "true";
    root.addEventListener("change", function (event) {
      if (event.target && event.target.type === "checkbox") {
        sync(root);
      }
    });
    var search = root.querySelector("[data-pick-search]");
    if (search) {
      search.addEventListener("input", function () {
        filter(root, search.value);
      });
      // Enter in the search box must not submit the surrounding form
      search.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
        }
      });
    }
    var all = root.querySelector("[data-pick-all]");
    if (all) {
      all.addEventListener("click", function () {
        setAll(root, true);
      });
    }
    var clear = root.querySelector("[data-pick-clear]");
    if (clear) {
      clear.addEventListener("click", function () {
        var hidden = options(root).filter(function (option) {
          return option.hidden;
        });
        hidden.forEach(function (option) {
          option.hidden = false;
        });
        setAll(root, false);
        if (search) {
          filter(root, search.value);
        }
      });
    }
    sync(root);
  }

  function init() {
    document.querySelectorAll("[data-pick]").forEach(bind);
  }

  window.PortalPick = { init: init, sync: sync };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  document.addEventListener("portal:content-loaded", init);
})();

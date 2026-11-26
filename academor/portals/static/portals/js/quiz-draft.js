/* Keeps a running quiz's answers across a page reload (F5).
   Answers are stored in sessionStorage (this browser tab only) under the attempt key the
   start gate gets from the server, restored once the quiz starts again, and removed when
   the quiz is finished. Plain form fields only: radios, checkboxes, text, textareas, selects. */
(function () {
  "use strict";

  var ROOT_SELECTOR = "[data-quiz-take], [data-quiz-manual-take], [data-quiz-reading-take]";
  var PREFIX = "academor-quiz-draft:";

  function storage() {
    try {
      var s = window.sessionStorage;
      s.setItem(PREFIX + "probe", "1");
      s.removeItem(PREFIX + "probe");
      return s;
    } catch (e) {
      return null;
    }
  }

  function fields(root) {
    return Array.prototype.filter.call(
      root.querySelectorAll("input[name], textarea[name], select[name]"),
      function (el) {
        var type = (el.type || "").toLowerCase();
        return !el.disabled && type !== "hidden" && type !== "file" && type !== "submit" && type !== "button"
          && el.name !== "csrfmiddlewaretoken";
      }
    );
  }

  function collect(root) {
    var data = {};
    fields(root).forEach(function (el) {
      var type = (el.type || "").toLowerCase();
      if (type === "radio") {
        if (el.checked) {
          data[el.name] = el.value;
        }
      } else if (type === "checkbox") {
        var list = data[el.name] || [];
        if (el.checked) {
          list.push(el.value);
        }
        data[el.name] = list;
      } else if (el.value) {
        data[el.name] = el.value;
      }
    });
    return data;
  }

  function fire(el) {
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function restore(root, data) {
    fields(root).forEach(function (el) {
      if (!Object.prototype.hasOwnProperty.call(data, el.name)) {
        return;
      }
      var saved = data[el.name];
      var type = (el.type || "").toLowerCase();
      if (type === "radio") {
        if (el.value === saved && !el.checked) {
          el.checked = true;
          fire(el);
        }
      } else if (type === "checkbox") {
        var on = Array.isArray(saved) && saved.indexOf(el.value) !== -1;
        if (on !== el.checked) {
          el.checked = on;
          fire(el);
        }
      } else if (typeof saved === "string" && el.value !== saved) {
        el.value = saved;
        fire(el);
      }
    });
  }

  function init() {
    var root = document.querySelector(ROOT_SELECTOR);
    var store = storage();
    if (!root || !store || root.dataset.quizDraftBound === "true") {
      return;
    }
    root.dataset.quizDraftBound = "true";

    function key() {
      var attempt = root.getAttribute("data-quiz-attempt-key") || "";
      return attempt ? PREFIX + window.location.pathname + ":" + attempt : "";
    }

    var restoring = false;

    function save() {
      var k = key();
      if (!k || restoring || root.getAttribute("data-quiz-finished") === "true") {
        return;
      }
      try {
        store.setItem(k, JSON.stringify(collect(root)));
      } catch (e) {
        // storage full or blocked: the quiz still works, only the draft is not kept
      }
    }

    function start() {
      var k = key();
      if (!k) {
        return;
      }
      // after the take scripts have set up their listeners, so counters and navigation update
      window.setTimeout(function () {
        var raw = null;
        try {
          raw = store.getItem(k);
        } catch (e) {
          raw = null;
        }
        if (!raw) {
          return;
        }
        try {
          restoring = true;
          restore(root, JSON.parse(raw) || {});
        } catch (e) {
          // a broken draft is ignored
        } finally {
          restoring = false;
        }
      }, 60);
    }

    root.addEventListener("input", save, true);
    root.addEventListener("change", save, true);

    // forget the draft once the quiz is submitted
    new MutationObserver(function () {
      if (root.getAttribute("data-quiz-finished") === "true") {
        var k = key();
        try {
          if (k) {
            store.removeItem(k);
          }
        } catch (e) {
          // ignore
        }
      }
    }).observe(root, { attributes: true, attributeFilter: ["data-quiz-finished"] });

    if (root.getAttribute("data-quiz-started") === "true") {
      start();
    } else {
      document.addEventListener("portal-quiz-started", start, { once: true });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

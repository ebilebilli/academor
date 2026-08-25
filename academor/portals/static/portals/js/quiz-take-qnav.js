(function () {
  "use strict";

  function isAnswered(card) {
    if (!card) {
      return false;
    }

    var spr = card.querySelector("[data-quiz-spr-input]");
    if (spr) {
      return spr.value.trim() !== "";
    }

    var dropdown = card.querySelector("[data-quiz-dropdown]");
    if (dropdown) {
      return dropdown.value !== "";
    }

    if (card.querySelector(".portal-quiz-play-option__input:checked, input[type='radio']:checked")) {
      return true;
    }

    var fields = card.querySelectorAll(
      "textarea[name^='quiz-q-'], input[type='text'][name^='quiz-q-'], textarea[name^='listening-q-'], input[type='text'][name^='listening-q-'], textarea[name^='reading-q-'], input[type='text'][name^='reading-q-'], textarea[data-writing-answer], input[data-writing-answer], [data-manual-submission], [data-reading-answer]"
    );
    for (var i = 0; i < fields.length; i += 1) {
      var field = fields[i];
      if (field.type === "radio" || field.type === "checkbox") {
        if (field.checked) {
          return true;
        }
        continue;
      }
      if (String(field.value || "").trim() !== "") {
        return true;
      }
    }

    return false;
  }

  function cardForTarget(id) {
    var el = document.getElementById(id);
    if (!el) {
      return null;
    }
    if (el.matches("[data-quiz-question-card], [data-quiz-writing-card], [data-listening-task]")) {
      return el;
    }
    return el.closest("[data-quiz-question-card], [data-quiz-writing-card], [data-listening-task]") || el;
  }

  function activateReadingSection(sectionNumber) {
    if (!sectionNumber) {
      return;
    }
    var tabBtn = document.getElementById("reading-tab-" + sectionNumber);
    if (!tabBtn || tabBtn.classList.contains("active")) {
      return;
    }
    if (typeof bootstrap !== "undefined" && bootstrap.Tab) {
      bootstrap.Tab.getOrCreateInstance(tabBtn).show();
      return;
    }
    tabBtn.click();
  }

  function topOffset(root) {
    var offset = 12;
    var topbar = document.querySelector(".admin-navbar");
    if (topbar) {
      var styles = window.getComputedStyle(topbar);
      if (styles.position === "fixed" || styles.position === "sticky") {
        offset += Math.ceil(topbar.getBoundingClientRect().height);
      }
    }
    var timer = (root || document).querySelector(".portal-quiz-take-toolbar--timed:not(.is-hidden)");
    if (timer) {
      offset += Math.ceil(timer.getBoundingClientRect().height);
    }
    return offset;
  }

  function syncScrollMargin(root) {
    document.documentElement.style.setProperty("--quiz-qnav-offset", topOffset(root) + 8 + "px");
  }

  function initQuizQnav(wrap) {
    var root =
      wrap.closest("[data-quiz-take], [data-quiz-reading-take], [data-quiz-manual-take], .portal-quiz-take") ||
      document;
    var toggle = wrap.querySelector("[data-quiz-qnav-toggle]");
    var panel = wrap.querySelector("[data-quiz-qnav-panel]");
    var closeBtn = wrap.querySelector("[data-quiz-qnav-close]");
    var nav = wrap.querySelector("[data-quiz-qnav-nav]");
    if (!toggle || !panel || !nav) {
      return;
    }

    function setOpen(open) {
      wrap.classList.toggle("is-open", open);
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        syncAnswered();
        syncScrollMargin(root);
      }
    }

    function syncAnswered() {
      nav.querySelectorAll("[data-quiz-qnav-target]").forEach(function (btn) {
        var id = btn.getAttribute("data-quiz-qnav-target");
        var card = cardForTarget(id);
        var answered = isAnswered(card);
        btn.classList.toggle("is-answered", answered);
        btn.classList.toggle("is-unanswered", !answered);
      });
    }

    function scrollToQuestion(id, sectionNumber) {
      activateReadingSection(sectionNumber);
      syncScrollMargin(root);

      window.setTimeout(function () {
        var target = document.getElementById(id);
        if (!target) {
          return;
        }
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        target.classList.add("is-qnav-flash");
        window.setTimeout(function () {
          target.classList.remove("is-qnav-flash");
        }, 900);
      }, sectionNumber ? 80 : 0);
    }

    toggle.addEventListener("click", function () {
      setOpen(panel.hidden);
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        setOpen(false);
      });
    }

    nav.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-quiz-qnav-target]");
      if (!btn || !nav.contains(btn)) {
        return;
      }
      var id = btn.getAttribute("data-quiz-qnav-target");
      if (!id) {
        return;
      }
      scrollToQuestion(id, btn.getAttribute("data-quiz-qnav-section"));
    });

    document.addEventListener("click", function (event) {
      if (!wrap.classList.contains("is-open")) {
        return;
      }
      if (wrap.contains(event.target)) {
        return;
      }
      setOpen(false);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && wrap.classList.contains("is-open")) {
        setOpen(false);
      }
    });

    root.addEventListener("change", syncAnswered);
    root.addEventListener("input", syncAnswered);

    syncAnswered();
    syncScrollMargin(root);
    window.addEventListener("resize", function () {
      syncScrollMargin(root);
    }, { passive: true });
  }

  document.querySelectorAll("[data-quiz-qnav]").forEach(initQuizQnav);
})();

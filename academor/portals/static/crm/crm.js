/* Academor CRM: mobile menu, toasts, tabs, searchable selects and the leads board. */
(function () {
  "use strict";

  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function csrf() {
    var m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  /* mobile menu */
  qsa("[data-crm-open]").forEach(function (b) { b.addEventListener("click", function () { document.body.classList.add("crm-menu-open"); }); });
  qsa("[data-crm-close]").forEach(function (b) { b.addEventListener("click", function () { document.body.classList.remove("crm-menu-open"); }); });

  /* toasts fade out on their own */
  qsa(".crm-toast").forEach(function (t, i) {
    var close = function () { t.style.transition = "opacity .3s, transform .3s"; t.style.opacity = "0"; t.style.transform = "translateY(-6px)"; setTimeout(function () { t.remove(); }, 320); };
    var btn = t.querySelector("[data-crm-dismiss]");
    if (btn) btn.addEventListener("click", close);
    setTimeout(close, 5200 + i * 600);
  });

  /* tabs: <div data-crm-tabs> buttons[data-tab] + [data-tabpanel] */
  qsa("[data-crm-tabs]").forEach(function (box) {
    var buttons = qsa("[data-tab]", box);
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        buttons.forEach(function (x) { x.classList.toggle("is-active", x === b); });
        qsa("[data-tabpanel]", box).forEach(function (p) { p.hidden = p.getAttribute("data-tabpanel") !== b.getAttribute("data-tab"); });
      });
    });
  });

  /* searchable <select>: a filter box above long student lists */
  qsa("select[data-crm-search]").forEach(function (sel) {
    var input = document.createElement("input");
    input.type = "search";
    input.className = "crm-input";
    input.placeholder = "Axtar…";
    input.style.marginBottom = "6px";
    sel.parentNode.insertBefore(input, sel);
    var all = qsa("option", sel).map(function (o) { return { o: o, t: o.textContent.toLowerCase() }; });
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var first = null;
      all.forEach(function (x) {
        var show = !q || !x.o.value || x.t.indexOf(q) !== -1;
        x.o.hidden = !show;
        if (show && x.o.value && !first) first = x.o;
      });
      if (q && first && sel.value !== first.value) {
        sel.value = first.value;
        sel.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
  });

  /* leads board: drag a card to another column to change its status */
  var board = document.querySelector("[data-crm-board]");
  if (board) {
    var dragged = null;
    qsa(".crm-lead[draggable]", board).forEach(function (card) {
      card.addEventListener("dragstart", function (e) {
        dragged = card;
        card.classList.add("is-dragging");
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", card.getAttribute("data-id"));
      });
      card.addEventListener("dragend", function () { card.classList.remove("is-dragging"); dragged = null; });
    });
    qsa("[data-status-col]", board).forEach(function (col) {
      var drop = col.querySelector(".crm-col__cards");
      col.addEventListener("dragover", function (e) { e.preventDefault(); col.classList.add("is-over"); });
      col.addEventListener("dragleave", function (e) { if (!col.contains(e.relatedTarget)) col.classList.remove("is-over"); });
      col.addEventListener("drop", function (e) {
        e.preventDefault();
        col.classList.remove("is-over");
        if (!dragged) return;
        var from = dragged.closest("[data-status-col]");
        if (from === col) return;
        var card = dragged;
        drop.insertBefore(card, drop.firstChild);
        recount();
        fetch(card.getAttribute("data-move-url"), {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },
          body: JSON.stringify({ status: col.getAttribute("data-status-col") }),
          credentials: "same-origin"
        }).then(function (r) { if (!r.ok) throw new Error("move failed"); return r.json(); })
          .then(function (data) {
            // "Qeydiyyatdan keçdi": open the form that turns the lead into a student
            if (data && data.redirect) window.location.href = data.redirect;
          })
          .catch(function () {
            from.querySelector(".crm-col__cards").insertBefore(card, from.querySelector(".crm-col__cards").firstChild);
            recount();
            alert("Status dəyişmədi, yenidən cəhd edin.");
          });
      });
    });
    var recount = function () {
      qsa("[data-status-col]", board).forEach(function (col) {
        var c = col.querySelector(".crm-col__count");
        if (c) c.textContent = col.querySelectorAll(".crm-lead").length;
      });
    };
  }
})();

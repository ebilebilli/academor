(function () {
    "use strict";

    // Long descriptions scroll inside their box. On wide screens the box grows so the text ends
    // level with the poster (and the buttons under it) on the right; it never gets smaller than this.
    var MIN_PX = 352;
    var desktop = window.matchMedia("(min-width: 992px)");

    // page position without CSS transforms (the fade-in animations move blocks while they run)
    function docTop(el) {
        var y = 0;
        while (el) {
            y += el.offsetTop;
            el = el.offsetParent;
        }
        return y;
    }

    function asideBottom() {
        var col = document.querySelector(".course-detail-layout__aside");
        var card = col && col.querySelector(".course-detail-aside__card");
        if (!col || !card) return null;
        // measured from the column, not the sticky card, so scrolling does not change it
        var aside = card.parentElement;
        var offset = aside && aside !== col ? parseFloat(getComputedStyle(aside).marginTop) || 0 : 0;
        return docTop(col) + offset + card.offsetHeight;
    }

    function fit(wrap) {
        var inner = wrap.querySelector(".course-detail-prose-wrap__inner");
        if (!inner || inner.offsetParent === null) return; // hidden tab: measure when shown
        var limit = MIN_PX;
        var bottom = desktop.matches ? asideBottom() : null;
        if (bottom) {
            var panel = wrap.closest(".course-detail-tab-panels");
            var cs = panel ? getComputedStyle(panel) : null;
            var pad = cs ? (parseFloat(cs.paddingBottom) || 0) + (parseFloat(cs.borderBottomWidth) || 0) : 0;
            var top = docTop(inner);
            limit = Math.max(MIN_PX, Math.round(bottom - top - pad));
        }
        wrap.style.setProperty("--prose-max", limit + "px");
        wrap.classList.toggle("is-scrollable", inner.scrollHeight > limit + 24);
    }

    function fitAll() {
        document.querySelectorAll("[data-prose-scroll]").forEach(fit);
    }

    var timer = null;
    function later() {
        clearTimeout(timer);
        timer = setTimeout(fitAll, 120);
    }

    document.addEventListener("DOMContentLoaded", function () {
        fitAll();
        var img = document.querySelector(".course-detail-gallery__img");
        if (img && !img.complete) img.addEventListener("load", fitAll, { once: true });
        document.addEventListener("shown.bs.tab", fitAll);
        if (desktop.addEventListener) desktop.addEventListener("change", fitAll);
    });
    window.addEventListener("load", fitAll);
    window.addEventListener("resize", later, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);
})();

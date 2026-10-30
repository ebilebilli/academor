/* Homepage scroll reveals, one light signature per section (see home-motion.css).

   Kept cheap on purpose: parts animate opacity + transform only (compositor work, no
   repaint), the observer does all DOM writes inside one animation frame, and nothing runs
   while the page is just scrolling.

   How it plays with scroll-reveal.js
   - The hero stays with scroll-reveal.js (its "settled" event drives the tagline).
   - For the sections below the hero, this file takes the reveal over: it strips the
     scroll-reveal classes before the reveal engine starts, animates the parts itself, and
     once a part has settled it gives the scroll-reveal "revealed" classes back, so hover
     rules that key off them keep working.
   - Carousels reveal as one shell; only the slides on screen at that moment get the inner
     stagger, so off-screen slides are never left hidden.
   Reduced motion: nothing is hidden or moved. */
(function () {
    "use strict";

    var main = document.querySelector(".home-page-main");
    if (!main || !window.matchMedia) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (!("IntersectionObserver" in window)) return;

    /* sel: section; parts: [selector, role] — role names the motion in home-motion.css */
    var SECTIONS = [
        { sel: ".about-intro-section--home", sig: "about", parts: [
            [".about-intro-image-card", "media"],
            [".row > div:last-child > *", "text"]
        ] },
        { sel: ".home-sales-section", sig: "offers", parts: [
            [".home-sales-section__eyebrow", "text"],
            [".home-sales-section__title", "title"],
            [".discount-banner", "item"]
        ] },
        { sel: ".hsvc-section", sig: "services", parts: [
            [".hsvc-header > div > *", "title"],
            [".hsvc-header > a", "text"],
            [".hsvc-card-wrap", "item"]
        ] },
        { sel: ".home-prices-section", sig: "prices", parts: [
            [".home-prices-section__title", "title"],
            [".home-prices-carousel-wrap", "carousel"]
        ] },
        { sel: ".home-mock-prices-section", sig: "prices", parts: [
            [".home-mock-prices-section__eyebrow", "text"],
            [".home-mock-prices-section__title", "title"],
            [".home-mock-prices-grid > *", "item"]
        ] },
        { sel: ".home-abroad-band", sig: "abroad", parts: [
            [".abroad-hero__card", "media"],
            [".abroad-advantages__title", "title"],
            [".abroad-advantages__item", "pop"],
            [".abroad-card", "item"]
        ] },
        { sel: ".home-team-section", sig: "team", parts: [
            [".home-team-section__title", "title"],
            [".courses-alt__carousel-shell", "carousel"],
            [".home-team-grid .course-alt-card", "item"],
            [".index-team-see-all-wrap", "text"]
        ] },
        { sel: ".reviews-testimonials-section--home", sig: "reviews", parts: [
            [".reviews-home__eyebrow", "text"],
            [".reviews-home__title", "title"],
            [".testimonial-carousel-shell", "carousel"],
            [".reviews-home-cta", "text"]
        ] },
        { sel: ".home-faq", sig: "faq", parts: [
            [".home-faq__title", "title"],
            [".home-faq__accordion > .accordion-item", "item"]
        ] }
    ];

    var REVEAL_CLASSES = [
        "scroll-reveal", "reveal", "reveal--up", "reveal--down", "reveal--left", "reveal--right",
        "reveal--fade", "reveal--scale", "wow", "animated", "fadeInUp", "fadeInDown", "fadeIn",
        "fadeInLeft", "fadeInRight", "is-revealed", "is-visible"
    ];

    function qsa(sel, scope) {
        return Array.prototype.slice.call((scope || document).querySelectorAll(sel));
    }

    function cssMs(name, fallback) {
        var raw = window.getComputedStyle(document.body).getPropertyValue(name).trim();
        var n = parseFloat(raw);
        if (!raw || isNaN(n)) return fallback;
        return raw.slice(-2) === "ms" ? n : raw.slice(-1) === "s" ? n * 1000 : n;
    }

    /* ---------------------------------------------------------------- setup */
    var parts = [];

    function stripReveal(el) {
        var had = el.classList.contains("scroll-reveal") || el.classList.contains("wow") || el.classList.contains("reveal");
        REVEAL_CLASSES.forEach(function (c) { el.classList.remove(c); });
        el.style.removeProperty("--reveal-delay");
        el.style.opacity = "";
        el.style.animationDelay = "";
        if (had) el.setAttribute("data-hm-had-reveal", "");
    }

    function claimSections() {
        SECTIONS.forEach(function (def) {
            qsa(def.sel, main).forEach(function (section) {
                if (section.hasAttribute("data-hm")) return;
                section.setAttribute("data-hm", def.sig);
                /* the reveal engine must not animate anything in here (or the section itself) */
                stripReveal(section);
                qsa(".scroll-reveal, .wow, .reveal", section).forEach(stripReveal);
                def.parts.forEach(function (pair) {
                    qsa(pair[0], section).forEach(function (el) {
                        if (el.classList.contains("hm-part")) return;
                        el.classList.add("hm-part");
                        el.setAttribute("data-hm-role", pair[1]);
                        parts.push(el);
                    });
                });
            });
        });
    }

    /* ---------------------------------------------------------------- reveal */
    var STAGGER = 60;
    var STAGGER_MAX = 6;
    var DURATION = 600;
    var observer = null;
    var started = false;
    var pending = [];
    var done = [];
    var frameQueued = false;

    function release(el) {
        /* hand the element back: plain revealed state + the classes hover rules expect */
        el.classList.remove("hm-part", "hm-in");
        el.removeAttribute("data-hm-role");
        el.style.removeProperty("--hm-delay");
        if (el.hasAttribute("data-hm-had-reveal")) {
            el.classList.add("scroll-reveal", "is-revealed", "is-visible");
        }
        qsa(".hm-sub", el).forEach(function (sub) {
            sub.classList.remove("hm-sub", "hm-in");
            sub.style.removeProperty("--hm-delay");
        });
    }

    function markCarouselSlides(shell, baseDelay) {
        /* only the slides on screen now: the rest are off to the side, behind overflow */
        var vw = window.innerWidth;
        var k = 0;
        qsa(".swiper-slide", shell).forEach(function (slide) {
            var r = slide.getBoundingClientRect();
            if (r.right <= 0 || r.left >= vw || r.width === 0) return;
            slide.classList.add("hm-sub");
            slide.style.setProperty("--hm-delay", (baseDelay + Math.min(k + 1, STAGGER_MAX) * STAGGER) + "ms");
            k += 1;
        });
        return k;
    }

    function flush() {
        frameQueued = false;

        /* settled parts first: one batch of class changes */
        if (done.length) {
            var now = performance.now();
            done = done.filter(function (item) {
                if (item.at > now) return true;
                release(item.el);
                return false;
            });
        }

        if (!pending.length) {
            if (done.length) queueFrame();
            return;
        }
        var batch = pending;
        pending = [];
        /* reading order: whatever arrives together is staggered top-to-bottom */
        batch.sort(function (a, b) {
            return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
        });

        /* reads (slide rects) before writes */
        var k = 0;
        var lastSection = null;
        var plan = batch.map(function (el) {
            var section = el.closest("[data-hm]");
            if (section !== lastSection) {
                k = 0;
                lastSection = section;
            }
            var delay = Math.min(k, STAGGER_MAX) * STAGGER;
            k += 1;
            var slides = el.getAttribute("data-hm-role") === "carousel" ? markCarouselSlides(el, delay) : 0;
            return { el: el, delay: delay, slides: slides };
        });

        plan.forEach(function (item) {
            item.el.style.setProperty("--hm-delay", item.delay + "ms");
        });
        /* next frame: the hidden state (and any new .hm-sub) has been styled, now flip it */
        requestAnimationFrame(function () {
            var now = performance.now();
            plan.forEach(function (item) {
                item.el.classList.add("hm-in");
                qsa(".hm-sub", item.el).forEach(function (sub) { sub.classList.add("hm-in"); });
                var tail = item.slides ? (Math.min(item.slides, STAGGER_MAX) + 1) * STAGGER : 0;
                done.push({ el: item.el, at: now + item.delay + tail + DURATION + 150 });
            });
            queueFrame();
        });
    }

    function queueFrame() {
        if (frameQueued) return;
        frameQueued = true;
        /* release settled parts lazily, never more often than every ~300ms */
        window.setTimeout(function () { requestAnimationFrame(flush); }, pending.length ? 0 : 300);
    }

    function start() {
        if (started) return;
        started = true;
        if (!parts.length) return;
        STAGGER = cssMs("--hm-stagger", STAGGER);
        DURATION = cssMs("--hm-duration", DURATION);
        observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                observer.unobserve(entry.target);
                pending.push(entry.target);
            });
            if (pending.length) {
                frameQueued = false;
                queueFrame();
            }
        }, { threshold: 0, rootMargin: "0px 0px -6% 0px" });
        parts.forEach(function (el) { observer.observe(el); });
    }

    /* ---------------------------------------------------------------- boot */
    document.documentElement.classList.add("hm-ready");
    claimSections();

    document.addEventListener("academor:page-ready", function () {
        requestAnimationFrame(start);
    });
    window.addEventListener("load", function () {
        /* page-ready normally fires first (spinner hidden); this is the fallback */
        window.setTimeout(start, 600);
    });
    /* safety net: never leave sections hidden */
    window.setTimeout(start, 6000);
})();

/* Homepage scroll choreography.

   Every homepage section gets its own entrance "signature" (see home-motion.css): the
   about block wipes its video in, the offers flip up, services bloom out of a blur, the
   abroad band fans its cards, the FAQ cascades, and so on. Items reveal as they reach the
   viewport; whatever arrives together is staggered in reading order.

   How it plays with scroll-reveal.js
   - The hero stays with scroll-reveal.js (its "settled" event drives the tagline).
   - For the sections below the hero, this file takes the reveal over: it strips the
     scroll-reveal classes from them before the reveal engine starts, animates the parts
     itself, and when a part has finished it gives the scroll-reveal "revealed" classes
     back, so hover rules that key off them keep working.
   - Carousels animate as one shell; only the slides on screen at that moment get the
     inner stagger, so off-screen slides are never left hidden.

   Scroll-linked extras: the marquee speeds up with scroll velocity (Web Animations
   playbackRate, so it never jumps); hero / about / abroad parallax is pure CSS
   (animation-timeline: view()) and simply absent where unsupported.
   Reduced motion: nothing is hidden or moved. */
(function () {
    "use strict";

    var main = document.querySelector(".home-page-main");
    if (!main || !window.matchMedia) return;

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var root = document.documentElement;

    /* sel: section; parts: [selector, role] — role names the motion in home-motion.css */
    var SECTIONS = [
        { sel: ".about-intro-section--home", sig: "about", parts: [
            [".about-intro-image-card", "media"],
            [".row > div:last-child > *", "text"]
        ] },
        { sel: ".home-sales-section", sig: "offers", parts: [
            [".home-sales-section__eyebrow", "eyebrow"],
            [".home-sales-section__title", "title"],
            [".discount-banner", "item"]
        ] },
        { sel: ".hsvc-section", sig: "services", parts: [
            [".hsvc-header > div > *", "title"],
            [".hsvc-header > a", "cta"],
            [".hsvc-card-wrap", "item"]
        ] },
        { sel: ".home-prices-section", sig: "prices", parts: [
            [".home-prices-section__title", "title"],
            [".home-prices-carousel-wrap", "carousel"]
        ] },
        { sel: ".home-mock-prices-section", sig: "prices", parts: [
            [".home-mock-prices-section__eyebrow", "eyebrow"],
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
            [".index-team-see-all-wrap", "cta"]
        ] },
        { sel: ".reviews-testimonials-section--home", sig: "reviews", parts: [
            [".reviews-home__eyebrow", "eyebrow"],
            [".reviews-home__title", "title"],
            [".testimonial-carousel-shell", "carousel"],
            [".reviews-home-cta", "cta"]
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
    var CAROUSEL_SLIDES = ".swiper-slide";

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
        return had;
    }

    function claimSections() {
        SECTIONS.forEach(function (def) {
            qsa(def.sel, main).forEach(function (section) {
                if (section.hasAttribute("data-hm")) return;
                section.setAttribute("data-hm", def.sig);
                /* the reveal engine must not animate anything in here (or the section itself) */
                if (stripReveal(section)) section.setAttribute("data-hm-had-reveal", "");
                qsa(".scroll-reveal, .wow, .reveal", section).forEach(function (el) {
                    if (stripReveal(el)) el.setAttribute("data-hm-had-reveal", "");
                });
                def.parts.forEach(function (pair) {
                    qsa(pair[0], section).forEach(function (el) {
                        if (el.classList.contains("hm-part")) return;
                        if (el.offsetParent === null && getComputedStyle(el).position !== "fixed") return; /* hidden (d-none etc.) */
                        el.classList.add("hm-part");
                        el.setAttribute("data-hm-role", pair[1]);
                        parts.push(el);
                    });
                });
            });
        });
    }

    /* ---------------------------------------------------------------- reveal */
    var STAGGER = 80;
    var STAGGER_MAX = 7;
    var DURATION = 900;
    var observer = null;
    var started = false;

    function finish(el) {
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

    function staggerCarousel(shell, baseDelay) {
        /* only the slides on screen now: the rest are off to the side, behind overflow */
        var vw = window.innerWidth;
        var k = 0;
        qsa(CAROUSEL_SLIDES, shell).forEach(function (slide) {
            if (slide.classList.contains("swiper-slide-duplicate")) return;
            var r = slide.getBoundingClientRect();
            if (r.right <= 0 || r.left >= vw || r.width === 0) return;
            slide.classList.add("hm-sub");
            slide.style.setProperty("--hm-delay", (baseDelay + 120 + Math.min(k, STAGGER_MAX) * STAGGER) + "ms");
            k += 1;
        });
        return k;
    }

    function reveal(batch) {
        /* reading order: whatever arrives together is staggered top-to-bottom, left-to-right */
        batch.sort(function (a, b) {
            return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
        });
        var k = 0;
        var lastSection = null;
        batch.forEach(function (el) {
            var section = el.closest("[data-hm]");
            if (section !== lastSection) {
                k = 0;
                lastSection = section;
                section.classList.add("hm-seen");
            }
            var delay = Math.min(k, STAGGER_MAX) * STAGGER;
            el.style.setProperty("--hm-delay", delay + "ms");
            var extra = 0;
            if (el.getAttribute("data-hm-role") === "carousel") {
                extra = staggerCarousel(el, delay) * STAGGER + 120;
            }
            k += 1;
            requestAnimationFrame(function () {
                requestAnimationFrame(function () {
                    el.classList.add("hm-in");
                    qsa(".hm-sub", el).forEach(function (sub) { sub.classList.add("hm-in"); });
                });
            });
            window.setTimeout(function () { finish(el); }, delay + extra + DURATION + 200);
        });
    }

    function revealAll() {
        parts.forEach(finish);
        parts = [];
    }

    function start() {
        if (started) return;
        started = true;
        if (!parts.length) return;
        if (!("IntersectionObserver" in window)) {
            revealAll();
            return;
        }
        STAGGER = cssMs("--hm-stagger", STAGGER);
        DURATION = cssMs("--hm-duration", DURATION);
        var pending = [];
        var flushQueued = false;
        observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                observer.unobserve(entry.target);
                pending.push(entry.target);
            });
            if (pending.length && !flushQueued) {
                flushQueued = true;
                requestAnimationFrame(function () {
                    flushQueued = false;
                    var batch = pending;
                    pending = [];
                    reveal(batch);
                });
            }
        }, { threshold: 0, rootMargin: "0px 0px -8% 0px" });
        parts.forEach(function (el) { observer.observe(el); });
    }

    /* ---------------------------------------------------------------- marquee */
    function initMarqueeVelocity() {
        var track = main.querySelector(".home-marquee__track");
        if (!track || typeof track.getAnimations !== "function") return;
        var lastY = window.pageYOffset;
        var lastT = performance.now();
        var rate = 1;
        var target = 1;
        var running = false;

        function anim() {
            var list = track.getAnimations();
            return list.length ? list[0] : null;
        }

        function step() {
            rate += (target - rate) * 0.12;
            target += (1 - target) * 0.06;
            var a = anim();
            if (a) a.playbackRate = rate;
            track.style.setProperty("--hm-skew", ((rate - 1) * -1.6).toFixed(2) + "deg");
            if (Math.abs(rate - 1) > 0.01 || Math.abs(target - 1) > 0.01) {
                requestAnimationFrame(step);
            } else {
                rate = target = 1;
                if (a) a.playbackRate = 1;
                track.style.setProperty("--hm-skew", "0deg");
                running = false;
            }
        }

        window.addEventListener("scroll", function () {
            var now = performance.now();
            var y = window.pageYOffset;
            var dy = y - lastY;
            var dt = Math.max(now - lastT, 16);
            lastY = y;
            lastT = now;
            /* a jump (anchor link, Home / End) is not a gesture: ignore it */
            if (Math.abs(dy) > window.innerHeight) return;
            var v = dy / dt; /* px per ms; + down, - up */
            /* scrolling down speeds the strip up; scrolling up runs it backwards for a moment */
            target = Math.max(-1.5, Math.min(3.5, 1 + v * 1.6));
            if (!running) {
                running = true;
                requestAnimationFrame(step);
            }
        }, { passive: true });
    }

    /* ---------------------------------------------------------------- boot */
    if (reduceMotion) return;

    root.classList.add("hm-ready");
    claimSections();
    initMarqueeVelocity();

    document.addEventListener("academor:page-ready", function () {
        requestAnimationFrame(function () { requestAnimationFrame(start); });
    });
    window.addEventListener("load", function () {
        /* page-ready normally fires first (spinner hidden); this is the fallback */
        window.setTimeout(start, 600);
    });
    /* safety net: never leave sections hidden */
    window.setTimeout(function () {
        if (!started) start();
    }, 6000);
})();

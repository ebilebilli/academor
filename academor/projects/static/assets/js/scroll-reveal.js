(function () {
    "use strict";

    var STAGGER_MS = 100;
    var CARD_SELECTORS =
        ".hsvc-card, .course-alt-card, .abroad-card, .hb-card, .hb-hero, " +
        ".blog-card, .blog-featured-card, .testimonial-item, a.svc-card-link";
    var BLOCK_SELECTORS =
        ".hsvc-header, .hsvc-empty, .courses-alt__heading, .courses-alt__carousel-shell, " +
        ".index-team-see-all-wrap, .testimonial-carousel-shell, .reviews-home-cta, " +
        ".home-faq, .abroad-hero__card, .universities-carousel";
    var STAGGER_PARENTS = ".hsvc-grid, .row, .swiper-wrapper, #abroad-destinations";
    var SKIP_ANCESTOR = ".hbh-section, .footer, footer";

    var prefersReducedMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function qsa(sel, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    }

    function shouldSkip(el) {
        if (!el || el.classList.contains("is-revealed")) return true;
        if (el.closest(SKIP_ANCESTOR)) return true;
        if (el.classList.contains("swiper-slide-duplicate")) return true;
        /* Cards inside review carousel: hidden until Swiper inits — reveal via shell + main.js */
        if (el.matches(".testimonial-item") && el.closest(".testimonial-swiper")) return true;
        return false;
    }

    function stripWowClasses(el) {
        el.classList.remove("wow", "fadeInUp", "fadeInDown", "fadeIn", "fadeInLeft", "fadeInRight");
        el.style.opacity = "";
        el.style.animationDelay = "";
    }

    function parseDelaySeconds(attr) {
        if (!attr) return 0;
        var s = String(attr).trim();
        if (s.slice(-2) === "ms") return parseFloat(s) / 1000 || 0;
        if (s.slice(-1) === "s") return parseFloat(s) || 0;
        return parseFloat(s) / 1000 || 0;
    }

    function staggerIndexForCard(el) {
        var root = el.closest(STAGGER_PARENTS);
        if (!root) return 0;
        var cards = qsa(CARD_SELECTORS, root).filter(function (node) {
            return !shouldSkip(node);
        });
        var idx = cards.indexOf(el);
        return idx >= 0 ? idx : 0;
    }

    function prepareElement(el, opts) {
        if (shouldSkip(el)) return false;
        if (el.classList.contains("scroll-reveal")) return true;

        var wowDelay = el.getAttribute("data-wow-delay");
        stripWowClasses(el);
        el.classList.add("scroll-reveal");

        var delayMs = 0;
        if (opts && opts.isCard) {
            delayMs = staggerIndexForCard(el) * STAGGER_MS;
        } else if (wowDelay) {
            delayMs = Math.round(parseDelaySeconds(wowDelay) * 1000);
        } else if (opts && opts.staggerIndex != null) {
            delayMs = opts.staggerIndex * STAGGER_MS;
        }

        el.style.setProperty("--reveal-delay", delayMs + "ms");
        return true;
    }

    function collectTargets() {
        var seen = typeof WeakSet !== "undefined" ? new WeakSet() : null;
        var list = [];

        function add(el, opts) {
            if (!el || shouldSkip(el)) return;
            if (seen) {
                if (seen.has(el)) return;
                seen.add(el);
            } else if (list.indexOf(el) !== -1) {
                return;
            }
            if (prepareElement(el, opts)) list.push(el);
        }

        qsa(CARD_SELECTORS).forEach(function (el) {
            add(el, { isCard: true });
        });

        qsa(BLOCK_SELECTORS).forEach(function (el) {
            add(el, { isCard: false });
        });

        qsa("[data-scroll-reveal]").forEach(function (el) {
            add(el, { isCard: el.matches(CARD_SELECTORS) });
        });

        qsa(".wow").forEach(function (el) {
            add(el, { isCard: el.matches(CARD_SELECTORS) });
        });

        return list;
    }

    function initScrollReveal() {
        var targets = collectTargets();

        if (prefersReducedMotion) {
            targets.forEach(function (el) {
                el.classList.add("is-revealed");
                el.style.willChange = "auto";
            });
            return;
        }

        if (!targets.length || !("IntersectionObserver" in window)) {
            targets.forEach(function (el) {
                el.classList.add("is-revealed");
            });
            return;
        }

        var observer = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    var el = entry.target;
                    el.classList.add("is-revealed");
                    obs.unobserve(el);
                });
            },
            { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
        );

        targets.forEach(function (el) {
            observer.observe(el);
        });
    }

    function boot() {
        initScrollReveal();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

    window.ScrollReveal = { init: boot };
})();

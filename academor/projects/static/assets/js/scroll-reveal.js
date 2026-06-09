(function () {
    "use strict";

    var STAGGER_MS = 100;
    var CARD_SELECTORS =
        ".hsvc-card, .course-alt-card, .abroad-card, .hb-card, .hb-hero, " +
        ".blog-card, .blog-featured-card, .testimonial-item, a.svc-card-link";
    var BLOCK_SELECTORS =
        ".hsvc-header, .hsvc-empty, .courses-alt__heading, .courses-alt__carousel-shell, " +
        ".index-team-see-all-wrap, .testimonial-carousel-shell, .reviews-home-cta, " +
        ".home-faq, .abroad-hero__card, .abroad-advantages__item, .abroad-advantages__title, " +
        ".hbh-top-bar, .hbh-grid, .hbh-reg-wrap";
    var STAGGER_PARENTS =
        ".hsvc-grid, .row, .swiper-wrapper, #abroad-destinations, .hbh-inner .container, .abroad-advantages__grid";
    var SKIP_ANCESTOR = "";

    var prefersReducedMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var preparedTargets = [];
    var revealObserver = null;
    var revealStarted = false;
    var revealSettledFired = false;
    var heroSettlePending = null;
    var REVEAL_TRANSITION_MS = 850;

    function qsa(sel, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    }

    function qs(sel, root) {
        return (root || document).querySelector(sel);
    }

    /* ---- Scroll progress bar ---- */
    var progressBar = qs("#scrollProgressBar");
    var lastProgress = -1;

    function updateProgress() {
        if (!progressBar) return;
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
        var docHeight = document.documentElement.scrollHeight - window.innerHeight;
        var progress = docHeight > 0 ? Math.min(Math.max(scrollTop / docHeight, 0), 1) : 0;
        if (Math.abs(progress - lastProgress) < 0.001) return;
        lastProgress = progress;
        progressBar.style.transform = "scaleX(" + progress + ")";
    }

    /* ---- Scroll spy ---- */
    var sections = [];
    var navLinks = qsa(".navbar-nav .nav-link[href^='#']");

    function refreshSections() {
        sections = qsa("section[id]").map(function (sec) {
            return {
                id: sec.id,
                top: sec.offsetTop - 150
            };
        });
    }

    var activeLink = null;

    function updateActiveNav() {
        if (!navLinks.length || !sections.length) return;
        var scrollPos = window.pageYOffset + 100;
        var current = null;
        for (var i = sections.length - 1; i >= 0; i--) {
            if (scrollPos >= sections[i].top) {
                current = sections[i].id;
                break;
            }
        }
        if (activeLink === current) return;
        activeLink = current;
        navLinks.forEach(function (link) {
            link.classList.toggle("is-active", link.getAttribute("href") === "#" + current);
        });
    }

    /* ---- Premium reveal ---- */
    function shouldSkip(el) {
        if (!el || el.classList.contains("is-revealed") || el.classList.contains("is-visible")) {
            return true;
        }
        if (SKIP_ANCESTOR && el.closest(SKIP_ANCESTOR)) return true;
        if (el.classList.contains("swiper-slide-duplicate")) return true;
        if (el.matches(".testimonial-item") && el.closest(".testimonial-swiper")) return true;
        if (el.matches(".universities-carousel-shell")) return true;
        return false;
    }

    function directionFromWow(el) {
        if (el.classList.contains("fadeInDown")) return "reveal--down";
        if (el.classList.contains("fadeInLeft")) return "reveal--left";
        if (el.classList.contains("fadeInRight")) return "reveal--right";
        if (el.classList.contains("fadeIn")) return "reveal--fade";
        return "reveal--up";
    }

    function stripWowClasses(el) {
        var direction = directionFromWow(el);
        el.classList.remove(
            "wow",
            "animated",
            "fadeInUp",
            "fadeInDown",
            "fadeIn",
            "fadeInLeft",
            "fadeInRight"
        );
        el.style.opacity = "";
        el.style.animationDelay = "";
        return direction;
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
        if (!el.classList.contains("scroll-reveal")) {
            var direction = stripWowClasses(el);
            el.classList.add("scroll-reveal", "reveal", direction);
        }

        var delayMs = 0;
        var wowDelay = el.getAttribute("data-wow-delay");
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

        qsa(".reveal").forEach(function (el) {
            add(el, { isCard: el.matches(CARD_SELECTORS) });
        });

        return list;
    }

    function scheduleMarkRevealed(el, obs) {
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                markRevealed(el);
                obs.unobserve(el);
            });
        });
    }

    function parseRevealDelayMs(el) {
        var raw = window.getComputedStyle(el).getPropertyValue("--reveal-delay").trim();
        if (!raw) return 0;
        if (raw.slice(-2) === "ms") return parseFloat(raw) || 0;
        if (raw.slice(-1) === "s") return (parseFloat(raw) || 0) * 1000;
        return parseFloat(raw) || 0;
    }

    function isInViewport(el) {
        var rect = el.getBoundingClientRect();
        return rect.top < window.innerHeight && rect.bottom > 0;
    }

    function dispatchRevealSettled() {
        if (revealSettledFired) return;
        revealSettledFired = true;
        document.dispatchEvent(new CustomEvent("academor:reveal-settled"));
    }

    function scheduleHeroRevealSettled() {
        if (!heroSettlePending || !heroSettlePending.length) {
            dispatchRevealSettled();
            return;
        }
        var maxEnd = 0;
        heroSettlePending.forEach(function (el) {
            maxEnd = Math.max(maxEnd, parseRevealDelayMs(el) + REVEAL_TRANSITION_MS);
        });
        setTimeout(dispatchRevealSettled, maxEnd + 40);
        heroSettlePending = null;
    }

    function markRevealed(el) {
        el.classList.add("is-revealed", "is-visible");
        el.style.willChange = "auto";

        if (!heroSettlePending) return;
        var idx = heroSettlePending.indexOf(el);
        if (idx === -1) return;
        heroSettlePending.splice(idx, 1);
        if (!heroSettlePending.length) {
            scheduleHeroRevealSettled();
        }
    }

    function prepareReveal() {
        preparedTargets = collectTargets();
        document.documentElement.classList.add("reveal-pending");
    }

    function disconnectRevealObserver() {
        if (revealObserver) {
            revealObserver.disconnect();
            revealObserver = null;
        }
    }

    function startReveal() {
        if (revealStarted) return;
        revealStarted = true;
        document.documentElement.classList.remove("reveal-pending");
        document.documentElement.classList.add("reveal-ready");

        var targets = preparedTargets.length ? preparedTargets : collectTargets();
        heroSettlePending = targets.filter(function (el) {
            return el.closest(".hbh-section") && isInViewport(el);
        });

        if (prefersReducedMotion) {
            heroSettlePending = null;
            targets.forEach(markRevealed);
            dispatchRevealSettled();
            return;
        }

        if (!targets.length || !("IntersectionObserver" in window)) {
            heroSettlePending = null;
            targets.forEach(markRevealed);
            dispatchRevealSettled();
            return;
        }

        if (!heroSettlePending.length) {
            dispatchRevealSettled();
        }

        disconnectRevealObserver();

        revealObserver = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    scheduleMarkRevealed(entry.target, obs);
                });
            },
            { threshold: 0.08, rootMargin: "0px 0px -4% 0px" }
        );

        requestAnimationFrame(function () {
            targets.forEach(function (el) {
                revealObserver.observe(el);
            });
        });
    }

    function scheduleRevealStart() {
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                startReveal();
            });
        });
    }

    function boot() {
        revealStarted = false;
        disconnectRevealObserver();
        refreshSections();
        prepareReveal();
        scheduleRevealStart();
        updateProgress();
        updateActiveNav();
    }

    /* ---- Throttled scroll handler ---- */
    var ticking = false;

    function onScroll() {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(function () {
            updateProgress();
            updateActiveNav();
            ticking = false;
        });
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener(
        "resize",
        function () {
            refreshSections();
            onScroll();
        },
        { passive: true }
    );

    function onDomReady() {
        refreshSections();
        prepareReveal();
        updateProgress();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", onDomReady);
    } else {
        onDomReady();
    }

    document.addEventListener("academor:page-ready", scheduleRevealStart);

    window.addEventListener("load", function () {
        refreshSections();
        onScroll();
        if (!revealStarted && !qs("#spinner")) {
            scheduleRevealStart();
        }
    });

    window.AcademorScroll = {
        initReveal: boot,
        refresh: function () {
            refreshSections();
            onScroll();
        }
    };

    window.ScrollReveal = { init: boot };
})();

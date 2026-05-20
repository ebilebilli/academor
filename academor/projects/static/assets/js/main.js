(function () {
    "use strict";

    function qs(sel, root) {
        return (root || document).querySelector(sel);
    }

    function qsa(sel, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    }

    var prefersReducedMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* Spinner */
    var sp = qs("#spinner");
    var spinnerHidden = false;
    function hideSpinner() {
        if (spinnerHidden || !sp) return;
        spinnerHidden = true;
        setTimeout(function () {
            sp.classList.add("hide");
        }, 50);
    }
    window.addEventListener("load", hideSpinner);
    setTimeout(hideSpinner, 800);

    /* WOW → IntersectionObserver + Animate.css (.wow.* → add .animated when visible) */
    function initWowReplacement() {
        var narrow = window.innerWidth < 768;
        var disabled = prefersReducedMotion || narrow;
        qsa(".wow").forEach(function (el) {
            var delay = el.getAttribute("data-wow-delay") || "0s";
            el.style.animationDelay = delay;
            if (disabled) {
                el.style.opacity = "";
                el.classList.add("animated");
                return;
            }
            el.style.opacity = "0";
            var obs = new IntersectionObserver(
                function (entries, o) {
                    entries.forEach(function (entry) {
                        if (!entry.isIntersecting) return;
                        el.style.opacity = "";
                        el.classList.add("animated");
                        o.disconnect();
                    });
                },
                { threshold: 0.15 }
            );
            obs.observe(el);
        });
    }
    initWowReplacement();

    /* Sticky navbar + reading progress */
    var stickyScrolled = null;
    var scrollProgressBar = qs("#scrollProgressBar");
    function updateStickyNavbar() {
        var y = window.pageYOffset || document.documentElement.scrollTop || 0;
        var isScrolled = y > 8;
        if (stickyScrolled === isScrolled) return;
        qsa(".navbar-light.sticky-top").forEach(function (nav) {
            nav.classList.toggle("sticky-navbar--scrolled", isScrolled);
        });
        stickyScrolled = isScrolled;
    }

    function updateScrollProgress() {
        if (!scrollProgressBar) return;
        var scrollTop =
            window.pageYOffset ||
            document.documentElement.scrollTop ||
            document.body.scrollTop ||
            0;
        var doc = document.documentElement;
        var scrollable = Math.max(doc.scrollHeight - window.innerHeight, 0);
        var progress =
            scrollable > 0 ? Math.min(Math.max(scrollTop / scrollable, 0), 1) : 0;
        scrollProgressBar.style.transform = "scaleX(" + progress + ")";
    }

    /* Dropdown hover (lg+) */
    var hoverBindings = typeof WeakMap !== "undefined" ? new WeakMap() : null;
    var menuHoverEnabled = null;

    function setDropdownOpen(dropdown, open) {
        dropdown.classList.toggle("show", open);
        var toggle = dropdown.querySelector(".dropdown-toggle");
        var menu = dropdown.querySelector(".dropdown-menu");
        if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
        if (menu) menu.classList.toggle("show", open);
    }

    var hoverCloseDelayMs = 180;

    function syncMenuHoverMode() {
        var shouldEnable = window.matchMedia("(min-width: 992px)").matches;
        if (menuHoverEnabled === shouldEnable) return;

        var dropdowns = qsa(".dropdown:not(.nav-lang-dropdown)");
        dropdowns.forEach(function (dropdown) {
            if (hoverBindings) {
                var prev = hoverBindings.get(dropdown);
                if (prev) {
                    dropdown.removeEventListener("mouseenter", prev.enter);
                    dropdown.removeEventListener("mouseleave", prev.leave);
                    hoverBindings.delete(dropdown);
                }
            }
            if (!shouldEnable) {
                setDropdownOpen(dropdown, false);
            }
        });

        if (shouldEnable) {
            dropdowns.forEach(function (dropdown) {
                var closeTimer = null;
                function enter() {
                    if (closeTimer) {
                        clearTimeout(closeTimer);
                        closeTimer = null;
                    }
                    setDropdownOpen(dropdown, true);
                }
                function leave() {
                    if (closeTimer) clearTimeout(closeTimer);
                    closeTimer = setTimeout(function () {
                        setDropdownOpen(dropdown, false);
                        closeTimer = null;
                    }, hoverCloseDelayMs);
                }
                dropdown.addEventListener("mouseenter", enter);
                dropdown.addEventListener("mouseleave", leave);
                if (hoverBindings) {
                    hoverBindings.set(dropdown, { enter: enter, leave: leave });
                }
            });
        }

        menuHoverEnabled = shouldEnable;
    }

    var resizeTicking = false;
    window.addEventListener("load", function () {
        syncMenuHoverMode();
    });
    window.addEventListener(
        "resize",
        function () {
            if (resizeTicking) return;
            resizeTicking = true;
            window.requestAnimationFrame(function () {
                syncMenuHoverMode();
                resizeTicking = false;
            });
        },
        { passive: true }
    );
    syncMenuHoverMode();

    /* Back to top */
    var backToTop = qs(".back-to-top");
    function getScrollTop() {
        return (
            window.pageYOffset ||
            document.documentElement.scrollTop ||
            document.body.scrollTop ||
            0
        );
    }
    var backToTopVisible = null;
    function updateBackToTop() {
        if (!backToTop) return;
        var nextVisible = getScrollTop() > 300;
        if (backToTopVisible === nextVisible) return;
        if (nextVisible) {
            backToTop.classList.add("back-to-top--visible");
            backToTop.setAttribute("tabindex", "0");
            backToTop.setAttribute("aria-hidden", "false");
        } else {
            backToTop.classList.remove("back-to-top--visible");
            backToTop.setAttribute("tabindex", "-1");
            backToTop.setAttribute("aria-hidden", "true");
        }
        backToTopVisible = nextVisible;
    }

    var scrollTicking = false;
    window.addEventListener(
        "scroll",
        function () {
            if (!scrollTicking) {
                scrollTicking = true;
                window.requestAnimationFrame(function () {
                    updateStickyNavbar();
                    updateBackToTop();
                    updateScrollProgress();
                    scrollTicking = false;
                });
            }
        },
        { passive: true }
    );
    window.addEventListener(
        "resize",
        function () {
            window.requestAnimationFrame(function () {
                updateStickyNavbar();
                updateBackToTop();
                updateScrollProgress();
            });
        },
        { passive: true }
    );
    window.addEventListener("load", function () {
        updateStickyNavbar();
        updateBackToTop();
        updateScrollProgress();
    });
    updateStickyNavbar();
    updateBackToTop();
    updateScrollProgress();

    if (backToTop) {
        backToTop.addEventListener("click", function (e) {
            e.preventDefault();
            if ("scrollBehavior" in document.documentElement.style) {
                window.scrollTo({ top: 0, behavior: "smooth" });
            } else {
                window.scrollTo(0, 0);
            }
        });
    }

    /* Swiper carousels */
    if (typeof Swiper !== "undefined") {
    var heroEl = qs(".header-swiper");
    if (heroEl) {
        var headerSlides = heroEl.querySelectorAll(".swiper-slide");
        var headerMulti = headerSlides.length > 1;
        new Swiper(".header-swiper", {
            loop: headerMulti,
            autoplay:
                !prefersReducedMotion && headerMulti
                    ? { delay: 5000, disableOnInteraction: false }
                    : false,
            pagination: {
                el: ".header-swiper .swiper-pagination",
                clickable: true,
            },
            navigation: {
                nextEl: ".header-swiper .header-carousel-owl-nav .swiper-button-next",
                prevEl: ".header-swiper .header-carousel-owl-nav .swiper-button-prev",
            },
            watchOverflow: true,
        });
    }

    qsa(".team-swiper").forEach(function (teamRoot) {
        var teamSlides = teamRoot.querySelectorAll(".swiper-slide");
        if (!teamSlides.length) return;
        var teamCount = teamSlides.length;
        var teamPagParent = teamRoot.parentElement;
        var teamPagEl =
            teamPagParent &&
            teamPagParent.querySelector(".team-swiper-pagination-outer");
        if (!teamPagEl) {
            teamPagEl = teamRoot.querySelector(".swiper-pagination");
        }
        var teamPagConfig = teamPagEl
            ? { el: teamPagEl, clickable: true }
            : false;
        new Swiper(teamRoot, {
            slidesPerView: 1,
            spaceBetween: 16,
            loop: teamCount > 4,
            rewind: teamCount <= 4,
            autoplay: false,
            pagination: teamPagConfig,
            navigation: {
                nextEl: teamRoot.querySelector(".swiper-button-next"),
                prevEl: teamRoot.querySelector(".swiper-button-prev"),
            },
            /* Hide prev/next when all slides fit (e.g. 4 members on desktop at slidesPerView 4) */
            watchOverflow: true,
            breakpoints: {
                576: { slidesPerView: 2, spaceBetween: 20 },
                768: { slidesPerView: 3, spaceBetween: 20 },
                992: { slidesPerView: 4, spaceBetween: 20 },
            },
        });
    });

    var testimonialEl = qs(".testimonial-swiper");
    if (testimonialEl) {
        var testimonialCount =
            testimonialEl.querySelectorAll(".swiper-slide").length;
        var tMulti = testimonialCount > 1;
        new Swiper(".testimonial-swiper", {
            centeredSlides: true,
            spaceBetween: 24,
            loop: testimonialCount > 2,
            rewind: testimonialCount <= 2,
            autoplay:
                !prefersReducedMotion && tMulti
                    ? { delay: 4200, disableOnInteraction: false }
                    : false,
            pagination: {
                el: ".testimonial-swiper .swiper-pagination",
                clickable: true,
            },
            navigation: {
                nextEl: ".testimonial-swiper .swiper-button-next",
                prevEl: ".testimonial-swiper .swiper-button-prev",
            },
            watchOverflow: true,
            breakpoints: {
                0: { slidesPerView: 1 },
                768: { slidesPerView: 2 },
                992: { slidesPerView: 3 },
            },
        });
    }
    }

    /* LCP, CLS, FCP via PerformanceObserver — dev only */
    if (typeof __DEV__ !== "undefined" && __DEV__)
        (function initPerfObservers() {
            if (!("PerformanceObserver" in window)) {
                console.warn("[Perf] PerformanceObserver not supported");
                return;
            }

            var clsValue = 0;
            var lcpEntry = null;
            var fcpMs = null;

            function logPerfSnapshot(reason) {
                var lcpStr = lcpEntry ? Math.round(lcpEntry.startTime) + " ms" : "n/a";
                var fcpStr = fcpMs != null ? Math.round(fcpMs) + " ms" : "n/a";
                console.log(
                    "[Perf] snapshot (" +
                        reason +
                        ") — FCP:",
                    fcpStr,
                    "| LCP:",
                    lcpStr,
                    "| CLS:",
                    Number(clsValue.toFixed(4))
                );
            }

            try {
                var fcpObserver = new PerformanceObserver(function (list) {
                    var entries = list.getEntries();
                    for (var i = 0; i < entries.length; i++) {
                        var entry = entries[i];
                        if (entry.name === "first-contentful-paint") {
                            fcpMs = entry.startTime;
                            console.log("[Perf] FCP:", Math.round(fcpMs), "ms");
                        }
                    }
                });
                fcpObserver.observe({ type: "paint", buffered: true });
            } catch (e) {}

            try {
                var clsObserver = new PerformanceObserver(function (list) {
                    var entries = list.getEntries();
                    for (var i = 0; i < entries.length; i++) {
                        var entry = entries[i];
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    }
                });
                clsObserver.observe({ type: "layout-shift", buffered: true });
            } catch (e) {}

            try {
                var lcpObserver = new PerformanceObserver(function (list) {
                    var entries = list.getEntries();
                    lcpEntry = entries[entries.length - 1] || lcpEntry;
                });
                lcpObserver.observe({ type: "largest-contentful-paint", buffered: true });
            } catch (e) {}

            document.addEventListener("visibilitychange", function () {
                if (document.visibilityState === "hidden") {
                    logPerfSnapshot("tab hidden / navigating away");
                }
            });
        })();
})();

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
            document.dispatchEvent(new CustomEvent("academor:page-ready"));
        }, 50);
    }
    function hideSpinnerAfterLayout() {
        requestAnimationFrame(function () {
            requestAnimationFrame(hideSpinner);
        });
    }
    window.addEventListener("load", hideSpinnerAfterLayout);
    setTimeout(hideSpinner, 4000);

    /* Pause marquee / globe / orbit / uni ticker when off-screen */
    function initPausableMotion() {
        if (prefersReducedMotion || !("IntersectionObserver" in window)) return;

        var roots = [];
        qsa(".home-marquee").forEach(function (el) {
            roots.push(el);
        });
        qsa(".abroad-hero__visual").forEach(function (el) {
            roots.push(el);
        });
        qsa(".universities-carousel--home").forEach(function (el) {
            roots.push(el);
        });
        if (!roots.length) return;

        var motionObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    entry.target.classList.toggle("motion-paused", !entry.isIntersecting);
                });
            },
            { threshold: 0, rootMargin: "64px 0px" }
        );

        roots.forEach(function (el) {
            motionObserver.observe(el);
        });
    }
    initPausableMotion();

    function initUniversitiesCarouselReveal() {
        var shell = qs(".universities-carousel-shell--reveal-pending");
        if (!shell || shell.dataset.uniRevealInit === "1") return;
        shell.dataset.uniRevealInit = "1";

        function reveal() {
            shell.classList.add("is-revealed");
        }

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            reveal();
            return;
        }

        var revealObserver = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    reveal();
                    obs.unobserve(shell);
                });
            },
            { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
        );

        revealObserver.observe(shell);
    }
    initUniversitiesCarouselReveal();

    function initUniversitiesCarouselDrag() {
        if (prefersReducedMotion) return;

        var SCROLL_MS = 28000;
        var DRAG_THRESHOLD_PX = 6;

        qsa(".universities-carousel--home").forEach(function (carousel) {
            if (carousel.dataset.uniDragInit === "1") return;
            var track = carousel.querySelector(".universities-list__track");
            if (!track) return;
            carousel.dataset.uniDragInit = "1";

            var offset = 0;
            var loopWidth = 0;
            var pointerTracking = false;
            var dragging = false;
            var suppressClick = false;
            var startX = 0;
            var startOffset = 0;
            var hoverPaused = false;
            var rafId = null;
            var lastTs = null;
            var activePointerId = null;

            function measureLoopWidth() {
                loopWidth = track.scrollWidth / 2;
            }

            function readTransformOffset() {
                var matrix = window.getComputedStyle(track).transform;
                if (!matrix || matrix === "none") return 0;
                if (typeof DOMMatrixReadOnly !== "undefined") {
                    return new DOMMatrixReadOnly(matrix).m41;
                }
                var match = matrix.match(/matrix\(([^)]+)\)/);
                if (!match) return 0;
                var parts = match[1].split(",");
                return parseFloat(parts[parts.length - 2]) || 0;
            }

            function normalizeOffset() {
                if (loopWidth <= 0) return;
                while (offset <= -loopWidth) offset += loopWidth;
                while (offset > 0) offset -= loopWidth;
            }

            function applyTransform() {
                track.style.transform = "translate3d(" + offset + "px, 0, 0)";
            }

            function shouldAutoScroll() {
                return (
                    !dragging &&
                    !hoverPaused &&
                    !carousel.classList.contains("motion-paused") &&
                    loopWidth > 0
                );
            }

            function tick(ts) {
                if (lastTs == null) lastTs = ts;
                var dt = ts - lastTs;
                lastTs = ts;

                if (shouldAutoScroll()) {
                    offset -= (loopWidth / SCROLL_MS) * dt;
                    normalizeOffset();
                    applyTransform();
                }

                rafId = window.requestAnimationFrame(tick);
            }

            function startManualControl() {
                carousel.classList.add("universities-carousel--interactive");
                offset = readTransformOffset();
                track.style.animation = "none";
                normalizeOffset();
                applyTransform();
                if (!rafId) {
                    lastTs = null;
                    rafId = window.requestAnimationFrame(tick);
                }
            }

            function beginDrag(e) {
                dragging = true;
                suppressClick = true;
                carousel.classList.add("is-dragging");
                if (carousel.setPointerCapture) {
                    carousel.setPointerCapture(e.pointerId);
                }
            }

            function onPointerDown(e) {
                if (e.pointerType === "mouse" && e.button !== 0) return;
                pointerTracking = true;
                dragging = false;
                suppressClick = false;
                activePointerId = e.pointerId;
                startX = e.clientX;
                startOffset = offset;
            }

            function onPointerMove(e) {
                if (!pointerTracking || e.pointerId !== activePointerId) return;
                var delta = e.clientX - startX;
                if (!dragging && Math.abs(delta) >= DRAG_THRESHOLD_PX) {
                    beginDrag(e);
                }
                if (!dragging) return;
                offset = startOffset + delta;
                normalizeOffset();
                applyTransform();
            }

            function endDrag(e) {
                if (!pointerTracking || (e && e.pointerId !== activePointerId)) return;
                pointerTracking = false;
                dragging = false;
                activePointerId = null;
                carousel.classList.remove("is-dragging");
                if (suppressClick) {
                    window.setTimeout(function () {
                        suppressClick = false;
                    }, 250);
                }
                if (carousel.releasePointerCapture && e && e.pointerId != null) {
                    try {
                        carousel.releasePointerCapture(e.pointerId);
                    } catch (err) {}
                }
            }

            carousel.addEventListener("pointerdown", onPointerDown);
            carousel.addEventListener("pointermove", onPointerMove);
            carousel.addEventListener("pointerup", endDrag);
            carousel.addEventListener("pointercancel", endDrag);
            carousel.addEventListener("lostpointercapture", endDrag);

            carousel.addEventListener("mouseenter", function () {
                hoverPaused = true;
            });
            carousel.addEventListener("mouseleave", function () {
                hoverPaused = false;
            });

            track.addEventListener(
                "click",
                function (e) {
                    if (!suppressClick) return;
                    e.preventDefault();
                    e.stopPropagation();
                },
                true
            );

            window.addEventListener("resize", function () {
                measureLoopWidth();
                normalizeOffset();
                applyTransform();
            });

            window.requestAnimationFrame(function () {
                measureLoopWidth();
                if (loopWidth <= 0) return;
                startManualControl();
            });
        });
    }
    initUniversitiesCarouselDrag();

    /* Sticky navbar */
    var stickyScrolled = null;
    function updateStickyNavbar() {
        var y = window.pageYOffset || document.documentElement.scrollTop || 0;
        var isScrolled = y > 10;
        if (stickyScrolled === isScrolled) return;
        qsa(".navbar-light.sticky-top").forEach(function (nav) {
            nav.classList.toggle("sticky-navbar--scrolled", isScrolled);
        });
        stickyScrolled = isScrolled;
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
        var nextVisible = getScrollTop() > 400;
        if (backToTopVisible === nextVisible) return;
        backToTop.classList.toggle("is-visible", nextVisible);
        backToTop.classList.toggle("back-to-top--visible", nextVisible);
        backToTop.setAttribute("tabindex", nextVisible ? "0" : "-1");
        backToTop.setAttribute("aria-hidden", nextVisible ? "false" : "true");
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
            });
        },
        { passive: true }
    );
    window.addEventListener("load", function () {
        updateStickyNavbar();
        updateBackToTop();
    });
    updateStickyNavbar();
    updateBackToTop();

    if (backToTop) {
        backToTop.addEventListener("click", function (e) {
            e.preventDefault();
            window.scrollTo(0, 0);
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
            /* Center cards when fewer members than visible slots (e.g. 2 on desktop). */
            centerInsufficientSlides: true,
            /* Hide prev/next when all slides fit (e.g. 4 members on desktop at slidesPerView 4) */
            watchOverflow: true,
            breakpoints: {
                576: { slidesPerView: 2, spaceBetween: 20 },
                768: { slidesPerView: 3, spaceBetween: 20 },
                992: { slidesPerView: 4, spaceBetween: 20 },
            },
        });
    });

    qsa(".home-prices-swiper").forEach(function (pricesRoot) {
        var priceSlides = pricesRoot.querySelectorAll(".swiper-slide");
        if (!priceSlides.length) return;
        var priceCount = priceSlides.length;
        var priceWrap =
            pricesRoot.closest(".home-prices-carousel-wrap") ||
            pricesRoot.parentElement;
        var pricePagEl =
            priceWrap &&
            priceWrap.querySelector(".home-prices-swiper-pagination-outer");
        var pricePagConfig = pricePagEl
            ? { el: pricePagEl, clickable: true }
            : false;
        new Swiper(pricesRoot, {
            slidesPerView: "auto",
            spaceBetween: 16,
            centeredSlides: true,
            centerInsufficientSlides: true,
            slidesPerGroup: 1,
            loop: priceCount > 4,
            rewind: true,
            autoplay:
                !prefersReducedMotion && priceCount > 1
                    ? { delay: 4800, disableOnInteraction: false }
                    : false,
            pagination: pricePagConfig,
            navigation: {
                nextEl: priceWrap && priceWrap.querySelector(".swiper-button-next"),
                prevEl: priceWrap && priceWrap.querySelector(".swiper-button-prev"),
            },
            watchOverflow: true,
            breakpoints: {
                768: {
                    centeredSlides: false,
                    centerInsufficientSlides: true,
                    spaceBetween: 20,
                },
            },
        });
    });

    function revealTestimonialSlides(swiperRoot) {
        if (!swiperRoot) return;
        qsa(".testimonial-item", swiperRoot).forEach(function (item) {
            item.classList.remove("scroll-reveal", "reveal");
            item.classList.add("is-revealed", "is-visible");
            item.style.opacity = "";
            item.style.transform = "";
        });
    }

    var testimonialEl = qs(".testimonial-swiper");
    if (testimonialEl) {
        var testimonialCount =
            testimonialEl.querySelectorAll(".swiper-slide").length;
        var tMulti = testimonialCount > 1;
        var isReviewsHome = testimonialEl.classList.contains("testimonial-swiper--home");
        var swiperOpts = isReviewsHome
            ? {
                  centeredSlides: true,
                  centerInsufficientSlides: true,
                  slidesPerView: 1.12,
                  spaceBetween: 12,
                  loop: testimonialCount > 5,
                  rewind: testimonialCount <= 5,
                  slideToClickedSlide: true,
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
                      0: { slidesPerView: 1.12, spaceBetween: 10 },
                      576: { slidesPerView: 2, spaceBetween: 12 },
                      768: { slidesPerView: 3, spaceBetween: 14 },
                      992: { slidesPerView: 4, spaceBetween: 16 },
                      1200: { slidesPerView: 5, spaceBetween: 16 },
                  },
                  on: {
                      init: function () {
                          revealTestimonialSlides(testimonialEl);
                      },
                  },
              }
            : {
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
                  on: {
                      init: function () {
                          revealTestimonialSlides(testimonialEl);
                      },
                  },
              };
        new Swiper(".testimonial-swiper", swiperOpts);
        revealTestimonialSlides(testimonialEl);
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

    /* Review form — interactive star rating */
    function initReviewStarRating(root) {
        qsa("[data-review-star-rating]", root).forEach(function (wrap) {
            if (wrap.dataset.starRatingInit === "1") return;
            var input = wrap.querySelector(".review-form-rating-input");
            if (!input) return;
            wrap.dataset.starRatingInit = "1";

            var stars = qsa("[data-rating-value]", wrap);
            var min = 1;
            var max = 5;

            function setRating(n) {
                n = Math.max(min, Math.min(max, parseInt(n, 10) || min));
                input.value = String(n);
                stars.forEach(function (btn) {
                    var v = parseInt(btn.getAttribute("data-rating-value"), 10);
                    var on = v <= n;
                    btn.classList.toggle("is-active", on);
                    btn.setAttribute("aria-pressed", on ? "true" : "false");
                });
            }

            stars.forEach(function (btn) {
                btn.addEventListener("click", function () {
                    setRating(btn.getAttribute("data-rating-value"));
                });
            });

            setRating(parseInt(input.value, 10) || max);
        });
    }

    initReviewStarRating(document);
    var reviewFormModal = qs("#reviewFormModal");
    if (reviewFormModal) {
        reviewFormModal.addEventListener("shown.bs.modal", function () {
            initReviewStarRating(reviewFormModal);
        });
    }
})();

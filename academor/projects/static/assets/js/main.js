(function ($) {
    "use strict";

    // Spinner: hide on load, but no longer than 1.5s regardless
    var $sp = $('#spinner');
    var _spinnerHidden = false;
    function _hideSpinner() {
        if (_spinnerHidden) return;
        _spinnerHidden = true;
        setTimeout(function () { $sp.addClass('hide'); }, 50);
    }
    $(window).on('load', _hideSpinner);
    setTimeout(_hideSpinner, 1500);
    
    
    // Initiate wowjs (skip on small screens / reduced motion)
    var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!prefersReducedMotion && window.innerWidth >= 768) {
        new WOW({
            mobile: false,
            offset: 0
        }).init();
    }


    // Sticky Navbar (one rAF with back-to-top; class toggle avoids inline style churn)
    var stickyVisible = null;
    function updateStickyNavbar() {
        var y = window.pageYOffset || document.documentElement.scrollTop || 0;
        var nextVisible = y > 300;
        if (stickyVisible !== nextVisible) {
            $('.navbar-light.sticky-top').toggleClass('sticky-navbar--revealed', nextVisible);
            stickyVisible = nextVisible;
        }
    }
    
    
    // Dropdown on mouse hover (bind once per mode)
    const $dropdown = $(".dropdown");
    const $dropdownToggle = $(".dropdown-toggle");
    const $dropdownMenu = $(".dropdown-menu");
    const showClass = "show";
    var menuHoverEnabled = null;
    function syncMenuHoverMode() {
        var shouldEnable = window.matchMedia("(min-width: 992px)").matches;
        if (menuHoverEnabled === shouldEnable) return;
        $dropdown.off(".menuHover");
        if (shouldEnable) {
            $dropdown.on("mouseenter.menuHover", function () {
                const $this = $(this);
                $this.addClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "true");
                $this.find($dropdownMenu).addClass(showClass);
            });
            $dropdown.on("mouseleave.menuHover", function () {
                const $this = $(this);
                $this.removeClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "false");
                $this.find($dropdownMenu).removeClass(showClass);
            });
        }
        menuHoverEnabled = shouldEnable;
    }
    var resizeTicking = false;
    $(window).on("load.menuHover resize.menuHover", function () {
        if (resizeTicking) return;
        resizeTicking = true;
        window.requestAnimationFrame(function () {
            syncMenuHoverMode();
            resizeTicking = false;
        });
    });
    syncMenuHoverMode();
    
    
    // Back to top — class toggles display:flex (see style.css); robust scrollTop for document/body
    var $backToTop = $('.back-to-top');
    function getScrollTop() {
        return window.pageYOffset
            || document.documentElement.scrollTop
            || document.body.scrollTop
            || 0;
    }
    var backToTopVisible = null;
    function updateBackToTop() {
        var nextVisible = getScrollTop() > 300;
        if (backToTopVisible === nextVisible) return;
        if (nextVisible) {
            $backToTop.addClass('back-to-top--visible').attr({ tabindex: '0', 'aria-hidden': 'false' });
        } else {
            $backToTop.removeClass('back-to-top--visible').attr({ tabindex: '-1', 'aria-hidden': 'true' });
        }
        backToTopVisible = nextVisible;
    }
    var scrollTicking = false;
    window.addEventListener('scroll', function () {
        if (!scrollTicking) {
            scrollTicking = true;
            window.requestAnimationFrame(function () {
                updateStickyNavbar();
                updateBackToTop();
                scrollTicking = false;
            });
        }
    }, { passive: true });
    $(window).on('load.backToTop', function () {
        updateStickyNavbar();
        updateBackToTop();
    });
    updateStickyNavbar();
    updateBackToTop();

    $backToTop.on('click', function (e) {
        e.preventDefault();
        if ('scrollBehavior' in document.documentElement.style) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            $('html, body').stop(true).animate({ scrollTop: 0 }, 600, 'swing');
        }
    });


    // Header carousel (index only — other pages have no .header-carousel)
    var $headerCarousel = $(".header-carousel");
    if ($headerCarousel.length) {
        var headerSlideCount = $headerCarousel.find(".owl-carousel-item").length;
        var headerMulti = headerSlideCount > 1;
        $headerCarousel.owlCarousel({
            autoplay: !prefersReducedMotion && headerMulti,
            autoplayTimeout: 5000,
            autoplayHoverPause: true,
            smartSpeed: 850,
            items: 1,
            dots: false,
            loop: headerMulti,
            nav: headerMulti,
            lazyLoad: false,
            mouseDrag: headerMulti,
            touchDrag: headerMulti,
            navText: [
                '<i class="bi bi-chevron-left"></i>',
                '<i class="bi bi-chevron-right"></i>'
            ]
        });
    }


    // Course categories carousel (index)
    var $catCarousel = $(".categories-carousel");
    if ($catCarousel.length) {
        var catCount = $catCarousel.find(".item").length;
        $catCarousel.owlCarousel({
            autoplay: !prefersReducedMotion && catCount > 1,
            autoplayTimeout: 3200,
            autoplayHoverPause: true,
            smartSpeed: 420,
            margin: 20,
            dots: true,
            nav: true,
            lazyLoad: false,
            mouseDrag: catCount > 1,
            touchDrag: catCount > 1,
            slideBy: 1,
            navText: [
                '<i class="bi bi-chevron-left"></i>',
                '<i class="bi bi-chevron-right"></i>'
            ],
            loop: catCount > 1,
            responsive: {
                0: {
                    items: 1,
                    stagePadding: 24
                },
                576: {
                    items: 2,
                    stagePadding: 16
                },
                768: {
                    items: 3,
                    stagePadding: 12
                },
                992: {
                    items: 4,
                    stagePadding: 0
                }
            }
        });
    }

    // Team members carousel (index + team page)
    var $teamCarousel = $(".team-carousel");
    if ($teamCarousel.length && $teamCarousel.find(".item").length) {
        var teamCount = $teamCarousel.find(".item").length;
        $teamCarousel.owlCarousel({
            autoplay: !prefersReducedMotion,
            autoplayTimeout: 4500,
            autoplayHoverPause: true,
            smartSpeed: 650,
            margin: 24,
            dots: true,
            nav: true,
            lazyLoad: false,
            mouseDrag: teamCount > 1,
            touchDrag: teamCount > 1,
            navText: [
                '<i class="bi bi-chevron-left"></i>',
                '<i class="bi bi-chevron-right"></i>'
            ],
            loop: teamCount > 4,
            rewind: teamCount <= 4,
            responsive: {
                0: {
                    items: 1,
                    stagePadding: 28,
                    margin: 16
                },
                576: {
                    items: 2,
                    stagePadding: 16,
                    margin: 20
                },
                992: {
                    items: 3,
                    stagePadding: 8,
                    margin: 22
                },
                1200: {
                    items: 4,
                    stagePadding: 0,
                    margin: 24
                }
            }
        });
    }


    // Reviews carousel (pages that include reviews section only)
    var $testimonialCarousel = $(".testimonial-carousel");
    if ($testimonialCarousel.length) {
        $testimonialCarousel.owlCarousel({
            autoplay: !prefersReducedMotion,
            autoplayTimeout: 4200,
            autoplayHoverPause: true,
            smartSpeed: 700,
            center: true,
            margin: 24,
            dots: true,
            loop: true,
            nav: false,
            lazyLoad: false,
            responsive: {
                0: {
                    items: 1
                },
                768: {
                    items: 2
                },
                992: {
                    items: 3
                }
            }
        });
    }

    // LCP, CLS, FCP via PerformanceObserver — console only (dev mode only)
    if (typeof __DEV__ !== 'undefined' && __DEV__) (function initPerfObservers() {
        if (!('PerformanceObserver' in window)) {
            console.warn('[Perf] PerformanceObserver not supported');
            return;
        }

        var clsValue = 0;
        var lcpEntry = null;
        var fcpMs = null;

        function logPerfSnapshot(reason) {
            var lcpStr = lcpEntry ? Math.round(lcpEntry.startTime) + ' ms' : 'n/a';
            var fcpStr = fcpMs != null ? Math.round(fcpMs) + ' ms' : 'n/a';
            console.log('[Perf] snapshot (' + reason + ') — FCP:', fcpStr, '| LCP:', lcpStr, '| CLS:', Number(clsValue.toFixed(4)));
        }

        try {
            var fcpObserver = new PerformanceObserver(function (list) {
                var entries = list.getEntries();
                for (var i = 0; i < entries.length; i++) {
                    var entry = entries[i];
                    if (entry.name === 'first-contentful-paint') {
                        fcpMs = entry.startTime;
                        console.log('[Perf] FCP:', Math.round(fcpMs), 'ms');
                    }
                }
            });
            fcpObserver.observe({ type: 'paint', buffered: true });
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
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {}

        try {
            var lcpObserver = new PerformanceObserver(function (list) {
                var entries = list.getEntries();
                lcpEntry = entries[entries.length - 1] || lcpEntry;
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (e) {}

        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState === 'hidden') {
                logPerfSnapshot('tab hidden / navigating away');
            }
        });
    })();
    
})(jQuery);


(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate wowjs (skip on small screens / reduced motion)
    var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!prefersReducedMotion && window.innerWidth >= 768) {
        new WOW({
            mobile: false,
            offset: 40
        }).init();
    }


    // Sticky Navbar (throttled via requestAnimationFrame + avoid redundant writes)
    var stickyTicking = false;
    var stickyVisible = null;
    function updateStickyNavbar() {
        var y = window.pageYOffset || document.documentElement.scrollTop || 0;
        var nextVisible = y > 300;
        if (stickyVisible !== nextVisible) {
            $('.sticky-top').css('top', nextVisible ? '0px' : '-100px');
            stickyVisible = nextVisible;
        }
        stickyTicking = false;
    }
    window.addEventListener('scroll', function () {
        if (!stickyTicking) {
            window.requestAnimationFrame(updateStickyNavbar);
            stickyTicking = true;
        }
    }, { passive: true });
    updateStickyNavbar();
    
    
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
        if (!resizeTicking) {
            window.requestAnimationFrame(function () {
                syncMenuHoverMode();
                resizeTicking = false;
            });
            resizeTicking = true;
        }
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
    var backToTopTicking = false;
    window.addEventListener('scroll', function () {
        if (!backToTopTicking) {
            window.requestAnimationFrame(function () {
                updateBackToTop();
                backToTopTicking = false;
            });
            backToTopTicking = true;
        }
    }, { passive: true });
    $(window).on('load.backToTop', updateBackToTop);
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
        $headerCarousel.owlCarousel({
            autoplay: !prefersReducedMotion,
            autoplayTimeout: 5000,
            autoplayHoverPause: true,
            smartSpeed: 850,
            items: 1,
            dots: false,
            loop: true,
            nav: true,
            lazyLoad: true,
            mouseDrag: true,
            touchDrag: true,
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
            lazyLoad: true,
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
            lazyLoad: true,
            mouseDrag: teamCount > 1,
            touchDrag: teamCount > 1,
            navText: [
                '<i class="bi bi-chevron-left"></i>',
                '<i class="bi bi-chevron-right"></i>'
            ],
            loop: teamCount > 4,
            rewind: true,
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
            lazyLoad: true,
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

    // Core Web Vitals-style console metrics (console only; no UI)
    (function initPerfObservers() {
        if (!('PerformanceObserver' in window)) return;

        var clsValue = 0;
        var lcpEntry = null;

        try {
            var fcpObserver = new PerformanceObserver(function (list) {
                var entries = list.getEntries();
                for (var i = 0; i < entries.length; i++) {
                    var entry = entries[i];
                    if (entry.name === 'first-contentful-paint') {
                        console.log('[Perf] FCP:', Math.round(entry.startTime), 'ms');
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
                console.log('[Perf] CLS:', Number(clsValue.toFixed(4)));
            });
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {}

        try {
            var lcpObserver = new PerformanceObserver(function (list) {
                var entries = list.getEntries();
                lcpEntry = entries[entries.length - 1] || lcpEntry;
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

            function logLcpOnPageHide() {
                if (lcpEntry) {
                    console.log('[Perf] LCP:', Math.round(lcpEntry.startTime), 'ms');
                }
            }
            document.addEventListener('visibilitychange', function () {
                if (document.visibilityState === 'hidden') {
                    logLcpOnPageHide();
                }
            });
            window.addEventListener('pagehide', logLcpOnPageHide);
        } catch (e) {}
    })();
    
})(jQuery);


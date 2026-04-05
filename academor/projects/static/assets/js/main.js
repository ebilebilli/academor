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
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.sticky-top').css('top', '0px');
        } else {
            $('.sticky-top').css('top', '-100px');
        }
    });
    
    
    // Dropdown on mouse hover
    const $dropdown = $(".dropdown");
    const $dropdownToggle = $(".dropdown-toggle");
    const $dropdownMenu = $(".dropdown-menu");
    const showClass = "show";
    
    $(window).on("load resize", function() {
        if (this.matchMedia("(min-width: 992px)").matches) {
            $dropdown.hover(
            function() {
                const $this = $(this);
                $this.addClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "true");
                $this.find($dropdownMenu).addClass(showClass);
            },
            function() {
                const $this = $(this);
                $this.removeClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "false");
                $this.find($dropdownMenu).removeClass(showClass);
            }
            );
        } else {
            $dropdown.off("mouseenter mouseleave");
        }
    });
    
    
    // Back to top — class toggles display:flex (see style.css); robust scrollTop for document/body
    var $backToTop = $('.back-to-top');
    function getScrollTop() {
        return window.pageYOffset
            || document.documentElement.scrollTop
            || document.body.scrollTop
            || 0;
    }
    function updateBackToTop() {
        if (getScrollTop() > 300) {
            $backToTop.addClass('back-to-top--visible').attr({ tabindex: '0', 'aria-hidden': 'false' });
        } else {
            $backToTop.removeClass('back-to-top--visible').attr({ tabindex: '-1', 'aria-hidden': 'true' });
        }
    }
    $(window).on('scroll.backToTop', updateBackToTop);
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
            autoplay: true,
            smartSpeed: 1500,
            items: 1,
            dots: false,
            loop: true,
            nav: true,
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
            autoplay: false,
            smartSpeed: 500,
            margin: 20,
            dots: true,
            nav: true,
            navText: [
                '<i class="bi bi-chevron-left"></i>',
                '<i class="bi bi-chevron-right"></i>'
            ],
            loop: catCount > 4,
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
            autoplay: true,
            autoplayTimeout: 4500,
            autoplayHoverPause: true,
            smartSpeed: 650,
            margin: 24,
            dots: true,
            nav: true,
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


    // Testimonials carousel (pages that include reviews section only)
    var $testimonialCarousel = $(".testimonial-carousel");
    if ($testimonialCarousel.length) {
        $testimonialCarousel.owlCarousel({
            autoplay: true,
            smartSpeed: 1000,
            center: true,
            margin: 24,
            dots: true,
            loop: true,
            nav: false,
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
    
})(jQuery);


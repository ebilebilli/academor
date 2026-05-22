(function () {
    "use strict";

    var prefersReducedMotion =
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function initScrollReveal() {
        if (prefersReducedMotion) return;

        // Select all major sections and cards, excluding WOW-animated elements
        var scrollElements = document.querySelectorAll(
            "section:not(.wow), .card:not(.wow), .hsvc-card:not(.wow), .course-alt-card:not(.wow), [data-scroll-reveal]"
        );

        var revealOptions = {
            threshold: 0.15,
            rootMargin: "0px 0px -100px 0px"
        };

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;

                var el = entry.target;

                // Skip if already revealed or already animated
                if (el.classList.contains("is-revealed") || el.classList.contains("animated")) return;

                // Calculate stagger delay for cards in grid or carousel
                var staggerIndex = 0;
                if (el.dataset.scrollStaggerIndex !== undefined) {
                    staggerIndex = parseInt(el.dataset.scrollStaggerIndex, 10);
                } else if (el.parentElement) {
                    var parent = el.parentElement;
                    if (parent.classList.contains("hsvc-grid")) {
                        var siblings = parent.children;
                        for (var i = 0; i < siblings.length; i++) {
                            if (siblings[i] === el) {
                                staggerIndex = i;
                                break;
                            }
                        }
                    } else if (parent.classList.contains("swiper-wrapper")) {
                        var slides = parent.children;
                        for (var j = 0; j < slides.length; j++) {
                            if (slides[j] === el) {
                                staggerIndex = j;
                                break;
                            }
                        }
                    }
                }

                var delay = staggerIndex * 80;
                el.style.animationDelay = delay + "ms";

                el.classList.add("is-revealed");
                observer.unobserve(el);
            });
        }, revealOptions);

        scrollElements.forEach(function (el) {
            observer.observe(el);
        });
    }

    // Wait for DOM to be ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initScrollReveal);
    } else {
        initScrollReveal();
    }

    // Expose for manual initialization if needed
    window.ScrollReveal = {
        init: initScrollReveal
    };
})();

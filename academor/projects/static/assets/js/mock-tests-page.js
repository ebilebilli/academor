(function () {
    function reveal(root) {
        var nodes = (root || document).querySelectorAll('.mock-tests-reveal');
        if (!nodes.length) {
            return;
        }

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            nodes.forEach(function (el) {
                el.classList.add('is-in');
            });
            return;
        }

        if (!('IntersectionObserver' in window)) {
            nodes.forEach(function (el) {
                el.classList.add('is-in');
            });
            return;
        }

        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    entry.target.classList.add('is-in');
                    observer.unobserve(entry.target);
                });
            },
            {
                root: null,
                rootMargin: '0px 0px -8% 0px',
                threshold: 0.12,
            }
        );

        nodes.forEach(function (el) {
            observer.observe(el);
        });
    }

    function boot() {
        reveal(document);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();

/**
 * Branded lazy frames: fade real image in when loaded (per-img load/error listeners; IMG load does not bubble).
 */
(function () {
    'use strict';

    function markLoaded(img) {
        var wrap = img.closest('[data-academor-lazy-brand]');
        if (wrap) {
            wrap.classList.add('academor-branded-lazy--loaded');
        }
    }

    document.addEventListener(
        'load',
        function (e) {
            var t = e.target;
            if (t && t.tagName === 'IMG' && t.classList.contains('academor-branded-lazy__img')) {
                markLoaded(t);
            }
        },
        true
    );

    function sweep(root) {
        var scope = root || document;
        scope.querySelectorAll('img.academor-branded-lazy__img').forEach(function (img) {
            if (img.complete && img.naturalWidth) {
                markLoaded(img);
            } else {
                /* IMG "load" does not bubble; document capture listener never sees it */
                img.addEventListener(
                    'load',
                    function () {
                        markLoaded(img);
                    },
                    { once: true }
                );
                img.addEventListener(
                    'error',
                    function () {
                        markLoaded(img);
                    },
                    { once: true }
                );
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            sweep();
        });
    } else {
        sweep();
    }
})();

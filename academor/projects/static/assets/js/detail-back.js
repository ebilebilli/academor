(function () {
    'use strict';

    var STORAGE_KEY = 'academor:return-state';

    var DETAIL_PATH =
        /^\/(?:courses|team|blog|abroad|tests|topics)\/[^/]+\/?$|^\/abroad\/universities\/[^/]+\/?$/;

    function parseUrl(href) {
        try {
            return new URL(href, window.location.origin);
        } catch (err) {
            return null;
        }
    }

    function isDetailPath(pathname) {
        return DETAIL_PATH.test(pathname);
    }

    function isSameOriginReferrer() {
        if (!document.referrer) {
            return false;
        }
        var ref = parseUrl(document.referrer);
        return ref && ref.origin === window.location.origin;
    }

    function saveReturnState() {
        try {
            sessionStorage.setItem(
                STORAGE_KEY,
                JSON.stringify({
                    url: window.location.href,
                    scrollY: window.scrollY,
                    hash: window.location.hash || '',
                })
            );
        } catch (err) {
            /* ignore */
        }
    }

    function isBackForwardNavigation() {
        var entries = window.performance && window.performance.getEntriesByType;
        if (entries) {
            var nav = window.performance.getEntriesByType('navigation')[0];
            if (nav && nav.type === 'back_forward') {
                return true;
            }
        }
        var legacy = window.performance && window.performance.navigation;
        return !!(legacy && legacy.type === 2);
    }

    function clearStaleReturnState() {
        try {
            var raw = sessionStorage.getItem(STORAGE_KEY);
            if (!raw) {
                return;
            }
            var state = JSON.parse(raw);
            var current = window.location.href;
            var same =
                state.url === current ||
                state.url === window.location.pathname + window.location.search;
            if (same) {
                sessionStorage.removeItem(STORAGE_KEY);
            }
        } catch (err) {
            sessionStorage.removeItem(STORAGE_KEY);
        }
    }

    function restoreReturnState() {
        var raw;
        try {
            raw = sessionStorage.getItem(STORAGE_KEY);
        } catch (err) {
            return;
        }
        if (!raw) {
            return;
        }
        try {
            var state = JSON.parse(raw);
            var current = window.location.href;
            var same =
                state.url === current ||
                state.url === window.location.pathname + window.location.search;
            if (!same) {
                return;
            }
            sessionStorage.removeItem(STORAGE_KEY);
            window.requestAnimationFrame(function () {
                if (state.hash) {
                    var target = document.querySelector(state.hash);
                    if (target) {
                        target.scrollIntoView({ block: 'start', behavior: 'auto' });
                        return;
                    }
                }
                if (typeof state.scrollY === 'number' && state.scrollY > 0) {
                    window.scrollTo(0, state.scrollY);
                }
            });
        } catch (err) {
            sessionStorage.removeItem(STORAGE_KEY);
        }
    }

    function shouldUseHistoryBack() {
        if (window.history.length <= 1) {
            return false;
        }
        if (isSameOriginReferrer()) {
            return true;
        }
        try {
            return !!sessionStorage.getItem(STORAGE_KEY);
        } catch (err) {
            return window.history.length > 1;
        }
    }

    function goBack(fallbackHref) {
        if (shouldUseHistoryBack()) {
            window.history.back();
            return;
        }
        if (fallbackHref) {
            window.location.href = fallbackHref;
        }
    }

    document.addEventListener('click', function (event) {
        var backLink = event.target.closest('[data-history-back]');
        if (backLink) {
            event.preventDefault();
            goBack(backLink.getAttribute('href'));
            return;
        }

        var link = event.target.closest('a[href]');
        if (!link || link.hasAttribute('data-history-back')) {
            return;
        }
        if (link.target === '_blank' || event.metaKey || event.ctrlKey || event.shiftKey) {
            return;
        }
        if (link.hasAttribute('download')) {
            return;
        }

        var dest = parseUrl(link.href);
        if (!dest || dest.origin !== window.location.origin) {
            return;
        }
        if (!isDetailPath(dest.pathname) || isDetailPath(window.location.pathname)) {
            return;
        }

        saveReturnState();
    });

    window.addEventListener('pageshow', function (event) {
        if (event.persisted || isBackForwardNavigation()) {
            restoreReturnState();
            return;
        }
        if (!isDetailPath(window.location.pathname)) {
            clearStaleReturnState();
        }
    });
})();

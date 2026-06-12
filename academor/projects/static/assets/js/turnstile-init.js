(function () {
    function getSitekey() {
        var inline = document.querySelector('.cf-turnstile[data-sitekey]');
        if (inline) {
            return inline.getAttribute('data-sitekey') || '';
        }
        var host = document.querySelector('[data-turnstile-site-key]');
        if (host) {
            return host.getAttribute('data-turnstile-site-key') || '';
        }
        return '';
    }

    function isInsideHiddenModal(el) {
        var modal = el.closest('.modal');
        return modal && !modal.classList.contains('show');
    }

    function removeDeferred(el) {
        if (!el || !window.turnstile) {
            return;
        }
        var widgetId = el.getAttribute('data-turnstile-widget-id');
        if (widgetId) {
            try {
                turnstile.remove(widgetId);
            } catch (e) {
                /* ignore */
            }
        }
        el.removeAttribute('data-turnstile-rendered');
        el.removeAttribute('data-turnstile-widget-id');
        el.innerHTML = '';
    }

    function renderDeferred(el, sitekey) {
        if (!window.turnstile || !el || !sitekey) {
            return;
        }
        if (el.getAttribute('data-turnstile-rendered') === '1') {
            return;
        }
        try {
            var widgetId = turnstile.render(el, {
                sitekey: sitekey,
                theme: 'light',
                size: 'normal',
                callback: function () {
                    el.dispatchEvent(
                        new CustomEvent('turnstile:success', { bubbles: true })
                    );
                },
                'expired-callback': function () {
                    el.dispatchEvent(
                        new CustomEvent('turnstile:expired', { bubbles: true })
                    );
                },
            });
            el.setAttribute('data-turnstile-rendered', '1');
            el.setAttribute('data-turnstile-widget-id', String(widgetId));
        } catch (e) {
            /* ignore */
        }
    }

    function loadTurnstileScript(cb) {
        if (window.turnstile) {
            cb();
            return;
        }
        var s = document.createElement('script');
        s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
        s.async = true;
        s.onload = cb;
        document.head.appendChild(s);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var sitekey = getSitekey();
        var hasInline = document.querySelector('.cf-turnstile');
        var deferred = Array.prototype.slice.call(
            document.querySelectorAll('[data-turnstile-deferred]')
        );
        if (!hasInline && deferred.length === 0) {
            return;
        }
        if (!sitekey && deferred.length) {
            return;
        }

        loadTurnstileScript(function () {
            deferred.forEach(function (el) {
                if (!isInsideHiddenModal(el)) {
                    renderDeferred(el, sitekey);
                }
            });
        });

        function bindDeferredTurnstileOnModal(modalId) {
            var modalEl = document.getElementById(modalId);
            if (!modalEl) {
                return;
            }
            modalEl.addEventListener('shown.bs.modal', function () {
                loadTurnstileScript(function () {
                    var modalDeferred = modalEl.querySelectorAll(
                        '[data-turnstile-deferred]'
                    );
                    modalDeferred.forEach(function (el) {
                        if (el.getAttribute('data-turnstile-rendered') !== '1') {
                            renderDeferred(el, sitekey);
                        }
                    });
                });
            });
            modalEl.addEventListener('hidden.bs.modal', function () {
                modalEl.querySelectorAll('[data-turnstile-deferred]').forEach(
                    removeDeferred
                );
            });
        }

        bindDeferredTurnstileOnModal('reviewFormModal');
    });
})();

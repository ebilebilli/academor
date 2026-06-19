(function () {
    'use strict';

    var booted = false;

    function getIconUrl() {
        var scriptEl = document.querySelector('script[data-plyr-icon]');
        return scriptEl ? scriptEl.getAttribute('data-plyr-icon') : '';
    }

    function bindTap(el, handler) {
        if (!el) return;
        el.addEventListener('pointerup', function (evt) {
            if (evt.pointerType === 'mouse' && evt.button !== 0) return;
            handler(evt);
        });
        el.addEventListener('keydown', function (evt) {
            if (evt.key !== 'Enter' && evt.key !== ' ') return;
            evt.preventDefault();
            handler(evt);
        });
    }

    function initAboutVideoPlayers() {
        document.querySelectorAll('[data-about-vp]').forEach(function (root) {
            if (root.dataset.aboutVpInit === '1') return;

            var video = root.querySelector('video');
            var cover = root.querySelector('.about-vp__cover');
            var playBtn = root.querySelector('.about-vp__play-btn');
            if (!video) return;

            root.dataset.aboutVpInit = '1';
            root.classList.remove('is-playing');

            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');

            function revealPlayer() {
                root.classList.add('is-playing');
            }

            function hidePlayer() {
                root.classList.remove('is-playing');
            }

            function runPlay(playFn) {
                var result;
                try {
                    result = playFn();
                } catch (err) {
                    hidePlayer();
                    return;
                }
                if (result && typeof result.then === 'function') {
                    result.catch(function () {
                        hidePlayer();
                    });
                }
            }

            var player = null;
            if (typeof Plyr !== 'undefined') {
                try {
                    player = new Plyr(video, {
                        iconUrl: getIconUrl() || 'https://cdn.jsdelivr.net/npm/plyr@3.7.8/dist/plyr.svg',
                        loadSprite: true,
                        clickToPlay: true,
                        controls: ['play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'fullscreen'],
                        resetOnEnd: true,
                    });
                } catch (err) {
                    player = null;
                }
            }

            function startPlayback(evt) {
                if (evt) {
                    evt.preventDefault();
                    evt.stopPropagation();
                }
                revealPlayer();
                if (player) {
                    runPlay(function () {
                        return player.play();
                    });
                    return;
                }
                video.controls = true;
                runPlay(function () {
                    return video.play();
                });
            }

            bindTap(cover, startPlayback);
            bindTap(playBtn, startPlayback);

            if (player) {
                player.on('play', revealPlayer);
                player.on('ended', function () {
                    player.stop();
                    hidePlayer();
                });
            } else {
                video.addEventListener('play', revealPlayer);
                video.addEventListener('ended', function () {
                    video.pause();
                    video.currentTime = 0;
                    hidePlayer();
                });
                video.addEventListener('pause', function () {
                    if (video.ended || video.currentTime === 0) {
                        hidePlayer();
                    }
                });
            }
        });
    }

    function boot() {
        if (booted) {
            initAboutVideoPlayers();
            return;
        }
        booted = true;
        initAboutVideoPlayers();
    }

    function bootWhenReady() {
        if (typeof Plyr !== 'undefined') {
            boot();
            return;
        }

        var attempts = 0;
        var timer = window.setInterval(function () {
            attempts += 1;
            if (typeof Plyr !== 'undefined' || attempts >= 50) {
                window.clearInterval(timer);
                boot();
            }
        }, 60);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootWhenReady);
    } else {
        bootWhenReady();
    }

    window.addEventListener('load', boot);
})();

(function () {
    'use strict';

    function initAboutVideoPlayers() {
        if (typeof Plyr === 'undefined') {
            return;
        }

        var scriptEl = document.currentScript
            || document.querySelector('script[data-plyr-icon]');
        var iconUrl = scriptEl ? scriptEl.getAttribute('data-plyr-icon') : '';

        document.querySelectorAll('[data-about-vp]').forEach(function (root) {
            var video = root.querySelector('video');
            var cover = root.querySelector('.about-vp__cover');
            var playBtn = root.querySelector('.about-vp__play-btn');
            if (!video) {
                return;
            }

            root.classList.remove('is-playing');

            var player = new Plyr(video, {
                iconUrl: iconUrl || 'https://cdn.jsdelivr.net/npm/plyr@3.7.8/dist/plyr.svg',
                loadSprite: true,
                clickToPlay: false,
                controls: ['play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'fullscreen'],
                resetOnEnd: true,
            });

            function startPlayback(evt) {
                if (evt) {
                    evt.preventDefault();
                    evt.stopPropagation();
                }
                player.play();
            }

            if (cover) {
                cover.addEventListener('click', startPlayback);
            }
            if (playBtn) {
                playBtn.addEventListener('click', startPlayback);
            }

            player.on('play', function () {
                root.classList.add('is-playing');
            });

            player.on('ended', function () {
                player.stop();
                root.classList.remove('is-playing');
            });
        });
    }

    function boot() {
        initAboutVideoPlayers();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();

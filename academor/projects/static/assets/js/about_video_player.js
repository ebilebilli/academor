(function () {
    'use strict';

    var scriptEl = document.currentScript
                || document.querySelector('script[data-plyr-icon]');
    var iconUrl  = scriptEl ? scriptEl.getAttribute('data-plyr-icon') : '';

    document.querySelectorAll('[data-about-vp]').forEach(function (root) {
        var video  = root.querySelector('video');
        var cover  = root.querySelector('.about-vp__cover');
        var playBtn = root.querySelector('.about-vp__play-btn');
        if (!video) return;

        var player = new Plyr(video, {
            iconUrl   : iconUrl || 'https://cdn.jsdelivr.net/npm/plyr@3.7.8/dist/plyr.svg',
            loadSprite: true,
            controls  : ['play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'fullscreen'],
            resetOnEnd: true,
        });

        /* Cover overlay: click → play */
        if (cover) {
            cover.addEventListener('click', function () {
                player.play();
            });
        }

        /* Video başlayanda cover-i gizlə */
        player.on('play', function () {
            root.classList.add('is-playing');
        });

        /* Video bitəndə cover-i geri gətir */
        player.on('ended', function () {
            player.stop();
            root.classList.remove('is-playing');
        });
    });
})();

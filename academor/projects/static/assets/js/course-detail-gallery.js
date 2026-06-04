(function () {
    var root = document.getElementById('course-detail-gallery');
    if (!root) {
        return;
    }

    var dataEl = document.getElementById('course-detail-gallery-data');
    var images = [];
    try {
        images = dataEl ? JSON.parse(dataEl.textContent) : [];
    } catch (e) {
        images = [];
    }

    var frame = root.querySelector('.course-detail-gallery__frame');
    var img = root.querySelector('.course-detail-gallery__img');
    var empty = root.querySelector('.course-detail-gallery__empty');
    var prev = root.querySelector('[data-gallery-prev]');
    var next = root.querySelector('[data-gallery-next]');
    var counter = root.querySelector('[data-gallery-counter]');
    var dots = root.querySelectorAll('.course-detail-gallery__dot');
    var title = root.getAttribute('data-gallery-title') || '';
    var imageLabelBase = root.getAttribute('data-image-label') || 'Image';

    function setNavState() {
        var n = images.length;
        var disabled = n <= 1;
        if (prev) {
            prev.disabled = disabled;
            prev.setAttribute('aria-disabled', disabled ? 'true' : 'false');
            prev.classList.toggle('is-disabled', disabled);
        }
        if (next) {
            next.disabled = disabled;
            next.setAttribute('aria-disabled', disabled ? 'true' : 'false');
            next.classList.toggle('is-disabled', disabled);
        }
    }

    function syncDots(idx) {
        for (var d = 0; d < dots.length; d++) {
            var on = d === idx;
            dots[d].classList.toggle('is-active', on);
            dots[d].setAttribute('aria-selected', on ? 'true' : 'false');
        }
    }

    var galleryInitialized = false;

    function applyFrameAspectFromImg() {
        if (!frame || !img || img.classList.contains('d-none')) {
            return;
        }
        var w = img.naturalWidth;
        var h = img.naturalHeight;
        if (w > 0 && h > 0) {
            frame.style.aspectRatio = w + ' / ' + h;
        }
    }

    function resetFrameAspect() {
        if (frame) {
            frame.style.removeProperty('aspect-ratio');
        }
    }

    if (img) {
        img.addEventListener('load', applyFrameAspectFromImg);
        img.addEventListener('error', resetFrameAspect);
    }

    function show(i) {
        if (!images.length) {
            if (img) {
                img.classList.add('d-none');
            }
            if (empty) {
                empty.classList.remove('d-none');
                empty.classList.add('d-flex');
            }
            if (counter) {
                counter.textContent = '';
            }
            resetFrameAspect();
            setNavState();
            return;
        }
        var idx = ((i % images.length) + images.length) % images.length;
        if (empty) {
            empty.classList.add('d-none');
            empty.classList.remove('d-flex');
        }
        if (img) {
            img.classList.remove('d-none');
            var alt = title
                ? title + ' — ' + (idx + 1)
                : imageLabelBase + ' ' + (idx + 1);
            var useFade = galleryInitialized && images.length > 1;
            if (useFade) {
                img.classList.add('is-fading');
                window.setTimeout(function () {
                    img.src = images[idx];
                    img.alt = alt;
                    img.classList.remove('is-fading');
                    window.requestAnimationFrame(function () {
                        if (img.complete && img.naturalWidth) {
                            applyFrameAspectFromImg();
                        }
                    });
                }, 100);
            } else {
                img.src = images[idx];
                img.alt = alt;
                window.requestAnimationFrame(function () {
                    if (img.complete && img.naturalWidth) {
                        applyFrameAspectFromImg();
                    }
                });
            }
        }
        if (counter) {
            counter.textContent = idx + 1 + ' / ' + images.length;
        }
        root.dataset.galleryIndex = String(idx);
        syncDots(idx);
        setNavState();
        galleryInitialized = true;
    }

    show(0);
    window.requestAnimationFrame(function () {
        if (img && img.complete && img.naturalWidth) {
            applyFrameAspectFromImg();
        }
    });

    if (prev) {
        prev.addEventListener('click', function () {
            show(parseInt(root.dataset.galleryIndex || '0', 10) - 1);
        });
    }
    if (next) {
        next.addEventListener('click', function () {
            show(parseInt(root.dataset.galleryIndex || '0', 10) + 1);
        });
    }
    for (var di = 0; di < dots.length; di++) {
        dots[di].addEventListener('click', function () {
            var j = parseInt(this.getAttribute('data-dot-idx'), 10);
            if (!isNaN(j)) {
                show(j);
            }
        });
    }
    root.addEventListener('keydown', function (e) {
        if (images.length <= 1) {
            return;
        }
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            if (prev) {
                prev.click();
            }
        }
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            if (next) {
                next.click();
            }
        }
    });
})();

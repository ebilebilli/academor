(function () {
    "use strict";

    var SCRAMBLE_CHARS = "!<>-_/\\[]{}@#$%^&*";
    var WORD_MS = 600;
    var GAP_MS = 250;
    var CURSOR_HIDE_MS = 1500;

    function delay(ms) {
        return new Promise(function (resolve) {
            setTimeout(resolve, ms);
        });
    }

    function scrambleWord(el, target, duration) {
        var len = target.length;
        var start = performance.now();

        return new Promise(function (resolve) {
            function tick(now) {
                var progress = Math.min((now - start) / duration, 1);
                var revealed = Math.floor(progress * len);
                var out = "";

                for (var i = 0; i < len; i++) {
                    if (i < revealed) {
                        out += target.charAt(i);
                    } else {
                        out += SCRAMBLE_CHARS.charAt(
                            Math.floor(Math.random() * SCRAMBLE_CHARS.length)
                        );
                    }
                }

                el.textContent = out;

                if (progress < 1) {
                    requestAnimationFrame(tick);
                } else {
                    el.textContent = target;
                    resolve();
                }
            }

            requestAnimationFrame(tick);
        });
    }

    function revealDot(wrapper) {
        var dot = wrapper && wrapper.querySelector(".hbh-dot");
        if (dot) {
            dot.classList.add("is-visible");
        }
    }

    function showFinalState(root, cursor) {
        var words = root.querySelectorAll(".word-text");
        words.forEach(function (el) {
            var target = el.getAttribute("data-word") || "";
            el.textContent = target;
            revealDot(el.closest(".word-wrapper"));
        });
        if (cursor) {
            cursor.classList.remove("is-active");
            cursor.classList.add("is-done");
        }
        root.classList.add("is-complete");
    }

    async function runTaglineScramble() {
        var root = document.querySelector(".hbh-tagline-scramble");
        if (!root || root.dataset.scrambleInit === "1") {
            return;
        }
        root.dataset.scrambleInit = "1";

        var wrappers = Array.prototype.slice.call(root.querySelectorAll(".word-wrapper"));
        var cursor = root.querySelector(".hbh-tagline-cursor");

        var reduced =
            window.matchMedia &&
            window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        if (reduced) {
            showFinalState(root, cursor);
            return;
        }

        root.classList.add("is-running");

        for (var i = 0; i < wrappers.length; i++) {
            var wrap = wrappers[i];
            var textEl = wrap.querySelector(".word-text");
            if (!textEl) {
                continue;
            }
            var target = textEl.getAttribute("data-word") || "";
            var dot = wrap.querySelector(".hbh-dot");
            if (dot) {
                dot.classList.remove("is-visible");
            }
            textEl.textContent = "";
            await scrambleWord(textEl, target, WORD_MS);
            revealDot(wrap);
            if (i < wrappers.length - 1) {
                await delay(GAP_MS);
            }
        }

        if (cursor) {
            cursor.classList.add("is-active");
            setTimeout(function () {
                cursor.classList.remove("is-active");
                cursor.classList.add("is-done");
            }, CURSOR_HIDE_MS);
        }

        root.classList.add("is-complete");
        root.classList.remove("is-running");
    }

    function scheduleStart() {
        requestAnimationFrame(function () {
            requestAnimationFrame(runTaglineScramble);
        });
    }

    document.addEventListener("academor:reveal-settled", scheduleStart);
})();

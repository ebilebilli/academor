(function () {
    "use strict";

    var WORD_STAGGER_MS = 70;

    function wrapTaglineWords(block) {
        var textEl = block.querySelector(".page-header__tagline");
        if (!textEl || textEl.dataset.wordsWrapped === "1") {
            return;
        }
        var text = (textEl.textContent || "").trim();
        if (!text) {
            return;
        }
        textEl.dataset.wordsWrapped = "1";
        textEl.textContent = "";

        text.split(/\s+/).forEach(function (word, index) {
            var span = document.createElement("span");
            span.className = "page-tagline-reveal__word";
            span.style.setProperty("--word-delay", index * WORD_STAGGER_MS + "ms");
            span.textContent = word;
            textEl.appendChild(span);
        });
    }

    function reveal(block) {
        block.classList.add("is-revealed");
    }

    function initPageTaglineBlocks() {
        var blocks = document.querySelectorAll("[data-page-tagline-block]");
        if (!blocks.length) {
            return;
        }

        var reduced =
            window.matchMedia &&
            window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        blocks.forEach(function (block) {
            if (block.dataset.taglineRevealInit === "1") {
                return;
            }
            block.dataset.taglineRevealInit = "1";
            wrapTaglineWords(block);

            if (reduced) {
                reveal(block);
                return;
            }

            if (!("IntersectionObserver" in window)) {
                reveal(block);
                return;
            }

            var observer = new IntersectionObserver(
                function (entries, obs) {
                    entries.forEach(function (entry) {
                        if (!entry.isIntersecting) {
                            return;
                        }
                        reveal(entry.target);
                        obs.unobserve(entry.target);
                    });
                },
                { threshold: 0.2, rootMargin: "0px 0px -4% 0px" }
            );

            observer.observe(block);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initPageTaglineBlocks);
    } else {
        initPageTaglineBlocks();
    }
})();

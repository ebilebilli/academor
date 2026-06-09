(function () {
    "use strict";

    var tagline = document.getElementById("hbh-motto");
    if (!tagline || tagline.dataset.revealInit === "1") {
        return;
    }
    tagline.dataset.revealInit = "1";

    var reduced =
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function reveal() {
        tagline.classList.add("is-revealed");
    }

    if (reduced) {
        reveal();
        return;
    }

    if (!("IntersectionObserver" in window)) {
        reveal();
        return;
    }

    var observer = new IntersectionObserver(
        function (entries, obs) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }
                reveal();
                obs.unobserve(tagline);
            });
        },
        { threshold: 0.4, rootMargin: "0px 0px -8% 0px" }
    );

    observer.observe(tagline);
})();

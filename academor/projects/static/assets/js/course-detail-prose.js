(function () {
    "use strict";

    var MAX_SCROLL_PX = 352;

    function initProseScroll(wrap) {
        var inner = wrap.querySelector(".course-detail-prose-wrap__inner");
        if (!inner) return;

        if (inner.scrollHeight > MAX_SCROLL_PX + 24) {
            wrap.classList.add("is-scrollable");
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-prose-scroll]").forEach(initProseScroll);
    });
})();

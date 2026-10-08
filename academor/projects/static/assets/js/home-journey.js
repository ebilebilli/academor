/* Homepage "journey" layer: a flight route BAK → LHR → CDG → JFK drawn down the page
   gutters. Scrolling moves a small plane along it; stops light up as it passes; it lands
   at the Study Abroad section. Purely decorative (aria-hidden), desktop ≥1200px only.

   Motion contract: only transform / opacity change per frame. The route itself is static;
   the "travelled" part is revealed by moving a clip rectangle (transform), not by
   animating stroke-dashoffset. Reduced motion → static route, stops shown, no plane. */
(function () {
    "use strict";

    var root = document.querySelector("[data-home-journey]");
    var main = document.querySelector(".home-page-main");
    if (!root || !main || !window.matchMedia) return;

    var NS = "http://www.w3.org/2000/svg";
    var desktopMQ = window.matchMedia("(min-width: 1200px)");
    var reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");

    /* Stops are pinned to the start of real sections, alternating gutters. The route
       crosses the page only inside the empty band just above each stop's section. */
    var STOPS = [
        { code: "BAK", section: ".about-intro-section", side: "left" },
        { code: "LHR", section: ".home-sales-section", side: "right" },
        { code: "CDG", section: ".hsvc-section", side: "left" },
        /* full-width marquee sits right above Study Abroad: cross before it, fly under it */
        { code: "JFK", section: ".abroad-section", side: "right", crossBefore: ".home-marquee" }
    ];
    var CROSS_BAND = 44;   /* half-height of the S-curve that crosses between gutters */
    var PIN_OFFSET = 28;   /* stop sits this far below its section's top edge */
    var TRAIL = 5;         /* comet-trail dots behind the plane */
    var TRAIL_GAP = 14;    /* px of route between trail dots */

    var svg, routePath, travelledPath, clipRect, plane, trailDots = [], stopEls = [];
    var lut = null;        /* Float32Array [len, x, y] triples, sampled every 4px */
    var stopLens = [];
    var built = false, ticking = false, lastLen = -1;

    function el(name, attrs, parent) {
        var node = document.createElementNS(NS, name);
        for (var k in attrs) node.setAttribute(k, attrs[k]);
        if (parent) parent.appendChild(node);
        return node;
    }

    function measure() {
        var mainRect = main.getBoundingClientRect();
        var top = mainRect.top + window.scrollY;
        var container = main.querySelector(".container");
        var width = main.clientWidth;
        var inner = container ? container.getBoundingClientRect().width : 1296;
        var gutter = Math.max((width - inner) / 2, 24);
        var xs = { left: gutter / 2, right: width - gutter / 2 };
        var points = [];
        for (var i = 0; i < STOPS.length; i++) {
            var s = main.querySelector(STOPS[i].section);
            if (!s) return null;
            var sTop = s.getBoundingClientRect().top + window.scrollY - top;
            var y = sTop + PIN_OFFSET;
            var crossY = y;
            if (STOPS[i].crossBefore) {
                var c = main.querySelector(STOPS[i].crossBefore);
                if (c) crossY = Math.min(y, c.getBoundingClientRect().top + window.scrollY - top - 20);
            }
            points.push({ x: xs[STOPS[i].side], y: y, crossY: crossY, code: STOPS[i].code, side: STOPS[i].side });
        }
        return { width: width, height: main.scrollHeight, points: points };
    }

    /* Vertical runs in a gutter, then a smooth S-curve across the empty band above the
       next section. y never decreases along the path, so y → length is a simple lookup. */
    function buildD(points) {
        var p = points[0];
        var d = "M" + p.x + " " + p.y;
        for (var i = 1; i < points.length; i++) {
            var a = points[i - 1], b = points[i];
            var cy = b.crossY;
            var crossTop = cy - CROSS_BAND * 2;
            d += " L" + a.x + " " + Math.max(crossTop, a.y);
            d += " C" + a.x + " " + (cy - CROSS_BAND * 0.6) + " " + b.x + " " + (cy - CROSS_BAND * 1.4) + " " + b.x + " " + cy;
            if (b.y > cy) d += " L" + b.x + " " + b.y;
        }
        return d;
    }

    function buildLut(path) {
        var total = path.getTotalLength();
        var n = Math.ceil(total / 4) + 1;
        var arr = new Float32Array(n * 3);
        for (var i = 0; i < n; i++) {
            var len = Math.min(i * 4, total);
            var pt = path.getPointAtLength(len);
            arr[i * 3] = len; arr[i * 3 + 1] = pt.x; arr[i * 3 + 2] = pt.y;
        }
        return arr;
    }

    function sampleAt(len) {
        var i = Math.max(0, Math.min(Math.round(len / 4), lut.length / 3 - 1));
        return { x: lut[i * 3 + 1], y: lut[i * 3 + 2], i: i };
    }

    function lenForY(y) {
        var lo = 0, hi = lut.length / 3 - 1;
        if (y <= lut[2]) return 0;
        if (y >= lut[hi * 3 + 2]) return lut[hi * 3];
        while (lo < hi) {
            var mid = (lo + hi) >> 1;
            if (lut[mid * 3 + 2] < y) lo = mid + 1; else hi = mid;
        }
        return lut[lo * 3];
    }

    function angleAt(len) {
        var a = sampleAt(Math.max(len - 6, 0)), b = sampleAt(len + 6);
        return Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
    }

    function build() {
        var m = measure();
        if (!m) return teardown();
        root.textContent = "";
        stopEls = []; trailDots = [];
        svg = el("svg", { width: m.width, height: m.height, viewBox: "0 0 " + m.width + " " + m.height, focusable: "false" }, root);
        var defs = el("defs", {}, svg);
        var clip = el("clipPath", { id: "home-journey-clip" }, defs);
        clipRect = el("rect", { x: 0, y: 0, width: m.width, height: m.height }, clip);

        var d = buildD(m.points);
        routePath = el("path", { d: d, class: "home-journey__route" }, svg);
        travelledPath = el("path", { d: d, class: "home-journey__travelled", "clip-path": "url(#home-journey-clip)" }, svg);
        lut = buildLut(routePath);
        stopLens = m.points.map(function (p) { return lenForY(p.y); });

        m.points.forEach(function (p, i) {
            var g = el("g", { class: "home-journey__stop" + (i === m.points.length - 1 ? " home-journey__stop--final" : ""), transform: "translate(" + p.x + " " + p.y + ")" }, svg);
            el("circle", { r: 9, class: "home-journey__ping" }, g);
            el("circle", { r: 4.5, class: "home-journey__pin" }, g);
            /* the final stop sits right under the marquee band: put its code below the pin */
            var label = el("text", { x: 0, y: p.y > p.crossY ? 24 : -16, "text-anchor": "middle", class: "home-journey__code" }, g);
            label.textContent = p.code;
            stopEls.push(g);
        });

        for (var t = 0; t < TRAIL; t++) {
            trailDots.push(el("circle", { r: 2.2 - t * 0.3, class: "home-journey__trail", style: "opacity:" + (0.55 - t * 0.1) }, svg));
        }
        plane = el("g", { class: "home-journey__plane" }, svg);
        /* soft halo + top-view airliner silhouette, nose pointing to +x, centred on 0,0 */
        el("circle", { r: 17, class: "home-journey__halo" }, plane);
        el("path", {
            d: "M14 0 C14 -1.4 12.6 -2.2 11 -2.2 L4.5 -2.2 L-2.5 -12 L-6 -12 L-2.2 -2.2 L-8.5 -2.2 L-11 -6 L-13.5 -6 L-12 0 L-13.5 6 L-11 6 L-8.5 2.2 L-2.2 2.2 L-6 12 L-2.5 12 L4.5 2.2 L11 2.2 C12.6 2.2 14 1.4 14 0 Z",
            class: "home-journey__plane-body"
        }, plane);

        built = true;
        lastLen = -1;
        root.classList.add("is-ready");
        if (reduceMQ.matches) {
            root.classList.add("is-static");
            stopEls.forEach(function (g) { g.classList.add("is-reached"); });
            clipRect.setAttribute("transform", "scale(1 1)");
            return;
        }
        root.classList.remove("is-static");
        update();
    }

    function teardown() {
        built = false;
        root.textContent = "";
        root.classList.remove("is-ready", "is-static");
    }

    function update() {
        ticking = false;
        if (!built || reduceMQ.matches) return;
        var mainTop = main.getBoundingClientRect().top;          /* viewport coords */
        var focusY = window.innerHeight * 0.55 - mainTop;         /* plane follows reading line */
        var len = lenForY(focusY);
        if (Math.abs(len - lastLen) < 0.5) return;
        lastLen = len;

        var p = sampleAt(len);
        plane.setAttribute("transform", "translate(" + p.x + " " + p.y + ") rotate(" + angleAt(len) + ")");
        for (var t = 0; t < trailDots.length; t++) {
            var q = sampleAt(Math.max(len - (t + 1) * TRAIL_GAP, 0));
            trailDots[t].setAttribute("transform", "translate(" + q.x + " " + q.y + ")");
        }
        /* reveal the solid "travelled" line down to the plane by scaling the clip rect */
        var h = +svg.getAttribute("height") || 1;
        clipRect.setAttribute("transform", "scale(1 " + Math.max(p.y / h, 0) + ")");

        var end = lut[lut.length - 3];
        root.classList.toggle("is-landed", len >= end - 1);
        root.classList.toggle("is-departing", len <= 1);
        for (var s = 0; s < stopEls.length; s++) {
            stopEls[s].classList.toggle("is-reached", len >= stopLens[s] - 2);
        }
    }

    function requestUpdate() {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(update);
    }

    var rebuildTimer = null;
    function scheduleRebuild() {
        clearTimeout(rebuildTimer);
        rebuildTimer = setTimeout(function () {
            if (desktopMQ.matches) build(); else teardown();
        }, 150);
    }

    function start() {
        if (desktopMQ.matches) build();
        window.addEventListener("scroll", requestUpdate, { passive: true });
        window.addEventListener("resize", scheduleRebuild, { passive: true });
        window.addEventListener("load", scheduleRebuild);
        /* section heights settle late (images, content-visibility) — rebuild when main resizes */
        if ("ResizeObserver" in window) {
            var lastH = 0;
            new ResizeObserver(function (entries) {
                var h = entries[0].contentRect.height;
                if (Math.abs(h - lastH) > 8) { lastH = h; scheduleRebuild(); }
            }).observe(main);
        }
        var onChange = function () { scheduleRebuild(); };
        if (desktopMQ.addEventListener) {
            desktopMQ.addEventListener("change", onChange);
            reduceMQ.addEventListener("change", onChange);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();

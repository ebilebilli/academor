/* Homepage "journey" layer: a flight route BAK → LHR → CDG → JFK drawn down the page
   gutters. A real airliner (Adobe Stock photo, background removed with Adobe Photoshop API)
   flies it as you scroll: it takes off at the first stop, weaves gently down the gutters,
   banks through wide turns between them, leaves dissipating contrails and lands at the
   Study Abroad section. Purely decorative (aria-hidden), desktop ≥1200px only.

   Motion contract
   - Per frame only transform / opacity change (plane, shadow, contrail puffs, clip rect).
   - Scroll sets a *target* distance; the plane follows it with a critically damped spring,
     so fast scrolls ease in and out instead of jumping. Heading and bank are smoothed too:
     reverse the scroll and the plane turns round instead of flying backwards.
   - The loop only runs while something is still moving, then stops.
   - Reduced motion → static route with every stop shown, no plane. */
(function () {
    "use strict";

    var root = document.querySelector("[data-home-journey]");
    var main = document.querySelector(".home-page-main");
    if (!root || !main || !window.matchMedia) return;

    var NS = "http://www.w3.org/2000/svg";
    var desktopMQ = window.matchMedia("(min-width: 1200px)");
    var reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
    var PLANE_SRC = root.getAttribute("data-plane-src");
    var SHADOW_SRC = root.getAttribute("data-shadow-src");

    /* Stops are pinned to the start of real sections. Several homepage sections are
       conditional (About only when shown on the homepage, Sales only when a sale is live),
       so stops are picked from whichever candidates exist, in page order. The last stop is
       always Study Abroad (JFK); sides alternate backwards from it so JFK lands on the right. */
    var CANDIDATES = [
        ".about-intro-section",
        ".home-sales-section",
        ".hsvc-section",
        ".home-prices-section",
        ".home-mock-prices-section"
    ];
    var FINAL = { section: ".abroad-section", crossBefore: ".home-marquee" };
    var CODES = ["BAK", "LHR", "CDG"];   /* departures, in order; final is JFK */

    var PIN_OFFSET = 28;     /* stop sits this far below its section's top edge */
    var CROSS_BAND = 110;    /* vertical room the turn between gutters takes */
    var WEAVE_STEP = 240;    /* px between gentle left/right drifts inside a gutter */
    var LUT_STEP = 3;        /* px of route between lookup-table samples */

    /* Plane art: 360×287 sprite, nose → +x. Shadow sprite has 14px padding at 180px wide. */
    var ART_RATIO = 287 / 360;
    var SHADOW_SCALE = 208 / 180;

    /* Spring + feel */
    var OMEGA = 7.5;             /* spring stiffness (rad/s); ~0.5s to settle, no overshoot */
    var MAX_SPEED = 3200;        /* px/s cap so long jumps still read as flight */
    var TURN_RATE = 7;           /* heading smoothing (1/s) */
    var BANK_GAIN = 0.11;        /* degrees of bank per deg/s of turn rate */
    var MAX_BANK = 38;
    var TAKEOFF = 260;           /* px of route over which the plane climbs / descends */
    var PUFF_EVERY = 11;         /* px of travel between contrail puffs */
    var PUFF_POOL = 56;

    var svg, routePath, clipRect, stopEls = [];
    var fx, planeEl, shadowEl, puffs = [], puffIdx = 0;
    var lut = null, lutN = 0, total = 0, stopLens = [];
    var planeLen = 80;
    var built = false, running = false, lastT = 0;
    var state = { len: 0, vel: 0, target: 0, heading: 90, bank: 0, reversed: false, lastPuffLen: 0, lastHeading: 90, y: null };

    function el(name, attrs, parent) {
        var node = document.createElementNS(NS, name);
        for (var k in attrs) node.setAttribute(k, attrs[k]);
        if (parent) parent.appendChild(node);
        return node;
    }

    function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
    function smoothstep(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }
    function angleDiff(a, b) { var d = (b - a) % 360; if (d > 180) d -= 360; if (d < -180) d += 360; return d; }

    function pickStops() {
        var finalEl = main.querySelector(FINAL.section);
        if (!finalEl) return null;
        var finalTop = finalEl.getBoundingClientRect().top;
        var found = [];
        CANDIDATES.forEach(function (sel) {
            var node = main.querySelector(sel);
            if (node && node.getBoundingClientRect().top < finalTop - 200) found.push({ node: node, sel: sel });
        });
        found.sort(function (a, b) { return a.node.getBoundingClientRect().top - b.node.getBoundingClientRect().top; });
        found = found.slice(0, CODES.length);
        if (!found.length) return null;
        var stops = found.map(function (f, i) { return { code: CODES[i], section: f.sel }; });
        stops.push({ code: "JFK", section: FINAL.section, crossBefore: FINAL.crossBefore });
        for (var i = stops.length - 1, side = "right"; i >= 0; i--, side = side === "right" ? "left" : "right") {
            stops[i].side = side;
        }
        return stops;
    }

    function measure() {
        var mainRect = main.getBoundingClientRect();
        var top = mainRect.top + window.scrollY;
        var container = main.querySelector(".container");
        var width = main.clientWidth;
        var inner = container ? container.getBoundingClientRect().width : 1296;
        var gutter = Math.max((width - inner) / 2, 24);
        var xs = { left: gutter / 2, right: width - gutter / 2 };
        var STOPS = pickStops();
        if (!STOPS) return null;
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
        return { width: width, height: main.scrollHeight, gutter: gutter, points: points };
    }

    /* Waypoints: from each stop the route runs down its gutter with a gentle weave, then
       swings across to the next gutter in one wide turn just above the next section. */
    function waypoints(points, gutter) {
        var weave = clamp(gutter * 0.16, 4, 16);
        var wp = [{ x: points[0].x, y: points[0].y - 90 }, { x: points[0].x, y: points[0].y }];
        for (var i = 1; i < points.length; i++) {
            var a = points[i - 1], b = points[i];
            var turnTop = b.crossY - CROSS_BAND;
            var runway = turnTop - a.y;
            var steps = Math.max(Math.floor(runway / WEAVE_STEP), 0);
            for (var k = 1; k <= steps; k++) {
                var y = a.y + (runway * k) / (steps + 1);
                wp.push({ x: a.x + (k % 2 ? weave : -weave) * (a.side === "left" ? 1 : -1), y: y });
            }
            wp.push({ x: a.x, y: Math.max(turnTop, a.y + 20) });
            wp.push({ x: b.x, y: b.crossY });
            if (b.y > b.crossY + 4) wp.push({ x: b.x, y: b.y });
        }
        var last = wp[wp.length - 1];
        wp.push({ x: last.x, y: last.y + 60 });
        return wp;
    }

    /* Centripetal Catmull-Rom through the waypoints → cubic Béziers: smooth curvature
       everywhere, no overshoot loops at the turns. First and last points are guides only. */
    function catmullRomD(p) {
        function dist(a, b) { return Math.pow(Math.hypot(b.x - a.x, b.y - a.y), 0.5) || 1e-4; }
        var d = "M" + p[1].x.toFixed(1) + " " + p[1].y.toFixed(1);
        for (var i = 1; i < p.length - 2; i++) {
            var p0 = p[i - 1], p1 = p[i], p2 = p[i + 1], p3 = p[i + 2];
            var t1 = dist(p0, p1), t2 = dist(p1, p2), t3 = dist(p2, p3);
            var m1x = t2 * ((p1.x - p0.x) / t1 - (p2.x - p0.x) / (t1 + t2) + (p2.x - p1.x) / t2);
            var m1y = t2 * ((p1.y - p0.y) / t1 - (p2.y - p0.y) / (t1 + t2) + (p2.y - p1.y) / t2);
            var m2x = t2 * ((p2.x - p1.x) / t2 - (p3.x - p1.x) / (t2 + t3) + (p3.x - p2.x) / t3);
            var m2y = t2 * ((p2.y - p1.y) / t2 - (p3.y - p1.y) / (t2 + t3) + (p3.y - p2.y) / t3);
            d += " C" + (p1.x + m1x / 3).toFixed(1) + " " + (p1.y + m1y / 3).toFixed(1) + " " +
                (p2.x - m2x / 3).toFixed(1) + " " + (p2.y - m2y / 3).toFixed(1) + " " +
                p2.x.toFixed(1) + " " + p2.y.toFixed(1);
        }
        return d;
    }

    /* [x, y, monotonic y] per LUT_STEP px of route */
    function buildLut(path) {
        total = path.getTotalLength();
        lutN = Math.ceil(total / LUT_STEP) + 1;
        var arr = new Float32Array(lutN * 3), maxY = -Infinity;
        for (var i = 0; i < lutN; i++) {
            var pt = path.getPointAtLength(Math.min(i * LUT_STEP, total));
            maxY = Math.max(maxY, pt.y);
            arr[i * 3] = pt.x; arr[i * 3 + 1] = pt.y; arr[i * 3 + 2] = maxY;
        }
        return arr;
    }

    function pointAt(len) {
        var f = clamp(len / LUT_STEP, 0, lutN - 1), i = Math.floor(f), j = Math.min(i + 1, lutN - 1), t = f - i;
        return { x: lut[i * 3] + (lut[j * 3] - lut[i * 3]) * t, y: lut[i * 3 + 1] + (lut[j * 3 + 1] - lut[i * 3 + 1]) * t };
    }

    function tangentAt(len) {
        var a = pointAt(len - 10), b = pointAt(len + 10);
        return Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
    }

    function lenForY(y) {
        var lo = 0, hi = lutN - 1;
        if (y <= lut[2]) return 0;
        if (y >= lut[hi * 3 + 2]) return total;
        while (lo < hi) {
            var mid = (lo + hi) >> 1;
            if (lut[mid * 3 + 2] < y) lo = mid + 1; else hi = mid;
        }
        return lo * LUT_STEP;
    }

    function buildFx(width, height) {
        fx = document.createElement("div");
        fx.className = "home-journey__fx";
        puffs = [];
        for (var i = 0; i < PUFF_POOL; i++) {
            var p = document.createElement("span");
            p.className = "home-journey__puff";
            fx.appendChild(p);
            puffs.push(p);
        }
        shadowEl = document.createElement("img");
        shadowEl.className = "home-journey__shadow";
        planeEl = document.createElement("div");
        planeEl.className = "home-journey__plane";
        var art = document.createElement("img");
        art.className = "home-journey__plane-art";
        [shadowEl, art].forEach(function (img) { img.alt = ""; img.decoding = "async"; img.draggable = false; });
        shadowEl.src = SHADOW_SRC;
        art.src = PLANE_SRC;
        planeEl.appendChild(art);
        fx.appendChild(shadowEl);
        fx.appendChild(planeEl);
        root.appendChild(fx);

        var h = planeLen * ART_RATIO;
        planeEl.style.width = planeLen + "px";
        planeEl.style.height = h + "px";
        planeEl.style.marginLeft = (-planeLen / 2) + "px";
        planeEl.style.marginTop = (-h / 2) + "px";
        var sw = planeLen * SHADOW_SCALE, shh = sw * (172 / 208);
        shadowEl.style.width = sw + "px";
        shadowEl.style.height = shh + "px";
        shadowEl.style.marginLeft = (-sw / 2) + "px";
        shadowEl.style.marginTop = (-shh / 2) + "px";
    }

    function build() {
        /* a rebuild (late images, resize) must not teleport the plane: remember where it was */
        var carryY = built && planeEl ? state.y : null;
        var m = measure();
        if (!m) { teardown(); root.setAttribute("data-journey", "off: anchor sections not found"); return; }
        root.textContent = "";
        stopEls = [];
        planeLen = clamp(Math.round(m.gutter * 0.9), 64, 112);
        svg = el("svg", { width: m.width, height: m.height, viewBox: "0 0 " + m.width + " " + m.height, focusable: "false" }, root);
        var defs = el("defs", {}, svg);
        var clip = el("clipPath", { id: "home-journey-clip" }, defs);
        clipRect = el("rect", { x: 0, y: 0, width: m.width, height: m.height }, clip);

        var d = catmullRomD(waypoints(m.points, m.gutter));
        routePath = el("path", { d: d, class: "home-journey__route" }, svg);
        el("path", { d: d, class: "home-journey__travelled", "clip-path": "url(#home-journey-clip)" }, svg);
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

        built = true;
        root.classList.add("is-ready");
        root.setAttribute("data-journey", (reduceMQ.matches ? "static (prefers-reduced-motion)" : "on") + ": " + m.points.map(function (p) { return p.code; }).join(" → "));
        if (reduceMQ.matches || !PLANE_SRC) {
            root.classList.add("is-static");
            stopEls.forEach(function (g) { g.classList.add("is-reached"); });
            return;
        }
        root.classList.remove("is-static");
        buildFx(m.width, m.height);

        state.target = targetLen();
        if (carryY === null) {
            /* first build: start where the reading line already is, no fly-in on page load */
            state.len = state.target;
            state.vel = 0;
            state.heading = tangentAt(state.len);
            state.bank = 0;
            state.reversed = false;
        } else {
            state.len = lenForY(carryY);   /* same spot on the new route; keep speed and heading */
        }
        state.lastHeading = state.heading;
        state.lastPuffLen = state.len;
        render(0);
        if (state.len !== state.target && !running) { running = true; lastT = 0; window.requestAnimationFrame(frame); }
    }

    function offNarrow() {
        teardown();
        root.setAttribute("data-journey", "off: viewport narrower than 1200px");
    }

    function teardown() {
        built = false;
        planeEl = null;
        running = false;
        root.textContent = "";
        root.classList.remove("is-ready", "is-static", "is-landed");
    }

    function targetLen() {
        var mainTop = main.getBoundingClientRect().top;
        return lenForY(window.innerHeight * 0.55 - mainTop);   /* plane follows the reading line */
    }

    /* altitude 0 on the ground at either end of the route, 1 at cruise */
    function altitudeAt(len) {
        return Math.min(smoothstep(len / TAKEOFF), smoothstep((total - len) / TAKEOFF));
    }

    function emitPuffs(p, headingRad, alt) {
        if (alt < 0.35) return;
        /* two contrails from the outer engines, half a wingspan apart, just behind the wing */
        var span = planeLen * ART_RATIO * 0.62;
        var back = planeLen * 0.08;
        var cx = Math.cos(headingRad), cy = Math.sin(headingRad);
        for (var side = -1; side <= 1; side += 2) {
            var x = p.x - cx * back - cy * span * 0.5 * side;
            var y = p.y - cy * back + cx * span * 0.5 * side;
            var puff = puffs[puffIdx = (puffIdx + 1) % puffs.length];
            puff.style.transform = "translate3d(" + x.toFixed(1) + "px," + y.toFixed(1) + "px,0)";
            if (puff.animate) {
                puff.animate([
                    { opacity: 0.5 * alt, transform: "translate3d(" + x.toFixed(1) + "px," + y.toFixed(1) + "px,0) scale(0.35)" },
                    { opacity: 0, transform: "translate3d(" + x.toFixed(1) + "px," + (y + 6).toFixed(1) + "px,0) scale(2.4)" }
                ], { duration: 1400, easing: "cubic-bezier(0.23, 1, 0.32, 1)", fill: "forwards" });
            }
        }
    }

    function render(dt) {
        var len = state.len;
        var p = pointAt(len);
        state.y = p.y;
        var alt = altitudeAt(len);
        var tangent = tangentAt(len);

        /* nose follows the direction of travel; reversing the scroll turns the plane round */
        if (state.vel < -24) state.reversed = true;
        else if (state.vel > 24) state.reversed = false;
        var targetHeading = tangent + (state.reversed ? 180 : 0);
        if (dt > 0) {
            state.heading += angleDiff(state.heading, targetHeading) * (1 - Math.exp(-dt * TURN_RATE));
            var turnRate = angleDiff(state.lastHeading, state.heading) / dt;   /* deg/s */
            var bankTarget = clamp(turnRate * BANK_GAIN, -MAX_BANK, MAX_BANK) * alt;
            state.bank += (bankTarget - state.bank) * (1 - Math.exp(-dt * 6));
        }
        state.lastHeading = state.heading;

        /* banking seen from above: wings foreshorten, the fuselage leans a touch sideways */
        var bankRad = state.bank * Math.PI / 180;
        var wingScale = Math.cos(bankRad);
        var scale = 0.72 + 0.28 * alt;                       /* closer to the camera at cruise */
        var lift = 4 + 18 * alt;                             /* shadow drifts away as it climbs */
        var hd = state.heading.toFixed(2);

        planeEl.style.transform = "translate3d(" + p.x.toFixed(1) + "px," + p.y.toFixed(1) + "px,0) rotate(" + hd +
            "deg) scale(" + scale.toFixed(3) + "," + (scale * wingScale).toFixed(3) + ")";
        shadowEl.style.transform = "translate3d(" + (p.x + lift * 0.55).toFixed(1) + "px," + (p.y + lift).toFixed(1) + "px,0) rotate(" + hd +
            "deg) scale(" + (scale * 0.92).toFixed(3) + "," + (scale * 0.92 * wingScale).toFixed(3) + ")";
        shadowEl.style.opacity = (0.35 + 0.4 * (1 - alt)).toFixed(3);

        if (Math.abs(len - state.lastPuffLen) >= PUFF_EVERY && Math.abs(state.vel) > 40) {
            state.lastPuffLen = len;
            emitPuffs(p, state.heading * Math.PI / 180, alt);
        }

        /* reveal the solid "travelled" line down to the plane by scaling the clip rect */
        var h = +svg.getAttribute("height") || 1;
        clipRect.setAttribute("transform", "scale(1 " + Math.max(p.y / h, 0) + ")");

        root.classList.toggle("is-landed", len >= total - 2);
        for (var s = 0; s < stopEls.length; s++) {
            stopEls[s].classList.toggle("is-reached", len >= stopLens[s] - 2);
        }
    }

    function frame(t) {
        if (!built || reduceMQ.matches) { running = false; return; }
        var dt = lastT ? Math.min((t - lastT) / 1000, 1 / 30) : 1 / 60;
        lastT = t;

        /* critically damped spring toward the scroll target */
        var x = state.len - state.target;
        var acc = -OMEGA * OMEGA * x - 2 * OMEGA * state.vel;
        state.vel = clamp(state.vel + acc * dt, -MAX_SPEED, MAX_SPEED);
        state.len = clamp(state.len + state.vel * dt, 0, total);
        render(dt);

        var settled = Math.abs(state.len - state.target) < 0.25 && Math.abs(state.vel) < 2 &&
            Math.abs(angleDiff(state.heading, tangentAt(state.len) + (state.reversed ? 180 : 0))) < 0.3 &&
            Math.abs(state.bank) < 0.2;
        if (settled) { running = false; lastT = 0; return; }
        window.requestAnimationFrame(frame);
    }

    function onScroll() {
        if (!built || reduceMQ.matches || !planeEl) return;
        state.target = targetLen();
        if (!running) {
            running = true;
            lastT = 0;
            window.requestAnimationFrame(frame);
        }
    }

    var rebuildTimer = null;
    function scheduleRebuild() {
        clearTimeout(rebuildTimer);
        rebuildTimer = setTimeout(function () {
            if (desktopMQ.matches) build(); else offNarrow();
        }, 150);
    }

    function start() {
        if (desktopMQ.matches) build(); else offNarrow();
        window.addEventListener("scroll", onScroll, { passive: true });
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

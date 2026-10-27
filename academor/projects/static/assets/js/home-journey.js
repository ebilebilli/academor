/* Homepage "journey" layer: a flight down the right-hand page gutter, Baku → Paris → London → New York.
   A real airliner (Adobe Stock photo, background removed with the Adobe Photoshop API)
   follows the reading line as you scroll. Each stop is a die-cut sticker of the city's
   landmark (Flame Towers, Big Ben, Eiffel Tower, Statue of Liberty — Adobe Stock photos,
   cut out the same way) that pops when the plane reaches it. Desktop ≥1200px only.

   Motion contract
   - The route stays in the right gutter and is a function of y (a gentle sine weave), so
     position and heading come straight from y: no path-length lookups, no crossings and
     no sudden bursts of speed.
   - Scroll sets a target y; the plane follows with a critically damped spring and a speed
     cap. A jump further than ~1.5 screens (anchor link, Home/End) fades it across instead
     of racing.
   - Per frame only transform / opacity change; the loop stops once everything settles.
   - Reduced motion → static route and stickers, no plane. */
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
    var STICKER_SRC = {
        "Baku": root.getAttribute("data-stop-bak"),
        "Paris": root.getAttribute("data-stop-cdg"),
        "London": root.getAttribute("data-stop-lhr"),
        "New York": root.getAttribute("data-stop-jfk")
    };

    /* Preferred stop sections, in page order; see pickStops() for what happens when some of
       them are not on the page. The last stop is always Study Abroad (New York). */
    var CANDIDATES = [
        ".about-intro-section",
        ".home-sales-section",
        ".hsvc-section",
        ".home-prices-section",
        ".home-mock-prices-section"
    ];
    var FINAL = ".abroad-section";
    var CODES = ["Baku", "Paris", "London"];   /* departures, in order; final is New York */

    var PIN_OFFSET = 56;         /* sticker centre sits this far below its section's top edge */
    var WEAVE_WAVE = 1100;       /* px of page per full left-right-left drift */
    var ART_RATIO = 287 / 360;   /* plane sprite, nose → +x */
    var SHADOW_SCALE = 208 / 180;
    var SHADOW_RATIO = 172 / 208;

    var OMEGA = 6;               /* spring stiffness (rad/s): settles in ~0.6s, no overshoot */
    var MAX_SPEED = 1700;        /* px/s */
    var FAR_JUMP = 1.5;          /* screens; further than this fades across instead of flying */
    var TURN_RATE = 6;           /* heading smoothing (1/s) */
    var CLIMB = 220;             /* px over which the plane climbs after Baku / descends to New York */
    var PUFF_EVERY = 16;         /* px of travel between contrail puffs */
    var PUFF_POOL = 28;

    var svg, fx, planeEl, shadowEl, puffs = [], puffIdx = 0, stops = [];
    var cx = 0, amp = 0, y0 = 0, y1 = 0, planeLen = 72;
    var built = false, running = false, lastT = 0;
    var state = { y: 0, vel: 0, target: 0, heading: 90, reversed: false, lastPuffY: 0, hidden: false, landed: null };

    function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
    function smoothstep(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }
    function angleDiff(a, b) { var d = (b - a) % 360; if (d > 180) d -= 360; if (d < -180) d += 360; return d; }

    /* the route: x as a function of y, easing the weave in after Baku and out before New York */
    function weaveEnv(y) { return Math.min(smoothstep((y - y0) / 300), smoothstep((y1 - y) / 300)); }
    function xAt(y) { return cx + amp * weaveEnv(y) * Math.sin((y - y0) / WEAVE_WAVE * Math.PI * 2); }
    function headingAt(y) { return Math.atan2(2, xAt(y + 1) - xAt(y - 1)) * 180 / Math.PI; }   /* 90 = straight down */
    function altitudeAt(y) { return Math.min(smoothstep((y - y0) / CLIMB), smoothstep((y1 - y) / CLIMB)); }

    /* Always four stops. Preferred sections first; when some are missing (no sale, no price
       packages, About hidden…) the gaps are filled from the other homepage sections, keeping
       stops at least MIN_GAP apart, and as a last resort spaced evenly before New York.
       Returns [{code, top}] with top in document coordinates. */
    var MIN_GAP = 320;
    function pickStops() {
        var finalEl = main.querySelector(FINAL);
        if (!finalEl) return null;
        var sy = window.scrollY;
        var topOf = function (el) { return el.getBoundingClientRect().top + sy; };
        var finalTop = topOf(finalEl);
        var limit = finalTop - 200;
        var tops = [];
        function tryAdd(top) {
            if (top >= limit || tops.length >= CODES.length) return;
            for (var i = 0; i < tops.length; i++) if (Math.abs(tops[i] - top) < MIN_GAP) return;
            tops.push(top);
        }
        CANDIDATES.forEach(function (sel) {
            var node = main.querySelector(sel);
            if (node && node.offsetHeight > 0) tryAdd(topOf(node));
        });
        if (tops.length < CODES.length) {
            Array.prototype.forEach.call(main.children, function (el) {
                if (el === root || el.offsetHeight < 150 || el.matches("script, style")) return;
                tryAdd(topOf(el));
            });
        }
        tops.sort(function (a, b) { return a - b; });
        if (tops.length < CODES.length) {
            /* even spacing between the first stop (or the top of main) and New York */
            var start = tops.length ? tops[0] : topOf(main) + 120;
            var n = CODES.length;
            tops = [];
            for (var k = 0; k < n; k++) tops.push(start + (finalTop - start) * k / n);
        }
        var list = tops.map(function (top, i) { return { code: CODES[i], top: top }; });
        list.push({ code: "New York", top: finalTop });
        return list;
    }

    function make(tag, cls, parent) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (parent) parent.appendChild(node);
        return node;
    }

    function build() {
        var carryY = built && planeEl ? state.y : null;
        var list = pickStops();
        if (!list) { teardown(); root.setAttribute("data-journey", "off: anchor sections not found"); return; }

        var mainTop = main.getBoundingClientRect().top + window.scrollY;
        var width = main.clientWidth;
        var container = main.querySelector(".container");
        var inner = container ? container.getBoundingClientRect().width : 1296;
        var gutter = Math.max((width - inner) / 2, 40);
        cx = width - gutter / 2;
        amp = clamp(gutter * 0.12, 3, 12);
        planeLen = clamp(Math.round(gutter * 0.95), 64, 104);
        var stickerH = clamp(Math.round(gutter * 1.6), 96, 150);
        var stickerW = Math.max(Math.round(gutter * 1.9), 104);   /* wide skylines (Baku) */

        /* the sticker's top edge, even at the 1.12× arrival pop, stays inside its own section
           (the final one sits right under the marquee band, which is drawn above this layer) */
        var pinOffset = Math.max(PIN_OFFSET, Math.round(stickerH * 0.56) + 24);
        stops = list.map(function (s, i) {
            var extra = i === list.length - 1 ? 24 : 0;
            return { code: s.code, y: s.top - mainTop + pinOffset + extra };
        });
        y0 = stops[0].y;
        y1 = stops[stops.length - 1].y;

        root.textContent = "";
        var height = main.scrollHeight;

        /* static route: drawn once, never touched per frame */
        svg = document.createElementNS(NS, "svg");
        svg.setAttribute("width", width);
        svg.setAttribute("height", height);
        svg.setAttribute("focusable", "false");
        var d = "M" + xAt(y0).toFixed(1) + " " + y0.toFixed(1);
        for (var y = y0 + 8; y < y1; y += 8) d += " L" + xAt(y).toFixed(1) + " " + y.toFixed(1);
        d += " L" + xAt(y1).toFixed(1) + " " + y1.toFixed(1);
        var path = document.createElementNS(NS, "path");
        path.setAttribute("d", d);
        path.setAttribute("class", "home-journey__route");
        svg.appendChild(path);
        root.appendChild(svg);

        fx = make("div", "home-journey__fx", root);

        stops.forEach(function (s, i) {
            var wrap = make("div", "home-journey__stop" + (i === stops.length - 1 ? " home-journey__stop--final" : ""), fx);
            wrap.style.transform = "translate3d(" + cx.toFixed(1) + "px," + s.y.toFixed(1) + "px,0)";
            var img = make("img", "home-journey__sticker", wrap);
            img.alt = "";
            img.decoding = "async";
            img.draggable = false;
            img.style.maxHeight = stickerH + "px";
            img.style.maxWidth = stickerW + "px";
            if (STICKER_SRC[s.code]) img.src = STICKER_SRC[s.code];
            var label = make("span", "home-journey__code", wrap);
            label.textContent = s.code;
            label.style.top = (stickerH / 2 + 2) + "px";
            /* keep the sticker and the full city name on screen: nudge left past the edge */
            var keepOnScreen = function (node) {
                var over = cx + node.offsetWidth / 2 - (width - 6);
                node.style.marginLeft = over > 0 ? (-over) + "px" : "";
            };
            keepOnScreen(label);
            if (img.complete) keepOnScreen(img); else img.addEventListener("load", function () { keepOnScreen(img); });
            s.el = wrap;
            s.reached = false;
        });

        built = true;
        root.classList.add("is-ready");
        root.setAttribute("data-journey", (reduceMQ.matches ? "static (prefers-reduced-motion)" : "on") + ": " + stops.map(function (s) { return s.code; }).join(" → "));

        if (reduceMQ.matches || !PLANE_SRC) {
            root.classList.add("is-static");
            stops.forEach(function (s) { s.el.classList.add("is-reached"); });
            return;
        }
        root.classList.remove("is-static");

        puffs = [];
        for (var p = 0; p < PUFF_POOL; p++) puffs.push(make("span", "home-journey__puff", fx));
        shadowEl = make("img", "home-journey__shadow", fx);
        planeEl = make("div", "home-journey__plane", fx);
        var art = make("img", "home-journey__plane-art", planeEl);
        [shadowEl, art].forEach(function (img) { img.alt = ""; img.decoding = "async"; img.draggable = false; });
        shadowEl.src = SHADOW_SRC;
        art.src = PLANE_SRC;
        var ph = planeLen * ART_RATIO;
        planeEl.style.cssText = "width:" + planeLen + "px;height:" + ph + "px;margin:" + (-ph / 2) + "px 0 0 " + (-planeLen / 2) + "px";
        var sw = planeLen * SHADOW_SCALE, sh = sw * SHADOW_RATIO;
        shadowEl.style.cssText = "width:" + sw + "px;height:" + sh + "px;margin:" + (-sh / 2) + "px 0 0 " + (-sw / 2) + "px";

        state.target = targetY();
        if (carryY === null) {
            state.y = state.target;   /* first build: start at the reading line, no fly-in */
            state.vel = 0;
            state.heading = headingAt(state.y);
            state.reversed = false;
        } else {
            state.y = clamp(carryY, y0, y1);
        }
        state.lastPuffY = state.y;
        state.landed = null;
        render(0);
        kick();
    }

    function offNarrow() {
        teardown();
        root.setAttribute("data-journey", "off: viewport narrower than 1200px");
    }

    function teardown() {
        built = false;
        running = false;
        planeEl = null;
        root.textContent = "";
        root.classList.remove("is-ready", "is-static", "is-landed");
    }

    function targetY() {
        return clamp(window.innerHeight * 0.55 - main.getBoundingClientRect().top, y0, y1);
    }

    function emitPuffs(x, y, headingRad, alt) {
        if (alt < 0.4 || !puffs[0].animate) return;
        /* two contrails from the outer engines, either side of the fuselage, behind the wing */
        var half = planeLen * ART_RATIO * 0.3;
        var back = planeLen * 0.1;
        var hx = Math.cos(headingRad), hy = Math.sin(headingRad);
        for (var side = -1; side <= 1; side += 2) {
            var px = x - hx * back - hy * half * side;
            var py = y - hy * back + hx * half * side;
            var puff = puffs[puffIdx = (puffIdx + 1) % puffs.length];
            var at = "translate3d(" + px.toFixed(1) + "px," + py.toFixed(1) + "px,0)";
            puff.animate([
                { opacity: 0.55 * alt, transform: at + " scale(0.4)" },
                { opacity: 0, transform: at + " scale(2.2)" }
            ], { duration: 1200, easing: "cubic-bezier(0.23, 1, 0.32, 1)", fill: "forwards" });
        }
    }

    function render(dt) {
        var y = state.y;
        var x = xAt(y);
        var alt = altitudeAt(y);

        /* nose follows the direction of travel; scrolling back up turns the plane round */
        if (state.vel < -30) state.reversed = true;
        else if (state.vel > 30) state.reversed = false;
        var target = headingAt(y) + (state.reversed ? 180 : 0);
        var prev = state.heading;
        state.heading = dt > 0 ? prev + angleDiff(prev, target) * (1 - Math.exp(-dt * TURN_RATE)) : target;

        /* banking seen from above: the wings foreshorten while the plane turns */
        var turnRate = dt > 0 ? Math.abs(angleDiff(prev, state.heading)) / dt : 0;
        var wing = 1 - Math.min(turnRate / 900, 0.3);
        var scale = 0.74 + 0.26 * alt;          /* climbs towards the camera, descends into JFK */
        var lift = 3 + 16 * alt;                /* shadow drifts away from the plane as it climbs */
        var hd = state.heading.toFixed(2);

        planeEl.style.transform = "translate3d(" + x.toFixed(1) + "px," + y.toFixed(1) + "px,0) rotate(" + hd + "deg) scale(" + scale.toFixed(3) + "," + (scale * wing).toFixed(3) + ")";
        shadowEl.style.transform = "translate3d(" + (x - lift * 0.6).toFixed(1) + "px," + (y + lift).toFixed(1) + "px,0) rotate(" + hd + "deg) scale(" + (scale * 0.9).toFixed(3) + "," + (scale * 0.9 * wing).toFixed(3) + ")";

        if (Math.abs(y - state.lastPuffY) >= PUFF_EVERY && Math.abs(state.vel) > 60) {
            state.lastPuffY = y;
            emitPuffs(x, y, state.heading * Math.PI / 180, alt);
        }

        /* DOM classes only change when a state actually flips */
        for (var s = 0; s < stops.length; s++) {
            var reached = y >= stops[s].y - 4;
            if (reached !== stops[s].reached) { stops[s].reached = reached; stops[s].el.classList.toggle("is-reached", reached); }
        }
        var landed = y >= y1 - 2;
        if (landed !== state.landed) { state.landed = landed; root.classList.toggle("is-landed", landed); }
    }

    function frame(t) {
        if (!built || !planeEl) { running = false; return; }
        var dt = lastT ? Math.min((t - lastT) / 1000, 1 / 30) : 1 / 60;
        lastT = t;

        /* critically damped spring toward the reading line, with a speed cap */
        var acc = -OMEGA * OMEGA * (state.y - state.target) - 2 * OMEGA * state.vel;
        state.vel = clamp(state.vel + acc * dt, -MAX_SPEED, MAX_SPEED);
        state.y = clamp(state.y + state.vel * dt, y0, y1);
        render(dt);

        var settled = Math.abs(state.y - state.target) < 0.3 && Math.abs(state.vel) < 3 &&
            Math.abs(angleDiff(state.heading, headingAt(state.y) + (state.reversed ? 180 : 0))) < 0.3;
        if (settled) { running = false; lastT = 0; return; }
        window.requestAnimationFrame(frame);
    }

    function kick() {
        if (running) return;
        running = true;
        lastT = 0;
        window.requestAnimationFrame(frame);
    }

    function onScroll() {
        if (!built || !planeEl) return;
        state.target = targetY();
        if (Math.abs(state.target - state.y) > window.innerHeight * FAR_JUMP && !state.hidden) {
            /* long jump: fade out, re-appear at the reading line instead of racing there */
            state.hidden = true;
            root.classList.add("is-jumping");
            setTimeout(function () {
                state.y = state.lastPuffY = state.target;
                state.vel = 0;
                state.heading = headingAt(state.y) + (state.reversed ? 180 : 0);
                if (planeEl) render(0);
                root.classList.remove("is-jumping");
                state.hidden = false;
                state.target = targetY();   /* the page may still be scrolling (smooth scroll) */
                kick();
            }, 180);
            return;
        }
        if (!state.hidden) kick();
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

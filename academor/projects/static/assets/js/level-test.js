/* Level test pages (tests.html, test-take.html result): scroll pop-in, 3D card tilt,
   result confetti and the downloadable level sticker drawn on a canvas.
   Styles: assets/css/level-test.css. */
(function () {
    "use strict";

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var root = document.documentElement;

    /* ---- pop-in on scroll ---- */
    var pops = document.querySelectorAll("[data-lt-pop]");
    if (pops.length && "IntersectionObserver" in window && !reduceMotion) {
        root.classList.add("lt-js");
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-in");
                io.unobserve(entry.target);
            });
        }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
        pops.forEach(function (el) { io.observe(el); });
    }

    /* ---- 3D tilt on test cards (mouse only) ---- */
    if (!reduceMotion && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
        document.querySelectorAll("[data-lt-tilt]").forEach(function (card) {
            card.addEventListener("pointermove", function (e) {
                var r = card.getBoundingClientRect();
                var px = (e.clientX - r.left) / r.width - 0.5;
                var py = (e.clientY - r.top) / r.height - 0.5;
                card.style.setProperty("--rx", (px * 10).toFixed(2) + "deg");
                card.style.setProperty("--ry", (-py * 10).toFixed(2) + "deg");
            });
            card.addEventListener("pointerleave", function () {
                card.style.setProperty("--rx", "0deg");
                card.style.setProperty("--ry", "0deg");
            });
        });
    }

    /* ---- result confetti from the coin ---- */
    var stage = document.querySelector(".ltr-stage");
    if (stage && !reduceMotion) {
        var colors = ["#ff5414", "#00313d", "#ff8a5d", "#0e5060", "#ffd3c0", "#25c26e"];
        var frag = document.createDocumentFragment();
        for (var i = 0; i < 42; i++) {
            var bit = document.createElement("span");
            var angle = Math.random() * Math.PI * 2;
            var dist = 120 + Math.random() * 260;
            bit.className = "ltr-confetti";
            bit.style.setProperty("--x0", "130px");
            bit.style.setProperty("--y0", "50%");
            bit.style.setProperty("--dx", Math.round(Math.cos(angle) * dist) + "px");
            bit.style.setProperty("--dy", Math.round(Math.sin(angle) * dist + 80) + "px");
            bit.style.setProperty("--rot", Math.round(Math.random() * 720 - 360) + "deg");
            bit.style.setProperty("--delay", (0.9 + Math.random() * 0.25).toFixed(2) + "s");
            bit.style.setProperty("--c", colors[i % colors.length]);
            if (i % 3 === 0) bit.style.borderRadius = "50%";
            frag.appendChild(bit);
        }
        stage.appendChild(frag);
        setTimeout(function () {
            stage.querySelectorAll(".ltr-confetti").forEach(function (b) { b.remove(); });
        }, 3200);
    }

    /* ---- level sticker (canvas) ---- */
    var canvas = document.querySelector("[data-lt-sticker]");
    if (!canvas || !canvas.getContext) return;

    var TONES = {
        orange: { bg: "#ff5414", ink: "#fff3eb", shade: "#00313d", pill: "#00313d" },
        teal: { bg: "#0e5060", ink: "#fff3eb", shade: "#ff5414", pill: "#0e5060" },
        dark: { bg: "#00313d", ink: "#fff3eb", shade: "#ff5414", pill: "#00313d" }
    };
    var DISPLAY = '"Archivo Black", Impact, "Arial Black", sans-serif';

    function roundRect(ctx, x, y, w, h, r) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.arcTo(x + w, y, x + w, y + h, r);
        ctx.arcTo(x + w, y + h, x, y + h, r);
        ctx.arcTo(x, y + h, x, y, r);
        ctx.arcTo(x, y, x + w, y, r);
        ctx.closePath();
    }

    function fitFont(ctx, text, maxWidth, start, min) {
        var size = start;
        do {
            ctx.font = size + "px " + DISPLAY;
            if (ctx.measureText(text).width <= maxWidth) break;
            size -= 4;
        } while (size > min);
        return size;
    }

    function loadImage(src) {
        return new Promise(function (resolve) {
            var img = new Image();
            img.onload = function () { resolve(img); };
            img.onerror = function () { resolve(null); };
            img.src = src;
        });
    }

    function draw(hand) {
        var d = canvas.dataset;
        var tone = TONES[d.tone] || TONES.orange;
        var ctx = canvas.getContext("2d");
        var W = canvas.width, H = canvas.height;
        ctx.clearRect(0, 0, W, H);
        ctx.save();
        ctx.translate(W / 2, H / 2 + 20);
        ctx.rotate(-0.07);

        var bw = 720, bh = 600, bx = -bw / 2, by = -bh / 2;

        // die-cut white border with a soft lift
        ctx.save();
        ctx.shadowColor = "rgba(0, 49, 61, 0.28)";
        ctx.shadowBlur = 40;
        ctx.shadowOffsetY = 18;
        roundRect(ctx, bx - 30, by - 30, bw + 60, bh + 60, 90);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.restore();

        // body
        roundRect(ctx, bx, by, bw, bh, 64);
        ctx.fillStyle = tone.bg;
        ctx.fill();
        ctx.lineWidth = 8;
        ctx.strokeStyle = "#00313d";
        ctx.stroke();

        // halftone dots in the corner
        ctx.save();
        roundRect(ctx, bx, by, bw, bh, 64);
        ctx.clip();
        ctx.fillStyle = "rgba(255, 255, 255, 0.14)";
        for (var gy = 0; gy < 9; gy++) {
            for (var gx = 0; gx < 9; gx++) {
                var rad = Math.max(0, 9 - (gx + gy) * 0.55);
                if (!rad) continue;
                ctx.beginPath();
                ctx.arc(bx + 40 + gx * 30, by + bh - 40 - gy * 30, rad, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        ctx.restore();

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        // brand line
        ctx.font = "34px " + DISPLAY;
        ctx.fillStyle = tone.ink;
        if ("letterSpacing" in ctx) ctx.letterSpacing = "6px";
        ctx.fillText("ACADEMOR · LEVEL TEST", 0, by + 70);
        if ("letterSpacing" in ctx) ctx.letterSpacing = "0px";

        // level code with a hard offset shadow
        ctx.font = "250px " + DISPLAY;
        ctx.fillStyle = tone.shade;
        ctx.fillText(d.code, 12, -40 + 12);
        ctx.fillStyle = tone.ink;
        ctx.fillText(d.code, 0, -40);

        // slang title
        var titleSize = fitFont(ctx, d.title, bw - 90, 96, 40);
        ctx.font = titleSize + "px " + DISPLAY;
        ctx.fillStyle = tone.shade;
        ctx.fillText(d.title, 5, 135 + 5);
        ctx.fillStyle = tone.ink;
        ctx.fillText(d.title, 0, 135);

        // tag pill
        ctx.save();
        ctx.translate(0, by + bh + 4);
        ctx.rotate(0.05);
        ctx.font = "44px " + DISPLAY;
        var tw = ctx.measureText(d.tag).width + 70;
        roundRect(ctx, -tw / 2, -44, tw, 88, 44);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.lineWidth = 7;
        ctx.strokeStyle = "#00313d";
        ctx.stroke();
        ctx.fillStyle = tone.pill;
        ctx.fillText(d.tag, 0, 2);
        ctx.restore();

        ctx.restore();

        // hand sticker over the top-right corner
        if (hand) {
            var hh = 300, hw = hand.width * (hh / hand.height);
            if (hw > 340) { hw = 340; hh = hand.height * (hw / hand.width); }
            ctx.save();
            ctx.translate(W - 170, 170);
            ctx.rotate(0.22);
            ctx.shadowColor = "rgba(0, 49, 61, 0.3)";
            ctx.shadowBlur = 24;
            ctx.shadowOffsetY = 10;
            ctx.drawImage(hand, -hw / 2, -hh / 2, hw, hh);
            ctx.restore();
        }
    }

    var fontReady = document.fonts && document.fonts.load
        ? document.fonts.load("100px \"Archivo Black\"").catch(function () {})
        : Promise.resolve();
    Promise.all([fontReady, loadImage(canvas.dataset.hand)]).then(function (res) {
        draw(res[1]);
    });

    function toBlob() {
        return new Promise(function (resolve) { canvas.toBlob(resolve, "image/png"); });
    }

    var dl = document.querySelector("[data-lt-sticker-download]");
    if (dl) {
        dl.addEventListener("click", function () {
            toBlob().then(function (blob) {
                if (!blob) return;
                var url = URL.createObjectURL(blob);
                var a = document.createElement("a");
                a.href = url;
                a.download = canvas.dataset.file || "academor-level.png";
                document.body.appendChild(a);
                a.click();
                a.remove();
                setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
            });
        });
    }

    var share = document.querySelector("[data-lt-sticker-share]");
    if (share && navigator.canShare && window.File) {
        var probe = new File([""], "probe.png", { type: "image/png" });
        if (navigator.canShare({ files: [probe] })) {
            share.hidden = false;
            share.addEventListener("click", function () {
                toBlob().then(function (blob) {
                    if (!blob) return;
                    var file = new File([blob], canvas.dataset.file || "academor-level.png", { type: "image/png" });
                    navigator.share({ files: [file], title: "Academor" }).catch(function () {});
                });
            });
        }
    }
})();

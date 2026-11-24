/* Score report (templates/level-exam-result.html, and the English level test result in
   templates/test-take.html): print button, Instagram story card (drawn on a
   canvas, shared on phones or downloaded) and numbers that count up once in step with the scale. */
(function () {
  "use strict";

  /* ---------------------------------------------------------------- Instagram story card */
  var W = 1080;
  var H = 1920;
  var INK = "#00313d";
  var ORANGE = "#ff5414";
  var SAND = "#ede6dc";
  var MUTED = "#52676d";
  var FONT = '"Host Grotesk", "Segoe UI", Arial, sans-serif';

  // "i" must become "İ" in Azerbaijani, so upper-case with the page language
  function upper(text) {
    var lang = document.documentElement.lang || undefined;
    try {
      return String(text || "").toLocaleUpperCase(lang);
    } catch (e) {
      return String(text || "").toUpperCase();
    }
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function fitText(ctx, text, maxWidth, weight, size, minSize) {
    var s = size;
    ctx.font = weight + " " + s + "px " + FONT;
    while (s > minSize && ctx.measureText(text).width > maxWidth) {
      s -= 2;
      ctx.font = weight + " " + s + "px " + FONT;
    }
    return s;
  }

  function wrapLines(ctx, text, maxWidth) {
    var words = String(text || "").split(/\s+/);
    var lines = [];
    var line = "";
    words.forEach(function (word) {
      var test = line ? line + " " + word : word;
      if (ctx.measureText(test).width > maxWidth && line) {
        lines.push(line);
        line = word;
      } else {
        line = test;
      }
    });
    if (line) {
      lines.push(line);
    }
    return lines;
  }

  function loadImage(src) {
    return new Promise(function (resolve) {
      var img = new Image();
      img.onload = function () { resolve(img); };
      img.onerror = function () { resolve(null); };
      img.src = src;
    });
  }

  function drawArt(ctx, art, x, y, w) {
    // the compass illustration as a taped, slightly tilted card in the sand band
    var h = Math.round(w * art.height / art.width);
    var frame = 14;
    ctx.save();
    ctx.translate(x + w / 2, y + h / 2);
    ctx.rotate(0.045);
    ctx.shadowColor = "rgba(0,49,61,0.28)";
    ctx.shadowBlur = 40;
    ctx.shadowOffsetY = 18;
    roundRect(ctx, -w / 2 - frame, -h / 2 - frame, w + frame * 2, h + frame * 2, 34);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.shadowColor = "rgba(0,0,0,0)";
    ctx.save();
    roundRect(ctx, -w / 2, -h / 2, w, h, 24);
    ctx.clip();
    ctx.drawImage(art, -w / 2, -h / 2, w, h);
    ctx.restore();
    ctx.rotate(-0.12);
    ctx.fillStyle = "rgba(255,84,20,0.85)";
    ctx.fillRect(-60, -h / 2 - frame - 22, 120, 40);
    ctx.restore();
  }

  function drawStory(data, logo, art) {
    var canvas = document.createElement("canvas");
    canvas.width = W;
    canvas.height = H;
    var ctx = canvas.getContext("2d");
    var pad = 96;

    // paper + sand band
    ctx.fillStyle = "#fbf9f6";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = SAND;
    ctx.fillRect(0, 0, W, 760);

    var textW = W - pad * 2;
    if (art) {
      var artW = 300;
      drawArt(ctx, art, W - pad - artW + 10, 236, artW);
      textW = W - pad * 2 - artW - 56;
    } else {
      // answer-sheet bubbles, top right
      var bx = W - pad - 4 * 64;
      for (var r = 0; r < 3; r++) {
        for (var c = 0; c < 4; c++) {
          var cx = bx + c * 64 + 26;
          var cy = 150 + r * 64;
          ctx.beginPath();
          ctx.arc(cx, cy, 22, 0, Math.PI * 2);
          var filled = (r === 0 && c === 1) || (r === 1 && c === 3) || (r === 2 && c === 0);
          ctx.fillStyle = filled ? ORANGE : "rgba(0,0,0,0)";
          ctx.fill();
          ctx.lineWidth = 3;
          ctx.strokeStyle = filled ? ORANGE : "rgba(0,49,61,0.35)";
          ctx.stroke();
        }
      }
    }

    // brand
    if (logo) {
      ctx.drawImage(logo, pad - 12, 96, 84, 105);
    }
    ctx.fillStyle = INK;
    ctx.font = "800 56px " + FONT;
    ctx.fillText("Academor", pad + 86, 168);

    // kicker, name, test
    ctx.fillStyle = ORANGE;
    fitText(ctx, upper(data.kicker), textW, "800", 30, 22);
    ctx.fillText(upper(data.kicker), pad, 330);
    ctx.fillStyle = INK;
    fitText(ctx, data.name || "", textW, "800", 120, 56);
    ctx.fillText(data.name || "", pad, 470);
    ctx.fillStyle = MUTED;
    ctx.font = "600 40px " + FONT;
    wrapLines(ctx, data.test, textW).slice(0, 2).forEach(function (line, i) {
      ctx.fillText(line, pad, 560 + i * 52);
    });
    ctx.font = "600 32px " + FONT;
    ctx.fillText(data.date || "", pad, 690);

    // sections
    // sections: sized so the cards, the SAT total and the call to action never overlap
    var y = 820;
    var rows = data.rows || [];
    var multi = rows.length > 1;
    var cardH = multi ? (data.total ? 250 : 300) : 420;
    var valueSize = multi ? 96 : 200;
    rows.forEach(function (row) {
      roundRect(ctx, pad, y, W - pad * 2, cardH, 40);
      ctx.fillStyle = "#ffffff";
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = "rgba(0,49,61,0.12)";
      ctx.stroke();
      ctx.fillStyle = ORANGE;
      ctx.font = "800 30px " + FONT;
      ctx.fillText(upper(row.label), pad + 56, y + 76);
      ctx.fillStyle = INK;
      var size = fitText(ctx, row.value, W - pad * 2 - 112, "800", valueSize, 64);
      ctx.fillText(row.value, pad + 52, y + 104 + size * 0.72);
      ctx.fillStyle = MUTED;
      ctx.font = "600 34px " + FONT;
      ctx.fillText(row.sub || "", pad + 56, y + cardH - 36);
      y += cardH + 30;
    });

    if (data.total) {
      y += 6;
      roundRect(ctx, pad, y, W - pad * 2, 210, 40);
      ctx.fillStyle = INK;
      ctx.fill();
      ctx.fillStyle = "rgba(255,255,255,0.7)";
      ctx.font = "800 28px " + FONT;
      ctx.fillText(upper(data.total_label), pad + 56, y + 70);
      ctx.fillStyle = "#ffffff";
      ctx.font = "800 96px " + FONT;
      ctx.fillText(data.total, pad + 52, y + 170);
      y += 246;
    }

    // call to action
    var ctaY = H - 250;
    roundRect(ctx, pad, ctaY, W - pad * 2, 150, 75);
    ctx.fillStyle = ORANGE;
    ctx.fill();
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.font = "800 40px " + FONT;
    ctx.fillText(data.cta || "", W / 2, ctaY + 66);
    ctx.font = "600 34px " + FONT;
    ctx.fillText(data.site || "", W / 2, ctaY + 116);
    ctx.textAlign = "left";
    return canvas;
  }

  function shareStory(button) {
    var holder = document.getElementById("lx-story-data");
    if (!holder) {
      return;
    }
    var data = JSON.parse(holder.textContent || "{}");
    button.disabled = true;
    var fontsReady = document.fonts && document.fonts.load
      ? Promise.all([
        document.fonts.load('800 60px "Host Grotesk"'),
        document.fonts.load('600 30px "Host Grotesk"'),
      ]).catch(function () {})
      : Promise.resolve();
    Promise.all([fontsReady, loadImage(data.logo), data.art ? loadImage(data.art) : null])
      .then(function (parts) {
        var canvas = drawStory(data, parts[1], parts[2]);
        return new Promise(function (resolve) {
          canvas.toBlob(resolve, "image/png");
        });
      })
      .then(function (blob) {
        if (!blob) {
          throw new Error("no image");
        }
        var name = data.filename || "academor-result.png";
        var file = window.File ? new File([blob], name, { type: "image/png" }) : null;
        if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
          return navigator.share({ files: [file], title: data.test || "Academor" }).catch(function () {});
        }
        var url = URL.createObjectURL(blob);
        var link = document.createElement("a");
        link.href = url;
        link.download = name;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
        return null;
      })
      .catch(function () {
        window.alert(button.getAttribute("data-msg-error") || "Could not create the image.");
      })
      .then(function () {
        button.disabled = false;
      });
  }

  document.addEventListener("click", function (event) {
    var printBtn = event.target.closest && event.target.closest("[data-lx-print]");
    if (printBtn) {
      window.print();
      return;
    }
    var storyBtn = event.target.closest && event.target.closest("[data-lx-story]");
    if (storyBtn) {
      shareStory(storyBtn);
    }
  });

  window.AcademorStoryCard = { draw: drawStory };

  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-lx-count"));
    var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
    if (isNaN(target)) {
      return;
    }
    var duration = 1300;
    var start = null;
    function frame(now) {
      if (start === null) {
        start = now;
      }
      var t = Math.min(1, (now - start) / duration);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (t < 1) {
        window.requestAnimationFrame(frame);
      }
    }
    el.textContent = (0).toFixed(decimals);
    window.setTimeout(function () {
      window.requestAnimationFrame(frame);
    }, 350);
  }

  function init() {
    document.querySelectorAll("[data-lx-count]").forEach(countUp);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

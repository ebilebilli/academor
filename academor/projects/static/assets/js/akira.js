/* AKIRA: the particle orb with Academor's mark, and the comment card. No dependencies. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var TAU = Math.PI * 2;
  var MODES = {
    idle: { wave: 0.3, rotation: 0.05, amplitude: 0.03, voice: 0.15, speed: 0.6 },
    think: { wave: 1.8, rotation: 0.55, amplitude: 0.07, voice: 0.4, speed: 2.2 },
    speak: { wave: 1.2, rotation: 0.14, amplitude: 0.1, voice: 1, speed: 1 }
  };

  function Orb(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.mode = canvas.getAttribute('data-mode') || 'speak';
    this.t = 0;
    this.phase = 69.49;
    this.angle = 18.38;
    this.level = 0;
    this.rings = [];
    this.lastRing = -9;
    this.points = [];
    var count = 240;
    for (var i = 0; i < count; i++) {
      var y = 1 - 2 * (i + 0.5) / count;
      var a = i * Math.PI * (3 - Math.sqrt(5));
      var r = Math.sqrt(1 - y * y);
      this.points.push({ x: Math.cos(a) * r, y: y, z: Math.sin(a) * r, i: i });
    }
    var mark = canvas.getAttribute('data-mark');
    if (mark) {
      this.mark = new Image();
      this.mark.src = mark;
    }
  }

  Orb.prototype.setMode = function (mode) { if (MODES[mode]) this.mode = mode; };

  Orb.prototype.voice = function (dt) {
    var t = this.t, cfg = MODES[this.mode];
    var phrase = Math.min(1, Math.max(0, (Math.sin(t * 0.45) + 0.35) * 1.6));
    var syll = Math.pow(Math.max(0, Math.sin(t * 6.2)), 2) * (0.55 + 0.45 * Math.sin(t * 1.7));
    var target = (syll * 0.8 + 0.12 * Math.abs(Math.sin(t * 13.1)) + 0.06) * phrase * cfg.voice;
    this.level += (target - this.level) * Math.min(1, dt * 10 + 0.02);
    if (this.level > 0.45 * cfg.voice && t - this.lastRing > 0.38) {
      this.rings.push({ b: t, s: this.level / Math.max(cfg.voice, 0.01) });
      this.lastRing = t;
    }
    this.rings = this.rings.filter(function (rg) { return t - rg.b < 1.8; });
  };

  Orb.prototype.draw = function () {
    var c = this.canvas, ctx = this.ctx;
    var W = c.clientWidth, H = c.clientHeight;
    if (!W || !H) return;
    var d = Math.min(window.devicePixelRatio || 1, 2);
    if (c.width !== Math.round(W * d)) { c.width = Math.round(W * d); c.height = Math.round(H * d); }
    ctx.setTransform(d, 0, 0, d, 0, 0);
    ctx.clearRect(0, 0, W, H);
    var cfg = MODES[this.mode], t = this.t, lv = this.level;
    var radius = Math.min(W, H) * 0.29;
    var R = radius * 1.04;
    var cy = Math.cos(this.angle), sy = Math.sin(this.angle), cp = Math.cos(-0.51), sp = Math.sin(-0.51);
    var self = this;

    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    this.rings.forEach(function (rg) {
      var age = (t - rg.b) / 1.8, base = R * (1.1 + age * 0.45);
      ctx.globalAlpha = Math.pow(1 - age, 2) * 0.55 * Math.min(1, rg.s);
      ctx.strokeStyle = '#FF7A45';
      ctx.lineWidth = 1.2 * (1.4 - age);
      ctx.beginPath();
      for (var s = 0; s <= 120; s++) {
        var th = s / 120 * TAU;
        var rr = base + R * 0.02 * rg.s * Math.sin(7 * th + rg.b * 9 + age * 5) + R * 0.012 * Math.sin(13 * th - age * 8);
        var x = W / 2 + Math.cos(th) * rr, y = H / 2 + Math.sin(th) * rr;
        if (s) ctx.lineTo(x, y); else ctx.moveTo(x, y);
      }
      ctx.stroke();
    });
    [['255,84,20', 3, 2.1, 0.16, 0], ['255,234,0', 5, -2.8, 0.11, 1.7], ['244,243,255', 7, 3.6, 0.08, 3.1], ['75,60,255', 4, -1.6, 0.1, 4.4]].forEach(function (b) {
      var amp = R * b[3] * (lv + 0.03);
      var wv = function (th) { return Math.abs(Math.sin(b[1] * th + t * b[2] + b[4]) * (0.6 + 0.4 * Math.sin(2 * th - t * 1.3 + b[4]))); };
      ctx.beginPath();
      for (var s = 0; s <= 120; s++) {
        var th = s / 120 * TAU, rr = R * 1.1 + amp * wv(th);
        if (s) ctx.lineTo(W / 2 + Math.cos(th) * rr, H / 2 + Math.sin(th) * rr); else ctx.moveTo(W / 2 + Math.cos(th) * rr, H / 2 + Math.sin(th) * rr);
      }
      for (var k = 120; k >= 0; k--) {
        var th2 = k / 120 * TAU, r2 = R * 1.1 - amp * 0.35 * wv(th2);
        ctx.lineTo(W / 2 + Math.cos(th2) * r2, H / 2 + Math.sin(th2) * r2);
      }
      ctx.closePath();
      ctx.globalAlpha = 0.2; ctx.fillStyle = 'rgb(' + b[0] + ')'; ctx.fill();
      ctx.globalAlpha = 0.5; ctx.strokeStyle = 'rgb(' + b[0] + ')'; ctx.lineWidth = 0.8; ctx.stroke();
    });
    ctx.restore();

    var projected = this.points.map(function (v) {
      var f = 3;
      var w = 0.56 * Math.sin(v.x * f * 2 + self.phase) * Math.cos(v.y * f - self.phase * 0.7) + 0.44 * Math.sin(v.z * f * 2 - self.phase * 0.8) * Math.cos(v.x * f + self.phase * 0.3);
      var r = 1 + cfg.amplitude * w + lv * 0.07 * Math.sin(Math.atan2(v.z, v.x) * 5 + t * 7) * Math.cos(v.y * 3);
      var x = v.x * r, y = v.y * r, z = v.z * r;
      var xx = x * cy + z * sy, zz = z * cy - x * sy;
      var yy = y * cp - zz * sp, depth = y * sp + zz * cp;
      var scale = 4.8 / (4.8 - depth);
      return { sx: W / 2 + xx * radius * scale, sy: H / 2 + yy * radius * scale, depth: depth, scale: scale };
    });
    projected.sort(function (a, b) { return a.depth - b.depth; });
    projected.forEach(function (p) {
      var depth = Math.max(0, Math.min(1, (p.depth + 1.6) / 3.2));
      var dist = Math.min(1, Math.hypot(p.sx - W / 2, p.sy - H / 2) / (radius * 0.62));
      var zone = self.mark && self.mark.complete ? 0.1 + 0.9 * dist * dist : 1;
      ctx.globalAlpha = (0.2 + 0.8 * depth) * zone;
      ctx.fillStyle = depth > 0.5 ? '#FF5414' : '#F4F3FF';
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, Math.max(0.6, W / 160) * p.scale * (0.5 + depth * 0.6), 0, TAU);
      ctx.fill();
    });
    if (this.mark && this.mark.complete && this.mark.naturalWidth) {
      var mw = radius * 1.05, mh = mw * this.mark.naturalHeight / this.mark.naturalWidth;
      ctx.globalAlpha = 1;
      ctx.drawImage(this.mark, W / 2 - mw / 2, H / 2 - mh / 2, mw, mh);
    }
    ctx.globalAlpha = 1;
  };

  Orb.prototype.step = function (dt) {
    var cfg = MODES[this.mode];
    this.t += dt * cfg.speed;
    this.phase += dt * cfg.wave;
    this.angle += dt * cfg.rotation;
    this.voice(dt);
    this.draw();
  };

  var orbs = [];
  function loop(now) {
    var dt = loop.last ? Math.min((now - loop.last) / 1000, 0.05) : 0;
    loop.last = now;
    orbs.forEach(function (o) { if (o.visible !== false) o.step(dt); });
    window.requestAnimationFrame(loop);
  }

  function startOrbs(root) {
    (root || document).querySelectorAll('canvas[data-akira-orb]').forEach(function (canvas) {
      if (canvas.akiraOrb) return;
      var orb = new Orb(canvas);
      canvas.akiraOrb = orb;
      orbs.push(orb);
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries) { orb.visible = entries[0].isIntersecting; }).observe(canvas);
      }
      if (orb.mark) orb.mark.onload = function () { orb.draw(); };
      orb.draw();
    });
    if (!reduceMotion && orbs.length && !loop.started) {
      loop.started = true;
      window.requestAnimationFrame(loop);
    }
  }

  function csrf(card) {
    var input = card.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function post(card, body) {
    return fetch(card.getAttribute('data-url'), {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf(card), 'X-Requested-With': 'XMLHttpRequest', Accept: 'application/json' },
      body: JSON.stringify(body || {})
    }).then(function (r) { if (!r.ok) throw new Error(String(r.status)); return r.json(); });
  }

  function setOrb(card, mode) {
    var canvas = card.querySelector('canvas[data-akira-orb]');
    if (canvas && canvas.akiraOrb) canvas.akiraOrb.setMode(mode);
  }

  function showComment(card, data) {
    var box = card.querySelector('[data-akira-comment]');
    var p = document.createElement('p');
    p.textContent = data.comment;
    box.appendChild(p);
    box.classList.add('is-ready');
    setOrb(card, 'speak');
    window.setTimeout(function () { setOrb(card, 'idle'); }, 6000);
    var vote = card.querySelector('[data-akira-vote]');
    if (vote && card.getAttribute('data-can-vote') && data.helpful === null) vote.hidden = false;
  }

  function showFallback(card) {
    var box = card.querySelector('[data-akira-comment]');
    if (box) box.hidden = true;
    card.querySelector('[data-akira-fallback]').hidden = false;
    setOrb(card, 'idle');
  }

  function load(card, tries) {
    post(card, {}).then(function (data) {
      if (data.status === 'ready' && data.comment) return showComment(card, data);
      if (data.status === 'pending' && tries < 1) return window.setTimeout(function () { load(card, tries + 1); }, 4000);
      if (data.status === 'none') { card.hidden = true; return; }
      showFallback(card);
    }).catch(function () { showFallback(card); });
  }

  function initCard(card) {
    load(card, 0);
    card.querySelectorAll('[data-akira-helpful]').forEach(function (button) {
      button.addEventListener('click', function () {
        post(card, { helpful: button.getAttribute('data-akira-helpful') === '1' }).catch(function () {});
        card.querySelector('[data-akira-vote]').hidden = true;
        card.querySelector('[data-akira-thanks]').hidden = false;
      });
    });
  }

  function init() {
    startOrbs(document);
    document.querySelectorAll('[data-akira-card]').forEach(initCard);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

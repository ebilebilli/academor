/* Study abroad hero globe (templates/includes/abroad_grid_section.html).
   A 3D world globe on canvas: real land (Natural Earth 1:50m, as a dot grid), flight arcs
   from Baku to the study destinations, and orange energy rings orbiting in 3D.
   Drag to turn it. Pauses off-screen and in background tabs; prefers-reduced-motion
   gets one still frame. */
(function () {
  "use strict";

  /* Land mask: rows from 90N to 90S every STEP degrees, each row has
     round(360 * cos(lat) / STEP) cells; one bit per cell (1 = land). */
  var STEP = 1.2;
  var LAND = "AAAAAAAAAAAAAAAIAAAA2AEAAADwfwABAACw/jAAAQAAvX8wAAgAACjqHwgACAAAEIT+AQAGDgAAAHnwBwAQ+EABADAK8A8AAOADAAAA/hn8AwAg8v8IwP//////////////HzyAJx//AcABeP//HwD/vysd/AHA8KcAAAAA/////////w9QQAAAAAD4/////////0ACBAAAAID8/////////yMGAAAAAAAA+P//3zg4wADe////////P+D///8BBQcAwPv///////9/8P///8EDGAAA3////////68H+Pr//4ADEAAAvv///////z8OAAf+/w94AAAAgI////////8nAgAI4P9/wA8AAABo+P//////P0AAAALw///AHwAAwND8//////9/gAMABAD//z/8AwAAOAT///////9/AAMABAD4///zPwAAQEP1////////D+AAAAAA/P//+38AAEDm//////////8DAwAAAMD//z//DwAA2P3//////////wEBAAAAAP////8PAAAA9///////////LwAAAAAAwP///78AAAAA/P//////////vwAAAAAAAPr////nAAAA6P///////////xcAAAAAAAD9////gwEAAOD///////////8fAAAAAAAA4P///38AAAAA+P///Pj//////w8AAAAAAADg////PwEAAADgn3/08///////PwIAAAAAAAD8////AwAAAADwyT/w+f//////PwwAAAAAAAD4////DwAAAAD8wfgAHv///////+AAAAAAAAAA/v///wMAAAAA/oD5HJ////////8AAAAAAAAAAPz///8DAAAAAPCDyPz/+f////+/BwgAAAAAAAAA/////wAAAAAA/ALI/P/4/////x8ECAAAAAAAAAD4////AQAAAADABzDm/4///////4OAAAAAAAAAAAD+////AAAAAABA8ANC+f///////4/BAQAAAAAAAAD4////AQAAAAAA4h9A0P///////38wHwAAAAAAAAAA/P//PwAAAAAAgP8HAOD///////9/QAMAAAAAAAAAAPD//z8AAAAAAAD/PwCA/////////wcCAAAAAAAAAAAA/v//AwAAAAAA4P8/HPD/////////AQEAAAAAAAAAAAD6//8DAAAAAADg///9//////////8HAAAAAAAAAAAAAND/ZxgAAAAAAAD///////P///////8AAAAAAAAAAAAAAPZ/AAYAAAAAAOD///+///P//////38AAAAAAAAAAAAAAMh/AAwAAAAAAMD//////Y/9//////8BAAAAAAAAAAAAAAD9B4AAAAAAAAD+////P/+H//////8/AAAAAAAAAAAAAADA/AEAAQAAAAAA/////z//I8D/////nwAAAAAAAAAAAAAAAPIHAAAAAAAAAP7/////+f8D/P///38CAAAAAAAAAAAAAAAAPwA4AAAAAADg/////z///4D///7/AwAAAAAAAAAAAAAAAIAfGDAAAAAAAPD/////P/9/AP0f/k8AAAAAAAAAAAABAAAAgD8YAAQAAAAA4P////9//H8A+B/4HwEAAAAAAAAAAAAAAAAA+HMAdAAAAAAA///////H/wOA/4D/CBAAAAAAAAAAAAAAAAAA/A8AAAAAAADg///////xPwDwD+B/AAQAAAAAAAAAAAAAAAAA3AMAAAAAAADw///////4BwDwA7D/AAYAAAAAAAAAAAAAAAAAgH8AAAAAAADw///////jBwDAAwD+AwgAAAAAAAAAAAAAAAAAAPABAAAAAACA//////+/BwAAHgDwH8ABAAAAAAAAAAAAAAAAAAAegAAAAAAA+P//////DxAA4AMA+gEAAAAAAAAAAAAAAAAAAAAAAyQAAAAAAP7//////8EAAHAAAHwAFAAAAAAAAAAAAAAAAAAAwMB/BQAAAAD+//////8/AAAYACAMAAIAAAAAAAAAAAAAAAAAAIDs/wMAAAAA/v//////PwAASAAgBAAIAAAAAAAAAAAAAAAAAAAA8v8PAAAAAPz//////z8AAMAAQAAAGgAAAAAAAAAAAAAAAAAAAMD/HwAAAADg//////9/AAAAAwADQCAAAAAAAAAAAAAAAAAAAAAA//8fAAAAAP7g/////wEAAAAAMAAPAAAAAAAAAAAAAAAAAAAAAPj//wEAAAAAAPj///8HAAAAAJgBHAAAAAAAAAAAAAAAAAAAAADA//8fAAAAAACA////PwAAAAAAG+ABAAAAAAAAAAAAAAAAAAAAAPz//wEAAAAAAPj///8AAAAAAGBCHyAAAAAAAAAAAAAAAAAAAADw//8fAAAAAACA////BwAAAAAAHfx5AgAAAAAAAAAAAAAAAAAAAP///wYAAAAAAPj//z8AAAAAAMDBHwACAAAAAAAAAAAAAAAAAADw///fAwAAAACA////AwAAAAAAOPgMaAcAAAAAAAAAAAAAAAAAAP////8DAAAAAPD//w8AAAAAAACHT8H2AQAAAAAAAAAAAAAAAAD4////fwAAAAAA//9/AAAAAAAAMAAYwH8gAAAAAAAAAAAAAAAAwP////8PAAAAAPD//wcAAAAAAEABgADwhwAAAAAAAAAAAAAAAAD8////fwAAAADA//8PAAAAAAAAOAAAgD8AAAAAAAAAAAAAAAAA8P////8BAAAAAP//PwAAAAAAAAAPIIBvAAEAAAAAAAAAAAAAAOD/////AQAAAAD+/z8AAAAAAAAAQCAAjAgEAAAAAAAAAAAAAADg/////wAAAAAA/v8/AAAAAAAAAAAAAIABAAAAAAAAAAAAAAAA4P///x8AAAAAgP//HwAAAAAAAAAAAAkBAAAAAAAAAAAAAAAAAPj///8HAAAAAPD//wcCAAAAAAAAAPAhAAAAAAAAAAAAAAAAAAD///8/AAAAAAD//z8wAAAAAAAAAMAHAwAAAAAAAAAAAAAAAAD4////AQAAAAD8///BAQAAAAAAAOAfHAAAAAAAAAAAAAAAAADA////AwAAAAD8///hAQAAAAAAAOB/HACAAAAAAAAAAAAAAACA////AQAAAAD+/z94AAAAAAAAAP5/DwAAIAAAAAAAAAAAAADA//8/AAAAAID//wMPAAAAAAAA4P//AAAAAAAAAAAAAAAAAAD+//8BAAAAAPz/BzgAAAAAAADA//8PAAAAAAAAAAAAAAAAAPz//wEAAAAA8P8PeAAAAAAAAPj//x8AAgAAAAAAAAAAAAAA/P//AAAAAAD4/wceAAAAAAAA////DwAAAAAAAAAAAAAAAID//wMAAAAAAP//wAEAAAAAAPj///8AAAAAAAAAAAAAAAAA/v8HAAAAAAD8/wEDAAAAAADg////AwAAAAAAAAAAAAAAAP7/AwAAAAAA/n8AAAAAAAAA8P///wEAAAAAAAAAAAAAAMD/PwAAAAAAwP8HAAAAAAAAgP///w8AAAAAAAAAAAAAAAD//wAAAAAAAP8PAAAAAAAAAP///x8AAAAAAAAAAAAAAID/PwAAAAAAgP8BAAAAAAAAwP///wMAAAAAAAAAAAAAAPj/AQAAAAAA/A8AAAAAAAAA////DwAAAAAAAAAAAAAA8P8DAAAAAAD4BwAAAAAAAAD/8/8HAAAAAAAAAAAAAAD8fwAAAAAAAP4AAAAAAAAA4AfsPwAAAAAAAAAAAAAA8P8BAAAAAAAYAAAAAAAAAOAA6D8AAAAAAAAAAAAAAPg/AAAAAAAAAAAAAAAAAAAAAPgHAAQAAAAAAAAAAID/AwAAAAAAAAAAAAAAAAAAAOAPABAAAAAAAAAAAMD/AQAAAAAAAAAAAAAAAAAAAPgAAAwAAAAAAAAAAPwBAAAAAAAAAAAAAAAAAAAAAAAAHAAAAAAAAAAA/AEAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAOAHAAAAAAAAAAAAAAAAAAAAwACAAAAAAAAAAADABwAAAAAAAAAAAAAAAAAAABAAEAAAAAAAAAAAPgAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAHwAAAAAAAAAAAAAAAAAAAADAAQAAAAAAAAB4AAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAADwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAACABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAADgAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAEAAAAAAAACAAAAAAAAAAAAAAAAAgAHAGx4AAAAAACAAAAAA/vD//wAAAAAAKAAAAOA/////AAAAAIAAAAD6n////wAAAAAeAOz/f////wMAAAAHgP//////DwAY/gfg/////38A8PMPwP////8fgP9/AP////8foP8P+P///3/A/4f8////B/wP8f//f8D/8f//P/C//v//8P///wcAAAAAAAAAAAAA";

  var DEG = Math.PI / 180;
  var BAKU = [40.41, 49.87];
  var DESTINATIONS = [
    [43.65, -79.38], // Toronto
    [40.71, -74.0], // New York
    [48.86, 2.35], // Paris
    [51.51, -0.13], // London
    [41.01, 28.98], // Istanbul
    [47.5, 19.04], // Budapest
    [52.52, 13.4], // Berlin
    [41.9, 12.5] // Rome
  ];

  var CREAM = "237,230,220"; // #EDE6DC
  var ORANGE = "255,84,20"; // #FF5414
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function unit(lat, lon) {
    var la = lat * DEG;
    var lo = lon * DEG;
    var c = Math.cos(la);
    return [c * Math.sin(lo), Math.sin(la), c * Math.cos(lo)];
  }

  var landPoints = null;
  function decodeLand() {
    if (landPoints) {
      return landPoints;
    }
    var bin = window.atob(LAND);
    var out = [];
    var rows = Math.floor(180 / STEP);
    var bit = 0;
    for (var k = 0; k < rows; k++) {
      var lat = 90 - (k + 0.5) * STEP;
      var n = Math.max(1, Math.round((360 * Math.cos(lat * DEG)) / STEP));
      for (var i = 0; i < n; i++, bit++) {
        if ((bin.charCodeAt(bit >> 3) >> (bit & 7)) & 1) {
          var p = unit(lat, -180 + ((i + 0.5) * 360) / n);
          out.push(p[0], p[1], p[2]);
        }
      }
    }
    landPoints = new Float32Array(out);
    return landPoints;
  }

  function slerpArc(a, b, steps) {
    var dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    var w = Math.acos(Math.max(-1, Math.min(1, dot)));
    var s = Math.sin(w) || 1;
    var lift = 0.05 + 0.14 * (w / Math.PI);
    var pts = [];
    for (var i = 0; i <= steps; i++) {
      var t = i / steps;
      var f1 = Math.sin((1 - t) * w) / s;
      var f2 = Math.sin(t * w) / s;
      var h = 1 + lift * Math.sin(Math.PI * t);
      pts.push([(f1 * a[0] + f2 * b[0]) * h, (f1 * a[1] + f2 * b[1]) * h, (f1 * a[2] + f2 * b[2]) * h]);
    }
    return pts;
  }

  function graticule() {
    var lines = [];
    var lat;
    var lon;
    for (lon = -180; lon < 180; lon += 30) {
      var m = [];
      for (lat = -90; lat <= 90; lat += 4) {
        m.push(unit(lat, lon));
      }
      lines.push(m);
    }
    for (lat = -60; lat <= 60; lat += 30) {
      var p = [];
      for (lon = -180; lon <= 180; lon += 4) {
        p.push(unit(lat, lon));
      }
      lines.push(p);
    }
    return lines;
  }

  /* energy rings: radius (x globe radius), tilt around X and Z, speed (rad/s), comets */
  var RINGS = [
    { r: 1.16, ax: 74 * DEG, az: -22 * DEG, speed: 0.9, comets: [0, Math.PI] },
    { r: 1.3, ax: 68 * DEG, az: 28 * DEG, speed: -0.65, comets: [1.2] },
    { r: 1.44, ax: 80 * DEG, az: 6 * DEG, speed: 0.45, comets: [2.4, 4.6] }
  ];

  function ringPoint(ring, theta) {
    var x = Math.cos(theta) * ring.r;
    var z = Math.sin(theta) * ring.r;
    // tilt around X
    var y = -z * Math.sin(ring.ax);
    z = z * Math.cos(ring.ax);
    // tilt around Z
    var x2 = x * Math.cos(ring.az) - y * Math.sin(ring.az);
    var y2 = x * Math.sin(ring.az) + y * Math.cos(ring.az);
    return [x2, y2, z];
  }

  function makeSparks(count) {
    var sparks = [];
    var seed = 7;
    function rnd() {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    }
    for (var i = 0; i < count; i++) {
      sparks.push({
        ring: { r: 1.1 + rnd() * 0.45, ax: (55 + rnd() * 35) * DEG, az: (rnd() * 80 - 40) * DEG },
        theta: rnd() * Math.PI * 2,
        speed: (0.25 + rnd() * 0.5) * (rnd() > 0.5 ? 1 : -1),
        size: 0.6 + rnd() * 1.1,
        twinkle: rnd() * Math.PI * 2
      });
    }
    return sparks;
  }

  function Globe(root) {
    this.root = root;
    this.canvas = root.querySelector("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.points = decodeLand();
    this.grid = graticule();
    var baku = unit(BAKU[0], BAKU[1]);
    this.baku = baku;
    this.arcs = DESTINATIONS.map(function (d, i) {
      return { pts: slerpArc(baku, unit(d[0], d[1]), 56), end: unit(d[0], d[1]), offset: i * 0.37 };
    });
    this.sparks = makeSparks(34);
    this.lon = 30; // longitude facing the viewer: Europe and Azerbaijan first
    this.lat = 24; // camera latitude: the northern hemisphere a bit more in view
    this.spin = reduceMotion ? 0 : 7; // degrees per second
    this.t = 0;
    this.running = false;
    this.visible = false;
    this.drag = null;
    this.velocity = 0;
    this.resize();
    this.bind();
    this.draw();
  }

  Globe.prototype.resize = function () {
    var rect = this.canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.size = rect.width || 300;
    this.canvas.width = Math.round(this.size * dpr);
    this.canvas.height = Math.round(this.size * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.R = this.size * 0.31;
    this.cx = this.size / 2;
    this.cy = this.size / 2;
  };

  Globe.prototype.bind = function () {
    var self = this;
    var canvas = this.canvas;
    canvas.addEventListener("pointerdown", function (e) {
      self.drag = { x: e.clientX, y: e.clientY, lon: self.lon, lat: self.lat, last: e.clientX, time: performance.now() };
      self.velocity = 0;
      self.root.classList.add("is-dragging");
      if (canvas.setPointerCapture) {
        canvas.setPointerCapture(e.pointerId);
      }
    });
    canvas.addEventListener("pointermove", function (e) {
      if (!self.drag) {
        return;
      }
      var k = 180 / (Math.PI * self.R);
      self.lon = self.drag.lon - (e.clientX - self.drag.x) * k;
      self.lat = Math.max(-10, Math.min(55, self.drag.lat + (e.clientY - self.drag.y) * k));
      var now = performance.now();
      var dt = Math.max(1, now - self.drag.time);
      self.velocity = (-(e.clientX - self.drag.last) * k * 1000) / dt;
      self.drag.last = e.clientX;
      self.drag.time = now;
      if (!self.running) {
        self.draw();
      }
    });
    function end() {
      if (!self.drag) {
        return;
      }
      self.drag = null;
      self.root.classList.remove("is-dragging");
      if (reduceMotion) {
        self.velocity = 0;
      }
    }
    canvas.addEventListener("pointerup", end);
    canvas.addEventListener("pointercancel", end);

    if ("ResizeObserver" in window) {
      new ResizeObserver(function () {
        self.resize();
        self.draw();
      }).observe(canvas);
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        self.visible = entries[0].isIntersecting;
        self.update();
      }).observe(this.root);
    } else {
      this.visible = true;
      this.update();
    }
    document.addEventListener("visibilitychange", function () {
      self.update();
    });
  };

  Globe.prototype.update = function () {
    var shouldRun = this.visible && !document.hidden && !reduceMotion;
    if (shouldRun && !this.running) {
      this.running = true;
      this.last = performance.now();
      var self = this;
      var loop = function (now) {
        if (!self.running) {
          return;
        }
        var dt = Math.min(0.05, (now - self.last) / 1000);
        self.last = now;
        self.t += dt;
        if (!self.drag) {
          // ease a fling back to the steady auto spin
          self.velocity += (self.spin - self.velocity) * Math.min(1, dt * 1.6);
          self.lon += self.velocity * dt;
        }
        self.draw();
        window.requestAnimationFrame(loop);
      };
      window.requestAnimationFrame(loop);
    } else if (!shouldRun) {
      this.running = false;
    }
  };

  /* camera rotation: longitude `lon` faces the viewer, seen from latitude `lat` */
  Globe.prototype.camera = function () {
    var a = this.lon * DEG;
    var b = this.lat * DEG;
    return { ca: Math.cos(a), sa: Math.sin(a), cb: Math.cos(b), sb: Math.sin(b) };
  };

  function rotate(p, c) {
    var x = p[0] * c.ca - p[2] * c.sa;
    var z = p[0] * c.sa + p[2] * c.ca;
    var y = p[1] * c.cb - z * c.sb;
    var z2 = p[1] * c.sb + z * c.cb;
    return [x, y, z2];
  }

  /* a point above the surface is visible when in front or outside the disc */
  function seen(q) {
    return q[2] >= 0 || q[0] * q[0] + q[1] * q[1] > 1;
  }

  Globe.prototype.drawRings = function (front) {
    var ctx = this.ctx;
    var R = this.R;
    var cx = this.cx;
    var cy = this.cy;
    var t = this.t;
    var self = this;
    ctx.lineCap = "round";

    RINGS.forEach(function (ring) {
      // faint full orbit
      ctx.beginPath();
      var steps = 120;
      var pen = false;
      for (var i = 0; i <= steps; i++) {
        var p = ringPoint(ring, (i / steps) * Math.PI * 2);
        if (p[2] >= 0 === front) {
          if (pen) {
            ctx.lineTo(cx + p[0] * R, cy - p[1] * R);
          } else {
            ctx.moveTo(cx + p[0] * R, cy - p[1] * R);
            pen = true;
          }
        } else {
          pen = false;
        }
      }
      ctx.strokeStyle = "rgba(" + ORANGE + "," + (front ? 0.32 : 0.16) + ")";
      ctx.lineWidth = 1;
      ctx.stroke();

      // comets with a fading tail
      ring.comets.forEach(function (start) {
        var head = start + t * ring.speed;
        var dir = ring.speed >= 0 ? -1 : 1;
        var segs = 26;
        var tail = 1.35;
        var prev = ringPoint(ring, head);
        for (var s = 1; s <= segs; s++) {
          var q = ringPoint(ring, head + dir * (s / segs) * tail);
          var mid = (prev[2] + q[2]) / 2;
          if (mid >= 0 === front) {
            var k = 1 - s / segs;
            var depth = 0.55 + 0.45 * ((mid / ring.r + 1) / 2);
            ctx.beginPath();
            ctx.moveTo(cx + prev[0] * R, cy - prev[1] * R);
            ctx.lineTo(cx + q[0] * R, cy - q[1] * R);
            ctx.strokeStyle = "rgba(" + ORANGE + "," + (0.16 * k * depth).toFixed(3) + ")";
            ctx.lineWidth = 7 * k + 1;
            ctx.stroke();
            ctx.strokeStyle = "rgba(255," + Math.round(120 + 100 * k) + "," + Math.round(60 + 120 * k) + "," + (0.95 * k * depth).toFixed(3) + ")";
            ctx.lineWidth = 2.4 * k + 0.4;
            ctx.stroke();
          }
          prev = q;
        }
        var h = ringPoint(ring, head);
        if (h[2] >= 0 === front) {
          self.glowDot(cx + h[0] * R, cy - h[1] * R, front ? 9 : 6, front ? 1 : 0.6);
        }
      });
    });

    // sparks
    this.sparks.forEach(function (sp) {
      var p = ringPoint(sp.ring, sp.theta + t * sp.speed);
      if (p[2] >= 0 !== front) {
        return;
      }
      var a = (0.35 + 0.65 * Math.abs(Math.sin(t * 2.2 + sp.twinkle))) * (front ? 0.95 : 0.45);
      ctx.beginPath();
      ctx.arc(cx + p[0] * R, cy - p[1] * R, sp.size, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(" + ORANGE + "," + a.toFixed(3) + ")";
      ctx.fill();
    });
  };

  Globe.prototype.glowDot = function (x, y, r, alpha) {
    var ctx = this.ctx;
    var g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, "rgba(255,255,255," + alpha + ")");
    g.addColorStop(0.25, "rgba(255,170,110," + 0.9 * alpha + ")");
    g.addColorStop(0.6, "rgba(" + ORANGE + "," + 0.35 * alpha + ")");
    g.addColorStop(1, "rgba(" + ORANGE + ",0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  };

  Globe.prototype.draw = function () {
    var ctx = this.ctx;
    var R = this.R;
    var cx = this.cx;
    var cy = this.cy;
    var t = this.t;
    var cam = this.camera();
    var i;
    var g;

    ctx.clearRect(0, 0, this.size, this.size);

    // orange aura
    g = ctx.createRadialGradient(cx, cy, R * 0.9, cx, cy, R * 1.32);
    g.addColorStop(0, "rgba(" + ORANGE + ",0.28)");
    g.addColorStop(0.45, "rgba(" + ORANGE + ",0.09)");
    g.addColorStop(1, "rgba(" + ORANGE + ",0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, R * 1.32, 0, Math.PI * 2);
    ctx.fill();

    this.drawRings(false);

    // ocean sphere
    g = ctx.createRadialGradient(cx - R * 0.38, cy - R * 0.42, R * 0.05, cx, cy, R * 1.04);
    g.addColorStop(0, "#1c6b7b");
    g.addColorStop(0.42, "#06414f");
    g.addColorStop(1, "#001b23");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.fill();

    // graticule
    ctx.lineWidth = 0.6;
    ctx.strokeStyle = "rgba(" + CREAM + ",0.09)";
    ctx.beginPath();
    this.grid.forEach(function (line) {
      var pen = false;
      line.forEach(function (p) {
        var q = rotate(p, cam);
        if (q[2] > 0) {
          if (pen) {
            ctx.lineTo(cx + q[0] * R, cy - q[1] * R);
          } else {
            ctx.moveTo(cx + q[0] * R, cy - q[1] * R);
            pen = true;
          }
        } else {
          pen = false;
        }
      });
    });
    ctx.stroke();

    // land dots, shaded by depth (4 alpha bands keep fill changes few)
    var pts = this.points;
    var bands = [[], [], [], []];
    for (i = 0; i < pts.length; i += 3) {
      var x = pts[i] * cam.ca - pts[i + 2] * cam.sa;
      var z = pts[i] * cam.sa + pts[i + 2] * cam.ca;
      var y = pts[i + 1] * cam.cb - z * cam.sb;
      var zz = pts[i + 1] * cam.sb + z * cam.cb;
      if (zz <= 0.02) {
        continue;
      }
      var band = zz > 0.75 ? 3 : zz > 0.5 ? 2 : zz > 0.25 ? 1 : 0;
      bands[band].push(cx + x * R, cy - y * R, zz);
    }
    var dot = Math.max(0.7, R / 105);
    var alphas = [0.22, 0.5, 0.76, 0.96];
    bands.forEach(function (list, b) {
      ctx.fillStyle = "rgba(" + CREAM + "," + alphas[b] + ")";
      ctx.beginPath();
      for (var j = 0; j < list.length; j += 3) {
        var r = dot * (0.55 + 0.6 * list[j + 2]);
        ctx.moveTo(list[j] + r, list[j + 1]);
        ctx.arc(list[j], list[j + 1], r, 0, Math.PI * 2);
      }
      ctx.fill();
    });

    // flight arcs from Baku with a travelling pulse
    var period = 3.4;
    this.arcs.forEach(function (arc) {
      var pts2 = arc.pts.map(function (p) {
        return rotate(p, cam);
      });
      ctx.beginPath();
      var pen = false;
      pts2.forEach(function (q) {
        if (seen(q)) {
          if (pen) {
            ctx.lineTo(cx + q[0] * R, cy - q[1] * R);
          } else {
            ctx.moveTo(cx + q[0] * R, cy - q[1] * R);
            pen = true;
          }
        } else {
          pen = false;
        }
      });
      ctx.strokeStyle = "rgba(" + ORANGE + ",0.55)";
      ctx.lineWidth = 1.2;
      ctx.stroke();

      var phase = ((t / period + arc.offset) % 1.4) / 1.0; // 0..1 travel, 1..1.4 rest
      var n = pts2.length - 1;
      if (phase <= 1) {
        var headIdx = Math.floor(phase * n);
        var tailLen = 12;
        for (var s = Math.max(1, headIdx - tailLen); s <= headIdx; s++) {
          var a = pts2[s - 1];
          var b2 = pts2[s];
          if (!seen(a) || !seen(b2)) {
            continue;
          }
          var k = 1 - (headIdx - s) / tailLen;
          ctx.beginPath();
          ctx.moveTo(cx + a[0] * R, cy - a[1] * R);
          ctx.lineTo(cx + b2[0] * R, cy - b2[1] * R);
          ctx.strokeStyle = "rgba(255," + Math.round(110 + 110 * k) + "," + Math.round(40 + 140 * k) + "," + (0.95 * k).toFixed(3) + ")";
          ctx.lineWidth = 2.2 * k + 0.4;
          ctx.stroke();
        }
      } else {
        // landing ping at the destination
        var end = rotate(arc.end, cam);
        if (end[2] > 0) {
          var pr = (phase - 1) / 0.4;
          ctx.beginPath();
          ctx.arc(cx + end[0] * R, cy - end[1] * R, 2 + pr * 9, 0, Math.PI * 2);
          ctx.strokeStyle = "rgba(" + ORANGE + "," + (0.8 * (1 - pr)).toFixed(3) + ")";
          ctx.lineWidth = 1.4;
          ctx.stroke();
        }
      }
      var e = rotate(arc.end, cam);
      if (e[2] > 0) {
        ctx.beginPath();
        ctx.arc(cx + e[0] * R, cy - e[1] * R, 2.1 * (0.6 + 0.4 * e[2]), 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + ORANGE + "," + (0.5 + 0.5 * e[2]).toFixed(3) + ")";
        ctx.fill();
      }
    });

    // Baku: the home hub
    var home = rotate(this.baku, cam);
    if (home[2] > 0) {
      var hx = cx + home[0] * R;
      var hy = cy - home[1] * R;
      var pulse = (t % 2) / 2;
      ctx.beginPath();
      ctx.arc(hx, hy, 3 + pulse * 12, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(" + ORANGE + "," + (0.7 * (1 - pulse) * home[2]).toFixed(3) + ")";
      ctx.lineWidth = 1.5;
      ctx.stroke();
      this.glowDot(hx, hy, 8, home[2]);
    }

    // light: highlight top-left, darker limb, warm rim bottom-right
    g = ctx.createRadialGradient(cx - R * 0.42, cy - R * 0.48, 0, cx - R * 0.42, cy - R * 0.48, R * 1.1);
    g.addColorStop(0, "rgba(255,255,255,0.16)");
    g.addColorStop(0.5, "rgba(255,255,255,0.03)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, R, 0, Math.PI * 2);
    ctx.fill();

    g = ctx.createRadialGradient(cx, cy, R * 0.72, cx, cy, R);
    g.addColorStop(0, "rgba(0,22,28,0)");
    g.addColorStop(1, "rgba(0,22,28,0.5)");
    ctx.fillStyle = g;
    ctx.fill();

    g = ctx.createLinearGradient(cx - R, cy - R, cx + R, cy + R);
    g.addColorStop(0, "rgba(140,220,235,0.35)");
    g.addColorStop(0.55, "rgba(" + ORANGE + ",0.15)");
    g.addColorStop(1, "rgba(" + ORANGE + ",0.85)");
    ctx.strokeStyle = g;
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.arc(cx, cy, R - 0.6, 0, Math.PI * 2);
    ctx.stroke();

    this.drawRings(true);
  };

  function init() {
    document.querySelectorAll("[data-abroad-globe]").forEach(function (root) {
      if (root.dataset.globeReady === "true") {
        return;
      }
      var canvas = root.querySelector("canvas");
      if (!canvas || !canvas.getContext) {
        return;
      }
      root.dataset.globeReady = "true";
      try {
        new Globe(root);
        root.classList.add("is-ready");
      } catch (err) {
        root.dataset.globeReady = "false";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

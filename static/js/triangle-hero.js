/**
 * triangle-hero.js
 * مثلث تعاملی هیرو -- تشخیص نزدیکی موس به هر ضلع، پرتو انرژی، هسته پویا، ذرات شناور.
 * بدون وابستگی به فریم‌ورک (Vanilla JS) -- مناسب برای استفاده در قالب‌های Django.
 */
(function () {
  "use strict";

  const VIEWBOX = 500;
  const PROXIMITY_THRESHOLD = 100;

  // مثلث وارونه (رأس رو به پایین) -- هر ضلع یک قابلیت شرکت را نمایش می‌دهد
  const VERTICES = {
    topLeft: { x: 90, y: 90 },
    topRight: { x: 410, y: 90 },
    bottom: { x: 250, y: 410 },
  };

  const EDGES = {
    top: { a: VERTICES.topLeft, b: VERTICES.topRight },
    left: { a: VERTICES.topLeft, b: VERTICES.bottom },
    right: { a: VERTICES.topRight, b: VERTICES.bottom },
  };

  // نقطه‌ای که پرتو انرژی به بیرون از قاب SVG می‌رسد (سمت کارت اطلاعات)
  const BEAM_EXIT = {
    top: { x: 250, y: -10 },
    left: { x: -10, y: 250 },
    right: { x: 510, y: 250 },
  };

  // محتوا و رنگ هر ضلع -- مطابق سه قابلیت اصلی سامان تجهیز اسپادان
  const SIDES = {
    top: {
      title: "مشاوره و طراحی",
      description: "ارائه راهکارهای مهندسی متناسب با نیاز پروژه شما",
      icon: "fa-drafting-compass",
      color: "#F97316",
      colorSoft: "#FDBA74",
      cardPosition: "top",
    },
    left: {
      title: "ساخت تابلوهای برق",
      description: "ساخت اختصاصی روی خط تولید با دقت مهندسی بالا",
      icon: "fa-industry",
      color: "#38BDF8",
      colorSoft: "#BAE6FD",
      cardPosition: "left",
    },
    right: {
      title: "تأمین تجهیزات",
      description: "واردات مستقیم از برندهای معتبر با تضمین اصالت کالا",
      icon: "fa-truck-fast",
      color: "#34D399",
      colorSoft: "#A7F3D0",
      cardPosition: "right",
    },
  };

  const SIDE_ORDER = ["top", "left", "right"];

  // ---------------------------------------------------------------------
  // توابع هندسی
  // ---------------------------------------------------------------------
  function closestPointOnSegment(p, a, b) {
    const abx = b.x - a.x;
    const aby = b.y - a.y;
    const abLenSq = abx * abx + aby * aby;
    let t = abLenSq === 0 ? 0 : ((p.x - a.x) * abx + (p.y - a.y) * aby) / abLenSq;
    t = Math.max(0, Math.min(1, t));
    return { x: a.x + abx * t, y: a.y + aby * t };
  }

  function distanceToSegment(p, a, b) {
    const c = closestPointOnSegment(p, a, b);
    return Math.hypot(p.x - c.x, p.y - c.y);
  }

  function findActiveEdge(p, threshold) {
    let closest = null;
    let minDist = Infinity;
    SIDE_ORDER.forEach((key) => {
      const { a, b } = EDGES[key];
      const d = distanceToSegment(p, a, b);
      if (d < minDist) {
        minDist = d;
        closest = key;
      }
    });
    return minDist <= threshold ? closest : null;
  }

  function lerp(start, end, factor) {
    return start + (end - start) * factor;
  }

  // ---------------------------------------------------------------------
  // ساخت ذرات شناور (یک‌بار در شروع)
  // ---------------------------------------------------------------------
  function makeParticles(count) {
    const particles = [];
    const center = { x: VIEWBOX / 2, y: VIEWBOX / 2 + 20 };
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = 130 + Math.random() * 180;
      const base = {
        x: center.x + Math.cos(angle) * radius,
        y: center.y + Math.sin(angle) * radius,
      };
      let closestEdge = "top";
      let minDist = Infinity;
      SIDE_ORDER.forEach((key) => {
        const { a, b } = EDGES[key];
        const foot = closestPointOnSegment(base, a, b);
        const d = Math.hypot(base.x - foot.x, base.y - foot.y);
        if (d < minDist) {
          minDist = d;
          closestEdge = key;
        }
      });
      const { a, b } = EDGES[closestEdge];
      particles.push({
        id: i,
        edge: closestEdge,
        base,
        foot: closestPointOnSegment(base, a, b),
        size: 1 + Math.random() * 1.8,
        phase: Math.random() * Math.PI * 2,
        speed: 0.6 + Math.random() * 0.6,
      });
    }
    return particles;
  }

  // ---------------------------------------------------------------------
  // راه‌اندازی
  // ---------------------------------------------------------------------
  function init() {
    const container = document.getElementById("triangle-hero");
    if (!container) return;

    const svg = container.querySelector("#triangle-svg");
    const rotor = container.querySelector("#triangle-rotor");
    const glowHalo = container.querySelector("#triangle-glow-halo");
    const coreCircle = container.querySelector("#triangle-core");
    const coreGradStop = container.querySelector("#core-grad-mid");
    const particleLayer = container.querySelector("#triangle-particles");
    const beamLayer = container.querySelector("#triangle-beam");
    const travelerLayer = container.querySelector("#triangle-traveler");
    const cardsLayer = container.querySelector("#triangle-cards");
    const edgeEls = {
      top: container.querySelector('[data-edge="top"]'),
      left: container.querySelector('[data-edge="left"]'),
      right: container.querySelector('[data-edge="right"]'),
    };

    if (!svg || !rotor) return;

    const particles = makeParticles(26);

    // ایجاد المان‌های ذرات
    const particleEls = particles.map((p) => {
      const el = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      el.setAttribute("r", p.size);
      el.setAttribute("cx", p.base.x);
      el.setAttribute("cy", p.base.y);
      el.setAttribute("fill", "#ffffff");
      el.setAttribute("opacity", "0.3");
      particleLayer.appendChild(el);
      return el;
    });

    // وضعیت جاری (برای حرکت نرم/لرپ)
    const state = {
      targetRotX: 0,
      targetRotY: 0,
      curRotX: 0,
      curRotY: 0,
      targetGlowX: 50,
      targetGlowY: 35,
      curGlowX: 50,
      curGlowY: 35,
      activeEdge: null,
      beamStart: null,
      travelT: 0,
    };

    let cardEl = null;

    function setActiveEdge(edge) {
      if (state.activeEdge === edge) return;
      state.activeEdge = edge;

      SIDE_ORDER.forEach((key) => {
        const el = edgeEls[key];
        if (!el) return;
        const isActive = key === edge;
        el.setAttribute("stroke", isActive ? `url(#edge-grad-${key})` : "rgba(255,255,255,0.22)");
        el.setAttribute("stroke-width", isActive ? "3" : "1.4");
        el.style.filter = isActive ? "url(#edge-glow)" : "none";
      });

      beamLayer.innerHTML = "";
      travelerLayer.innerHTML = "";

      if (edge) {
        const side = SIDES[edge];
        coreGradStop.setAttribute("stop-color", side.color);
        coreCircle.classList.add("triangle-core--active");

        // خط پرتو (بازسازی هر بار که ضلع فعال عوض می‌شود)
        const beamLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
        beamLine.setAttribute("id", "beam-line");
        beamLine.setAttribute("stroke", `url(#edge-grad-${edge})`);
        beamLine.setAttribute("stroke-width", "1.6");
        beamLine.setAttribute("stroke-dasharray", "3 7");
        beamLine.setAttribute("opacity", "0.85");
        beamLine.setAttribute("x2", BEAM_EXIT[edge].x);
        beamLine.setAttribute("y2", BEAM_EXIT[edge].y);
        beamLayer.appendChild(beamLine);

        // ذره نور در حال حرکت روی پرتو
        const beamDot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        beamDot.setAttribute("id", "beam-dot");
        beamDot.setAttribute("r", "3.2");
        beamDot.setAttribute("fill", side.colorSoft);
        beamDot.style.filter = "url(#edge-glow)";
        beamLayer.appendChild(beamDot);

        // نور در حال حرکت روی خود ضلع
        const traveler = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        traveler.setAttribute("id", "edge-traveler");
        traveler.setAttribute("r", "4");
        traveler.setAttribute("fill", side.colorSoft);
        traveler.style.filter = "url(#edge-glow)";
        travelerLayer.appendChild(traveler);

        // کارت اطلاعاتی
        showCard(edge);
      } else {
        coreCircle.classList.remove("triangle-core--active");
        hideCard();
      }
    }

    function showCard(edge) {
      hideCard();
      const side = SIDES[edge];
      cardEl = document.createElement("div");
      cardEl.className = `triangle-card triangle-card--${side.cardPosition}`;
      cardEl.innerHTML = `
        <div class="triangle-card-inner">
          <div class="triangle-card-icon" style="background:${side.color}26;color:${side.colorSoft}">
            <i class="fa-solid ${side.icon}"></i>
          </div>
          <p class="triangle-card-title">${side.title}</p>
          <p class="triangle-card-desc">${side.description}</p>
        </div>`;
      cardsLayer.appendChild(cardEl);
      requestAnimationFrame(() => cardEl.classList.add("triangle-card--visible"));
    }

    function hideCard() {
      if (!cardEl) return;
      const el = cardEl;
      el.classList.remove("triangle-card--visible");
      setTimeout(() => el.remove(), 250);
      cardEl = null;
    }

    // ---------------------------------------------------------------
    // رویدادهای موس
    // ---------------------------------------------------------------
    container.addEventListener("mousemove", (e) => {
      const rect = svg.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / rect.width;
      const ny = (e.clientY - rect.top) / rect.height;

      state.targetRotY = (nx - 0.5) * 18;
      state.targetRotX = (0.5 - ny) * 18;
      state.targetGlowX = nx * 100;
      state.targetGlowY = ny * 100;

      const svgPoint = { x: nx * VIEWBOX, y: ny * VIEWBOX };
      const edge = findActiveEdge(svgPoint, PROXIMITY_THRESHOLD);
      setActiveEdge(edge);

      if (edge) {
        const { a, b } = EDGES[edge];
        state.beamStart = closestPointOnSegment(svgPoint, a, b);
        const beamLine = document.getElementById("beam-line");
        if (beamLine) {
          beamLine.setAttribute("x1", state.beamStart.x);
          beamLine.setAttribute("y1", state.beamStart.y);
        }
      }
    });

    container.addEventListener("mouseleave", () => {
      state.targetRotX = 0;
      state.targetRotY = 0;
      state.targetGlowX = 50;
      state.targetGlowY = 35;
      setActiveEdge(null);
    });

    // ---------------------------------------------------------------
    // حلقه انیمیشن (rAF) -- لرپ برای حس فنری نرم + حرکت پرتو/نور روی ضلع
    // ---------------------------------------------------------------
    let lastTime = performance.now();

    function tick(now) {
      const dt = Math.min((now - lastTime) / 1000, 0.05);
      lastTime = now;

      state.curRotX = lerp(state.curRotX, state.targetRotX, 0.12);
      state.curRotY = lerp(state.curRotY, state.targetRotY, 0.12);
      state.curGlowX = lerp(state.curGlowX, state.targetGlowX, 0.15);
      state.curGlowY = lerp(state.curGlowY, state.targetGlowY, 0.15);

      rotor.style.transform = `rotateX(${state.curRotX}deg) rotateY(${state.curRotY}deg)`;
      glowHalo.style.background = `radial-gradient(circle at ${state.curGlowX}% ${state.curGlowY}%, ${
        state.activeEdge ? SIDES[state.activeEdge].color : "#F97316"
      }22, transparent 60%)`;

      // ذرات: شناوری آرام، یا کشیده‌شدن به سمت ضلع فعال
      particles.forEach((p, i) => {
        const el = particleEls[i];
        if (state.activeEdge === p.edge) {
          const cx = parseFloat(el.getAttribute("cx"));
          const cy = parseFloat(el.getAttribute("cy"));
          el.setAttribute("cx", lerp(cx, p.foot.x, 0.1));
          el.setAttribute("cy", lerp(cy, p.foot.y, 0.1));
          el.setAttribute("fill", SIDES[p.edge].color);
          el.setAttribute("opacity", "0.9");
        } else {
          p.phase += dt * p.speed;
          el.setAttribute("cx", p.base.x + Math.sin(p.phase) * 6);
          el.setAttribute("cy", p.base.y + Math.cos(p.phase * 0.8) * 6);
          el.setAttribute("fill", "#ffffff");
          el.setAttribute("opacity", (0.25 + Math.sin(p.phase) * 0.2).toFixed(2));
        }
      });

      // نور در حال حرکت روی ضلع فعال + پرتو
      if (state.activeEdge) {
        state.travelT += dt * 0.6;
        const t = (Math.sin(state.travelT) + 1) / 2; // نوسان ۰ تا ۱
        const { a, b } = EDGES[state.activeEdge];
        const traveler = document.getElementById("edge-traveler");
        if (traveler) {
          traveler.setAttribute("cx", lerp(a.x, b.x, t));
          traveler.setAttribute("cy", lerp(a.y, b.y, t));
        }
        const beamDot = document.getElementById("beam-dot");
        if (beamDot && state.beamStart) {
          const exit = BEAM_EXIT[state.activeEdge];
          const bt = (state.travelT * 1.4) % 1;
          beamDot.setAttribute("cx", lerp(state.beamStart.x, exit.x, bt));
          beamDot.setAttribute("cy", lerp(state.beamStart.y, exit.y, bt));
          beamDot.setAttribute("opacity", bt < 0.1 || bt > 0.9 ? "0" : "1");
        }
        const beamLine = document.getElementById("beam-line");
        if (beamLine) {
          const dashOffset = -((state.travelT * 40) % 40);
          beamLine.setAttribute("stroke-dashoffset", dashOffset);
        }
      }

      requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

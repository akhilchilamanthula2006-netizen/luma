/**
 * Luma Landing Page JavaScript Engine
 * Architecture: R1 Design System, R2 Motion System, R3 Particle Physics, R4 AI Streaming Simulation
 */

(function () {
    'use strict';

    // ── CONSTANTS & CONSTANTS CONFIG ──────────────────────────────────────────
    const INFLUENCE_RADIUS_BASE = 110;
    const INFLUENCE_RADIUS_MAX  = 180;
    const SPRING_STIFFNESS      = 0.025;
    const DAMPING               = 0.88;
    const WIND_STRENGTH         = 0.006;
    const ATTRACTION_STRENGTH   = 0.004;
    const MAX_EXPECTED_SPEED    = 30;

    // ── PARTICLE SYSTEM (R3) ──────────────────────────────────────────────────
    class ParticleSystem {
        constructor(canvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.count = 0;
            this.rafId = null;
            this.isMobile = window.innerWidth < 768;

            // Cursor state
            this.cursor = { x: -9999, y: -9999, active: false };
            this.prevCursor = { x: -9999, y: -9999 };
            this.cursorDir = { x: 0, y: 0 };
            this.cursorSpeed = 0;
            this.smoothSpeed = 0;

            // Typed Array Buffers (allocated at init)
            this.homeX = null;
            this.homeY = null;
            this.x = null;
            this.y = null;
            this.vx = null;
            this.vy = null;
            this.size = null;
            this.opacity = null;
            this.ambientFreqX = null;
            this.ambientFreqY = null;
            this.ambientAmpX = null;
            this.ambientAmpY = null;
            this.ambientPhaseX = null;
            this.ambientPhaseY = null;
            this.layer = null;

            this.resizeTimeout = null;
            this.init();
        }

        init() {
            const w = (this.canvas.width = window.innerWidth);
            const h = (this.canvas.height = window.innerHeight);

            // Adaptive particle count based on viewport area
            let targetCount = Math.min(Math.floor((w * h) / 8000), 300);
            if (this.isMobile) targetCount = Math.floor(targetCount * 0.5);
            this.count = targetCount;

            // Allocate buffers once
            this.homeX = new Float32Array(targetCount);
            this.homeY = new Float32Array(targetCount);
            this.x = new Float32Array(targetCount);
            this.y = new Float32Array(targetCount);
            this.vx = new Float32Array(targetCount);
            this.vy = new Float32Array(targetCount);
            this.size = new Float32Array(targetCount);
            this.opacity = new Float32Array(targetCount);
            this.ambientFreqX = new Float32Array(targetCount);
            this.ambientFreqY = new Float32Array(targetCount);
            this.ambientAmpX = new Float32Array(targetCount);
            this.ambientAmpY = new Float32Array(targetCount);
            this.ambientPhaseX = new Float32Array(targetCount);
            this.ambientPhaseY = new Float32Array(targetCount);
            this.layer = new Uint8Array(targetCount);

            const gridCols = Math.ceil(Math.sqrt(targetCount * (w / h)));
            const gridRows = Math.ceil(targetCount / gridCols);
            const stepX = w / gridCols;
            const stepY = h / gridRows;

            for (let i = 0; i < targetCount; i++) {
                const col = i % gridCols;
                const row = Math.floor(i / gridCols);

                // Grid positioning + organic jitter
                const jitterX = (Math.random() - 0.5) * stepX * 0.8;
                const jitterY = (Math.random() - 0.5) * stepY * 0.8;
                const hX = col * stepX + stepX / 2 + jitterX;
                const hY = row * stepY + stepY / 2 + jitterY;

                this.homeX[i] = this.x[i] = hX;
                this.homeY[i] = this.y[i] = hY;

                // Assign depth layers (0: 50%, 1: 35%, 2: 15%)
                const randLayer = Math.random();
                let l = 0;
                let mult = 0.6;
                if (randLayer > 0.85) {
                    l = 2; // Foreground
                    mult = 1.4;
                    this.size[i] = 2.0 + Math.random() * 0.8;
                    this.opacity[i] = 0.35 + Math.random() * 0.20;
                } else if (randLayer > 0.50) {
                    l = 1; // Midground
                    mult = 1.0;
                    this.size[i] = 1.4 + Math.random() * 0.6;
                    this.opacity[i] = 0.20 + Math.random() * 0.15;
                } else {
                    l = 0; // Background
                    mult = 0.6;
                    this.size[i] = 0.8 + Math.random() * 0.6;
                    this.opacity[i] = 0.10 + Math.random() * 0.10;
                }
                this.layer[i] = l;

                // Ambient oscillation params
                this.ambientFreqX[i] = 0.0004 + Math.random() * 0.0008;
                this.ambientFreqY[i] = 0.0003 + Math.random() * 0.0007;
                this.ambientAmpX[i]  = (0.3 + Math.random() * 0.5) * mult;
                this.ambientAmpY[i]  = (0.3 + Math.random() * 0.5) * mult;
                this.ambientPhaseX[i] = Math.random() * Math.PI * 2;
                this.ambientPhaseY[i] = Math.random() * Math.PI * 2;
            }

            this.bindEvents();
        }

        bindEvents() {
            if (!this.isMobile) {
                window.addEventListener('mousemove', (e) => {
                    const nx = e.clientX;
                    const ny = e.clientY;
                    if (this.cursor.active) {
                        const cvx = nx - this.prevCursor.x;
                        const cvy = ny - this.prevCursor.y;
                        const spd = Math.sqrt(cvx * cvx + cvy * cvy);
                        this.cursorSpeed = spd;
                        if (spd > 0.01) {
                            this.cursorDir.x = cvx / spd;
                            this.cursorDir.y = cvy / spd;
                        }
                    } else {
                        this.cursor.active = true;
                    }
                    this.prevCursor.x = this.cursor.x = nx;
                    this.prevCursor.y = this.cursor.y = ny;
                }, { passive: true });

                document.addEventListener('mouseleave', () => {
                    this.cursor.active = false;
                    this.smoothSpeed = 0;
                });
            }

            window.addEventListener('resize', () => {
                clearTimeout(this.resizeTimeout);
                this.resizeTimeout = setTimeout(() => this.resize(), 200);
            });

            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.stop();
                } else {
                    this.start();
                }
            });
        }

        resize() {
            const oldW = this.canvas.width;
            const oldH = this.canvas.height;
            const newW = (this.canvas.width = window.innerWidth);
            const newH = (this.canvas.height = window.innerHeight);

            // Proportional remap of particle positions
            const scaleX = newW / (oldW || 1);
            const scaleY = newH / (oldH || 1);

            for (let i = 0; i < this.count; i++) {
                this.homeX[i] *= scaleX;
                this.homeY[i] *= scaleY;
                this.x[i] *= scaleX;
                this.y[i] *= scaleY;
            }
        }

        tick() {
            const now = performance.now();
            const w = this.canvas.width;
            const h = this.canvas.height;

            this.ctx.clearRect(0, 0, w, h);

            // Smooth cursor speed decay
            this.smoothSpeed = this.smoothSpeed * 0.85 + this.cursorSpeed * 0.15;
            this.cursorSpeed *= 0.8; // Decay raw speed

            // Adaptive radius based on cursor speed
            const clampedSpeed = Math.min(this.smoothSpeed, MAX_EXPECTED_SPEED);
            const adaptiveRadius = INFLUENCE_RADIUS_BASE + (clampedSpeed / MAX_EXPECTED_SPEED) * (INFLUENCE_RADIUS_MAX - INFLUENCE_RADIUS_BASE);
            const radiusSq = adaptiveRadius * adaptiveRadius;

            // Render loop — 3 layer passes (back-to-front)
            for (let targetLayer = 0; targetLayer < 3; targetLayer++) {
                this.ctx.beginPath();

                for (let i = 0; i < this.count; i++) {
                    if (this.layer[i] !== targetLayer) continue;

                    // 1. Ambient drift
                    const ambDX = Math.sin(now * this.ambientFreqX[i] + this.ambientPhaseX[i]) * this.ambientAmpX[i];
                    const ambDY = Math.cos(now * this.ambientFreqY[i] + this.ambientPhaseY[i]) * this.ambientAmpY[i];

                    let ax = (this.homeX[i] - this.x[i]) * SPRING_STIFFNESS + ambDX * 0.012;
                    let ay = (this.homeY[i] - this.y[i]) * SPRING_STIFFNESS + ambDY * 0.012;

                    // 2. Cursor interaction (if active)
                    if (this.cursor.active) {
                        const dx = this.cursor.x - this.x[i];
                        const dy = this.cursor.y - this.y[i];
                        const distSq = dx * dx + dy * dy;

                        if (distSq < radiusSq && distSq > 0.1) {
                            const dist = Math.sqrt(distSq);
                            const falloff = 1 - dist / adaptiveRadius;

                            const pushX = this.cursorDir.x * this.smoothSpeed * WIND_STRENGTH * falloff;
                            const pushY = this.cursorDir.y * this.smoothSpeed * WIND_STRENGTH * falloff;

                            const attractX = (dx / dist) * ATTRACTION_STRENGTH * falloff * 0.3;
                            const attractY = (dy / dist) * ATTRACTION_STRENGTH * falloff * 0.3;

                            ax += pushX + attractX;
                            ay += pushY + attractY;
                        }
                    }

                    // 3. Integrate & damp
                    this.vx[i] = (this.vx[i] + ax) * DAMPING;
                    this.vy[i] = (this.vy[i] + ay) * DAMPING;
                    this.x[i] += this.vx[i];
                    this.y[i] += this.vy[i];

                    // Draw arc into batched layer path
                    this.ctx.moveTo(this.x[i] + this.size[i], this.y[i]);
                    this.ctx.arc(this.x[i], this.y[i], this.size[i], 0, Math.PI * 2);
                }

                // Batch fill layer
                let opacityVal = 0.2;
                if (targetLayer === 0) opacityVal = 0.15;
                if (targetLayer === 1) opacityVal = 0.28;
                if (targetLayer === 2) opacityVal = 0.45;

                this.ctx.fillStyle = `rgba(93, 216, 208, ${opacityVal})`;
                this.ctx.fill();
            }

            if (this.rafId) {
                this.rafId = requestAnimationFrame(() => this.tick());
            }
        }

        start() {
            if (!this.rafId) {
                // If prefers reduced motion, render single static frame
                if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                    this.tick();
                    this.stop();
                    return;
                }
                this.rafId = requestAnimationFrame(() => this.tick());
            }
        }

        stop() {
            if (this.rafId) {
                cancelAnimationFrame(this.rafId);
                this.rafId = null;
            }
        }
    }

    // ── NAVBAR CONTROLLER (R2) ────────────────────────────────────────────────
    class NavbarController {
        constructor(headerEl) {
            this.header = headerEl;
            this.init();
        }
        init() {
            if (!this.header) return;
            const onScroll = () => {
                if (window.scrollY > 80) {
                    this.header.classList.add('nav-scrolled');
                } else {
                    this.header.classList.remove('nav-scrolled');
                }
            };
            window.addEventListener('scroll', onScroll, { passive: true });
            onScroll();
        }
    }

    // ── SCROLL REVEAL (R2) ────────────────────────────────────────────────────
    class ScrollReveal {
        constructor() {
            this.init();
        }
        init() {
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

            const targets = document.querySelectorAll('[data-reveal]');
            if (!targets.length) return;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.12 });

            targets.forEach((el) => observer.observe(el));
        }
    }

    // ── AI STREAMING PREVIEW SIMULATOR (R4) ──────────────────────────────────
    function initStreamingSimulator() {
        const targetEl = document.getElementById('ai-stream-target');
        if (!targetEl) return;

        const fullText = targetEl.getAttribute('data-stream-text') || '';
        if (!fullText) return;

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            targetEl.textContent = fullText;
            return;
        }

        let hasStarted = false;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting && !hasStarted) {
                    hasStarted = true;
                    observer.unobserve(entry.target);
                    startStreaming(targetEl, fullText);
                }
            });
        }, { threshold: 0.2 });

        observer.observe(targetEl);
    }

    function startStreaming(targetEl, fullText) {
        // Pre-split full text into token-like chunks
        const chunks = [];
        let i = 0;
        while (i < fullText.length) {
            const rand = Math.random();
            let len = 2; // 80% 1-3 chars
            if (rand > 0.95) len = Math.floor(Math.random() * 5) + 8; // 5% 8-12
            else if (rand > 0.80) len = Math.floor(Math.random() * 4) + 4; // 15% 4-7
            else len = Math.floor(Math.random() * 3) + 1;

            chunks.push(fullText.slice(i, i + len));
            i += len;
        }

        // Add blinking cursor span
        const cursorEl = document.createElement('span');
        cursorEl.className = 'stream-cursor';
        cursorEl.setAttribute('aria-hidden', 'true');
        cursorEl.textContent = '▊';
        targetEl.appendChild(cursorEl);

        let chunkIdx = 0;

        function streamNextChunk() {
            if (chunkIdx < chunks.length) {
                const chunkText = chunks[chunkIdx++];
                targetEl.insertBefore(document.createTextNode(chunkText), cursorEl);

                const jitter = Math.floor(Math.random() * 32) - 8; // 28ms base + jitter
                const delay = Math.max(16, 28 + jitter);
                setTimeout(streamNextChunk, delay);
            } else {
                // Streaming complete: remove cursor element
                if (cursorEl && cursorEl.parentNode) {
                    cursorEl.parentNode.removeChild(cursorEl);
                }
            }
        }

        streamNextChunk();
    }

    // ── FAQ ACCORDION HANDLER ─────────────────────────────────────────────────
    function initFAQ() {
        const triggers = document.querySelectorAll('.faq-trigger');
        triggers.forEach((btn) => {
            btn.addEventListener('click', () => {
                const answerId = btn.getAttribute('aria-controls');
                const answerEl = document.getElementById(answerId);
                const isOpen = btn.classList.contains('open');

                if (isOpen) {
                    btn.classList.remove('open');
                    btn.setAttribute('aria-expanded', 'false');
                    if (answerEl) answerEl.classList.remove('open');
                } else {
                    btn.classList.add('open');
                    btn.setAttribute('aria-expanded', 'true');
                    if (answerEl) answerEl.classList.add('open');
                }
            });
        });
    }

    // ── MOBILE MENU HANDLER ───────────────────────────────────────────────────
    function initMobileMenu() {
        const btn = document.getElementById('mobile-menu-btn');
        const menu = document.getElementById('mobile-menu');
        if (!btn || !menu) return;

        btn.addEventListener('click', () => {
            const isOpen = !menu.classList.contains('hidden');
            if (isOpen) {
                menu.classList.add('hidden');
                btn.setAttribute('aria-expanded', 'false');
            } else {
                menu.classList.remove('hidden');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    }

    // ── INITIALIZATION ENTRY POINT (R7 Sequence) ──────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('luma-particle-canvas');
        if (canvas) {
            const ps = new ParticleSystem(canvas);
            ps.start();
        }

        const navHeader = document.getElementById('luma-nav');
        if (navHeader) {
            new NavbarController(navHeader);
        }

        new ScrollReveal();
        initStreamingSimulator();
        initFAQ();
        initMobileMenu();

        // Trigger hero entrance CSS keyframes
        document.body.classList.add('loaded');
    });

})();

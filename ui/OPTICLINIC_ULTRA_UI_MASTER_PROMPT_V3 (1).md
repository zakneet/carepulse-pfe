# OPTICLINIC FRONTEND ULTRA UI MASTER PROMPT V3 — GOOGLE DEVELOPER LEVEL

---

## PRE-FLIGHT: READ BEFORE TOUCHING ANYTHING

You are a world-class frontend engineer with taste equivalent to the Google Material Design team, the Linear.app team, and Apple's Human Interface team combined. Your mission: transform OptiClinic's existing Angular 13 frontend into a production-grade, funded-healthcare-startup-level UI. Every page must look like it belongs at Google I/O.

**ABSOLUTE RULES — NON-NEGOTIABLE:**
1. NEVER modify any `.ts` file EXCEPT `app.module.ts` (only to add new library imports)
2. NEVER break any Angular binding: `[(ngModel)]`, `(click)`, `*ngFor`, `*ngIf`, `routerLink`, `routerLinkActive`
3. NEVER change any HTTP call, service, guard, interceptor, or API payload
4. NEVER break the booking flow, email/Brevo flow, patient portal token flow, or PWA/Capacitor config
5. PRESERVE ALL existing `(ngSubmit)`, `(paste)`, `(keydown)`, `(input)` event handlers
6. After ALL changes: run `npm run build` — it MUST pass with 0 errors
7. If you touch `ngsw-config.json` or `capacitor.config.ts`, run `npx cap sync` afterwards
8. Provide a final summary of every modified file + a manual test checklist

---

## STEP 1 — PROJECT AUDIT (do this first)

Before editing anything:
```
List every file in frontend/src/app/ recursively
Read package.json
Read src/styles.css
Read tailwind.config.js
Read angular.json (styles[] and scripts[] arrays)
Read src/app/app.module.ts
```

Confirm you found all these pages:
- `home/` — Public landing page
- `booking/` — Smart AI booking wizard
- `patient-portal/` — Patient private portal
- `patient-dashboard/components/` — Dashboard sub-widgets (doctor-header, live-tracking, weather-widget, traffic-widget, appointment-history, appointment-suggestion)
- `medical-staff/authenticate/` — Staff PIN login
- `medical-staff/components/shell/` — Staff sidebar layout
- `medical-staff/components/dashboard/` — Doctor dashboard
- `medical-staff/components/planning/` — Calendar planning
- `medical-staff/components/appointments/` — Emergency appointments
- `medical-staff/components/patients/` — Patient list
- `medical-staff/components/waiting-list/` — Waiting list
- `medical-staff/components/optimization/` — AI optimization panel
- `medical-staff/components/analytics/` — Analytics
- `medical-staff/components/notifications/` — Notifications
- `medical-staff/components/settings/` — Settings
- `doctors/` — Doctors listing page
- `header/` — Shared header
- `shared/notification-toast/` — Toast component
- `shared/logo/` — Logo component

---

## STEP 2 — INSTALL LIBRARIES

Run in `frontend/`:

```bash
# Animation & scroll
npm install animate.css@4.1.1
npm install aos@2.3.4 @types/aos

# Lottie for AI loader animations
npm install lottie-web@5.12.2
npm install ngx-lottie@7.3.4

# Premium skeleton loaders
npm install ngx-skeleton-loader@7.0.0

# Premium toast notifications
npm install @ngneat/hot-toast@2.3.0

# CDK for overlays and focus management
npm install @angular/cdk@13.3.9

# Lightweight tilt effect (CSS-based, no heavy deps)
npm install vanilla-tilt@1.8.1

# Lucide icons (tree-shakeable, Angular-compatible via direct SVG import)
# DO NOT install any angular wrapper — use inline SVG directly, as already done in the project

# CountUp for animated numbers
npm install countup.js@2.8.0
```

**After install, in `angular.json` under `projects.test.architect.build.options.styles`:**
```json
"node_modules/animate.css/animate.min.css",
"node_modules/aos/dist/aos.css"
```

**In `angular.json` under `scripts`:**
```json
"node_modules/aos/dist/aos.js",
"node_modules/vanilla-tilt/dist/vanilla-tilt.min.js",
"node_modules/countup.js/dist/countUp.umd.js"
```

**In `app.module.ts` add:**
```typescript
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { LottieModule } from 'ngx-lottie';
import { HotToastModule } from '@ngneat/hot-toast';
import { OverlayModule } from '@angular/cdk/overlay';
import player from 'lottie-web';

export function playerFactory() { return player; }

// In imports[]:
NgxSkeletonLoaderModule.forRoot({ animation: 'progress-dark', loadingText: '' }),
LottieModule.forRoot({ player: playerFactory }),
HotToastModule.forRoot({
  position: 'top-right',
  style: {
    borderRadius: '16px',
    padding: '14px 18px',
    fontWeight: '600',
    fontFamily: 'DM Sans, sans-serif',
    boxShadow: '0 20px 60px rgba(0,0,0,0.15)'
  }
}),
OverlayModule,
```

---

## STEP 3 — GLOBAL DESIGN SYSTEM (`src/styles.css`)

**Replace the entire `:root` block and add all of the following. Keep the existing @import font lines.**

```css
/* ═══════════════════════════════════════════════════════════════
   OPTICLINIC — DESIGN TOKENS V3
   ═══════════════════════════════════════════════════════════════ */
:root {
  /* Brand */
  --oc-brand:          #0284c7;
  --oc-brand-dark:     #0369a1;
  --oc-brand-light:    #38bdf8;
  --oc-brand-xlight:   #e0f2fe;
  --oc-cyan:           #06b6d4;
  --oc-cyan-dark:      #0891b2;

  /* Semantic */
  --oc-success:        #10b981;
  --oc-warning:        #f59e0b;
  --oc-danger:         #ef4444;
  --oc-danger-dark:    #dc2626;
  --oc-purple:         #8b5cf6;

  /* Surfaces — Light mode */
  --oc-bg:             #f8fafc;
  --oc-surface-0:      #ffffff;
  --oc-surface-1:      rgba(255,255,255,0.72);
  --oc-surface-2:      rgba(248,250,252,0.88);
  --oc-border:         rgba(148,163,184,0.15);
  --oc-border-strong:  rgba(2,132,199,0.2);

  /* Surfaces — Dark mode (staff dashboard) */
  --oc-dark-bg:        #060d1f;
  --oc-dark-surface:   rgba(255,255,255,0.05);
  --oc-dark-border:    rgba(255,255,255,0.08);
  --oc-dark-text:      #e2e8f0;

  /* Text */
  --oc-text-1:         #0f172a;
  --oc-text-2:         #475569;
  --oc-text-3:         #94a3b8;

  /* Radius */
  --oc-r-sm:    0.75rem;
  --oc-r-md:    1rem;
  --oc-r-lg:    1.5rem;
  --oc-r-xl:    2rem;
  --oc-r-2xl:   2.5rem;
  --oc-r-3xl:   3rem;

  /* Shadows */
  --oc-shadow-xs: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --oc-shadow-sm: 0 4px 12px rgba(0,0,0,0.06), 0 2px 6px rgba(0,0,0,0.04);
  --oc-shadow-md: 0 8px 32px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
  --oc-shadow-lg: 0 24px 64px rgba(0,0,0,0.12), 0 8px 24px rgba(0,0,0,0.06);
  --oc-shadow-xl: 0 40px 80px rgba(0,0,0,0.16), 0 16px 40px rgba(0,0,0,0.08);
  --oc-shadow-brand: 0 8px 32px rgba(2,132,199,0.35);
  --oc-shadow-brand-lg: 0 16px 48px rgba(2,132,199,0.45);
  --oc-shadow-glow: 0 0 60px rgba(2,132,199,0.2);

  /* Transitions */
  --oc-ease:     cubic-bezier(0.4, 0, 0.2, 1);
  --oc-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);
  --oc-t-fast:   0.15s var(--oc-ease);
  --oc-t-base:   0.25s var(--oc-ease);
  --oc-t-slow:   0.4s  var(--oc-ease);
  --oc-t-spring: 0.5s  var(--oc-spring);
}

/* ═══════════════════════════════════════════════════════════════
   KEYFRAMES
   ═══════════════════════════════════════════════════════════════ */
@keyframes oc-float {
  0%,100% { transform: translateY(0)    scale(1); }
  50%      { transform: translateY(-18px) scale(1.03); }
}
@keyframes oc-pulse-ring {
  0%    { box-shadow: 0 0 0 0   rgba(2,132,199,0.4); }
  70%   { box-shadow: 0 0 0 20px rgba(2,132,199,0);   }
  100%  { box-shadow: 0 0 0 0   rgba(2,132,199,0);   }
}
@keyframes oc-mesh-drift {
  0%   { transform: translate(0,0)   scale(1); }
  33%  { transform: translate(50px,-40px) scale(1.08); }
  66%  { transform: translate(-30px, 25px) scale(0.94); }
  100% { transform: translate(0,0)   scale(1); }
}
@keyframes oc-spin-cw  { to { transform: rotate(360deg); } }
@keyframes oc-spin-ccw { to { transform: rotate(-360deg); } }
@keyframes oc-shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position:  400px 0; }
}
@keyframes oc-count-pop {
  0%   { opacity:0; transform: translateY(10px) scale(0.9); }
  60%  { transform: translateY(-3px) scale(1.04); }
  100% { opacity:1; transform: translateY(0) scale(1); }
}
@keyframes oc-fade-up {
  from { opacity:0; transform: translateY(24px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes oc-slide-in-right {
  from { opacity:0; transform: translateX(32px); }
  to   { opacity:1; transform: translateX(0); }
}
@keyframes oc-success-draw {
  from { stroke-dashoffset: 100; }
  to   { stroke-dashoffset: 0; }
}
@keyframes oc-shake {
  0%,100%{ transform: translateX(0); }
  20%    { transform: translateX(-8px); }
  40%    { transform: translateX(8px); }
  60%    { transform: translateX(-5px); }
  80%    { transform: translateX(5px); }
}
@keyframes oc-gradient-shift {
  0%,100% { background-position: 0% 50%; }
  50%     { background-position: 100% 50%; }
}
@keyframes oc-torus-spin {
  from { transform: translateY(-50%) rotateZ(0deg) rotateX(72deg); }
  to   { transform: translateY(-50%) rotateZ(360deg) rotateX(72deg); }
}

/* ═══════════════════════════════════════════════════════════════
   UTILITY CLASSES
   ═══════════════════════════════════════════════════════════════ */

/* Glass */
.oc-glass {
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.55);
}
.oc-glass-strong {
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(32px) saturate(200%);
  border: 1px solid rgba(255,255,255,0.7);
}
.oc-glass-dark {
  background: rgba(10,20,40,0.65);
  backdrop-filter: blur(24px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.07);
}

/* Gradient text */
.oc-gradient-text {
  background: linear-gradient(135deg, var(--oc-brand) 0%, var(--oc-cyan) 60%, var(--oc-brand-light) 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: oc-gradient-shift 4s ease infinite;
}
.oc-gradient-text-warm {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Cards */
.oc-card {
  background: #fff;
  border-radius: var(--oc-r-xl);
  box-shadow: var(--oc-shadow-md);
  border: 1px solid var(--oc-border);
  transition: transform var(--oc-t-slow), box-shadow var(--oc-t-slow);
}
.oc-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--oc-shadow-lg);
}
.oc-card-glass {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(24px) saturate(200%);
  border-radius: var(--oc-r-xl);
  border: 1px solid rgba(255,255,255,0.6);
  box-shadow: var(--oc-shadow-md);
  transition: transform var(--oc-t-slow), box-shadow var(--oc-t-slow);
}
.oc-card-glass:hover {
  transform: translateY(-6px);
  box-shadow: var(--oc-shadow-lg);
}

/* Tilt cards — activated by VanillaTilt JS */
.oc-tilt {
  transform-style: preserve-3d;
  will-change: transform;
}
.oc-tilt-inner {
  transform: translateZ(30px);
}

/* Buttons */
.oc-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all var(--oc-t-base);
  position: relative;
  overflow: hidden;
  white-space: nowrap;
}
.oc-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.15);
  opacity: 0;
  transition: opacity var(--oc-t-fast);
}
.oc-btn:hover::after  { opacity: 1; }
.oc-btn:active        { transform: scale(0.97); }

.oc-btn-primary {
  background: linear-gradient(135deg, var(--oc-brand) 0%, var(--oc-cyan) 100%);
  color: #fff;
  border-radius: 999px;
  padding: 0.875rem 2rem;
  box-shadow: var(--oc-shadow-brand);
  font-size: 0.9375rem;
}
.oc-btn-primary:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: var(--oc-shadow-brand-lg);
}
.oc-btn-ghost {
  background: transparent;
  color: var(--oc-brand);
  border: 2px solid rgba(2,132,199,0.25);
  border-radius: 999px;
  padding: 0.875rem 2rem;
  font-size: 0.9375rem;
}
.oc-btn-ghost:hover {
  background: rgba(2,132,199,0.06);
  border-color: var(--oc-brand);
}
.oc-btn-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff;
  border-radius: 999px;
  padding: 0.75rem 1.5rem;
  box-shadow: 0 8px 24px rgba(239,68,68,0.3);
}
.oc-btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(239,68,68,0.4);
}

/* Inputs */
.oc-input {
  width: 100%;
  height: 56px;
  padding: 0 1.25rem;
  background: rgba(248,250,252,0.8);
  border: 1.5px solid rgba(148,163,184,0.2);
  border-radius: var(--oc-r-lg);
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--oc-text-1);
  transition: all var(--oc-t-base);
  font-family: 'DM Sans', sans-serif;
}
.oc-input:focus {
  outline: none;
  border-color: var(--oc-brand);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(2,132,199,0.1);
}
.oc-input::placeholder { color: var(--oc-text-3); }
.oc-input-dark {
  background: rgba(255,255,255,0.07);
  border: 1.5px solid rgba(255,255,255,0.12);
  color: #fff;
  border-radius: var(--oc-r-md);
}
.oc-input-dark:focus {
  border-color: rgba(56,189,248,0.6);
  background: rgba(255,255,255,0.1);
  box-shadow: 0 0 0 4px rgba(56,189,248,0.12);
}

/* Badges */
.oc-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.oc-badge-brand  { background:rgba(2,132,199,0.1);  border:1px solid rgba(2,132,199,0.2);  color:var(--oc-brand); }
.oc-badge-green  { background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.2); color:#059669; }
.oc-badge-red    { background:rgba(239,68,68,0.1);  border:1px solid rgba(239,68,68,0.2);  color:#dc2626; }
.oc-badge-amber  { background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.2); color:#b45309; }
.oc-badge-purple { background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.2); color:#7c3aed; }
.oc-badge-dark   { background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);color:#e2e8f0; }

/* Live dot */
.oc-live-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--oc-success);
  animation: oc-pulse-ring 2s cubic-bezier(0.215,0.61,0.355,1) infinite;
  display: inline-block;
}

/* Skeleton shimmer override */
ngx-skeleton-loader .loader {
  border-radius: var(--oc-r-lg) !important;
  background: linear-gradient(90deg, #f1f5f9 25%, #e8eef5 50%, #f1f5f9 75%) !important;
  background-size: 400px 100% !important;
  animation: oc-shimmer 1.4s ease-in-out infinite !important;
}

/* Section titles */
.oc-section-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.4rem 1rem;
  background: linear-gradient(135deg, rgba(2,132,199,0.08), rgba(6,182,212,0.06));
  border: 1px solid rgba(2,132,199,0.18);
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--oc-brand);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
}

/* AOS custom easing */
[data-aos] { pointer-events: none; }
[data-aos].aos-animate { pointer-events: auto; }

/* Noise texture */
.oc-noise {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 200px 200px;
}

/* Mesh background */
.oc-mesh-bg {
  background:
    radial-gradient(ellipse 80% 60% at 20% -10%,  rgba(2,132,199,0.09)  0%, transparent 60%),
    radial-gradient(ellipse 60% 80% at 90%  80%,  rgba(6,182,212,0.07)  0%, transparent 60%),
    radial-gradient(ellipse 100% 100% at 50% 50%, rgba(248,250,252,0.99) 0%, transparent 100%),
    #f8fafc;
}

/* Responsive mobile */
@media (max-width: 768px) {
  .oc-card:hover,
  .oc-card-glass:hover { transform: none; }
  .oc-btn-primary:hover { transform: none; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## STEP 4 — PAGE-BY-PAGE REDESIGN

---

### 4.1 — HEADER (`header/header.component.html` + `.css`)

Transform the sticky header into a premium glassmorphism navbar with animated underline links, a gradient CTA button, and scroll-aware shadow.

**In the component TS (DO NOT touch logic — only add `@HostListener` for scroll class if not present):**
If `scrolled` boolean already exists, use it. If not, add only:
```typescript
@HostListener('window:scroll') onScroll() {
  this.scrolled = window.scrollY > 20;
}
scrolled = false;
```

**HTML — replace the header wrapper and its children's classes:**

```html
<header [class.oc-header--scrolled]="scrolled"
        class="oc-header sticky top-0 z-50 transition-all duration-300">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-[72px]">

      <!-- Logo — keep existing <app-logo> and routerLink -->
      <a routerLink="/" class="flex items-center gap-3 group" (click)="scrollTo('top', $event)">
        <div class="oc-header-logo-wrap">
          <app-logo size="md"></app-logo>
        </div>
      </a>

      <!-- Nav — keep all existing hrefs, routerLinks, scrollTo calls -->
      <nav class="hidden md:flex items-center gap-1">
        <a *ngFor="let link of navLinks"
           [href]="link.href"
           (click)="link.click ? link.click($event) : null"
           class="oc-nav-link group relative px-4 py-2.5 text-sm font-semibold text-slate-500 hover:text-slate-900 transition-colors rounded-xl hover:bg-slate-50">
          {{ link.label }}
          <span class="oc-nav-underline absolute bottom-1 left-4 right-4 h-0.5 bg-gradient-to-r from-sky-500 to-cyan-500 scale-x-0 group-hover:scale-x-100 transition-transform origin-left rounded-full"></span>
        </a>
      </nav>

      <!-- CTA — keep existing routerLink -->
      <a routerLink="/patient/booking"
         class="oc-btn oc-btn-primary text-sm"
         style="padding:0.625rem 1.5rem;border-radius:999px;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        Prendre RDV
      </a>
    </div>
  </div>
</header>
```

**CSS:**
```css
.oc-header {
  background: rgba(248,250,252,0.75);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(148,163,184,0.1);
}
.oc-header--scrolled {
  background: rgba(255,255,255,0.92);
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  border-bottom-color: rgba(148,163,184,0.15);
}
```

---

### 4.2 — HOME PAGE (`home/home.component.html` + `.css`)

Keep EVERY existing binding: `scrollTo()`, `onSearch()`, `*ngFor` on doctors, `routerLink` on doctor cards, `bookDoctor()`, section IDs.

**Add to the component's `ngOnInit()`** (in `.ts` — only add AOS init, nothing else):
```typescript
// Add at top of ngOnInit():
(window as any)['AOS']?.init({ duration: 700, once: true, offset: 60 });
```

**HTML structure — wrap each section in AOS attributes:**

```html
<main class="min-h-screen oc-mesh-bg text-slate-800 font-sans relative overflow-hidden scroll-smooth">

  <!-- Noise overlay -->
  <div class="fixed inset-0 z-0 pointer-events-none oc-noise opacity-[0.022]"></div>

  <!-- Grid pattern -->
  <div class="fixed inset-0 z-0 pointer-events-none"
       style="background-image:linear-gradient(rgba(2,132,199,0.035) 1px, transparent 1px),linear-gradient(90deg, rgba(2,132,199,0.035) 1px, transparent 1px);background-size:48px 48px;"></div>

  <!-- Animated orbs -->
  <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden">
    <div style="position:absolute;width:700px;height:700px;border-radius:50%;
                background:radial-gradient(circle,rgba(2,132,199,0.11) 0%,transparent 70%);
                top:-20%;left:-10%;animation:oc-mesh-drift 20s ease-in-out infinite;"></div>
    <div style="position:absolute;width:600px;height:600px;border-radius:50%;
                background:radial-gradient(circle,rgba(6,182,212,0.09) 0%,transparent 70%);
                bottom:-15%;right:-8%;animation:oc-mesh-drift 16s ease-in-out infinite reverse;"></div>
    <div style="position:absolute;width:400px;height:400px;border-radius:50%;
                background:radial-gradient(circle,rgba(56,189,248,0.07) 0%,transparent 70%);
                top:35%;left:45%;animation:oc-mesh-drift 24s ease-in-out infinite 4s;"></div>
  </div>

  <!-- ═══ HEADER (keep existing header component) ═══ -->

  <!-- ═══ HERO SECTION ═══ -->
  <section id="top" class="relative pt-24 pb-36 z-10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid lg:grid-cols-2 gap-20 items-center">

        <!-- LEFT: Copy -->
        <div class="max-w-2xl" data-aos="fade-right">

          <!-- Eyebrow badge with live dot -->
          <div class="oc-section-badge w-fit mb-8">
            <span class="oc-live-dot"></span>
            Plateforme médicale IA · Tunisia
          </div>

          <!-- Title with animated gradient -->
          <h1 class="text-5xl lg:text-[4.5rem] font-black text-slate-900 tracking-tight mb-6 leading-[1.05]">
            Votre santé.<br>Un rendez-vous en
            <span class="oc-gradient-text"> 30 secondes.</span>
          </h1>

          <p class="text-xl text-slate-500 mb-10 leading-relaxed font-medium max-w-lg">
            Trouvez le bon médecin et prenez rendez-vous instantanément.
            Notre IA Google OR-Tools optimise chaque créneau pour vous.
          </p>

          <!-- Search bar — KEEP ALL EXISTING BINDINGS, only improve wrapper style -->
          <div class="oc-glass-strong p-2.5 rounded-[2rem] flex flex-col md:flex-row gap-2 relative z-20"
               style="box-shadow:0 24px 64px -12px rgba(0,0,0,0.1),0 0 0 1px rgba(255,255,255,0.9) inset;">

            <!-- Keep existing input #specInput with all classes, just add wrapper -->
            <div class="flex-1 relative group">
              <div class="absolute inset-y-0 left-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-sky-500 transition-colors">
                <!-- existing icon SVG -->
              </div>
              <!-- KEEP EXISTING INPUT EXACTLY AS IS -->
            </div>

            <div class="w-px bg-slate-200/80 self-stretch mx-1 hidden md:block"></div>

            <!-- Keep existing select #regionInput exactly as is -->

            <!-- KEEP EXISTING SEARCH BUTTON with (click)="onSearch(...)" -->
            <!-- Just replace its class with: class="oc-btn oc-btn-primary shrink-0 h-14 px-8" -->
          </div>

          <!-- Trust metrics row -->
          <div class="flex flex-wrap items-center gap-6 mt-7">
            <div class="flex -space-x-2">
              <!-- 5 colored avatars -->
              <div *ngFor="let c of ['#ef4444','#0284c7','#10b981','#f59e0b','#8b5cf6']; let i=index"
                   class="w-9 h-9 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-black"
                   [style.background]="c"
                   [style.z-index]="5-i">
                {{ 'ABCDE'.charAt(i) }}
              </div>
            </div>
            <p class="text-sm text-slate-500 font-medium">
              <span class="font-black text-slate-800">+2 400</span> patients ce mois
            </p>
            <div class="flex items-center gap-1.5">
              <span style="color:#f59e0b;font-size:1rem;">★★★★★</span>
              <span class="text-sm font-black text-slate-700">4.9</span>
              <span class="text-sm text-slate-400 font-medium">/ 5</span>
            </div>
          </div>
        </div>

        <!-- RIGHT: 3D floating illustration -->
        <div class="relative lg:ml-auto" data-aos="fade-left" style="perspective:1000px">
          <!-- VanillaTilt wrapper — add id="hero-card" for JS init -->
          <div id="hero-card"
               class="relative rounded-[2.5rem] overflow-hidden oc-tilt"
               style="box-shadow:var(--oc-shadow-xl);transform:rotateY(-4deg) rotateX(2deg);">
            <img src="assets/booking_illustration.jpeg" alt="OptiClinic AI"
                 class="w-full object-cover" style="display:block;height:480px;object-fit:cover;">
            <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(6,18,44,0.65) 0%,rgba(6,18,44,0.1) 60%,transparent 100%);"></div>
            <div class="absolute bottom-8 left-8 right-8 oc-tilt-inner">
              <div class="oc-badge oc-badge-dark mb-3">
                <span class="oc-live-dot" style="width:6px;height:6px;"></span>
                IA Active
              </div>
              <p class="text-white font-black text-2xl leading-tight mb-1">Planification Intelligente</p>
              <p class="text-white/70 text-sm font-medium">Google OR-Tools · Optimisation temps réel</p>
            </div>
          </div>

          <!-- Floating card: confirmed appointment -->
          <div class="absolute -top-6 -right-5 oc-card-glass px-4 py-3 flex items-center gap-3"
               style="border-radius:1.5rem;min-width:190px;animation:oc-float 7s ease-in-out infinite;">
            <div style="width:38px;height:38px;border-radius:12px;flex-shrink:0;
                        background:linear-gradient(135deg,#10b981,#059669);
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:0 4px 16px rgba(16,185,129,0.4);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div>
              <p style="font-size:0.7rem;color:var(--oc-text-3);font-weight:600;margin:0;">RDV confirmé</p>
              <p style="font-size:0.875rem;font-weight:800;color:var(--oc-text-1);margin:0;">Dr. Ben Salah</p>
            </div>
          </div>

          <!-- Floating card: next slot -->
          <div class="absolute -bottom-5 -left-5 oc-card-glass px-4 py-3 flex items-center gap-3"
               style="border-radius:1.5rem;min-width:170px;animation:oc-float 9s ease-in-out infinite 2s;">
            <div style="width:38px;height:38px;border-radius:12px;flex-shrink:0;
                        background:linear-gradient(135deg,var(--oc-brand),var(--oc-cyan));
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:var(--oc-shadow-brand);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div>
              <p style="font-size:0.7rem;color:var(--oc-text-3);font-weight:600;margin:0;">Prochain créneau</p>
              <p style="font-size:0.875rem;font-weight:800;color:var(--oc-text-1);margin:0;">Aujourd'hui 14h30</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- ═══ FEATURES SECTION — id="fonctionnalites" ═══ -->
  <!-- Keep ALL existing content. Wrap each card in: -->
  <!-- <div class="oc-card-glass p-8 group relative overflow-hidden" data-aos="fade-up" data-aos-delay="Xms"> -->
  <!-- Add top accent bar: -->
  <!-- <div class="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-sky-500 to-cyan-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left rounded-full"></div> -->
  <!-- Wrap icons in: -->
  <!-- <div class="w-14 h-14 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg" style="background:linear-gradient(135deg,rgba(2,132,199,0.08),rgba(6,182,212,0.05));border:1px solid rgba(2,132,199,0.12);"> -->

  <!-- ═══ SPECIALTIES SECTION — id="specialites" ═══ -->
  <!-- Keep ALL existing (click)="onSearch(...)" bindings -->
  <!-- Wrap each specialty in: -->
  <!-- <div class="oc-card-glass p-7 text-center group cursor-pointer" data-aos="zoom-in" data-aos-delay="Xms"> -->
  <!-- Wrap emoji in: -->
  <!-- <div class="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-3xl mb-5 transition-all duration-400 group-hover:scale-110" style="background:linear-gradient(135deg,rgba(2,132,199,0.08),rgba(6,182,212,0.05));border:1px solid rgba(2,132,199,0.1);"> -->
  <!-- Add bottom: <span class="text-[10px] font-black text-emerald-500 bg-emerald-50 border border-emerald-100 px-2.5 py-1 rounded-full">Disponible →</span> -->

  <!-- ═══ DOCTORS SECTION ═══ -->
  <!-- Keep ALL *ngFor bindings, bookDoctor(), getInitials(), getReviews() calls -->
  <!-- Skeleton state: -->
  <!--
  <div *ngIf="isLoading" class="grid md:grid-cols-3 gap-6">
    <div *ngFor="let i of [1,2,3,4,5,6]">
      <ngx-skeleton-loader count="1" [theme]="{'height':'280px','border-radius':'1.75rem','background-color':'#f1f5f9'}"></ngx-skeleton-loader>
    </div>
  </div>
  -->
  <!-- Doctor card loaded state: wrap in: -->
  <!-- <div *ngFor="let doc of doctors" class="oc-card-glass p-6 flex flex-col group" data-aos="fade-up"> -->
  <!-- Doctor button: class="oc-btn oc-btn-primary w-full mt-4" style="border-radius:1rem;height:48px;" -->
  <!-- Add rating bar under stars:
  <div style="height:3px;background:#f1f5f9;border-radius:999px;overflow:hidden;margin-top:6px;">
    <div style="height:100%;background:linear-gradient(to right,#f59e0b,#fbbf24);border-radius:999px;"
         [style.width]="(getReviews(doc.nom).rating / 5 * 100) + '%'"></div>
  </div>
  -->

  <!-- ═══ HOW IT WORKS SECTION ═══ -->
  <!-- Keep content. Wrap each step in <div class="oc-card-glass p-8 text-center" data-aos="fade-up"> -->
  <!-- Number circle: style="width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,var(--oc-brand),var(--oc-cyan));color:white;font-size:1.5rem;font-weight:900;display:flex;align-items:center;justify-content:center;margin:0 auto 1.5rem;box-shadow:var(--oc-shadow-brand);" -->

  <!-- ═══ DOCTORS CTA SECTION (blue block) ═══ -->
  <!-- Wrap in: -->
  <!--
  <section class="py-24 relative z-10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="relative rounded-[3rem] p-12 md:p-16 overflow-hidden flex flex-col lg:flex-row items-center justify-between gap-14"
           style="background:linear-gradient(135deg,#0c4a6e 0%,var(--oc-brand) 45%,var(--oc-cyan) 85%,var(--oc-cyan-dark) 100%);
                  box-shadow:0 40px 80px rgba(2,132,199,0.3);">
  -->
  <!-- Stats cards: wrap each in <div class="oc-glass-dark rounded-3xl p-6 text-center" style="border:1px solid rgba(255,255,255,0.1);"> -->
  <!-- CTA buttons: class="oc-btn" with white bg for primary, ghost-white for secondary -->

  <!-- ═══ FOOTER ═══ -->
  <!-- Add a footer that currently doesn't exist: -->
  <footer class="relative z-10 py-14 border-t border-slate-100/80 mt-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid md:grid-cols-4 gap-12 mb-12">
        <div class="md:col-span-2">
          <app-logo size="md"></app-logo>
          <p class="text-slate-400 text-sm font-medium mt-4 max-w-xs leading-relaxed">
            La plateforme médicale intelligente de Tunisie. Sécurisée, rapide, certifiée RGPD.
          </p>
          <div class="flex gap-3 mt-6">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center cursor-pointer hover:scale-110 transition-transform"
                 style="background:rgba(2,132,199,0.08);border:1px solid rgba(2,132,199,0.15);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.71 3.45 2 2 0 0 1 3.69 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 8.91a16 16 0 0 0 6 6l.86-.86a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            </div>
            <div class="w-10 h-10 rounded-xl flex items-center justify-center cursor-pointer hover:scale-110 transition-transform"
                 style="background:rgba(2,132,199,0.08);border:1px solid rgba(2,132,199,0.15);">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </div>
          </div>
        </div>
        <div>
          <h4 class="font-black text-slate-900 text-sm mb-4 uppercase tracking-widest">Patients</h4>
          <ul class="space-y-2.5 text-sm text-slate-400 font-medium">
            <li><a routerLink="/patient/booking" class="hover:text-slate-700 transition-colors">Prendre RDV</a></li>
            <li><a routerLink="/doctors" class="hover:text-slate-700 transition-colors">Nos médecins</a></li>
            <li><a href="#specialites" class="hover:text-slate-700 transition-colors">Spécialités</a></li>
          </ul>
        </div>
        <div>
          <h4 class="font-black text-slate-900 text-sm mb-4 uppercase tracking-widest">Médecins</h4>
          <ul class="space-y-2.5 text-sm text-slate-400 font-medium">
            <li><a routerLink="/medical-staff/authenticate" class="hover:text-slate-700 transition-colors">Espace médecin</a></li>
            <li><a href="#" class="hover:text-slate-700 transition-colors">Rejoindre OptiClinic</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-slate-100 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p class="text-slate-400 text-sm font-medium">© 2024 OptiClinic. Tous droits réservés.</p>
        <div class="flex gap-6 text-sm text-slate-400 font-medium">
          <a href="#" class="hover:text-slate-700 transition-colors">Confidentialité</a>
          <a href="#" class="hover:text-slate-700 transition-colors">Mentions légales</a>
          <a href="#" class="hover:text-slate-700 transition-colors">RGPD</a>
        </div>
      </div>
    </div>
  </footer>

</main>
```

**In `home.component.css`, add VanillaTilt init:**
```css
/* Init VanillaTilt on hero-card after view init — add to ngAfterViewInit in TS: */
/* (window as any).VanillaTilt?.init(document.querySelectorAll('#hero-card'), { max:8, speed:400, glare:true, 'max-glare':0.15 }); */
```

---

### 4.3 — BOOKING PAGE (`booking/booking.component.html` + `.css`)

KEEP ALL: `step`, `formData`, `[(ngModel)]`, `submitSmartBooking()`, `requestAlternativeSlot()`, `optimizationResult`, `errorMessage`.

**Background:** Add `oc-mesh-bg` on `<main>`.

**Form step (step==='form'):** 
- Container: `class="oc-glass-strong"` with `border-radius:var(--oc-r-2xl);padding:2.5rem;`
- Progress bar at top:
```html
<div class="flex items-center gap-3 mb-8">
  <div class="flex-1 h-1.5 rounded-full bg-gradient-to-r from-sky-500 to-cyan-500"></div>
  <div class="flex-1 h-1.5 rounded-full bg-slate-100"></div>
  <div class="flex-1 h-1.5 rounded-full bg-slate-100"></div>
  <span class="text-xs text-slate-400 font-bold whitespace-nowrap ml-1">Étape 1/3</span>
</div>
```
- All inputs: add class `oc-input`
- Labels: add SVG icon before each (user, mail, phone, cake, stethoscope)
- Submit button: `class="oc-btn oc-btn-primary w-full"` with `height:56px;border-radius:var(--oc-r-lg);font-size:1rem;`

**Loading step (step==='loading'):**
```html
<div *ngIf="step === 'loading'"
     class="oc-glass-strong flex flex-col items-center justify-center text-center min-h-[500px]"
     style="border-radius:var(--oc-r-2xl);padding:4rem;">
  <!-- Tri-ring spinner -->
  <div class="relative w-28 h-28 mb-8">
    <div class="absolute inset-0 rounded-full" style="border:3px solid rgba(2,132,199,0.08);"></div>
    <div class="absolute inset-0 rounded-full" style="border:3px solid transparent;border-top-color:#0284c7;animation:oc-spin-cw 1s linear infinite;"></div>
    <div class="absolute inset-3 rounded-full" style="border:3px solid transparent;border-top-color:#06b6d4;animation:oc-spin-ccw 0.7s linear infinite;"></div>
    <div class="absolute inset-6 rounded-full" style="border:3px solid transparent;border-top-color:#38bdf8;animation:oc-spin-cw 0.5s linear infinite;"></div>
    <div class="absolute inset-[30px] rounded-full flex items-center justify-center"
         style="background:linear-gradient(135deg,var(--oc-brand),var(--oc-cyan));box-shadow:var(--oc-shadow-brand);animation:oc-pulse-ring 2s infinite;">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
        <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
      </svg>
    </div>
  </div>
  <h3 class="text-2xl font-black text-slate-900 mb-3">Optimisation IA en cours…</h3>
  <p class="text-slate-500 font-medium max-w-sm mb-6 leading-relaxed">Notre moteur Google OR-Tools analyse tous les créneaux disponibles pour trouver le match parfait.</p>
  <div class="flex gap-2">
    <div class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-bounce" style="animation-delay:0ms"></div>
    <div class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-bounce" style="animation-delay:150ms"></div>
    <div class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-bounce" style="animation-delay:300ms"></div>
  </div>
</div>
```

**Result step (step==='result'):**
- Container: `class="oc-glass-strong animate__animated animate__fadeInUp"` with same border-radius
- Success icon:
```html
<div class="w-18 h-18 rounded-full mx-auto mb-6 flex items-center justify-center"
     style="width:72px;height:72px;background:linear-gradient(135deg,#10b981,#059669);
            box-shadow:0 8px 32px rgba(16,185,129,0.4);animation:oc-pulse-ring 3s infinite;">
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
</div>
```
- Appointment card: `class="oc-card"` with gradient left border: `border-left:4px solid var(--oc-brand);`
- "Alternative slot" button: `class="oc-btn oc-btn-ghost"`

---

### 4.4 — PATIENT PORTAL (`patient-portal/patient-portal.component.html` + `.css`)

KEEP ALL: `activeSection`, `data`, `loading`, `unreadNotifications`, `isTrackingActive`, all section show/hide logic.

**Layout:** Transform into a modern app-like dashboard:

```css
/* Replace .pp-layout with: */
.pp-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: #f1f5f9;
}
@media (max-width: 1024px) {
  .pp-layout { grid-template-columns: 1fr; }
  .pp-sidebar { display: none; } /* shown via mobile drawer */
}

/* Sidebar premium */
.pp-sidebar {
  background: linear-gradient(180deg, #0c1f3f 0%, #0a1628 100%);
  padding: 2rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

/* Nav button */
.pp-nav button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0.875rem 1rem;
  border-radius: 14px;
  border: none;
  background: transparent;
  color: rgba(148,163,184,0.8);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  margin-bottom: 4px;
}
.pp-nav button:hover {
  background: rgba(255,255,255,0.06);
  color: #e2e8f0;
}
.pp-nav button.active {
  background: linear-gradient(135deg, rgba(2,132,199,0.2), rgba(6,182,212,0.1));
  color: #38bdf8;
  border: 1px solid rgba(56,189,248,0.15);
}
.pp-nav button.active::before {
  content:'';
  display:inline-block;
  width:3px;
  height:18px;
  background:linear-gradient(to bottom,#0284c7,#06b6d4);
  border-radius:2px;
  margin-right:-4px;
}

/* Cards */
.pp-card {
  background: #fff;
  border-radius: 1.75rem;
  padding: 1.75rem;
  box-shadow: var(--oc-shadow-sm);
  border: 1px solid rgba(148,163,184,0.1);
  transition: box-shadow 0.25s, transform 0.25s;
}
.pp-card:hover {
  box-shadow: var(--oc-shadow-md);
  transform: translateY(-3px);
}

/* Topbar */
.pp-topbar {
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(148,163,184,0.1);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 40;
}

/* Avatar in topbar */
.pp-avatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--oc-brand), var(--oc-cyan));
  color: white;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  box-shadow: var(--oc-shadow-brand);
}

/* Doctor card */
.pp-doctor-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid rgba(2,132,199,0.15);
}
.pp-doctor-avatar {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--oc-brand), var(--oc-cyan));
  color: white;
  font-weight: 900;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--oc-shadow-brand);
  flex-shrink: 0;
}

/* Tracking card */
.pp-tracking-card {
  background: linear-gradient(135deg, #0c1f3f 0%, #0a1628 100%);
  color: white;
  border: 1px solid rgba(56,189,248,0.1);
}
.pp-tracking-card .pp-card-label { color: rgba(148,163,184,0.9); }

/* Status badge */
.pp-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(148,163,184,0.1);
  color: var(--oc-text-3);
}
.pp-status--ok {
  background: rgba(16,185,129,0.1);
  color: #059669;
}
.pp-status--ok::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  animation: oc-pulse-ring 2s infinite;
  display: inline-block;
}

/* Section titles */
.pp-card-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--oc-text-3);
  margin-bottom: 1rem;
}
```

Add icons to each nav button (SVG inline):
- Tableau de bord → grid icon
- Mes rendez-vous → calendar icon
- Mes documents → file icon
- Notifications → bell icon

**Document cards:** each document item as `<div class="oc-card flex items-center gap-4">` with a colored file icon and a download button styled as `oc-btn oc-btn-ghost` (keep `(click)` handler).

**Empty states:** when no data, show:
```html
<div class="flex flex-col items-center justify-center py-20 text-center">
  <div style="width:80px;height:80px;border-radius:24px;background:rgba(2,132,199,0.06);border:1px solid rgba(2,132,199,0.1);display:flex;align-items:center;justify-content:center;margin-bottom:1.5rem;">
    <!-- relevant empty state icon -->
  </div>
  <h3 style="font-weight:800;color:var(--oc-text-1);margin-bottom:0.5rem;">Aucun élément</h3>
  <p style="color:var(--oc-text-3);font-size:0.875rem;">Rien à afficher pour le moment.</p>
</div>
```

---

### 4.5 — MEDICAL STAFF AUTHENTICATE (`medical-staff/authenticate/`)

The HTML already has a solid structure with `auth-root`, `auth-brand`, `auth-panel`, `auth-card`, `auth-code-box`. DO NOT change any of the Angular bindings: `authenticate()`, `onDigitInput()`, `onDigitKeydown()`, `onPaste()`, `toggleShowCode()`, `isDenied`, `isSuccess`, `isLoading`, `digits`, `showCode`.

**Only upgrade the CSS:**

```css
/* auth.component.css — replace entirely */

.auth-root {
  min-height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #050c1a 0%, #080f20 40%, #0a1628 70%, #0d1f3c 100%);
  font-family: 'DM Sans', sans-serif;
}

/* ── Background ── */
.auth-bg { position: absolute; inset: 0; pointer-events: none; z-index: 0; }

.auth-bg-gradient {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 80% 80% at 80% 50%, rgba(2,132,199,0.10) 0%, transparent 60%),
    radial-gradient(ellipse 50% 60% at 10% 80%, rgba(6,182,212,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 100% 50% at 50% 0%,  rgba(56,189,248,0.05) 0%, transparent 60%);
}

.auth-bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(2,132,199,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(2,132,199,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* 3D Torus rings — pure CSS */
.auth-torus-scene {
  position: absolute;
  right: -80px;
  top: 50%;
  transform: translateY(-50%);
  width: 650px;
  height: 650px;
}
.auth-torus {
  position: absolute;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform-origin: center center;
}
.auth-torus--outer {
  width: 580px; height: 580px;
  margin-left: -290px; margin-top: -290px;
  border: 2px solid rgba(2,132,199,0.1);
  box-shadow:
    0 0 80px rgba(2,132,199,0.08),
    inset 0 0 80px rgba(6,182,212,0.04);
  animation: oc-spin-cw 45s linear infinite;
}
.auth-torus--inner {
  width: 380px; height: 380px;
  margin-left: -190px; margin-top: -190px;
  border: 1.5px solid rgba(6,182,212,0.08);
  animation: oc-spin-ccw 30s linear infinite;
}
.auth-torus-glow {
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  top: 50%; left: 50%;
  margin-left: -150px; margin-top: -150px;
  background: radial-gradient(circle, rgba(2,132,199,0.08) 0%, transparent 70%);
  animation: oc-pulse-ring 6s ease-in-out infinite;
}

/* Also add 3 small orbiting dots around the torus */
.auth-torus--outer::before,
.auth-torus--outer::after {
  content: '';
  position: absolute;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: rgba(56,189,248,0.6);
  box-shadow: 0 0 12px rgba(56,189,248,0.8);
  top: 8px; left: 50%;
  margin-left: -4px;
}
.auth-torus--outer::after {
  bottom: 8px; top: auto;
  background: rgba(6,182,212,0.5);
}

/* ── Brand panel ── */
.auth-brand {
  width: 50%;
  display: none;
  flex-direction: column;
  justify-content: center;
  padding: 4rem 5rem;
  position: relative;
  z-index: 1;
}
@media (min-width: 1024px) { .auth-brand { display: flex; } }

.auth-brand__logo { margin-bottom: 3.5rem; }

.auth-brand__headline {
  font-size: 3.25rem;
  font-weight: 900;
  color: #f8fafc;
  line-height: 1.08;
  margin-bottom: 1.25rem;
  letter-spacing: -0.02em;
}

.auth-brand__sub {
  color: rgba(148,163,184,0.8);
  font-size: 1.0625rem;
  font-weight: 500;
  line-height: 1.7;
  max-width: 380px;
  margin-bottom: 3.5rem;
}

.auth-brand__features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.auth-brand__features li {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: rgba(226,232,240,0.85);
  font-size: 0.9375rem;
  font-weight: 600;
}

.auth-feature-icon {
  width: 44px; height: 44px;
  border-radius: 14px;
  flex-shrink: 0;
  background: rgba(2,132,199,0.12);
  border: 1px solid rgba(2,132,199,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Auth panel (right) ── */
.auth-panel {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  z-index: 1;
}
@media (min-width: 1024px) { .auth-panel { width: 50%; } }

/* ── Auth card ── */
.auth-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 2.5rem;
  padding: 2.75rem 2.5rem;
  box-shadow:
    0 40px 80px rgba(0,0,0,0.5),
    0 0 0 1px rgba(255,255,255,0.05) inset,
    0 0 60px rgba(2,132,199,0.06);
  transition: all 0.3s;
}
.auth-card--shake { animation: oc-shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }
.auth-card--loading { opacity: 0.8; pointer-events: none; }

/* Success card */
.auth-card--success {
  background: rgba(16,185,129,0.08);
  border-color: rgba(16,185,129,0.2);
  text-align: center;
  padding: 4rem 2.5rem;
}
.auth-success-ring {
  width: 80px; height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 8px 32px rgba(16,185,129,0.4);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
  animation: oc-pulse-ring 2s infinite;
}
.auth-success-title {
  font-size: 1.5rem;
  font-weight: 900;
  color: #f8fafc;
  margin-bottom: 0.5rem;
}
.auth-success-sub { color: rgba(148,163,184,0.8); font-size: 0.9rem; font-weight:500; margin-bottom:2rem; }
.auth-success-bar {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 999px;
  overflow: hidden;
}
.auth-success-bar__fill {
  height: 100%;
  background: linear-gradient(to right, #10b981, #06b6d4);
  border-radius: 999px;
  animation: oc-gradient-shift 1.5s ease-in-out forwards;
  width: 0%;
  animation-name: success-fill;
}
@keyframes success-fill {
  from { width: 0%; }
  to   { width: 100%; }
}

.auth-card__title {
  font-size: 1.625rem;
  font-weight: 900;
  color: #f8fafc;
  text-align: center;
  margin-bottom: 0.5rem;
}
.auth-card__subtitle {
  color: rgba(148,163,184,0.7);
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  margin-bottom: 2.5rem;
}

/* Error message */
.auth-error {
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.25);
  color: #fca5a5;
  padding: 0.875rem 1.25rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  text-align: center;
}

/* OTP input row */
.auth-code-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}
.auth-code-grid {
  display: flex;
  gap: 0.625rem;
}
.auth-code-box {
  width: 54px; height: 62px;
  border-radius: 14px;
  text-align: center;
  font-size: 1.625rem;
  font-weight: 900;
  color: #f8fafc;
  background: rgba(255,255,255,0.08);
  border: 1.5px solid rgba(255,255,255,0.12);
  transition: all 0.2s;
  caret-color: #38bdf8;
  letter-spacing: 0.1em;
}
.auth-code-box:focus {
  outline: none;
  border-color: rgba(56,189,248,0.6);
  background: rgba(56,189,248,0.08);
  box-shadow: 0 0 0 3px rgba(56,189,248,0.15), 0 4px 16px rgba(2,132,199,0.2);
}
.auth-code-box--filled {
  border-color: rgba(56,189,248,0.4);
  background: rgba(56,189,248,0.06);
}

/* Eye button */
.auth-eye-btn {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  width: 44px; height: 44px;
  display: flex; align-items: center; justify-content: center;
  color: rgba(148,163,184,0.7);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.auth-eye-btn:hover {
  background: rgba(255,255,255,0.12);
  color: #38bdf8;
  border-color: rgba(56,189,248,0.3);
}

/* Submit button */
.auth-submit {
  width: 100%;
  height: 56px;
  background: rgba(255,255,255,0.08);
  border: 1.5px solid rgba(255,255,255,0.12);
  border-radius: 1.25rem;
  color: rgba(148,163,184,0.6);
  font-size: 1rem;
  font-weight: 800;
  cursor: not-allowed;
  transition: all 0.3s;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  letter-spacing: 0.02em;
  font-family: 'DM Sans', sans-serif;
}
.auth-submit--active {
  background: linear-gradient(135deg, #0284c7, #06b6d4);
  border-color: transparent;
  color: white;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(2,132,199,0.45);
}
.auth-submit--active:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(2,132,199,0.55);
}

/* Spinner */
.auth-spinner {
  width: 18px; height: 18px;
  border: 2.5px solid rgba(255,255,255,0.2);
  border-top-color: white;
  border-radius: 50%;
  animation: oc-spin-cw 0.7s linear infinite;
  display: inline-block;
}

.auth-footer {
  text-align: center;
  color: rgba(100,116,139,0.6);
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 1.75rem;
  letter-spacing: 0.02em;
}

/* Denied state */
.auth-root--denied .auth-card {
  border-color: rgba(239,68,68,0.3);
  box-shadow: 0 0 0 3px rgba(239,68,68,0.08), 0 40px 80px rgba(0,0,0,0.5);
}
```

---

### 4.6 — MEDICAL STAFF SHELL (`medical-staff/components/shell/`)

Keep ALL existing: `baseRoute`, `emergencyBadge`, `waitingBadge`, all `routerLink`, all `routerLinkActive`.

**CSS (`medical-staff-shell.component.css`) — upgrade the `.oc-sidebar`:**

```css
.oc-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: #f1f5f9;
}

.oc-sidebar {
  background: linear-gradient(180deg, #0c1f3f 0%, #080f20 100%);
  padding: 1.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  border-right: 1px solid rgba(255,255,255,0.04);
}

.oc-logo {
  padding: 0.5rem 0.75rem 2rem;
}

.oc-nav-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0.8125rem 0.875rem;
  border-radius: 14px;
  color: rgba(148,163,184,0.75);
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}
.oc-nav-item:hover {
  background: rgba(255,255,255,0.06);
  color: #cbd5e1;
}
.oc-nav-active {
  background: linear-gradient(135deg, rgba(2,132,199,0.18), rgba(6,182,212,0.1));
  color: #38bdf8;
  border: 1px solid rgba(56,189,248,0.12);
}
.oc-nav-active::before {
  content: '';
  position: absolute;
  left: 0; top: 20%; bottom: 20%;
  width: 3px;
  background: linear-gradient(to bottom, #0284c7, #06b6d4);
  border-radius: 0 2px 2px 0;
}

.oc-badge {
  margin-left: auto;
  font-size: 0.65rem;
  font-weight: 900;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  min-width: 20px;
  text-align: center;
}
.oc-badge-red  { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.oc-badge-cyan { background: rgba(6,182,212,0.15); color: #22d3ee; border: 1px solid rgba(6,182,212,0.2); }

/* Content area */
.oc-content {
  background: #f1f5f9;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Topbar inside content */
.oc-topbar {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(148,163,184,0.1);
  padding: 0 2rem;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 30;
  box-shadow: 0 1px 0 rgba(0,0,0,0.03);
}
```

---

### 4.7 — DOCTOR DASHBOARD (`medical-staff/components/dashboard/`)

Keep ALL: `stats`, `currentUser`, `openPlanning()`, `openEmergency()`, `loading`, `errorMessage`.

**CSS — upgrade `.dash-` classes:**

```css
.dash-wrap {
  padding: 2rem 2.5rem;
  max-width: 1400px;
}

/* Hero banner */
.dash-hero {
  border-radius: 2rem;
  padding: 2.5rem 3rem;
  position: relative;
  overflow: hidden;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, #0c4a6e 0%, #0284c7 45%, #06b6d4 90%);
  box-shadow: 0 24px 64px rgba(2,132,199,0.3);
}
.dash-hero-blob1, .dash-hero-blob2 {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.dash-hero-blob1 {
  width: 400px; height: 400px;
  background: rgba(255,255,255,0.08);
  top: -100px; right: -100px;
}
.dash-hero-blob2 {
  width: 300px; height: 300px;
  background: rgba(6,182,212,0.15);
  bottom: -80px; left: 40%;
}

.dash-hero-body {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
  flex-wrap: wrap;
}

.dash-ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0.35rem 1rem;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  color: rgba(255,255,255,0.85);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
  width: fit-content;
}
.dash-ai-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #4ade80;
  animation: oc-pulse-ring 2s infinite;
  display: inline-block;
}

.dash-greeting {
  font-size: 2.25rem;
  font-weight: 900;
  color: #fff;
  margin-bottom: 0.75rem;
  line-height: 1.1;
}
.dash-greeting-name {
  display: block;
  font-size: 2.75rem;
}
.dash-greeting-sub {
  color: rgba(255,255,255,0.75);
  font-size: 1rem;
  font-weight: 500;
  max-width: 440px;
  line-height: 1.6;
  margin-bottom: 2rem;
}
.dash-emerg-count  { color: #fca5a5; }
.dash-opt-count    { color: #6ee7b7; }

.dash-hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Keep .btn-primary existing style but upgrade: */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.875rem 1.75rem;
  background: rgba(255,255,255,0.95);
  color: var(--oc-brand);
  font-weight: 800;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.btn-primary:hover {
  background: #fff;
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.btn-danger-outline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.875rem 1.75rem;
  background: rgba(239,68,68,0.12);
  color: #fca5a5;
  font-weight: 800;
  border-radius: 999px;
  border: 1.5px solid rgba(239,68,68,0.25);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.btn-danger-outline:hover {
  background: rgba(239,68,68,0.2);
  border-color: rgba(239,68,68,0.4);
  transform: translateY(-1px);
}

/* Mini stat cards */
.dash-hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.dash-mini-stat {
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 1.25rem;
  padding: 1.25rem;
  text-align: center;
  transition: all 0.2s;
}
.dash-mini-stat:hover {
  background: rgba(255,255,255,0.15);
  transform: translateY(-3px);
}
.dash-mini-stat-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 0.75rem;
}
.dash-mini-stat--blue .dash-mini-stat-icon  { background: rgba(56,189,248,0.2); color: #38bdf8; }
.dash-mini-stat--red  .dash-mini-stat-icon  { background: rgba(239,68,68,0.2);  color: #f87171; }
.dash-mini-stat--amber .dash-mini-stat-icon { background: rgba(245,158,11,0.2); color: #fbbf24; }
.dash-mini-stat-value {
  font-size: 2rem;
  font-weight: 900;
  color: #fff;
  line-height: 1;
  animation: oc-count-pop 0.6s var(--oc-spring) both;
}
.dash-mini-stat-label {
  font-size: 0.6rem;
  font-weight: 800;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 0.4rem;
}

/* Dashboard section cards */
.dash-section-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--oc-text-1);
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  gap: 10px;
}
.dash-section-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 18px;
  background: linear-gradient(to bottom, var(--oc-brand), var(--oc-cyan));
  border-radius: 2px;
}
```

---

### 4.8 — PLANNING (`medical-staff/components/planning/`)

Keep ALL FullCalendar bindings exactly. Only add CSS around the FullCalendar wrapper:

```css
/* planning.component.css */
:host {
  display: block;
  padding: 2rem 2.5rem;
}

.planning-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.75rem;
}

.planning-title {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--oc-text-1);
  display: flex;
  align-items: center;
  gap: 12px;
}

/* FullCalendar wrapper */
.planning-calendar-wrap {
  background: #fff;
  border-radius: 2rem;
  padding: 1.5rem;
  box-shadow: var(--oc-shadow-md);
  border: 1px solid var(--oc-border);
}

/* Override FullCalendar theme to match OptiClinic */
::ng-deep .fc-theme-standard th {
  border: none;
  background: transparent;
  padding: 0.75rem 0;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--oc-text-3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
::ng-deep .fc-daygrid-day, ::ng-deep .fc-timegrid-slot {
  border-color: rgba(148,163,184,0.1) !important;
}
::ng-deep .fc-toolbar-title {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--oc-text-1);
}
::ng-deep .fc-button {
  background: transparent !important;
  border: 1.5px solid var(--oc-border) !important;
  color: var(--oc-text-2) !important;
  border-radius: 0.75rem !important;
  font-weight: 700 !important;
  font-size: 0.8rem !important;
  padding: 0.5rem 1rem !important;
  transition: all 0.2s !important;
}
::ng-deep .fc-button:hover {
  background: rgba(2,132,199,0.06) !important;
  border-color: var(--oc-brand) !important;
  color: var(--oc-brand) !important;
}
::ng-deep .fc-button-primary:not(.fc-button-active) { /* today btn */
  background: linear-gradient(135deg, var(--oc-brand), var(--oc-cyan)) !important;
  border-color: transparent !important;
  color: white !important;
  box-shadow: var(--oc-shadow-brand) !important;
}
::ng-deep .fc-event {
  border-radius: 10px !important;
  border: none !important;
  font-size: 0.8125rem !important;
  font-weight: 700 !important;
  padding: 2px 8px !important;
}
```

---

### 4.9 — NOTIFICATION TOAST (`shared/notification-toast/`)

Replace the existing toast with a premium design. Keep ALL event bindings, `*ngFor`, `removeNotification()`.

```css
/* notification-toast.component.css */
.toast-container {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
  max-width: 360px;
}

.toast {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.7);
  border-radius: 1.25rem;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  box-shadow: 0 20px 60px rgba(0,0,0,0.12), 0 4px 16px rgba(0,0,0,0.06);
  pointer-events: auto;
  animation: oc-slide-in-right 0.4s var(--oc-spring) both;
  position: relative;
  overflow: hidden;
}

/* Colored left accent */
.toast::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  border-radius: 4px 0 0 4px;
}
.toast--success::before { background: linear-gradient(to bottom, #10b981, #059669); }
.toast--error::before   { background: linear-gradient(to bottom, #ef4444, #dc2626); }
.toast--warning::before { background: linear-gradient(to bottom, #f59e0b, #d97706); }
.toast--info::before    { background: linear-gradient(to bottom, #0284c7, #06b6d4); }

.toast-icon {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.toast--success .toast-icon { background: rgba(16,185,129,0.1); color: #10b981; }
.toast--error   .toast-icon { background: rgba(239,68,68,0.1);  color: #ef4444; }
.toast--warning .toast-icon { background: rgba(245,158,11,0.1); color: #f59e0b; }
.toast--info    .toast-icon { background: rgba(2,132,199,0.1);  color: #0284c7; }

.toast-title {
  font-size: 0.875rem;
  font-weight: 800;
  color: var(--oc-text-1);
  margin-bottom: 0.2rem;
}
.toast-message {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--oc-text-2);
  line-height: 1.4;
}
.toast-close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--oc-text-3);
  cursor: pointer;
  padding: 2px;
  border-radius: 6px;
  transition: color 0.15s;
  flex-shrink: 0;
}
.toast-close:hover { color: var(--oc-text-1); }
```

---

### 4.10 — DOCTORS PAGE (`doctors/`)

Apply same patterns: `oc-mesh-bg` background, `oc-card-glass` for each doctor card, `oc-btn oc-btn-primary` for CTA buttons, `ngx-skeleton-loader` for loading state.

---

### 4.11 — WAITING LIST, PATIENTS, OPTIMIZATION, ANALYTICS, SETTINGS

For each of these medical staff sub-pages:
- Wrap page in `<div style="padding:2rem 2.5rem;max-width:1400px;">`
- Table headers: `background:#f8fafc;font-size:0.7rem;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:var(--oc-text-3);`
- Table rows hover: `background:rgba(2,132,199,0.02);transition:background 0.15s;`
- Status badges: replace plain text with `<span class="oc-badge oc-badge-green/red/amber/purple">` as appropriate
- Action buttons: `oc-btn` with appropriate variant
- Section cards: `oc-card` with `padding:1.75rem;`
- Keep ALL data bindings, *ngFor, click handlers exactly as-is

---

## STEP 5 — MOBILE & PWA POLISH

Add to `styles.css`:

```css
/* Safe area for mobile */
.oc-safe-bottom {
  padding-bottom: max(1rem, env(safe-area-inset-bottom));
}
.oc-safe-top {
  padding-top: max(0px, env(safe-area-inset-top));
}

/* Mobile nav (patient portal bottom nav alternative) */
@media (max-width: 1023px) {
  .pp-sidebar { display: none; }
  .pp-layout  { grid-template-columns: 1fr; }

  /* Bottom tab bar for patient portal on mobile */
  .pp-mobile-nav {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.96);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(148,163,184,0.12);
    display: flex;
    padding: 0.5rem 0 max(0.5rem, env(safe-area-inset-bottom));
    z-index: 50;
    box-shadow: 0 -8px 32px rgba(0,0,0,0.06);
  }
  .pp-mobile-nav button {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    padding: 0.5rem 0;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.625rem;
    font-weight: 700;
    color: var(--oc-text-3);
    transition: color 0.2s;
  }
  .pp-mobile-nav button.active { color: var(--oc-brand); }
  .pp-mobile-nav button svg {
    width: 22px; height: 22px;
    stroke: currentColor;
  }
}
```

**Add mobile bottom nav to `patient-portal.component.html` BEFORE `</div>` (keep all existing `(click)` and `[class.active]`):**

```html
<!-- Mobile bottom nav — shown only on small screens -->
<nav class="pp-mobile-nav md:hidden">
  <button type="button" [class.active]="activeSection==='dashboard'" (click)="activeSection='dashboard'">
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
    Accueil
  </button>
  <button type="button" [class.active]="activeSection==='appointments'" (click)="activeSection='appointments'">
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
    RDV
  </button>
  <button type="button" [class.active]="activeSection==='documents'" (click)="activeSection='documents'">
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
    Documents
  </button>
  <button type="button" [class.active]="activeSection==='notifications'" (click)="activeSection='notifications'">
    <svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
    Alertes
    <span *ngIf="unreadNotifications" style="width:14px;height:14px;border-radius:50%;background:#ef4444;color:white;font-size:0.5rem;font-weight:900;display:flex;align-items:center;justify-content:center;position:absolute;top:4px;right:calc(25% - 18px);">{{ unreadNotifications }}</span>
  </button>
</nav>
```

---

## STEP 6 — FINAL CHECKLIST

### After all changes, run:
```bash
cd frontend
npm run build
# Must complete with 0 errors, warnings are acceptable
```

### If Capacitor/PWA files were touched:
```bash
npx cap sync
```

### Manual test checklist:
```
[ ] Home page loads, hero renders, search works, doctor cards load
[ ] Specialty click triggers search
[ ] "Prendre RDV" button navigates to /patient/booking
[ ] Booking form: all ngModel fields bind correctly, name saves as typed (not hardcoded)
[ ] Booking loading spinner shows during AI optimization
[ ] Booking result shows correct patient name from form
[ ] Patient portal: token access works, sections switch correctly
[ ] Patient portal: documents list and download work
[ ] Medical staff authenticate: OTP inputs focus correctly, auto-advance, paste works
[ ] Authenticate: correct PIN succeeds, wrong PIN shakes the card
[ ] Medical staff dashboard: stats load, buttons work
[ ] Planning: FullCalendar renders, events display
[ ] Medical staff shell: sidebar navigation works, badges update
[ ] Emergency badge on sidebar updates correctly
[ ] Notifications toast fires on real-time events (socket)
[ ] All hover effects are smooth, no layout shift
[ ] Mobile: patient portal shows bottom nav, no horizontal overflow
[ ] Mobile: booking form is usable on 375px width
[ ] PWA: install banner still works if enabled
[ ] No console errors (warnings OK)
```

---

## SUMMARY OF ALL FILES TO MODIFY

| File | Change type |
|---|---|
| `package.json` | + new dependencies |
| `angular.json` | + styles[] + scripts[] |
| `src/app/app.module.ts` | + module imports only |
| `src/styles.css` | **Full design system replacement** |
| `header/header.component.html` | Visual upgrade |
| `header/header.component.css` | Glass navbar |
| `home/home.component.html` | **Full cinematic redesign** |
| `home/home.component.css` | New styles + VanillaTilt init |
| `booking/booking.component.html` | Form upgrade + premium loader |
| `booking/booking.component.css` | Premium form styles |
| `patient-portal/patient-portal.component.html` | App-like redesign + mobile nav |
| `patient-portal/patient-portal.component.css` | Full portal style system |
| `medical-staff/authenticate/authenticate.component.css` | **Full dark premium CSS** |
| `medical-staff/components/shell/medical-staff-shell.component.css` | Dark sidebar |
| `medical-staff/components/dashboard/medical-staff-dashboard.component.css` | Hero banner + stats |
| `medical-staff/components/planning/planning.component.css` | FullCalendar overrides |
| `medical-staff/components/*/` | Badge, card, button upgrades |
| `shared/notification-toast/notification-toast.component.css` | Premium toast |
| `doctors/doctors.component.html` | Skeleton + card upgrade |
| `doctors/doctors.component.css` | Doctor card styles |

## FILES TO NEVER TOUCH:
```
src/app/services/*.ts
src/app/guards/*.ts
src/app/interceptors/*.ts
src/app/patient-portal/patient-portal.service.ts
src/app/booking/booking.component.ts
src/app/medical-staff/authenticate/authenticate.component.ts
src/app/medical-staff/services/*.ts
src/app/patient-dashboard/services/*.ts
capacitor.config.ts
ngsw-config.json
src/app/app-routing.module.ts
```

---

*End of OPTICLINIC FRONTEND ULTRA UI MASTER PROMPT V3*

---

## PATCH V3.1 — FONDS CLAIRS MÉDICAUX (À APPLIQUER EN PRIORITÉ)

> **Ce patch annule et remplace tous les fonds dark du prompt principal.**
> L'identité visuelle cible : **blanc médical · bleu glacier · cyan doux** — comme Apple Health, Google Health, ou Doctolib Pro.
> Seule exception autorisée au dark : la page `authenticate` (staff login) et la sidebar staff.

---

### CORRECTION GLOBALE — `src/styles.css`

**Remplace ENTIÈREMENT le bloc `body` et les variables de fond par ceci :**

```css
:root {
  /* ── Fonds médicaux clairs ── */
  --oc-bg:            #f8fafc;          /* fond global pages publiques */
  --oc-bg-alt:        #f0f9ff;          /* fond légèrement bleuté (booking) */
  --oc-bg-portal:     #f1f5f9;          /* fond patient portal */
  --oc-bg-dashboard:  #f4f7fb;          /* fond staff dashboard */

  /* ── Surfaces ── */
  --oc-surface-0:     #ffffff;
  --oc-surface-1:     rgba(255,255,255,0.80);
  --oc-surface-2:     rgba(240,249,255,0.90);

  /* ── Orbs clairs (pas de bleu foncé saturé) ── */
  --oc-orb-1: rgba(186,230,255,0.45);   /* bleu très pâle */
  --oc-orb-2: rgba(167,243,208,0.25);   /* vert menthe très doux */
  --oc-orb-3: rgba(224,242,254,0.60);   /* cyan glacier */
}

body {
  margin: 0;
  font-family: 'DM Sans', system-ui, -apple-system, Segoe UI, sans-serif;
  background: var(--oc-bg);
  color: #0f172a;
  min-height: 100vh;
  overflow-x: hidden;
  /* AUCUN gradient dark sur body — fond blanc pur */
}

/* Supprime les pseudo-éléments dark body::before / body::after existants */
body::before, body::after { display: none !important; }
```

---

### HOME PAGE — fond médical clair

**Remplace le fond `<main>` par :**

```html
<main class="min-h-screen text-slate-800 font-sans relative overflow-hidden scroll-smooth"
      style="background: #f8fafc;">

  <!-- Noise très subtil -->
  <div class="fixed inset-0 z-0 pointer-events-none oc-noise opacity-[0.018]"></div>

  <!-- Grid pattern très léger -->
  <div class="fixed inset-0 z-0 pointer-events-none"
       style="background-image:
                linear-gradient(rgba(2,132,199,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(2,132,199,0.03) 1px, transparent 1px);
              background-size: 48px 48px;">
  </div>

  <!-- Orbs médicaux CLAIRS — pas de bleu foncé -->
  <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden">

    <!-- Bleu glacier haut gauche -->
    <div style="position:absolute;width:700px;height:700px;border-radius:50%;
                background:radial-gradient(circle, rgba(186,230,255,0.5) 0%, transparent 70%);
                top:-20%;left:-10%;
                animation:oc-mesh-drift 22s ease-in-out infinite;"></div>

    <!-- Cyan très doux haut droite -->
    <div style="position:absolute;width:500px;height:500px;border-radius:50%;
                background:radial-gradient(circle, rgba(167,243,208,0.3) 0%, transparent 70%);
                top:-5%;right:-8%;
                animation:oc-mesh-drift 18s ease-in-out infinite reverse;"></div>

    <!-- Bleu très pâle centre bas -->
    <div style="position:absolute;width:600px;height:600px;border-radius:50%;
                background:radial-gradient(circle, rgba(224,242,254,0.6) 0%, transparent 70%);
                bottom:-15%;left:30%;
                animation:oc-mesh-drift 26s ease-in-out infinite 3s;"></div>

  </div>
```

**Header** — fond blanc pur avec ombre légère :
```css
.oc-header {
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(20px) saturate(160%);
  border-bottom: 1px solid rgba(148,163,184,0.1);
}
.oc-header--scrolled {
  background: rgba(255,255,255,0.97);
  box-shadow: 0 2px 20px rgba(0,0,0,0.04);
}
```

---

### BOOKING PAGE — fond bleu très pâle

```html
<main class="min-h-screen font-sans relative overflow-hidden"
      style="background: linear-gradient(160deg, #f0f9ff 0%, #f8fafc 50%, #ecfdf5 100%);">

  <!-- Orbs clairs -->
  <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden">
    <div style="position:absolute;width:500px;height:500px;border-radius:50%;
                background:radial-gradient(circle,rgba(186,230,255,0.45) 0%,transparent 70%);
                top:-15%;left:-10%;
                animation:oc-mesh-drift 20s ease-in-out infinite;"></div>
    <div style="position:absolute;width:400px;height:400px;border-radius:50%;
                background:radial-gradient(circle,rgba(167,243,208,0.3) 0%,transparent 70%);
                bottom:-10%;right:-5%;
                animation:oc-mesh-drift 16s ease-in-out infinite reverse;"></div>
  </div>
```

**Formulaire booking :**
```css
/* Form card — blanc pur avec ombre douce */
.booking-form-card {
  background: #ffffff;
  border-radius: var(--oc-r-2xl);
  box-shadow: 0 8px 40px rgba(2,132,199,0.06), 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(186,230,255,0.4);
  padding: 2.5rem;
}

/* Loader card */
.booking-loader-card {
  background: linear-gradient(135deg, #f0f9ff, #ecfeff);
  border: 1px solid rgba(186,230,255,0.5);
  border-radius: var(--oc-r-2xl);
}

/* Result card */
.booking-result-card {
  background: linear-gradient(135deg, #f0fdf4, #f0f9ff);
  border: 1px solid rgba(167,243,208,0.4);
  border-radius: var(--oc-r-2xl);
}
```

---

### PATIENT PORTAL — fond gris perle médical

```css
/* patient-portal.component.css */

.pp-layout {
  background: #f4f7fb;  /* gris perle médical */
  min-height: 100vh;
}

/* Sidebar : bleu nuit doux — PAS noir */
.pp-sidebar {
  background: linear-gradient(180deg, #1e3a5f 0%, #162d4a 100%);
  /* bleu marine médical — comme Doctolib */
}

/* Topbar blanc */
.pp-topbar {
  background: rgba(255,255,255,0.95);
  border-bottom: 1px solid rgba(148,163,184,0.08);
  box-shadow: 0 1px 8px rgba(0,0,0,0.04);
}

/* Cards blanches avec ombre très légère */
.pp-card {
  background: #ffffff;
  border-radius: 1.5rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.05), 0 1px 4px rgba(0,0,0,0.03);
  border: 1px solid rgba(148,163,184,0.08);
}

/* Doctor card — bleu très pâle */
.pp-doctor-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid rgba(186,230,255,0.5);
}

/* Tracking card — bleu marine doux (pas noir) */
.pp-tracking-card {
  background: linear-gradient(135deg, #1e3a5f 0%, #164e7a 100%);
  border: 1px solid rgba(56,189,248,0.12);
  color: #e2e8f0;
}
```

---

### STAFF DASHBOARD — fond clair avec hero coloré

```css
/* medical-staff-dashboard.component.css */

/* Fond de page — gris très clair */
.dash-wrap {
  background: #f4f7fb;
  min-height: 100%;
  padding: 2rem 2.5rem;
}

/* Hero banner — garde le gradient bleu UNIQUEMENT sur le hero */
.dash-hero {
  background: linear-gradient(135deg, #1e40af 0%, #0284c7 45%, #0891b2 85%, #06b6d4 100%);
  /* bleu médical professionnel — ni trop dark ni trop cyan */
  border-radius: 2rem;
  box-shadow: 0 16px 48px rgba(2,132,199,0.2);
}

/* Cards de stats blanches */
.dash-stat-card {
  background: #ffffff;
  border-radius: 1.5rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.05);
  border: 1px solid rgba(148,163,184,0.08);
  padding: 1.5rem;
  transition: all 0.25s;
}
.dash-stat-card:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  transform: translateY(-3px);
}

/* Mini stats sur hero — garder glass clair */
.dash-mini-stat {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 1.25rem;
  backdrop-filter: blur(12px);
}

/* Section de contenu sous le hero */
.dash-section {
  background: #ffffff;
  border-radius: 1.5rem;
  padding: 1.75rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.05);
  border: 1px solid rgba(148,163,184,0.08);
  margin-top: 1.5rem;
}
```

---

### STAFF SHELL SIDEBAR — bleu marine médical (pas noir)

```css
/* medical-staff-shell.component.css */

.oc-sidebar {
  /* Bleu marine doux style Doctolib/Apple Health — PAS noir */
  background: linear-gradient(180deg, #1a3a5c 0%, #142d48 100%);
  border-right: 1px solid rgba(255,255,255,0.04);
}

.oc-nav-item { color: rgba(148,163,184,0.75); }
.oc-nav-item:hover {
  background: rgba(255,255,255,0.07);
  color: #bfdbfe;  /* bleu pâle au hover */
}
.oc-nav-active {
  background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(14,165,233,0.08));
  color: #7dd3fc;
  border: 1px solid rgba(56,189,248,0.15);
}

/* Contenu principal — fond clair */
.oc-content {
  background: #f4f7fb;
}

/* Topbar staff — blanc */
.oc-topbar {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(148,163,184,0.08);
  box-shadow: 0 1px 0 rgba(0,0,0,0.03);
}
```

---

### AUTHENTICATE PAGE — garde le dark (seule exception)

La page authenticate **reste dark** — c'est voulu et cohérent avec la screenshot que tu as fournie. C'est la seule page dark du projet. Garde le CSS de la section 4.5 du prompt V3 sans modification.

---

### PALETTE MÉDICALE FINALE

```
Pages publiques (home, booking, doctors) :
  Fond global      → #f8fafc  (blanc cassé)
  Fond alt         → #f0f9ff  (bleu glacier)
  Orbs             → rgba(186,230,255,0.45) — bleu très pâle
  Cards            → #ffffff avec shadow très douce
  Accents          → #0284c7 / #06b6d4

Patient Portal :
  Layout bg        → #f4f7fb  (gris perle)
  Sidebar          → #1e3a5f → #162d4a  (bleu marine doux)
  Cards            → #ffffff

Staff Dashboard :
  Layout bg        → #f4f7fb
  Hero banner      → #1e40af → #0284c7 → #06b6d4
  Cards            → #ffffff
  Sidebar          → #1a3a5c → #142d48

Authenticate :
  Fond             → #050c1a → #0a1628  (dark — exception volontaire)
```


# Responsive UI/UX Redesign Implementation Plan (Option A: Modern Campus Consumer Food App)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Smart Meal Finder into a vibrant, modern, campus-centered food app for Universitas Indonesia students that is 100% responsive across mobile, tablet, and desktop devices, free of generic AI-slop, and provides delightful micro-interactions.

**Architecture:** Fluid responsive CSS design floor with Makara UI theme tokens, semantic HTML5 templates, Jinja2 template inheritance, custom monochromatic SVG icons, and vanilla JavaScript client-side interactivity without external framework bloat.

**Tech Stack:** Python 3.13, Flask 3.1.0, Jinja2, Vanilla CSS3 (Custom Properties, Flexbox, Grid, Clamp, Container Queries), Vanilla JS (ES6+), SVG.

**Spec:** Option A from brainstorming session: Modern Campus Consumer Food App with full cross-device responsiveness (viewport 375px to 1440px+).

## Global Constraints

- Zero external CSS/JS framework dependencies (no Bootstrap, Tailwind CDN, or jQuery) - keep it lightweight and blazing fast.
- Zero AI-slop emojis in user interface templates and CSS.
- Monochromatic, precise SVG vector icons via `app/templates/macros/icons.html`.
- Touch target sizes strictly $\ge 48$px for all interactive buttons, inputs, chips, and radio cards.
- High contrast compliant with WCAG AA standard (contrast ratio $\ge 4.5:1$).
- All 163 pytest unit/boundary tests and 4-tier E2E tests must continue to pass 100%.

---

## Tasks

### Task 1: Design Tokens, CSS Foundations & Responsive Layout Grid
**Files:**
- Modify: `app/static/css/style.css`

- [ ] Define comprehensive CSS custom property design system:
  - Theme colors: `--ui-yellow: #FFC700`, `--ui-yellow-hover: #E5B200`, `--ui-dark: #0B0F19`, `--slate-900: #0F172A`, `--slate-800: #1E293B`, `--slate-100: #F1F5F9`, `--slate-50: #F8FAFC`.
  - Faculty theme colors: `--canteen-dallas: #0F766E`, `--canteen-takor: #0369A1`, `--canteen-kansas: #9F1239`, `--canteen-pusgiwa: #6B21A8`, `--canteen-texas: #B45309`, `--canteen-fasilkom: #3730A3`.
  - Elevation & shadows: smooth multi-layer box shadows (`--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`).
  - Fluid typography: using `clamp()` for responsive headings that scale smoothly from 375px mobile to 1440px desktop without jarring jumps.
- [ ] Implement responsive utility classes and container layout (`max-width: 1140px`, fluid padding `1rem` to `2rem`).
- [ ] Add micro-interaction layers: `:hover { transform: translateY(-2px); }`, `:active { transform: translateY(0) scale(0.98); }`, accessible `:focus-visible`.

### Task 2: Base Layout, Sticky Navigation & Campus Footer Overhaul
**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/static/css/style.css`

- [ ] Update `base.html` with modern semantic structure:
  - Top Makara UI accent indicator.
  - Sticky glassmorphic navbar with crisp UI badge, responsive hamburger toggle, and clean mobile navigation drawer.
  - Rich campus footer with Kelompok 5 member roles and student IDs (NPM).
- [ ] Add mobile nav toggle styling and drawer animation in CSS.

### Task 3: Hero Section & Interactive Budget Engine (Home Page)
**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/static/css/style.css`
- Modify: `app/static/js/main.js`

- [ ] Build vibrant hero with live campus status pill:
  - "6 Kantin Kampus Aktif • 146 Menu Terverifikasi • Algoritma Knapsack DP".
  - Headline: "Makan Kenyang, Pas di Kantong Kampus Universitas Indonesia".
- [ ] Overhaul Budget Search Card:
  - High-visibility currency input with prefix `Rp` and live rupiah preview.
  - Tactile preset chips with contextual sublabels (`Rp 10.000 - Hemat Akhir Bulan`, `Rp 15.000 - Standard Mahasiswa`, `Rp 20.000 - Kenyang Lengkap`, `Rp 25.000 - Paket Puas`, `Rp 30.000 - Traktir Teman`).
  - Modern Segmented Toggle Cards for Format:
    - "Semua Pilihan (Fleksibel & Hemat)" vs "Wajib Kombo Lengkap (1 Makanan + 1 Minuman)".
  - Canteen select dropdown with campus badge icon.
  - Dietary preference filter pills with check indicators.
- [ ] Redesign 6 Canteen Showcase Cards:
  - Dallas, Takor, Kansas, Pusgiwa, Texas, Fasilkom with distinct faculty colors, description, and price floor indicator ("Mulai Rp 4.000").

### Task 4: Order-Ticket Style Results & Deficit Fallback Experience
**Files:**
- Modify: `app/templates/results.html`
- Modify: `app/static/css/style.css`

- [ ] Overhaul Recommendation Cards:
  - Digital order-ticket design with top perforation/tag border.
  - Header tier badges ("Rekomendasi Utama", "Paling Hemat", "Pas di Kantong (Sisa Rp 0)").
  - Remaining budget callout ("Sisa Saldo: Rp X.XXX").
  - Clear item rows with item category SVG icon, merchant name, canteen faculty tag, and dietary badges.
  - Collapsible Knapsack DP Algorithm Explainer card.
- [ ] Redesign Deficit View & Fallback Recommendations:
  - Informative deficit card with actionable buttons.
  - Prominent "TETAP BISA KENYANG DENGAN Rp 10.000" section displaying all affordable combinations $\le$ budget.

### Task 5: Mobile-First Optimization & Cross-Device Testing
**Files:**
- Modify: `app/static/css/style.css`
- Modify: `app/static/js/main.js`

- [ ] Add responsive styles for mobile ($375\text{px} - 640\text{px}$):
  - Horizontal smooth scrolling preset chips (`-webkit-overflow-scrolling: touch`).
  - Full-width touch buttons ($\ge 48$px height).
  - Sticky bottom action summary bar on results page when scrolling on mobile.
- [ ] Test on tablet viewports ($768\text{px} - 1024\text{px}$) and desktop ($1200\text{px} - 1440\text{px}$).

### Task 6: Test Verification & Synchronization
**Files:**
- Test: `tests/test_app.py`
- Test: `tests/e2e/test_tier1_features.py`
- Test: `tests/e2e/run_e2e.py`

- [ ] Run `pytest tests` to verify 163 tests pass 100%.
- [ ] Run `python tests/e2e/run_e2e.py` to confirm 69 E2E scenarios pass.
- [ ] Commit and sync changes to GitHub repository.

# Design Direction — Smart Meal Finder (Kampus UI)

**Design Read:** Reading this as a utilitarian campus meal planner web app for Universitas Indonesia students, in a Makara-accented clean paper-and-ink directory style, dial **ENERGY 2 / RHYTHM 2 / MOTION 1**.

## 1. Visual Dials
- **ENERGY 2 (Balanced):** Clear campus personality grounded in Universitas Indonesia identity without loud neon effects, blur-heavy glass cards, or marketing hype.
- **RHYTHM 2 (Consistent with intentional breaks):**
  - Home (`/`) uses an asymmetric desktop split (campus context & real dataset directory summary on the left, budget engine form on the right) followed by a structured campus canteen table-directory rather than repeating identical bento grids.
  - Results (`/recommend`) opens with an inline sticky-friendly refine bar so students can tweak budget, dining mode, canteen, or dietary tags immediately, followed by order-slip combo cards and an expandable Knapsack math explanation.
  - Directory (`/merchants`) pairs canteen zone tabs with live menu search and category pills.
- **MOTION 1 (Tactile Hover & Focus):** Subtle `150ms` border transitions, micro hover shift (`-1px`) on interactive cards, clear `:active` press scale (`0.99`), and automatic disable under `prefers-reduced-motion: reduce`.

## 2. System Tokens & Rule-31 Justifications
- **Core Palette (2 Neutrals + 1 Deliberate Accent):**
  - `--paper: #FFFFFF` & `--surface-muted: #F8FAFC` — High readability under outdoor campus sunlight on mobile screens.
  - `--ink: #0F172A` & `--ink-secondary: #475569` — Crisp slate-black text passing WCAG AA/AAA (`> 7:1` contrast).
  - `--ui-yellow: #FFC700` (Makara UI Yellow) & `--ui-yellow-ink: #78350F` — Used strictly for primary action buttons (`#0F172A` text on `#FFC700`), active brand monogram, and highlight underline bars; never as low-contrast yellow text on white backgrounds.
  - Semantic budget indicators only: `--emerald: #047857` (exact match / hemat) and `--crimson: #B91C1C` (deficit warning).
- **Typography:** `'Plus Jakarta Sans', system-ui, -apple-system, sans-serif` for clean geometric Indonesian display headings paired with `font-variant-numeric: tabular-nums` on every Rupiah amount so prices align visually across rows.
- **Border Radius:** Consistent functional hierarchy (`6px` for small tags, `10px` for inputs/buttons, `14px` for cards) instead of turning every element into a full pill.
- **Touch Targets & Responsive Floor:** Minimum `48px` tap target height across buttons, inputs, segmented controls, and nav links from `360px` viewports up to `1440px` desktop screens with zero horizontal overflow.

## 3. Copywriting & Anti-Slop Constraints
- Zero em dashes (`—`). Use commas, colons, periods, or parentheses.
- Zero AI marketing buzzwords (no "solusi mutakhir", "ekosistem revolusioner", "membuka potensi", "memudahkan perjalanan kuliner").
- Authentic Universitas Indonesia canteen names and faculties sourced from campus references (LBI FIB UI & BEM UI):
  - **Dallas** (FMIPA UI, di bawah musala: *Di Bawah Lindungan Allah SWT*)
  - **Kansas** (FIB UI: *Kantin Sastra*)
  - **Takor** (FISIP UI: *Taman Korea*, eks-Balsem)
  - **Kantek** (FT UI: *Kantin Teknik*, dekat Jembatan Teksas)
  - **Balgebun** (Fasilkom UI: *Balik Gedung Bundar*)
  - **Pusgiwa** (Pusat Kegiatan Mahasiswa UI)
- Ground all numbers displayed in templates in verified dataset counts dynamically passed from Flask (`canteen_count`, `merchant_count`, `available_item_count`).

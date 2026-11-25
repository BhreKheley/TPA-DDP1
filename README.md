# Smart Meal Finder (Pencari Makanan Kampus UI)

**Tugas Pemrograman Akhir (TPA) — Dasar-Dasar Pemrograman 1 (DDP1) Gasal 2026/2027**  
**Kelompok 5 — Fakultas Ilmu Komputer, Universitas Indonesia**

---

## Ringkasan Proyek

**Smart Meal Finder** adalah aplikasi web rekomendasi paket makan mahasiswa Universitas Indonesia berbasis batas uang saku harian. Aplikasi membantu mahasiswa di kampus Depok memilih kombinasi makanan dan minuman yang paling memuaskan di kantin kampus terdekat tanpa melewati anggaran yang tersedia.

Sistem memodelkan pemilihan menu sebagai **0/1 Knapsack Problem** menggunakan *Dynamic Programming*, dilengkapi dengan tiga alur makan riil mahasiswa (Kombo Lengkap Makan+Minum, Mode Bawa Tumbler/Makanan Saja, serta Mode Fleksibel/Jajan Hemat), analisis selisih budget (*deficit handling*), dan direktori 6 kantin ikonik Universitas Indonesia.

---

## Tim Pengembang (Kelompok 5)

| Anggota | NPM | GitHub & Email | Peran & Tanggung Jawab | Reviewer Rekan |
|---|---|---|---|---|
| **Bhre Nabil Faeyza** | `2606887563` | [@BhreKheley](https://github.com/BhreKheley) (`bhrenabil@gmail.com`) | Ketua & Core Algorithm Lead (`core/budget.py`, 0/1 Knapsack DP, GCD scaling, Pytest suite) | Review PR #1 (Naisya) |
| **Naisya Alikha Putri** | `2606888276` | [@naisyaalika](https://github.com/naisyaalika) (`naisyaa.alikha@gmail.com`) | Data & UX Design Lead (`data/merchants.json`, `core/loader.py`, copywriting, desain Figma) | Review PR #3 (Johannes) |
| **Johannes Praba Aji** | `2606748465` | [@Ojokz](https://github.com/Ojokz) (`johannespraba25@gmail.com`) | Web App & QA DevOps Lead (`app/routes.py`, Jinja templates, responsive CSS/JS, CI/CD, E2E suite) | Review PR #2 (Bhre) |

---

## Rancangan Sistem & Desain

- **Blueprint Workflow & Arsitektur Tim:** [docs/ARCHITECTURE_AND_WORKFLOW.md](docs/ARCHITECTURE_AND_WORKFLOW.md)
- **Dokumen Sistem Desain (Anti-Slop Direction):** [DESIGN.md](DESIGN.md)
- **Prototipe Figma:** [Smart Meal Finder UI - Figma](https://www.figma.com/design/a3I0azJfnOlE04Z8s3TvHB)

---

## Arsitektur Modular

Sistem dibangun menggunakan prinsip pemisahan tanggung jawab (*separation of concerns*):

1. **Lapisan Data & Validator (`core/loader.py`, `core/models.py`):**
   - Membaca dan memvalidasi dataset survei kantin UI (`data/merchants.json`).
   - Menggunakan `@dataclass(frozen=True)` (`MenuItem`) agar objek item menu bersifat *immutable*, serta hierarki *custom exception* (`DataFileNotFoundError`, `JSONParseError`, `DataValidationError`).
   - Menyediakan utilitas penyaringan item berdasarkan kantin, harga maksimum, dan normalisasi tag diet (`halal`, `vegetarian`, `spicy`/`pedas`, `non-spicy`).
2. **Lapisan Algoritma Anggaran (`core/budget.py`):**
   - Ditulis menggunakan pustaka standar Python tanpa dependensi optimasi eksternal.
   - `knapsack_01_dp`: Memaksimalkan total *satisfaction score* dalam batas anggaran menggunakan tabel Dynamic Programming 2D dengan penskalaan FPB/GCD untuk efisiensi memori dan runtime.
   - `recommend_meals`: Mengelompokkan kandidat per kantin agar item tetap dalam satu lokasi, mendukung mode Kombo Lengkap (`1 Makanan + 1 Minuman`), Mode Bawa Tumbler (`food_only=True`), dan Mode Fleksibel (`require_combo=False`), serta menghitung defisit dan opsi alternatif jika budget belum mencukupi paket komplit.
3. **Lapisan Web & REST API (`app/`, `run.py`):**
   - Dibangun dengan Flask menggunakan *application factory pattern* (`create_app`).
   - Menyediakan antarmuka web responsif (`/`, `/recommend`, `/merchants`) serta endpoint JSON (`/api/recommend`, `/api/merchants`).
4. **Pengujian Otomatis & CI/CD (`tests/`, `.github/workflows/ci.yml`):**
   - Pengujian unit, rute web, dan harness 4-tier E2E (163 kasus uji pytest + 69 skenario E2E).
   - Pipeline GitHub Actions menjalankan linting `flake8` dan pengujian `pytest` pada Python 3.10, 3.11, dan 3.12.

---

## Cakupan 6 Kantin Kampus UI Depok

Dataset `data/merchants.json` memuat **10 stan makanan dengan 41 menu (40 tersedia, 1 habis)** yang mencakup 6 kawasan kantin ikonik Universitas Indonesia:

1. **Dallas (Di Bawah Lindungan Allah SWT)** — FMIPA UI (di lantai bawah musala FMIPA)
2. **Takor (Taman Korea)** — FISIP UI (area yang dulunya dikenal sebagai Balsem / Balik Semak)
3. **Kansas (Kantin Sastra)** — FIB UI (bangunan beratap kerucut khas Fakultas Ilmu Pengetahuan Budaya)
4. **Kantek (Kantin Teknik)** — FT UI (area Fakultas Teknik dekat Jembatan Teksas)
5. **Balgebun (Kantin Fasilkom)** — Fasilkom UI (kantin area Balik Gedung Bundar)
6. **Pusgiwa (Pusat Kegiatan Mahasiswa)** — Gedung Pusgiwa UI

---

## Struktur Direktori

```text
TK DDP1/
├── .github/workflows/ci.yml              # Pipeline GitHub Actions CI
├── app/
│   ├── __init__.py                       # App factory & filter format_rupiah
│   ├── routes.py                         # Controller halaman web & REST API
│   ├── static/
│   │   ├── css/style.css                 # Stylesheet responsif (360px - 1440px+)
│   │   └── js/main.js                    # Interaksi form, preset mode & live search
│   └── templates/
│       ├── base.html                     # Layout utama, navigasi, footer
│       ├── index.html                    # Halaman awal & pencari budget
│       ├── results.html                  # Halaman tiket rekomendasi & defisit
│       ├── merchants.html                # Direktori kantin + filter live
│       ├── error.html                    # Halaman error HTTP 400/404/405
│       └── macros/icons.html             # Sistem ikon SVG kustom
├── core/
│   ├── __init__.py
│   ├── loader.py                         # Validator & pemuat dataset JSON
│   ├── models.py                         # Model data aplikasi
│   └── budget.py                         # Algoritma 0/1 Knapsack DP & optimizer
├── data/
│   └── merchants.json                    # Dataset 6 kantin UI (10 stan, 41 menu)
├── docs/
│   ├── ARCHITECTURE_AND_WORKFLOW.md      # Rancangan workflow & arsitektur tim
│   └── PR_REVIEWS.md                     # Catatan tinjauan Pull Request tim
├── tests/                                # Pytest unit, web route & 4-tier E2E
├── DESIGN.md                             # Dokumentasi arah desain UI/UX
├── README.md                             # Dokumentasi utama proyek
├── requirements.txt                      # Daftar dependensi Python
├── run.py                                # Titik masuk server Flask lokal
└── start.bat                             # Skrip peluncur cepat Windows
```

---

## Cara Menjalankan Aplikasi Secara Lokal

### 1. Prasyarat
- Python 3.10 atau lebih baru
- Git

### 2. Persiapan Lingkungan & Instalasi
```bash
git clone https://github.com/BhreKheley/TPA-DDP1.git
cd TPA-DDP1

python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Menjalankan Server Web
```bash
python run.py
```
Atau klik dua kali `start.bat` pada Windows. Buka `http://127.0.0.1:5000` di peramban.

### 4. Menjalankan Pengujian & Linting
```bash
pytest -v
python tests/e2e/run_e2e.py
flake8 core app tests --max-line-length=120
```

---

## Tautan Video Presentasi
- Video Demo (Maksimal 15 Menit): `https://youtu.be/placeholder` (diperbarui setelah perekaman selesai)

---

## Catatan Transparansi Penggunaan AI
Sesuai panduan Tugas Pemrograman Akhir DDP1 Gasal 2026/2027, kecerdasan buatan (AI) digunakan sebagai alat bantu penulisan kerangka pengujian awal dan penataan tata letak HTML/CSS. Seluruh algoritma inti (*0/1 Knapsack Dynamic Programming*, validasi skema, serta alur logika web) telah dipahami dan dikuasai oleh setiap anggota Kelompok 5 (Bhre, Naisya, Johannes).

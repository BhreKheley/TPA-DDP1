# Smart Meal Finder (Pencari Makanan Cerdas)
### Tugas Pemrograman Akhir (TPA) - Dasar-Dasar Pemrograman 1 (DDP1)
**Universitas Indonesia - Kelompok 5**

---

## 📌 Deskripsi Proyek / Project Overview
**Smart Meal Finder** adalah aplikasi web rekomendasi makanan berbasis anggaran (*budget-based meal recommendation*) yang dirancang khusus untuk mahasiswa Universitas Indonesia. Aplikasi ini membantu mahasiswa menemukan kombinasi makanan dan minuman optimal yang sesuai dengan batas anggaran harian mereka di berbagai kantin kampus Universitas Indonesia (Kantin Dallas, Takor, Kansas, Pusgiwa, Texas, dan Fasilkom).

Aplikasi ini menggabungkan algoritma optimasi berbasis *Dynamic Programming (0/1 Knapsack Problem)* dengan batasan kategori hidangan (1 Makanan + 1 Minuman), penanganan defisit anggaran yang informatif jika uang saku tidak mencukupi, serta antarmuka web yang intuitif dan responsif dengan tema khas Makara UI (*UI Yellow & Slate*).


### Fitur V2 (lihat `docs/SPEC-v2.md`)
- Merchant yang terjangkau (ada menu berharga <= nominal) dikelompokkan per kantin dan diurut menurut nama.
- Halaman detail merchant (`/merchant/<id>`): menu yang muat, kombinasi terlengkap dalam anggaran (`core/search.py: best_combo`), jam buka dan status buka (bila data ada).
- Label tanggal pembaruan harga, ditandai "mungkin sudah berubah" setelah lebih dari 1 bulan. Field `updated_at` dan `open_hours` di `data/merchants.json` bersifat opsional; isi dari survei asli, jangan dikarang.
- Input nominal menerima `15000`, `15.000`, atau `Rp 15.000`; 0, negatif, dan non-angka ditolak dengan pesan perbaikan.
- Jika tidak ada menu yang muat, halaman menampilkan harga termurah dan selisihnya.

---

## 👥 Tim Pengembang - Kelompok 5

| Nama Anggota | NPM | Akun GitHub & Email | Peran & Tanggung Jawab | Reviewer Rekan |
|---|---|---|---|---|
| **Bhre Nabil Faeyza** | 2606887563 | [@BhreKheley](https://github.com/BhreKheley) (`bhrenabil@gmail.com`) | Core Logic & QA (`core/budget.py`, DP Knapsack Solver, Pytest Suite) | Review kode Naisya |
| **Naisya Alikha Putri** | 2606888276 | [@naisyaalika](https://github.com/naisyaalika) (`naisyaa.alikha@gmail.com`) | Data Modeling & UX (`data/merchants.json`, `core/loader.py`, `core/models.py`) | Review kode Johannes |
| **Johannes Praba Aji** | 2606748465 | [@Ojokz](https://github.com/Ojokz) (`johannespraba25@gmail.com`) | Web Application & CI/CD (`app/routes.py`, Jinja Templates, CSS, GitHub Actions) | Review kode Bhre |

---

## 🎨 Desain Antarmuka & Prototipe Figma
Desain antarmuka UI/UX dirancang khusus tanpa template generik/AI slop, menggunakan sistem warna khas Universitas Indonesia (#FFC700 Makara Yellow & Slate #0F172A), tipografi terbaca jelas, dan sistem ikon vektor SVG kustom.
- **Tautan Figma File:** [Figma Design - Smart Meal Finder UI](https://www.figma.com/design/a3I0azJfnOlE04Z8s3TvHB)

---

## 🏛️ Arsitektur & Algoritma Inti

Sistem dibangun dengan prinsip modularitas tinggi (*separation of concerns*):

1. **Lapisan Data (`core/loader.py`)**:
   - Membaca dan memvalidasi dataset survei lapangan kantin UI (`data/merchants.json`).
   - Menerapkan model data berbasis *frozen dataclass* (`MenuItem`, `Merchant`) dan hierarki *custom exceptions* (`DataValidationError`).
   - Menyediakan fungsi pemfilteran berdasarkan kantin, harga maksimum, dan preferensi diet (*halal*, *vegetarian*).

2. **Lapisan Algoritma Inti (`core/budget.py`)**:
   - Murni menggunakan pustaka standar Python (*zero external algorithmic dependencies*).
   - **Canonical 0/1 Knapsack DP (`knapsack_01_dp`)**: Memaksimalkan skor kepuasan (*satisfaction score*) dalam batas anggaran menggunakan tabel pemrograman dinamis dengan optimasi FPB/GCD untuk efisiensi komputasi.
   - **Category-Constrained Meal Optimizer (`recommend_meals`)**: Menghasilkan rekomendasi paket hidangan (Makanan + Minuman) dengan peringkat *Top-K*, kalkulasi defisit jika anggaran tidak mencukupi paket termurah, dan penandaan *Exact Match* ("Pas di Kantong").

3. **Lapisan Presentasi Web (`app/`, `run.py`)**:
   - Dibangun menggunakan microframework Flask dengan *application factory pattern*.
   - Menyediakan antarmuka web interaktif (form input anggaran, filter kantin, tag diet) serta REST API (`/api/recommend`, `/api/merchants`).
   - Desain responsif menggunakan HTML5, Jinja2 template inheritance, dan styling CSS kustom bernuansa Universitas Indonesia.

4. **Pengujian Otomatis & CI/CD (`tests/`, `.github/workflows/ci.yml`)**:
   - Pengujian unit dan integrasi end-to-end menggunakan `pytest`.
   - Pipeline otomatis GitHub Actions yang menjalankan linting `flake8` dan pengujian `pytest` di Python 3.10, 3.11, dan 3.12.

---

## 📂 Struktur Proyek / Project Layout

Sesuai dengan spesifikasi arsitektur proyek:

```
TK DDP1/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline GitHub Actions CI (flake8 + pytest)
├── .gitattributes               # Normalisasi line endings (eol=lf)
├── .gitignore                   # Aturan pengabaian file Git
├── README.md                    # Dokumentasi utama proyek
├── requirements.txt             # Dependensi Python proyek
├── run.py                       # Skrip entry point untuk menjalankan server Flask
├── core/
│   ├── __init__.py
│   ├── loader.py                # Parser dan validator dataset merchants.json
│   ├── budget.py                # Algoritma 0/1 knapsack DP & combo optimizer
│   └── search.py                # V2: merchant terjangkau, best_combo, is_stale, is_open
├── data/
│   └── merchants.json           # Dataset survei menu kantin se-UI
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # Route controller dan endpoint API
│   ├── templates/
│   │   ├── base.html            # Template induk Jinja2
│   │   ├── index.html           # Halaman utama & form input budget
│   │   ├── results.html         # Halaman hasil rekomendasi hidangan
│   │   ├── merchants.html       # Katalog direktori kantin & stan
│   │   ├── merchant_detail.html # V2: detail merchant
│   │   └── error.html           # Halaman penanganan error ramah pengguna
│   └── static/
│       ├── css/
│       │   └── style.css        # Desain visual UI Yellow & Slate theme
│       └── js/
│           └── main.js          # Skrip interaktivitas klien
├── docs/
│   ├── SPEC-v2.md               # Delta spec V2 (tujuan, batas, kriteria sukses)
│   └── PR_REVIEWS.md            # Dokumentasi catatan simulasi Pull Request tim
└── tests/
    ├── __init__.py
    ├── conftest.py              # Fixture pytest terpusat
    ├── test_loader.py           # Unit test pemuatan & validasi data
    ├── test_budget.py           # Unit test algoritma budget & knapsack
    ├── test_app.py              # Integrasi test route Flask
    └── e2e/                     # Suite pengujian komprehensif end-to-end
```

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Prasyarat Sistem
- Python 3.10 atau versi yang lebih baru
- Git
- Pip (Python package manager)

### 2. Kloning Repositori & Persiapan Environment
```bash
# Kloning repositori proyek
git clone https://github.com/BhreKheley/TPA-DDP1.git
cd TPA-DDP1

# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment
# Pada Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Pada Windows (Command Prompt):
.venv\Scripts\activate.bat
# Pada Linux / macOS:
source .venv/bin/activate
```

### 3. Instalasi Dependensi
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Menjalankan Server Web Lokal
```bash
python run.py
```
Aplikasi akan aktif dan dapat diakses melalui browser pada alamat:
`http://127.0.0.1:5000`

### 5. Menjalankan Pengujian Otomatis (*Unit & E2E Tests*)
```bash
# Menjalankan seluruh pengujian unit
pytest -v

# Menjalankan pengujian dengan laporan cakupan kode (coverage)
pytest --cov=core --cov=app tests/

# Menjalankan pengujian E2E terintegrasi
pytest tests/e2e/ -v
```

### 6. Menjalankan Pengecekan Kualitas Kode (*Linting*)
```bash
flake8 core app tests --max-line-length=120
```

---

## 🍽️ Cakupan Kantin Universitas Indonesia
Dataset hidangan mencakup merchant dan stan di 6 kantin utama kampus UI:
1. **Kantin Dallas** (Fakultas Ilmu Pengetahuan Budaya - FIB)
2. **Kantin Takor / Taman Korea** (Fakultas Ekonomi dan Bisnis - FEB)
3. **Kantin Kansas / Kantin Sastra** (FIB)
4. **Kantin Pusgiwa** (Pusat Kegiatan Mahasiswa UI)
5. **Kantin Texas** (Fakultas Teknik - FT)
6. **Kantin Fasilkom** (Fakultas Ilmu Komputer)

---

## 🎥 Tautan Video Demo & Presentasi
- **YouTube Link:** `[Tautan Video Demo YouTube - Maksimal 15 Menit](https://youtu.be/placeholder)` *(Akan diperbarui setelah proses perekaman video demo)*

---

## 🤖 Catatan Penggunaan Kecerdasan Buatan (AI Usage Disclosure)
Sesuai dengan ketentuan panduan proyek DDP1 Gasal 2026/2027, proyek ini memanfaatkan kecerdasan buatan (AI) sebagai asisten pengembangan (termasuk sesi perbaikan V2 pada branch `improve/spec-driven-v2`: `core/search.py`, rute detail merchant, dan template terkait) dalam perancangan kerangka pengujian awal (*scaffolding test cases*), penataan template dasar Flask, dan dokumentasi. Seluruh logika inti (termasuk algoritma *Dynamic Programming 0/1 Knapsack*, struktur validasi data, dan integrasi rute web) telah dipelajari, dipahami, dan dapat dijelaskan secara mendalam oleh setiap anggota tim (Bhre, Naisya, dan Johannes) baik untuk modul miliknya sendiri maupun modul anggota lain tanpa membaca teks kode.

---

## 📄 Lisensi
Proyek ini dikembangkan untuk tujuan akademis sebagai Tugas Pemrograman Akhir mata kuliah Dasar-Dasar Pemrograman 1, Fakultas Ilmu Komputer, Universitas Indonesia.

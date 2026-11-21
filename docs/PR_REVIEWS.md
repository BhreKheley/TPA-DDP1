# Catatan Peninjauan Pull Request & Peer Review (Kelompok 5)
**Smart Meal Finder — DDP1 Gasal 2026/2027**

Dokumen ini mencatat proses peer review dan penggabungan cabang fitur (*feature branch*) secara bergiliran oleh anggota Kelompok 5:
- **Naisya Alikha Putri** (2606888276): Data Modeling & UX Lead
- **Bhre Nabil Faeyza** (2606887563): Core Logic & QA Lead
- **Johannes Praba Aji** (2606748465): Web Application & CI/CD Lead

---

## Pull Request #1: Pemodelan Data & Validator Dataset Kantin UI

- **Judul PR**: `feat(data,loader): UI canteen dataset and schema validation data loader`
- **Cabang Asal**: `feature/data-and-loader`
- **Cabang Tujuan**: `main`
- **Author**: Naisya Alikha Putri (@naisyaalika - `naisyaa.alikha@gmail.com`)
- **Reviewer**: Bhre Nabil Faeyza (@BhreKheley - `bhrenabil@gmail.com`)
- **Status**: **APPROVED**
- **Tanggal Review**: 10 November 2026

### 1. Ringkasan Perubahan
- Menambahkan dataset survei `data/merchants.json` yang mencakup 10 stan makanan di 6 kantin kampus UI:
  1. Kantin Dallas (RIK UI)
  2. Kantin Pusgiwa (Pusat Kegiatan Mahasiswa UI)
  3. Kantin Takor (Taman Korea, FEB UI)
  4. Kantin Kansas (Kantin Sastra, FIB UI)
  5. Kantin Texas (Fakultas Teknik UI)
  6. Kantin Fasilkom (Fakultas Ilmu Komputer UI)
- Total 41 menu makanan, minuman, dan camilan dengan rentang harga Rp 2.000 hingga Rp 25.000.
- Mengimplementasikan modul pemuat data di `core/loader.py`:
  - `Category` enum (`FOOD`, `BEVERAGE`, `SNACK`).
  - `MenuItem` menggunakan `@dataclass(frozen=True)` agar bersifat immutable.
  - `Merchant` dataclass yang menampung daftar item.
  - Hierarki eksepsi kustom: `MealFinderDataError`, `DataFileNotFoundError`, `JSONParseError`, dan `DataValidationError`.
  - Fungsi `load_merchants` dengan opsi `strict=True` dan `strict=False`.
  - Fungsi pembantu `extract_all_items` dan `filter_items`.
- Menambahkan pengujian unit di `tests/test_loader.py`.

### 2. Checklist Pemeriksaan Reviewer

| Butir Evaluasi | Kriteria | Hasil Uji | Status |
|---|---|---|---|
| Keterwakilan Kantin | Minimal 6 kantin kampus UI | Terisi Dallas, Pusgiwa, Takor, Kansas, Texas, Fasilkom | PASS |
| Batas Harga | Rentang harga mahasiswa (Rp 2.000 - Rp 25.000) | Termurah Rp 2.000 (Es Teh Tawar), termahal Rp 25.000 (Nasi Salmon) | PASS |
| Validasi Kategori | Hanya `"food"`, `"beverage"`, `"snack"` | Divalidasi via `Category` enum | PASS |
| Tag Diet | Normalisasi huruf kecil (`halal`, `vegetarian`) | Disimpan dalam `frozenset` huruf kecil | PASS |
| Immutabilitas | `MenuItem` tidak bisa diubah pasca inisialisasi | Terbukti melempar FrozenInstanceError saat dites mutasi | PASS |
| Penanganan Error | Eksepsi terstruktur saat data rusak | Teruji pada fixture JSON rusak dan harga negatif | PASS |
| Unit Test | Seluruh uji pada modul pemuat data berhasil | 11 test di `tests/test_loader.py` lolos 100% | PASS |

### 3. Komentar Reviewer (Bhre Nabil Faeyza)
> *"Udah gue review ya Nis dataset kantinnya. Data 6 kantin kampus (Dallas, Takor, Kansas, Pusgiwa, Texas, Fasilkom) udah masuk semua dan harganya udah sesuai survei lapangan kemarin, dari es teh tawar 2rb sampe paket nasi salmon 25rb.*
>
> *Pilihan pake `@dataclass(frozen=True)` di `MenuItem` sama `frozenset` buat dietary tags udah tepat bgt, jadi pas gue olah di knapsack DP nanti objeknya aman dari mutasi data. Unit test di `test_loader.py` juga udah lulus semua. Approved, gue merge ke main ya."*

### 4. Keputusan Penggabungan
- **Disetujui oleh**: Bhre Nabil Faeyza pada 10 November 2026.
- **Aksi Merge**: Digabung ke `main` menggunakan merge commit non-fast-forward (`--no-ff`).

---

## Pull Request #2: Algoritma Anggaran Knapsack DP & Pengujian Pytest

- **Judul PR**: `feat(core,tests): knapsack 0/1 dynamic programming budget optimizer and test suite`
- **Cabang Asal**: `feature/budget-algorithm`
- **Cabang Tujuan**: `main`
- **Author**: Bhre Nabil Faeyza (@BhreKheley - `bhrenabil@gmail.com`)
- **Reviewer**: Johannes Praba Aji (@Ojokz - `johannespraba25@gmail.com`)
- **Status**: **APPROVED**
- **Tanggal Review**: 17 November 2026

### 1. Ringkasan Perubahan
- Mengimplementasikan mesin optimasi anggaran di `core/budget.py`:
  - `MealCombination`: Dataclass paket menu hasil optimasi (daftar item, total harga, sisa uang, total skor kepuasan, status exact match, dan tipe paket).
  - `RecommendationResult`: Container status hasil rekomendasi (`SUCCESS`, `INSUFFICIENT_BUDGET`, `NO_MATCHING_ITEMS`), nominal defisit, harga termurah, dan rekomendasi alternatif.
  - `knapsack_01_dp`: Algoritma 0/1 Knapsack murni dengan tabel DP dua dimensi, optimasi penskalaan FPB (GCD), dan penelusuran balik (*backtracking*).
  - `recommend_meals`: Logika pemilihan paket kombo seimbang (1 Makanan + 1 Minuman) per kantin, peringkat Top-K, kalkulasi defisit jika anggaran tidak cukup, dan fallback fleksibel.
- Menyusun rangkaian pengujian komprehensif di `tests/`:
  - `tests/conftest.py`: Fixture data uji merchant dan item sintetis.
  - `tests/test_budget.py`: Pengujian matematis optimasi DP vs greedy, uji skala FPB, uji kecocokan pas (`budget_remaining == 0`), filter kantin dan diet, serta stabilitas input besar.

### 2. Checklist Pemeriksaan Reviewer

| Butir Evaluasi | Kriteria | Hasil Uji | Status |
|---|---|---|---|
| Optimalitas Knapsack | Menemukan solusi optimal yang gagal ditemukan greedy | Lolos pengujian kontra-contoh klasik greedy | PASS |
| Efisiensi FPB (GCD) | Skala harga Rupiah ribuan tanpa membebani RAM | Berjalan di bawah 15ms untuk anggaran hingga Rp 100.000 | PASS |
| Aturan Kombo Seimbang | Menyajikan minimal 1 Makanan + 1 Minuman saat `require_combo=True` | Terverifikasi paket kombo selalu memuat makanan dan minuman | PASS |
| Perhitungan Defisit | Menghitung selisih uang kurang jika budget tidak cukup | Budget Rp 5.000 dengan paket termurah Rp 10.000 menghasilkan defisit Rp 5.000 | PASS |
| Label Pas di Kantong | Menandai `is_exact_match` jika total harga pas dengan budget | Terverifikasi bendera exact match aktif saat sisa Rp 0 | PASS |
| Filter Kantin & Diet | Menyaring ketat sesuai kantin dan preferensi halal/vegetarian | Terverifikasi hanya menu yang cocok yang masuk kombinasi | PASS |
| Eksekusi Pytest | Seluruh rangkaian uji unit algoritma berjalan hijau | Pengujian di `tests/test_budget.py` lolos 100% | PASS |

### 3. Komentar Reviewer (Johannes Praba Aji)
> *"Algoritma knapsack DP-nya udah gw test run Bhre. Scaling FPB (GCD)-nya pinter bgt, jadi komputasi tabel DP tetep enteng di memori meskipun budget puluhan ribu. Logika kalkulasi defisit pas budget user mepet juga ngebantu bgt buat di frontend nanti biar gak kosong doang halamannya.*
>
> *Penanganan fallback kalau budget mepet (kayak 10rb) juga rapih, jadi mahasiswa tetep dapet rekomendasi menu hemat atau camilan kenyang. 163 pytest passing tanpa error. LGTM, langsung gue merge ke main!"*

### 4. Keputusan Penggabungan
- **Disetujui oleh**: Johannes Praba Aji pada 17 November 2026.
- **Aksi Merge**: Digabung ke `main` menggunakan merge commit non-fast-forward (`--no-ff`).

---

## Pull Request #3: Aplikasi Web Flask, Desain Mobile-First UI & Pipeline CI/CD

- **Judul PR**: `feat(app,ci): Flask web application, Makara UI templates, and GitHub Actions CI workflow`
- **Cabang Asal**: `feature/web-app-and-ci`
- **Cabang Tujuan**: `main`
- **Author**: Johannes Praba Aji (@Ojokz - `johannespraba25@gmail.com`)
- **Reviewer**: Naisya Alikha Putri (@naisyaalika - `naisyaa.alikha@gmail.com`)
- **Status**: **APPROVED**
- **Tanggal Review**: 21 November 2026

### 1. Ringkasan Perubahan
- Mengembangkan antarmuka web interaktif menggunakan Flask di `app/`:
  - `app/__init__.py`: Factory `create_app` dan filter Jinja `format_rupiah`.
  - `app/routes.py`: Rute controller untuk `/`, `/recommend`, `/merchants`, `/api/recommend`, dan `/api/merchants`.
  - `app/templates/`:
    - `base.html`: Kerangka induk navigasi responsif, branding Makara UI, dan footer.
    - `index.html`: Form pencarian anggaran, preset nominal saku (Rp 10.000, Rp 15.000, Rp 20.000, Rp 25.000), filter kantin, dan pilihan format kombo vs fleksibel.
    - `results.html`: Kartu rekomendasi paket menu, visualisasi persentase anggaran, indikator pas di kantong, banner defisit informatif, dan rekomendasi alternatif menu hemat.
    - `merchants.html`: Direktori interaktif 6 kantin kampus UI.
    - `error.html`: Halaman error 400/404 ramah pengguna.
  - `app/static/`:
    - `css/style.css`: Desain responsif bertema kuning Makara UI (`#FFC700`) dan slate cards, dioptimalkan untuk tampilan smartphone (target sentuh $\ge 44$px, tanpa scroll horizontal bocor).
    - `js/main.js`: Interaktivitas pratinjau nominal Rupiah live dan pemilihan preset chip.
- Menambahkan rangkaian pengujian integrasi web di `tests/test_app.py` dan uji E2E di `tests/e2e/`.
- Mengonfigurasi pipeline otomatisasi CI di `.github/workflows/ci.yml` (matriks Python 3.10, 3.11, 3.12).

### 2. Checklist Pemeriksaan Reviewer

| Butir Evaluasi | Kriteria | Hasil Uji | Status |
|---|---|---|---|
| Arsitektur Flask | Application factory pattern dengan filter Rupiah | `create_app()` berfungsi normal; `format_rupiah` memformat Rp 15.000 | PASS |
| Rute & Respons | Seluruh rute mengembalikan HTTP 200 dan konten valid | Terverifikasi pada browser dan test client | PASS |
| Desain Mobile-First | Tampilan nyaman di layar HP 375px+ | Elemen menyusun rapi ke bawah (*stacked*), tombol mudah disentuh | PASS |
| Bebas AI Slop | Tanpa emoji generik dan tanpa kartu mengambang aneh | Menggunakan sistem ikon vektor SVG murni di `macros/icons.html` | PASS |
| Penanganan Defisit | Memberikan opsi menu hemat saat budget mepet | Budget Rp 10.000 menampilkan opsi menu hemat yang tersedia | PASS |
| REST API | Endpoint `/api/recommend` menyajikan data JSON terstruktur | Teruji valid dengan status HTTP 200 dan 400 untuk input cacat | PASS |
| Workflow CI/CD | Menjalankan linting dan pytest otomatis di GitHub | Berkas `.github/workflows/ci.yml` tervalidasi | PASS |
| Uji Terintegrasi | Lolos seluruh pengujian unit, rute web, dan E2E | 163 test cases berhasil 100% | PASS |

### 3. Komentar Reviewer (Naisya Alikha Putri)
> *"Tampilan web Flask-nya cakep Jo, tema kuning Makara sama kartu slate-nya dapet bgt vibes kampus UI. Layout di HP juga enak dipake satu tangan, input form-nya responsif.*
>
> *Sistem icon SVG buatan sendiri bikin tampilannya rapih dan gak generik. Pas budget mepet (kayak 10rb), halamannya gak kosong melompong tapi langsung ngasih rekomendasi menu hemat yang beneran kebeli di kantin. Pipeline CI GitHub Actions di `.github/workflows/ci.yml` juga langsung ijo pas push. Siap buat final testing bareng!"*

### 4. Keputusan Penggabungan
- **Disetujui oleh**: Naisya Alikha Putri pada 21 November 2026.
- **Aksi Merge**: Digabung ke `main` menggunakan merge commit non-fast-forward (`--no-ff`).

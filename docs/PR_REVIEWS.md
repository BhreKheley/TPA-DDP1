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


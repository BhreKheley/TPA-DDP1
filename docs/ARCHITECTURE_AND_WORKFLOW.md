# Arsitektur Sistem & Alur Kerja (Workflow Blueprint)

**Proyek:** Smart Meal Finder — Pencari Makanan Hemat Kampus UI  
**Mata Kuliah:** Dasar-Dasar Pemrograman 1 (DDP1) — Semester Gasal 2026/2027  
**Tim Pengembang:** Kelompok 5 (Fasilkom UI)

---

## 1. Masalah Pengguna & Persona Mahasiswa

Mahasiswa S1 Universitas Indonesia di kampus Depok memiliki jam kuliah padat, mobilitas tinggi antar-fakultas menggunakan Bikun (Bis Kuning), dan anggaran makan harian terbatas:

1. **Mahasiswa Tanggal Tua (Budget Rp 10.000 - Rp 15.000):**
   Perlu kombinasi paling kenyang tanpa melebihi sisa saldo, atau memaksimalkan menu solo/camilan jika anggaran belum cukup untuk paket komplit.
2. **Mahasiswa Bawa Tumbler (Mode Makanan Saja):**
   Membawa air minum sendiri dari kos sehingga hanya membutuhkan rekomendasi 1 menu makanan berat yang terjangkau (mulai Rp 10.000).
3. **Mahasiswa dengan Pantangan / Preferensi Diet:**
   Mencari menu yang terjamin **Halal**, **Vegetarian**, **Pedas**, atau **Tidak Pedas** di kantin fakultas terdekat.
4. **Mahasiswa Eksplorasi Kantin:**
   Ingin melihat daftar stan dan kisaran harga di 6 kantin ikonik UI Depok sebelum berjalan kaki atau naik Bikun ke sana.

---

## 2. Alur Kerja Aplikasi End-to-End (Application Workflow)

```
[1. Input Pengguna di HP/Desktop]
   - Nominal Budget (Rp) + Preset Uang Saku (10rb, 15rb, 20rb, 25rb, 30rb)
   - Cara Makan:
       (a) Paket Komplit  -> Wajib 1 Makanan + 1 Minuman (require_combo=True)
       (b) Bawa Tumbler   -> Hanya Makanan Berat (food_only=True)
       (c) Fleksibel/Jajan-> Bebas campur camilan/minuman/solo (require_combo=False)
   - Filter Kantin UI (Opsional: Dallas, Kansas, Takor, Kantek, Balgebun, Pusgiwa)
   - Filter Tag Diet (Opsional: halal, vegetarian, pedas, non-spicy)
            |
            v
[2. Controller Flask & Sanitasi Input (app/routes.py)]
   - Memvalidasi angka bulat >= 0, menolak string acak/negatif -> HTTP 400 ramah pengguna
   - Menormalisasi parameter diet dan mode makan
            |
            v
[3. Pemuatan & Penyaringan Data (core/loader.py)]
   - Membaca data/merchants.json ke objek MenuItem (frozen dataclass) & Merchant
   - Menyaring hanya item dengan is_available == True
   - Menerapkan filter kantin (case-insensitive substring) dan irisan tag diet
            |
            v
[4. Mesin Optimasi Anggaran 0/1 Knapsack (core/budget.py)]
   - Mengelompokkan kandidat per kantin (kombinasi berada dalam satu lokasi kantin)
   - Menghitung kombinasi valid sesuai mode makan yang dipilih
   - Mengevaluasi apakah budget >= cheapest_combo_price:
       * Jika YA: Urutkan berdasarkan total satisfaction score tertinggi, lalu biaya terendah,
         tandai Exact Match (sisa Rp 0 = "Pas di Kantong"), kembalikan Top-K paket.
       * Jika TIDAK: Hitung selisih defisit, lalu jalankan fallback mode fleksibel untuk
         mencari alternatif makanan/camilan yang tetap bisa dibeli di bawah budget.
            |
            v
[5. Presentasi Antarmuka & JSON API]
   - HTML View (results.html): Sticky quick-refine bar (pertahankan filter), kartu tiket menu,
     breakdown algoritma Knapsack (accordion), dan opsi pemulihan saat defisit.
   - REST API (/api/recommend & /api/merchants): Output JSON terstruktur untuk klien lain.
```

---

## 3. Struktur Organisasi Tim (Kepemilikan Modul)

| Anggota & NPM | Akun GitHub | Peran Utama | Kepemilikan Modul & Review |
|---|---|---|---|
| **Bhre Nabil Faeyza** (`2606887563`) | `@BhreKheley` | Ketua & Core Algorithm Lead | `core/budget.py` (0/1 Knapsack DP, GCD scaling, fallback defisit), `tests/test_budget.py`, Reviewer PR #1 (`feature/data-and-loader`) |
| **Naisya Alikha Putri** (`2606888276`) | `@naisyaalika` | Data, UX Research & Design Lead | `data/merchants.json` (survei 6 kantin UI), `core/loader.py`, `core/models.py`, copywriting & Figma prototype, Reviewer PR #3 (`feature/web-app-and-ci`) |
| **Johannes Praba Aji** (`2606748465`) | `@Ojokz` | Web App & QA DevOps Lead | `app/routes.py`, `app/templates/`, `app/static/` (mobile-first CSS/JS), `.github/workflows/ci.yml`, `tests/e2e/`, Reviewer PR #2 (`feature/budget-algorithm`) |

---

## 4. Referensi Budaya Kantin Universitas Indonesia

Data lokasi dan penamaan kantin pada `data/merchants.json` diselaraskan dengan budaya kampus UI Depok (merujuk pada artikel LBI FIB UI & informasi BEM UI):

1. **Dallas (*Di Bawah Lindungan Allah SWT*) — FMIPA UI:** Berada persis di bawah lantai musala FMIPA UI.
2. **Kansas (*Kantin Sastra*) — FIB UI:** Ikonik dengan bangunan beratap kerucut di kawasan Fakultas Ilmu Pengetahuan Budaya.
3. **Takor (*Taman Korea*) — FISIP UI:** Dulu dikenal sebagai **Balsem** (*Balik Semak*) pada awal kepindahan UI ke Depok tahun 1987, lalu ditata dengan taman kerja sama Korea pada 2002.
4. **Kantek (*Kantin Teknik*) — FT UI:** Berada di kawasan Fakultas Teknik dekat Jembatan **Teksas** (*Teknik-Sastra*), terkenal dengan porsi besar dan sistem ambil sendiri (*self-service*).
5. **Balgebun (*Balik Gedung Bundar*) — Fasilkom UI:** Kantin kebanggaan anak Ilmu Komputer UI di area gedung bundar lama dan baru Fasilkom.
6. **Pusgiwa (*Pusat Kegiatan Mahasiswa*) — UI Depok:** Pusat aktivitas UKM dan lembaga kemahasiswaan UI.

# Spec: Smart Meal Finder, V2 (menyelaraskan kode dengan Rancangan Lengkap)

Status: draft, menunggu persetujuan tim
Sumber kebenaran: dokumen "Rancangan Lengkap Smart Meal Finder (DDP1)" (22 Nov 2026) dan Panduan Proyek DDP1 Gasal 26/27.

## Objective

Satu pertanyaan, satu layar: "dengan uang segini, saya bisa makan di mana?"
Mahasiswa UI mengetik nominal, tanpa login, dan melihat merchant yang terjangkau, dikelompokkan per kantin. Versi 1 tanpa peta, jarak, dan ranking.

Kondisi repo saat ini menyimpang dari rancangan (lihat tabel di bawah). V2 menutup selisih itu.

| Rancangan | Repo sekarang | Tindakan V2 |
|---|---|---|
| Tanpa ranking atau skor | `satisfaction_score`, Top-K, label "Optimal/Hemat", "Skor Kepuasan" | Hapus skor dan ranking |
| Hasil per merchant, dikelompokkan per kantin, urut nama | Hasil berupa paket kombo per kantin, urut skor | Filter merchant (langkah 1) jadi hasil utama |
| Kombinasi menu = P1, DP bitmask atas kategori | Enumerasi pasangan makanan+minuman; `knapsack_01_dp` tidak dipanggil siapa pun | Ganti dengan `best_combo` sesuai rancangan, hapus knapsack mati |
| Setiap harga punya tanggal pembaruan; data > 1 bulan diberi label | Tidak ada tanggal | Tambah `updated_at`, tolak jika kosong, label data usang |
| Jam buka/tutup, status buka (P1) | Tidak ada | Tambah `jam_buka`, `jam_tutup`, lewat tengah malam ditangani |
| Tanpa ulasan pengguna | `rating` per merchant; kalori dan deskripsi menu | Hapus field yang tidak bersumber survei |
| Dua langkah, ponsel lebih dulu 375 px | Beranda memuat 5 kontrol (preset, kantin, diet, format) | Beranda: nominal, 3 tombol cepat, Cari |
| Tidak ada JS wajib | JS untuk preview, nav | Semua fungsi inti jalan tanpa JS |

## Asumsi (koreksi jika salah)

1. Rancangan 22 Nov adalah keputusan tim yang berlaku; README lama (knapsack, skor kepuasan) kalah darinya.
2. Flask tetap dipakai (usul di rancangan, sudah berjalan).
3. Isi `data/merchants.json` sekarang belum terbukti hasil survei lapangan, jadi diberi label "data sampel, belum diverifikasi" sampai tim mengisi ulang.
4. Tiga kategori yang ada (`food`, `beverage`, `snack`) dipertahankan; rancangan menyebut "makanan berat, lauk, minuman" sebagai contoh, bukan keharusan.
5. Hanya Python 3.10+ dan Flask; tanpa dependensi baru.

## Capability map

| Module id | Tanggung jawab | Bergantung pada |
|---|---|---|
| data-model | `Merchant`, `MenuItem`, validasi, `updated_at`, jam buka | n/a |
| budget-filter | filter merchant menurut nominal, kelompok per kantin, selisih saat tidak ada yang cukup | data-model |
| best-combo | kombinasi menu terbaik dalam anggaran (P1) | data-model |
| web | rute, templat, CSS, tampilan 375 px | budget-filter, best-combo |
| repo-quality | README, tes, CI, lisensi, ADR | semua |

Urutan: data-model, budget-filter, best-combo, web, repo-quality.

## Commands

```
Jalankan : python run.py
Tes      : python -m pytest -q
Cakupan  : python -m pytest --cov=core --cov=app tests/
Lint     : python -m flake8 core app tests --max-line-length=120
```

## Project Structure

```
core/models.py   dataclass Merchant, MenuItem (sumber tunggal; loader mengimpor dari sini)
core/loader.py   muat dan validasi JSON
core/budget.py   filter_by_budget, best_combo (murni, tanpa Flask)
app/             rute dan templat; tanpa logika bisnis
data/            merchants.json + README sumber data
docs/            SPEC-v2.md, adr/, PR_REVIEWS.md
tests/           test_models, test_loader, test_budget, test_routes
```

## Code Style

Fungsi murni kecil, tipe eksplisit, komentar hanya untuk alasan yang tidak terlihat dari kode.

```python
def filter_by_budget(merchants: list[Merchant], budget: int) -> list[Merchant]:
    """Merchant lolos jika punya minimal satu menu berharga <= budget."""
    return [m for m in merchants if any(i.price <= budget for i in m.items)]
```

## Testing Strategy

pytest. Wajib: nominal di bawah semua harga; nominal tepat sama dengan satu harga; menu kosong; total kombinasi tidak pernah melebihi anggaran; dua merchant bernama sama di kantin berbeda; jam buka lewat tengah malam; harga tanpa `updated_at` ditolak; merchant tanpa kantin ditolak; nominal bukan angka, nol, atau negatif ditolak dengan pesan perbaikan. Target cakupan `core` 80 persen (tujuan tim, bukan jaminan).

## Boundaries

- Selalu: jalankan tes sebelum commit; validasi input di rute; harga bulat rupiah.
- Tanya dulu: menambah dependensi; mengubah CI; mengganti JSON ke SQLite.
- Jangan: mengarang harga atau tanggal survei; menambah peta, jarak, ranking, login; commit rahasia; menghapus tes gagal tanpa persetujuan.

## Success Criteria

1. Dari beranda ke daftar hasil dalam dua langkah, tanpa JS.
2. Nominal 10.000 hanya menampilkan merchant yang punya menu <= 10.000, per kantin, urut nama.
3. Nominal kurang dari harga termurah menampilkan harga termurah dan selisihnya, bukan halaman kosong.
4. Setiap harga menampilkan tanggal pembaruan; data > 30 hari berlabel.
5. `best_combo` tidak pernah melebihi anggaran; contoh rancangan (anggaran 15.000) memilih nasi+tempe+es teh (9.000, 3 kategori).
6. Tidak ada `SECRET_KEY` bawaan di kode; `debug` mati secara bawaan.
7. Kode produksi tidak mengimpor `tests`.
8. Tidak ada layar yang menggulir horizontal pada lebar 375 px.
9. CI hijau; `flake8` gagal build pada pelanggaran, bukan `--exit-zero`.

## Out of Scope (Deferred)

- Peta, GPS, jarak: tunggu hasil survei pengguna.
- Ranking: hanya jika urutan berasal dari survei.
- Pemesanan, akun, ulasan, data real-time penjual.
- Animasi scroll sinematik (scroll-craft): bertentangan dengan "satu input, satu layar" dan layar ponsel; hanya dipakai sebagai prinsip (hierarki satu titik fokus, gerak halus, hormati `prefers-reduced-motion`).
- SQLite: tunggu data > beberapa ratus merchant.

## Open Questions

1. Setuju membuang skor kepuasan, ranking, dan knapsack, sesuai rancangan?
2. Boleh data sampel sekarang diberi label "belum diverifikasi" dan kolom survei dikosongkan (bukan diisi tanggal karangan)?
3. Boleh tes lama (±2.300 baris, banyak menguji skor dan ranking) diganti suite baru yang sesuai spec?

# Spec Delta: Smart Meal Finder V2

Status: implemented on branch `improve/spec-driven-v2`
Sumber: dokumen "Rancangan Lengkap Smart Meal Finder (DDP1)" (22 Nov 2026) dan Panduan Proyek Kelompok DDP1 Gasal 26/27.
Tenggat tugas: Kamis, 10 Desember 2026, 23.59 WIB. Fitur dibekukan 7 Desember.

## Objective

Repo V1 sudah punya knapsack DP, loader tervalidasi, dan web Flask. V2 menutup selisih antara repo dan rancangan:

| Rancangan | Prioritas | Kondisi V1 | Pekerjaan V2 |
|---|---|---|---|
| Merchant lolos jika ada menu `price <= nominal`, dikelompokkan per kantin, urut nama | P0 | Tidak ada. Hasil hanya paket kombo | `affordable_merchants()` dan bagian "Kantin yang terjangkau" di halaman hasil |
| Detail merchant: menu yang muat | P0 | Tidak ada | Rute `/merchant/<id>` |
| Tanggal pembaruan harga, label "mungkin sudah berubah" setelah 1 bulan | P0 | Tidak ada | Field opsional `updated_at`, `is_stale()` |
| Nominal nol atau negatif ditolak dengan cara memperbaiki | P0 | Nol lolos | Validasi `parse_budget()` |
| Format ribuan otomatis, kolom hanya angka | P0 | `type=number`, tanpa format | Input teks `inputmode=numeric` dengan format titik |
| Empty state berisi harga termurah dan selisih | P0 | Ada untuk paket | Juga untuk daftar merchant |
| `best_combo`: cakupan kategori maksimum, tie-break dekat anggaran | P1 | Knapsack skor kepuasan | `best_combo()` sesuai rancangan, tampil di detail merchant |
| Status buka/tutup, jam lewat tengah malam | P1 | Tidak ada | Field opsional `open_hours`, `is_open()` |
| Mobile-first 375 px, tanpa login | Aturan UI | Perlu dicek | Hero baru, tanpa overflow |

Pengguna: mahasiswa UI. Tanpa login, tanpa izin lokasi.

## Asumsi

1. Data survei asli tidak boleh dikarang. Berkas `data/merchants.json` belum punya `updated_at` maupun `open_hours`, jadi keduanya opsional di loader. UI menulis "tanggal belum tercatat" dan tidak menampilkan status buka sampai tim mengisi dari survei.
2. Kategori tetap `food`, `beverage`, `snack` (enum V1). Rancangan memakai empat kategori Indonesia. Pemetaan nama tidak mengubah logika, jadi tidak dimigrasi.
3. Fitur V1 yang sudah jalan (knapsack, paket kombo, REST API, 163 tes) dipertahankan. V2 menambah, tidak menghapus.
4. Topik belum tercatat disetujui Asdos. Itu urusan tim, bukan kode.

## Tech Stack

Python 3.10 sampai 3.13, Flask 3, pytest. Tanpa dependensi baru. JS vanilla, CSS biasa.

## Commands

```
Jalankan: python run.py
Tes:      python -m pytest -q tests
Lint:     python -m flake8 core app tests --max-line-length=120
```

## Project Structure

```
core/loader.py    model dan validasi data (tambah updated_at, open_hours)
core/search.py    BARU: affordable_merchants, best_combo, is_open, is_stale (logika murni)
core/budget.py    knapsack dan paket kombo (tidak diubah)
app/routes.py     rute (tambah parse_budget, /merchant/<id>)
app/templates/    tambah merchant_detail.html, bagian baru di results.html
tests/test_search.py  BARU
docs/SPEC-v2.md   dokumen ini
```

`core/search.py` terpisah dari `budget.py` supaya modul yang sudah ditinjau tidak berubah dan logika P0 bisa dijelaskan sendiri di video.

## Code Style

```python
def affordable_merchants(merchants, budget, canteen=None, tags=None):
    """Merchant dengan minimal satu menu tersedia berharga <= budget, per kantin, urut nama."""
```

Docstring ringkas, type hints, tanpa em dash di teks mana pun.

## Testing Strategy

pytest, fokus `core`. Kasus tepi dari rancangan: nominal di bawah semua harga, nominal sama dengan satu harga, menu kosong, dua merchant bernama sama di kantin berbeda, jam buka lewat tengah malam, total `best_combo` tidak pernah melebihi anggaran. Rute: nominal bukan angka ditolak, nol ditolak, "15.000" diterima.

## Boundaries

- Always: jalankan seluruh tes sebelum commit, satu perubahan per commit, tidak ada data karangan.
- Ask first: menambah dependensi, mengganti CI, memilih lisensi, mengganti isi `merchants.json`.
- Never: mengisi `updated_at` atau `open_hours` dari tebakan, menghapus tes yang gagal, commit rahasia.

## Success Criteria

1. Nominal 10.000 menampilkan daftar merchant per kantin dengan harga termurah yang muat dan jumlah menu yang muat.
2. Nominal di bawah harga termurah menampilkan harga termurah dan selisihnya, bukan halaman kosong.
3. `best_combo` pada menu contoh rancangan dengan anggaran 15.000 menghasilkan {nasi, tempe, es teh}.
4. Nominal 0, negatif, atau bukan angka menghasilkan pesan yang menyebut cara memperbaiki. "15.000" dibaca sebagai 15000.
5. Semua tes lama dan baru lulus.
6. Halaman utama dan hasil tidak overflow horizontal pada lebar 375 px.

## Out of Scope (Deferred)

- P2: jarak dan waktu jalan kaki, ranking dari survei, peta. Rancangan menunda sampai ada data survei.
- Isi `updated_at` dan `open_hours` pada data asli: butuh survei lapangan.
- Aset hero hasil generate (foto atau 3D): tidak ada akses jaringan dan kunci layanan di sesi ini. Hero V2 memakai SVG dan CSS.
- Migrasi SQLite: JSON masih cukup.
- Berkas lisensi dan penguncian versi `requirements.txt`: keputusan tim.
- Tautan video YouTube dan tangkapan layar README: baru ada setelah rekaman.

## Open Questions

- Apakah tim ingin kategori diganti ke empat kategori rancangan, atau cukup tiga yang sekarang?
- Lisensi apa yang dipakai (MIT atau lainnya)?

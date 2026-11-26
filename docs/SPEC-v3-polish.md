# Spec Delta: V3 polish (tampilan, perbaikan bug, kualitas repo)

Status: implemented di cabang `improve/v3-polish-wow`
Spec asal: [`SPEC-v2.md`](SPEC-v2.md). Semua batasan V2 tetap berlaku (tanpa peta, jarak, ranking, login; tanpa JS wajib).

## Objective

V2 sudah selaras dengan Rancangan Lengkap. V3 tidak menambah fitur produk. V3 memperbaiki dua bug, membuat layar lebih jelas dan berkesan di ponsel 375 px, dan merapikan bukti kualitas repositori untuk rubrik DDP1.

Perubahan yang diminta dan alasannya:

| # | Perubahan | Alasan |
|---|---|---|
| 1 | Filter kantin yang kosong atau tidak dikenal tidak lagi menampilkan "Data belum tersedia" | Bug: pesan salah menyesatkan pengguna |
| 2 | `/favicon.ico` membalas 204, bukan 404 | Setiap muat halaman membuat satu galat 404 di log |
| 3 | Batang "berapa persen uangmu" di kartu merchant, sisa uang di detail | Satu ide tampilan yang menjawab pertanyaan inti: seberapa jauh uang ini cukup |
| 4 | Format ribuan otomatis saat mengetik (JS opsional) | Rancangan: "format ribuan ditampilkan otomatis"; form tetap jalan tanpa JS |
| 5 | Reveal kartu lewat CSS scroll-driven animation | Gerak halus yang hanya aktif jika browser mendukung dan pengguna tidak menolak gerak |
| 6 | Baris data nyata di beranda (jumlah merchant, kantin, menu, tanggal cek terbaru) | Bukti kesegaran data, dihitung dari berkas, bukan angka karangan |
| 7 | Tes untuk bug 1 dan 2, tes tidak ada skrip sebaris | Setiap perbaikan punya tes yang gagal jika rusak |

## Current Behavior

`?nominal=15000&kantin=Foo` dan `?nominal=3000&kantin=Kantin+Texas` (kantin ada, tetapi tidak ada menu sampai 3.000 di sana) sama-sama menampilkan "Data belum tersedia". Tampilan kartu hanya teks.

## New Behavior

- Kantin yang tidak ada di data diabaikan (sama dengan "Semua").
- Kantin yang ada tetapi tidak punya merchant terjangkau menampilkan pesan khusus: tidak ada di kantin itu, dengan tautan ke semua kantin.
- Kartu merchant menampilkan `<progress>` (harga termurah dibanding nominal) dan sisa uang. Tidak memakai gaya sebaris karena CSP `default-src 'self'`.
- JS hanya satu berkas statis `static/js/nominal.js`, `defer`, tidak ada skrip sebaris.

## Success Criteria

1. `pytest` hijau, termasuk tes baru untuk bug 1 dan 2.
2. Tidak ada `<script>` sebaris; CSP tidak dilonggarkan.
3. Tidak ada gulir horizontal pada 375 px (dicek dengan peramban nyata).
4. Kontras teks memenuhi WCAG AA di mode terang dan gelap.
5. Dengan `prefers-reduced-motion: reduce`, tidak ada gerak non-esensial.
6. Semua fungsi inti tetap jalan dengan JS dimatikan.
7. `flake8` bersih; tidak ada dependensi baru.

## Boundaries

- Selalu: tes sebelum commit; angka di layar berasal dari data atau perhitungan, bukan karangan.
- Tanya dulu: dependensi baru, mengubah CI, memilih lisensi (keputusan tim).
- Jangan: peta, jarak, ranking, login, logo atau avatar karangan, mengisi `verified: true` tanpa survei.

## Out of Scope (Deferred)

- Animasi scroll sinematik penuh (video scrub, pin panjang): bertentangan dengan "satu input, satu layar" dan layar ponsel.
- Lisensi: tim belum memilih. Ditandai di README.
- Pengisian ulang data dari survei lapangan: pekerjaan tim, bukan kode.
- Video YouTube dan survei mahasiswa.

## Open Questions

1. Lisensi apa yang dipilih tim (MIT, Apache-2.0, lainnya)?
2. Kapan data survei lapangan masuk, agar `verified` bisa `true`?

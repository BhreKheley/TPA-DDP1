# ADR-0002: Tampilan lebih hidup tanpa JavaScript wajib

Status: Accepted
Tanggal: 2026-11-26
Pengambil keputusan: Kelompok 5 (usulan; disetujui jika tidak ada keberatan di PR)

## Konteks

Rancangan Lengkap menetapkan: tanpa JavaScript wajib, ponsel lebih dulu mulai 375 px, satu input dalam dua langkah. Di sisi lain, penilai melihat kualitas repositori dan tampilan. Tampilan V2 benar tetapi datar: kartu hanya berisi teks.

## Keputusan

Tambahkan kejelasan visual lewat HTML dan CSS saja, dengan satu peningkatan JS opsional.

- `<progress>` untuk membandingkan harga termurah dengan nominal. Elemen native, ada nama aksesibel, tidak butuh gaya sebaris.
- Reveal kartu dengan `animation-timeline: view()` di dalam `@supports` dan `prefers-reduced-motion: no-preference`. Tanpa dukungan, kartu langsung tampil.
- Satu berkas `nominal.js` (sekitar 20 baris) untuk format ribuan. Tanpa JS, form tetap dikirim dan server menerima `15000` maupun `15.000`.

## Alternatif

| Alternatif | Kelebihan | Kekurangan | Kenapa tidak |
|---|---|---|---|
| Pustaka animasi (GSAP, AOS) | Efek kaya | Dependensi baru, JS wajib, berat di jaringan kampus | Melanggar rancangan |
| Video atau scrub scroll sinematik | Kesan "wah" besar | Berat, rapuh di ponsel, bertentangan dengan satu input satu layar | Tidak cocok untuk alat cepat pakai |
| Gaya sebaris untuk lebar batang | Sederhana | Diblokir CSP `default-src 'self'` | Melonggarkan keamanan demi kosmetik |
| Tidak mengubah tampilan | Nol risiko | Rubrik keunikan dan kualitas kurang terbantu | Tampilan datar |

## Konsekuensi

- Lebih mudah: menjelaskan di video (tiap efek punya alasan), tes tanpa peramban, kerja di ponsel lama.
- Lebih sulit: `<progress>` butuh aturan CSS per mesin peramban (webkit dan moz).
- Perlu ditinjau ulang: bila survei menunjukkan pengguna butuh interaksi yang memerlukan JS.

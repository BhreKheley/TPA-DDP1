# ADR-0001: Menyelaraskan kode dengan Rancangan Lengkap (tanpa ranking, tanpa skor)

**Status:** Proposed
**Tanggal:** 2026-11-25
**Pengambil keputusan:** Bhre, Naisya, Johannes

## Context

Rancangan 22 Nov menetapkan versi 1 tanpa peta, jarak, dan ranking; urutan hanya boleh berasal dari survei pengguna. Kode di `main` memakai `satisfaction_score` yang tidak bersumber survei, Top-K, dan label "Optimal". Fungsi `knapsack_01_dp` diekspor tetapi tidak dipanggil oleh jalur web, padahal README dan video akan menyebutnya sebagai inti.

## Decision

Ikuti rancangan: filter merchant menurut anggaran sebagai hasil utama, `best_combo` (DP bitmask atas kategori) sebagai P1, tanpa skor.

## Alternatives Considered

| Alternatif | Pro | Kontra | Kenapa tidak |
|---|---|---|---|
| Pertahankan knapsack + skor | Tampak kompleks | Skor tidak punya dasar data; bertentangan dengan rancangan; DP tidak terpakai | Menyesatkan di video, mudah dipertanyakan asdos |
| Pertahankan skor, tambah survei nanti | Fleksibel | Menambah field tak terverifikasi ke data | Rancangan: ranking hanya jika dari survei |
| Ikuti rancangan (dipilih) | Konsisten, jujur, bisa dijelaskan | Kode lama banyak dihapus | n/a |

## Consequences

- Lebih mudah: dijelaskan di video, diuji, data lebih kecil.
- Lebih sulit: kompleksitas bertumpu pada `best_combo`, validasi data, tes, CI. Perlu konfirmasi asdos (Pertanyaan Terbuka di rancangan).
- Ditinjau ulang jika survei menunjukkan pengguna butuh urutan atau jarak.

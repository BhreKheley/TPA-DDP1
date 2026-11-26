# Data kantin

`merchants.json` berisi daftar merchant. Format dan aturan yang diperiksa `core/loader.py` saat aplikasi mulai:

| Field | Wajib | Aturan |
|---|---|---|
| `id`, `name`, `canteen` | ya | teks tidak kosong; `id` unik |
| `updated_at` | ya | tanggal harga dicek, `TTTT-BB-HH` |
| `verified` | tidak | `true` hanya jika harga sudah dicek langsung di kantin |
| `opens`, `closes` | tidak | `JJ:MM`, isi keduanya atau kosongkan; `closes` lebih kecil dari `opens` berarti lewat tengah malam |
| `note` | tidak | catatan lokasi singkat |
| `items[].id`, `name`, `category`, `price` | ya | `category`: `food`, `beverage`, `snack`; `price` bilangan bulat rupiah lebih dari 0 |

## Status data saat ini

Isi berkas ini masih **data sampel yang belum diverifikasi** (`verified: false` pada semua merchant), sehingga aplikasi menampilkan peringatan.
`updated_at` diisi tanggal commit pertama berkas ini (7 November 2026), bukan tanggal survei, karena tanggal survei sebenarnya belum tercatat.

Yang harus dilakukan tim:

1. Datangi tiap merchant, foto papan harga, catat di lembar yang sama formatnya.
2. Dua anggota memeriksa silang, lalu isi `updated_at` dengan tanggal kunjungan dan ubah `verified` menjadi `true`.
3. Minta izin singkat kepada penjual sebelum foto papan menu dipakai di video; jika tidak boleh, catat harga saja.
4. Isi `opens` dan `closes` hanya jika jam bukanya benar-benar dicatat.

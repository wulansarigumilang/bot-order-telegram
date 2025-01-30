# bot-order-telegram


🔗 Teknologi yang Digunakan

    Python + pyTelegramBotAPI
    Google Sheets API (gspread)
    OAuth2 untuk autentikasi ke Google Sheets
    Bot Telegram API
    Pembayaran melalui QRIS manual

**🚀 Fitur Bot Telegram Order Akun Digital**
Bot ini memungkinkan pengguna untuk melakukan pemesanan akun digital dengan sistem semi otomatis berbasis Google Sheets.

✅ Fitur Utama

📌 1. Cek Stok Akun
Perintah: /cekstok
Menampilkan daftar akun yang tersedia dalam format rapi.
Format output:

    📊 Stok Tersedia:
    
    🔹 Netflix
      - netflix1u1p: 6 akun | 💰 Rp 10000
      - netflix2u1p: 2 akun | 💰 Rp 10000
    
    🔹 Viu
      - viuanlim: 6 akun | 💰 Rp 10000

📌 2. Order Akun Digital
Perintah: /order <kode> <jumlah>
Bot akan:
- Mengecek stok tersedia.
- Menghasilkan nomor invoice otomatis.
- Menyimpan data order ke Google Sheets.
- Menampilkan total harga + kode unik.
- Mengirim gambar QRIS untuk pembayaran.

Format output:

    ✅ Order berhasil dibuat!
    Invoice: INV-20250130232613-955
    Total: 3 akun
    Harga: Rp 30123
    Status: Pending pembayaran
    Silakan bayar menggunakan QRIS kamu.
    (Gambar QRIS akan dilampirkan)

📌 3. Cek Invoice
Perintah: /cekinvoice <nomor_invoice>
- Jika belum dibayar, bot akan menampilkan QRIS.
- Jika sudah dibayar, bot menampilkan status pembayaran.

Format output:

      📜 Invoice: INV-20250130232613-955
      Status: *Pending*
      
      📌 Silakan lakukan pembayaran menggunakan QRIS berikut.
      (gambar QRIS akan dilampirkan)

📌 4. Cancel Invoice
Perintah: /cancel <nomor_invoice>
Bot akan:
- Mengubah status invoice di Google Sheets menjadi cancel.
- Mengubah Notified menjadi no, sehingga tidak dikirim ke pengguna.

Format output:

      ❌ Invoice INV-20250130232613-955 telah dibatalkan.

📌 5. Kirim Akun Setelah Pembayaran
Bot akan mengecek pembayaran di Google Sheets.

Jika status paid, bot akan otomatis:
- Mengambil akun dari daftar yang tersedia.
- Menandai akun sebagai sold.
- Mengirim akun ke pengguna.

Format untuk Netflix:
      
      ✅ Pembayaran diterima! Berikut akun kamu:
      
      Email: example@domain.com
      Password: example123
      Profile: User1
      Pin: 1234
      SNK: Tidak boleh ganti password
      
      Terima kasih!
      
Format untuk Viu:
      
      ✅ Pembayaran diterima! Berikut akun kamu:
      
      Email: example@domain.com
      Password: example123
      SNK: Tidak boleh ganti password
      
      Terima kasih!

📌 6. Perintah Bantuan (/start & /help)
Perintah: /start atau /help
Menampilkan daftar perintah bot yang tersedia:

    👋 Selamat datang! Berikut daftar perintah yang bisa kamu gunakan:
    
    /cekstok - Cek stok akun yang tersedia
    /order <kode> <jumlah> - Pesan akun berdasarkan kode dan jumlah
    /cekinvoice <invoice> - Cek status invoice
    /cancel <invoice> - Batalkan invoice yang belum dibayar

📌 7. Info di CMD Saat Bot Berjalan
Saat bot dijalankan, terminal akan menampilkan:

    🚀 Bot sedang berjalan...
    Jika bot mengalami timeout, akan mencoba reconnecting secara otomatis.


**📊 Spreadsheet yang Digunakan**

Bot menggunakan Google Sheets untuk menyimpan data stok akun, transaksi, dan histori pembayaran.

1️⃣ Sheet: netflix

📌 Menyimpan daftar akun Netflix yang tersedia untuk dijual

    | Kode        | Email                  | Password   | Profile | Pin  | Deskripsi               | Harga  | Status  |
    |-------------|------------------------|-----------|----------|------|-------------------------|--------|---------|
    | netflix1u1p | user1@domain.com        | pass123   | User 1  | 1234 | Tidak boleh ganti pass  | 10000  | available |
    | netflix1u1p | user2@domain.com        | pass456   | User 2  | 5678 | Tidak boleh ganti pass  | 10000  | sold     |

🔹 Fungsi:
- Menyimpan akun Netflix yang tersedia.
- Bot akan mengambil akun available, lalu menandainya sold setelah dikirim ke user.

2️⃣ Sheet: viu

📌 Menyimpan daftar akun Viu yang tersedia untuk dijual

    | Kode      | Email                  | Password | Deskripsi               | Harga  | Status  |
    |-----------|------------------------|---------|--------------------------|--------|---------|
    | viuanlim | user1@domain.com        | viu123  | Tidak boleh ganti pass  | 10000  | available |
    | viuanlim | user2@domain.com        | viu456  | Tidak boleh ganti pass  | 10000  | sold     |

🔹 Fungsi:
- Menyimpan akun Viu yang tersedia.
- Bot akan mengambil akun available, lalu menandainya sold setelah dikirim ke user.

3️⃣ Sheet: historytrx

📌 Menyimpan histori transaksi pengguna

    | Invoice                | Telegram ID | Produk                 | Tanggal Order         | Status Pembayaran | Notified |
    |------------------------|-------------|------------------------|-----------------------|-------------------|----------|
    | INV-20250130232613-955 | 5143875356  | netflix1u1p (3)       | 2025-01-30 23:26:13   | pending           | no       |
    | INV-20250130232613-955 | 5143875356  | netflix1u1p (3)       | 2025-01-30 23:26:13   | paid              | yes      |

🔹 Fungsi:
- Invoice → Nomor unik yang dibuat otomatis untuk setiap order.
- Telegram ID → ID user Telegram yang melakukan transaksi.
- Produk → Kode produk yang dipesan, jumlah ditampilkan dalam format kode (jumlah).
- Tanggal Order → Waktu order dibuat.
- Status Pembayaran:
  - pending → Belum dibayar, bot menampilkan QRIS.
  - paid → Sudah dibayar, bot mengirim akun ke user.
  - cancel → Order dibatalkan oleh user.
- Notified:
  - no → Belum dikirim akun.
  - yes → Akun sudah dikirim ke user.

🛠️ Cara Kerja Otomatisasi di Spreadsheet

Saat user order /order <kode> <jumlah>

🔹 Bot akan menambahkan data ke historytrx, menandai akun di sheet netflix / viu sebagai sold.

Saat user cek invoice /cekinvoice <invoice>

🔹 Jika status pending, bot akan menampilkan QRIS untuk pembayaran.

Saat admin mengubah status ke paid di historytrx

🔹 Bot akan otomatis mengirim akun ke user berdasarkan akun yang tersedia di Netflix/Viu.

Saat user membatalkan order /cancel <invoice>

🔹 Status di historytrx akan berubah menjadi cancel, sehingga akun tidak akan dikirim.

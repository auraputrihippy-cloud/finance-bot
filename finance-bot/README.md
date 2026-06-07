# Dompet Bot 💰 — Asisten Keuangan Telegram

Bot Telegram berbasis AI untuk mencatat dan menganalisis keuangan pribadi.

## Fitur
- Catat pemasukan & pengeluaran lewat chat natural
- Analisis keuangan otomatis
- Ringkasan saldo kapan saja
- Saran pengelolaan keuangan

## Cara Setup

### Step 1: Buat Bot Telegram
1. Buka Telegram, cari @BotFather
2. Ketik `/newbot`
3. Ikuti instruksi, pilih nama bot (contoh: DompetKuBot)
4. Copy TOKEN yang diberikan BotFather

### Step 2: Siapkan API Key Anthropic
1. Buka https://console.anthropic.com
2. Daftar / login
3. Buat API Key baru
4. Copy key-nya

### Step 3: Deploy ke Railway
1. Buka https://railway.app dan daftar (gratis)
2. Klik "New Project" → "Deploy from GitHub repo"
   - Upload folder ini ke GitHub dulu, atau
   - Gunakan Railway CLI
3. Di Railway, masuk ke tab "Variables" dan tambahkan:
   - `TELEGRAM_TOKEN` = token dari BotFather
   - `ANTHROPIC_API_KEY` = API key dari Anthropic
4. Railway akan otomatis deploy botnya

### Step 4: Pakai Bot!
Cari bot kamu di Telegram dan mulai chat:
- "Jajan bakso 15rb" → otomatis tercatat sebagai pengeluaran
- "Dapat kiriman 500rb" → otomatis tercatat sebagai pemasukan
- `/ringkasan` → lihat laporan keuangan
- `/reset` → hapus semua data dan mulai dari awal

## Contoh Chat
```
Kamu: tadi beli kopi 20rb
Bot: Oke, udah aku catat pengeluaran Rp 20.000 untuk kopi ☕
     Saldo kamu sekarang Rp 480.000

Kamu: dapat kiriman dari mama 300rb
Bot: Wah ada tambahan pemasukan Rp 300.000 dari mama 🎉
     Saldo kamu sekarang Rp 780.000

Kamu: /ringkasan
Bot: Ringkasan keuangan bulan Juni 2026:
     - Total pemasukan: Rp 300.000
     - Total pengeluaran: Rp 20.000
     - Saldo saat ini: Rp 280.000
```

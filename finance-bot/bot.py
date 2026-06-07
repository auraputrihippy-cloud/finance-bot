import os
import json
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

DATA_FILE = "keuangan.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"transaksi": [], "percakapan": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ringkasan_keuangan(transaksi):
    if not transaksi:
        return "Belum ada transaksi."
    total_masuk = sum(t["jumlah"] for t in transaksi if t["tipe"] == "masuk")
    total_keluar = sum(t["jumlah"] for t in transaksi if t["tipe"] == "keluar")
    saldo = total_masuk - total_keluar
    bulan_ini = datetime.datetime.now().strftime("%B %Y")
    ringkasan = f"Ringkasan keuangan bulan {bulan_ini}:\n"
    ringkasan += f"- Total pemasukan: Rp {total_masuk:,.0f}\n"
    ringkasan += f"- Total pengeluaran: Rp {total_keluar:,.0f}\n"
    ringkasan += f"- Saldo saat ini: Rp {saldo:,.0f}\n"
    if transaksi:
        ringkasan += f"\n5 transaksi terakhir:\n"
        for t in transaksi[-5:]:
            tanda = "+" if t["tipe"] == "masuk" else "-"
            ringkasan += f"  {tanda}Rp {t['jumlah']:,.0f} ({t['kategori']}) - {t['catatan']} [{t['tanggal']}]\n"
    return ringkasan

SYSTEM_PROMPT = """Kamu adalah asisten keuangan pribadi bernama "Dompet" yang membantu pengguna mencatat dan menganalisis keuangan mereka lewat Telegram.

Kemampuanmu:
1. Mencatat pemasukan dan pengeluaran dari pesan natural bahasa Indonesia
2. Memberikan ringkasan dan analisis keuangan
3. Memberi saran pengelolaan keuangan

Cara mencatat transaksi:
- Jika pengguna menyebut pemasukan (terima, dapat, masuk, gaji, kiriman, dll) → catat sebagai PEMASUKAN
- Jika pengguna menyebut pengeluaran (beli, bayar, jajan, keluar, habis, dll) → catat sebagai PENGELUARAN

Jika ada transaksi yang perlu dicatat, balas dengan format JSON di dalam tag <transaksi>:
<transaksi>
{
  "tipe": "masuk" atau "keluar",
  "jumlah": angka_tanpa_titik,
  "kategori": "makan/transport/belanja/hiburan/kuliah/kesehatan/kiriman/lainnya",
  "catatan": "keterangan singkat"
}
</transaksi>

Lalu tambahkan respons teks yang ramah dan natural dalam bahasa Indonesia.
Jika tidak ada transaksi, cukup balas dengan teks biasa.
Selalu gunakan bahasa Indonesia yang santai dan friendly."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Aku *Dompet* 💰, asisten keuangan pribadimu!\n\n"
        "Kamu bisa chat ke aku dengan bahasa natural, contoh:\n"
        "• _'Tadi jajan bakso 15rb'_\n"
        "• _'Dapat kiriman dari ortu 500rb'_\n"
        "• _'Bayar ojol 12rb ke kampus'_\n\n"
        "Aku akan otomatis mencatat dan bantu analisis keuanganmu 📊\n\n"
        "Ketik /ringkasan untuk lihat laporan keuanganmu!",
        parse_mode="Markdown"
    )

async def ringkasan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    teks = ringkasan_keuangan(data["transaksi"])
    await update.message.reply_text(teks)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_data({"transaksi": [], "percakapan": []})
    await update.message.reply_text("Data keuangan berhasil direset! Mulai dari awal ya 🆕")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    data = load_data()

    ringkasan_saat_ini = ringkasan_keuangan(data["transaksi"])
    data["percakapan"].append({"role": "user", "content": user_message})
    if len(data["percakapan"]) > 20:
        data["percakapan"] = data["percakapan"][-20:]

    messages_to_send = [
        {"role": "user", "content": f"[Kondisi keuangan saat ini]\n{ringkasan_saat_ini}\n\n[Pesan pengguna]\n{user_message}"}
        if len(data["percakapan"]) == 1
        else msg
        for msg in data["percakapan"]
    ]
    if len(data["percakapan"]) > 1:
        messages_to_send = data["percakapan"].copy()
        messages_to_send[0] = {
            "role": "user",
            "content": f"[Kondisi keuangan saat ini]\n{ringkasan_saat_ini}\n\n[Pesan pengguna]\n{data['percakapan'][0]['content']}"
        }

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages_to_send
    )

    reply = response.content[0].text

    if "<transaksi>" in reply and "</transaksi>" in reply:
        start_idx = reply.index("<transaksi>") + len("<transaksi>")
        end_idx = reply.index("</transaksi>")
        json_str = reply[start_idx:end_idx].strip()
        transaksi_baru = json.loads(json_str)
        transaksi_baru["tanggal"] = datetime.datetime.now().strftime("%d/%m/%Y")
        transaksi_baru["jumlah"] = float(transaksi_baru["jumlah"])
        data["transaksi"].append(transaksi_baru)
        reply_bersih = reply.replace(f"<transaksi>{json_str}</transaksi>", "").strip()
    else:
        reply_bersih = reply

    data["percakapan"].append({"role": "assistant", "content": reply_bersih})
    save_data(data)

    await update.message.reply_text(reply_bersih)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ringkasan", ringkasan))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()

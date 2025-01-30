import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import random
import time
import requests.exceptions

# Konfigurasi Bot Telegram
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Konfigurasi Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("xxx.json", scope)
client = gspread.authorize(creds)

# Load Spreadsheet
spreadsheet = client.open("spreadsheet_name")
netflix_sheet = spreadsheet.worksheet("netflix")
viu_sheet = spreadsheet.worksheet("viu")
history_sheet = spreadsheet.worksheet("historytrx")

# Status Bot Running di Console
print("🚀 Bot sedang berjalan...")

# Fungsi generate nomor invoice
def generate_invoice():
    return f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}"

# Cek stok akun digital
@bot.message_handler(commands=['cekstok'])
def cek_stok(message):
    response = "\U0001F4CA *Stok Tersedia:*\n\n"
    
    sheets = {'Netflix': netflix_sheet, 'Viu': viu_sheet}
    for platform, sheet in sheets.items():
        data = sheet.get_all_records()
        available = {}
        for row in data:
            if row['status'].lower() == 'available':
                if row['kode'] not in available:
                    available[row['kode']] = 0
                available[row['kode']] += 1
        
        if available:
            response += f"📊  *{platform}*\n"
            for kode, jumlah in available.items():
                harga = next((row['harga'] for row in data if row['kode'] == kode), 'Unknown')
                response += f"{kode} : {jumlah} akun | 💰 Rp {harga}\n"
            response += "\n"
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# Proses order akun
@bot.message_handler(commands=['order'])
def order_akun(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Format salah")
        _, kode, jumlah = parts
        jumlah = int(jumlah)
        
        sheet = None
        if any(kode.lower() in row['kode'].lower() for row in netflix_sheet.get_all_records()):
            sheet = netflix_sheet
        elif any(kode.lower() in row['kode'].lower() for row in viu_sheet.get_all_records()):
            sheet = viu_sheet
        
        if not sheet:
            bot.send_message(message.chat.id, "Kode produk tidak valid!")
            return
        
        data = sheet.get_all_records()
        available_accounts = [row for row in data if row['kode'].lower() == kode.lower() and row['status'].lower() == 'available']
        
        if len(available_accounts) < jumlah:
            bot.send_message(message.chat.id, "Stok tidak mencukupi!")
            return
        
        invoice = generate_invoice()
        order_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        harga_satuan = int(next((row['harga'] for row in data if row['kode'].lower() == kode.lower()), 0))
        #total harga ditambah kode unik random agar kita bisa verifikasi secara manual
        total_harga = harga_satuan * jumlah + random.randint(1, 999)
        
        history_sheet.append_row([invoice, message.chat.id, f"{kode} ({jumlah})", order_date, 'pending', 'no'])
        
        for i in range(jumlah):
            selected_account = available_accounts.pop(0)
            sheet.update_cell(sheet.find(selected_account['email']).row, sheet.find('status').col, 'sold')
        
        bot.send_photo(message.chat.id, open("qris_image.png", "rb"), caption=f"✅ Order berhasil dibuat!\nInvoice: `{invoice}`\nTotal: {jumlah} akun\nHarga: Rp {total_harga}\nStatus: *Pending pembayaran*\nSilakan bayar menggunakan QRIS berikut. Tidak perlu kirim bukti transfer, pembayaran akan terkonfirmasi otomatis.\n\nApabila ada kendala atau masalah, hubungi @[your_telegram_username]", parse_mode='Markdown')
    except ValueError:
        bot.send_message(message.chat.id, "Format salah! Gunakan: `/order <kode> <jumlah>`", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

# Cek invoice
@bot.message_handler(commands=['cekinvoice'])
def cek_invoice(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Format salah! Gunakan: `/cekinvoice <invoice>`", parse_mode='Markdown')
            return
        _, invoice = parts
        data = history_sheet.get_all_records()
        invoice_data = next((row for row in data if row['Invoice'] == invoice), None)
        
        if invoice_data:
            status = invoice_data['Status Pembayaran']
            response = f"📜 *Invoice:* `{invoice}`\nStatus: *{status}*"
            if status.lower() == 'pending':
                response += "\n\n📌 Silakan lakukan pembayaran menggunakan QRIS berikut. Tidak perlu kirim bukti transfer, pembayaran akan terkonfirmasi otomatis.\n\nApabila ada kendala atau masalah, hubungi @[your_telegram_username]"
                bot.send_photo(message.chat.id, open("qris_image.png", "rb"), caption=response, parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, response, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Invoice tidak ditemukan!", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

# Cancel invoice
@bot.message_handler(commands=['cancel'])
def cancel_invoice(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Format salah! Gunakan: `/cancel <invoice>`", parse_mode='Markdown')
            return
        _, invoice = parts
        cell = history_sheet.find(invoice)
        if cell:
            history_sheet.update_cell(cell.row, history_sheet.find("Status Pembayaran").col, 'cancel')
            history_sheet.update_cell(cell.row, history_sheet.find("Notified").col, 'no')
            bot.send_message(message.chat.id, f"❌ Invoice `{invoice}` telah dibatalkan.", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Invoice tidak ditemukan!", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

# Cek status pembayaran dan kirim akun setelah paid
def cek_pembayaran():
    while True:
        try:
            data = history_sheet.get_all_records()
            for row in data:
                if row['Status Pembayaran'].lower() == 'paid' and row.get('Notified', 'no') == 'no':
                    kode_produk, jumlah = row['Produk'].split(' (')
                    jumlah = int(jumlah.replace(')', ''))
                    sheet = netflix_sheet if kode_produk.lower().startswith('n') else viu_sheet if kode_produk.lower().startswith('v') else None
                    if not sheet:
                        continue
                    
                    akun_list = [row for row in sheet.get_all_records() if row['kode'] == kode_produk and row['status'].lower() == 'sold'][:jumlah]
                    message = "✅ Pembayaran diterima! Berikut akun kamu:\n\n"
                    for akun_data in akun_list:
                        message += f"Email: {akun_data['email']}\nPassword: {akun_data['password']}\n"
                        if sheet == netflix_sheet:
                            message += f"Profile: {akun_data['profile']}\nPin: {akun_data['pin']}\nSNK: {akun_data['deskripsi']}"
                        else:
                            message += f"SNK: {akun_data['deskripsi']}"
                        message += "\n\n"
                    
                    notified_col = history_sheet.find('Notified')
                    if notified_col:
                        history_sheet.update_cell(history_sheet.find(row['Invoice']).row, notified_col.col, 'yes')
                    
                    bot.send_message(row['Telegram ID'], message + "Terima kasih!", parse_mode='Markdown')
            
            time.sleep(10)  # Delay agar tidak terus-menerus membaca Google Sheets

        except requests.exceptions.ReadTimeout:
            print("Timeout terjadi, mencoba kembali...")
            time.sleep(5)
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")
            time.sleep(5)

# Start command
@bot.message_handler(commands=['start'])
def start_message(message):
    response = "👋 Selamat datang! Berikut daftar perintah yang bisa kamu gunakan:\n\n"
    response += "`/cekstok` - Cek stok akun yang tersedia dan kode produk\n"
    response += "`/order <kode> <jumlah>` - Pesan akun berdasarkan kode dan jumlah\n"
    response += "`/cekinvoice <invoice>` - Cek status invoice\n"
    response += "`/cancel <invoice>` - Batalkan invoice yang belum dibayar\n"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# Jalankan bot
import threading
threading.Thread(target=cek_pembayaran, daemon=True).start()
while True:
    try:
        bot.polling(none_stop=True, timeout=180, long_polling_timeout=120)
    except Exception as e:
        print(f"Error pada polling: {e}, mencoba restart dalam 5 detik...")
        time.sleep(5)

import os
import sys
import logging
from dotenv import load_dotenv
from notifier import send_telegram

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def test_telegram_message():
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("\n❌ HATA: .env dosyasında TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik!")
        print("Lütfen .env dosyasına Telegram bilgilerinizi ekleyin:\n")
        print("TELEGRAM_BOT_TOKEN=123456789:ABCdef...")
        print("TELEGRAM_CHAT_ID=123456789\n")
        return
        
    print(f"🚀 Telegram testi gönderiliyor (Chat ID: {chat_id})...")
    test_text = """# 🚀 CuratorDailyNews Telegram Testi

Merhaba! Telegram bot entegrasyonu **başarıyla kuruldu.**

Bundan sonra her sabah TSİ 08:00'de günün en önemli **teknoloji, donanım (ESP32/Arduino), otomasyon ve Medscape sağlık özetleri** doğrudan bu Telegram sohbetine aktarılacaktır!
"""
    success = send_telegram(test_text)
    if success:
        print("\n✅ TEBRİKLER! Test mesajı Telegram hesabınıza başarıyla ulaştı.")
    else:
        print("\n❌ Mesaj gönderilemedi. Lütfen Bot Token ve Chat ID bilgilerinizi kontrol edin.")

if __name__ == "__main__":
    test_telegram_message()

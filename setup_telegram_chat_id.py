import os
import sys
import requests
import time
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

print(f"🤖 Bot Token: {token}")
print("👉 Lütfen Telegram'da @CuratorNewsRYBot adresine gidin ve /start yazın veya herhangi bir mesaj atın...")

url = f"https://api.telegram.org/bot{token}/getUpdates"

found = False
print("⏳ Telegram'dan @CuratorNewsRYBot adresine mesaj yazmanızı bekliyorum...")

while not found:
    try:
        res = requests.get(url, timeout=10).json()
        results = res.get("result", [])
        if results:
            last_update = results[-1]
            chat_id = None
            if "message" in last_update:
                chat_id = last_update["message"]["chat"]["id"]
                first_name = last_update["message"]["chat"].get("first_name", "Kullanıcı")
            elif "my_chat_member" in last_update:
                chat_id = last_update["my_chat_member"]["chat"]["id"]
                first_name = last_update["my_chat_member"]["chat"].get("first_name", "Kullanıcı")
                
            if chat_id:
                print(f"\n🎉 TEBRİKLER! Chat ID Tespit Edildi: {chat_id} ({first_name})")
                
                env_path = ".env"
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(env_path, "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.startswith("TELEGRAM_CHAT_ID="):
                            f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
                        else:
                            f.write(line)
                            
                print(f"✅ TELEGRAM_CHAT_ID={chat_id} .env dosyasına başarıyla kaydedildi!")
                found = True
                
                # Send first live digest directly to Telegram!
                print("\n🚀 İlk canlı Türkçe bülteniniz Telegram'a gönderiliyor...")
                from main import run_pipeline
                run_pipeline(dry_run=False)
                print("\n✨ İŞLEM TAMAMLANDI! Bülteniniz Telegram sohbetinizde!")
                break
    except Exception as e:
        pass
        
    time.sleep(2)

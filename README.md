# 🚀 CuratorDailyNews - Günlük Teknoloji, Donanım & Sağlık Bülteni

Bu proje; **Medscape (kardiyoloji/sağlık)** ve **Reddit (donanım, otomasyon, iş fikirleri)** gibi kaynaklardan günlük veri toplayıp, Yapay Zeka (OpenAI / Gemini) ile ürün geliştirme ve iş fırsatlarına yönelik **Türkçe Bülten** oluşturan ve **GitHub Actions** ile her sabah otomatik çalışan bir haber radarıdır.

---

## 📌 Özellikler

- **Çoklu Kaynak:** 
  - Sağlık: Medscape Cardiology (`theheart.org`), Medscape Medical News.
  - Teknoloji & Donanım: Reddit `r/sidehustle`, `r/business_ideas`, `r/automation`, `r/raspberrypi`, `r/esp32`, `r/arduino`.
- **Türkçe AI Ürün & İş Fikri Odaklı Sentez:**
  - Haberleri sadece özetlemez; Türkiye ve küresel pazar için **ürünleştirme ve otomasyon fikirleri** üretir.
- **Koyu Modlu HTML E-posta ve Telegram Desteği:**
  - Bülteni şık bir HTML e-posta olarak veya doğrudan Telegram botu üzerinden cebinize iletir.
- **GitHub Actions ile Ücretsiz CRON:**
  - Her sabah TSİ **08:00**'de (05:00 UTC) otomatik çalışır.

---

## 🛠️ Yerel Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 2. `.env` Dosyası Oluşturun

`.env.example` dosyasını kopyalayarak `.env` oluşturun ve API anahtarlarınızı ekleyin:

```bash
cp .env.example .env
```

### 3. Test Çalıştırması Yapın (Dry Run)

E-posta göndermeden sadece çıktı üretmek için:

```bash
python main.py --dry-run
```

Oluşturulan bülten `digest_output.md` ve `digest_output.html` dosyalarında saklanacaktır.

---

## ⚙️ GitHub Actions CRON Yapılandırması

Projeyi GitHub hesabınıza push ettikten sonra otomatik bülten almak için şu adımları izleyin:

1. GitHub Reponuzda **Settings > Secrets and variables > Actions** sayfasına gidin.
2. **New repository secret** butonuna tıklayarak aşağıdaki gizli anahtarları ekleyin:

| Secret Adı | Açıklama |
| :--- | :--- |
| `OPENAI_API_KEY` *(veya `GEMINI_API_KEY`)* | AI özetleme için API anahtarınız |
| `SENDER_EMAIL` | Bültenin gönderileceği Gmail / SMTP e-posta adresi |
| `SENDER_PASSWORD` | Gmail için "Uygulama Şifresi" (App Password) |
| `RECEIVER_EMAIL` | Bülteni alacak e-posta adresiniz |
| `TELEGRAM_BOT_TOKEN` *(Opsiyonel)* | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` *(Opsiyonel)* | Telegram Chat ID |

3. Artık sistem her sabah TSİ 08:00'de otomatik çalışacaktır! İsterseniz GitHub'daki **Actions** sekmesinden `Run workflow` butonuna basarak istediğiniz an manuel tetikleyebilirsiniz.

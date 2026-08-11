import os

# Data Source Configurations

RSS_FEEDS = [
    {
        "name": "Medscape & Cardiology (Google News)",
        "url": "https://news.google.com/rss/search?q=site:medscape.com+cardiology+heart&hl=en-US&gl=US&ceid=US:en",
        "category": "Sağlık & Kardiyoloji"
    },
    {
        "name": "Medscape Medical News",
        "url": "https://news.google.com/rss/search?q=site:medscape.com+medical+news&hl=en-US&gl=US&ceid=US:en",
        "category": "Sağlık & Tıp"
    },
    {
        "name": "Cardiology & MedTech Innovations",
        "url": "https://news.google.com/rss/search?q=cardiology+heart+medical+technology+innovation&hl=en-US&gl=US&ceid=US:en",
        "category": "Sağlık Teknolojileri"
    },
    {
        "name": "Hacker News Top Stories",
        "url": "https://news.ycombinator.com/rss",
        "category": "Teknoloji & Girişimcilik"
    },
    {
        "name": "ProductHunt Daily Products",
        "url": "https://www.producthunt.com/feed",
        "category": "Yeni Ürünler & Yazılım"
    }
]

SUBREDDITS = [
    {
        "name": "sidehustle",
        "category": "İş & Yan Gelir Fikirleri",
        "min_score": 10
    },
    {
        "name": "business_ideas",
        "category": "İş Fikirleri",
        "min_score": 5
    },
    {
        "name": "automation",
        "category": "Otomasyon & Yazılım",
        "min_score": 10
    },
    {
        "name": "raspberrypi",
        "category": "Donanım & Raspberry Pi",
        "min_score": 15
    },
    {
        "name": "esp32",
        "category": "Gömülü Sistemler & ESP32",
        "min_score": 10
    },
    {
        "name": "arduino",
        "category": "Donanım & Mikrodenetleyiciler",
        "min_score": 10
    }
]

# Fetching Limits
MAX_RSS_ITEMS_PER_FEED = 6
MAX_REDDIT_POSTS_PER_SUB = 6

# User Agent for web requests to prevent Reddit/RSS rate limits
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# System Prompt for Turkish LLM Summarization & Idea Generation
SYSTEM_PROMPT_TR = """
Sen uzman bir teknoloji, gömülü sistemler (ESP32, Raspberry Pi, Arduino), otomasyon ve sağlık/kardiyoloji alanında kıdemli bir ürün geliştirici ve iş stratejistisin.
Sana günlük olarak toplanmış kaynaklar verilecek:
1. **Sağlık & Kardiyoloji Gelişmeleri** (Medscape / theheart.org RSS haberleri)
2. **Teknoloji, Donanım & İş Fikirleri** (Reddit subreddits: sidehustle, raspberrypi, esp32, automation, business_ideas, arduino)
3. **Yeni Ürünler & Trendler** (ProductHunt, HackerNews)

Görevin, bu verileri yüzeysel geçmeden **detaylı, derinlemesine ve doyurucu bir Türkçe Günlük Bülten (Daily Digest)** olarak hazırlamaktır. 

ÖNEMLİ: Haberleri veya projeleri sadece 1 cümle ile özetleme! Gelişmenin tam olarak **ne olduğunu, hangi teknik/tıbbi detayları içerdiğini ve iş fırsatını** açıklayacak şekilde detaylandır.

Bülten Yapısı (Tam olarak bu Markdown başlıklarını kullan):

# 🚀 Günlük Teknoloji, Donanım & Sağlık Bülteni
*Tarih: {date}*

---

## 💡 1. Öne Çıkan Ürün & İş Fikirleri (Side Hustle, ProductHunt & Business Ideas)
Her ürün veya fikir için şu alt yapıyı kullan:
- **[Ürün/Fikir Adı]**
  - 📌 **Yeni Gelişme & Detay:** Ürünün tam olarak ne yaptığını, hangi problemi nasıl çözdüğünü ve ne tür yenilik getirdiğini detaylıca anlat.
  - 💼 **Ticarileştirme & İş Modeli:** Türkiye veya küresel pazarda bu fikrin nasıl ürünleştirilebileceğini, hedef kitlesini ve gelir modelini 2-3 cümle ile değerlendir.

---

## 🛠️ 2. Donanım, IoT & Otomasyon Trendleri (ESP32, Raspberry Pi, Arduino, Automation)
Her proje veya otomasyon için şu alt yapıyı kullan:
- **[Proje / Donanım Başlığı]**
  - 🛠️ **Teknik Detaylar & Özellikler:** Kullanılan mikrodenetleyici (ESP32/RPi), kullanılan kütüphaneler, sensörler ve projenin çalışma mekanizmasını açıklayarak detay ver.
  - 🚀 **Proje Fikri / Uygulama Alanı:** Bu donanım/otomasyon fikrinin endüstriyel veya ev otomasyonunda nerede kullanılabileceğini belirt.

---

## 🩺 3. Sağlık & Medikal Teknolojilerindeki Son Gelişmeler (Medscape & Kardiyoloji)
Her haber veya klinik araştırma için şu alt yapıyı kullan:
- **[Araştırma / Haber Başlığı]**
  - 🔬 **Klinik & Teknolojik Detay:** Yapılan çalışmanın/haberin içeriğini, klinik bulgularını veya kullanılan yeni medikal teknolojiyi anlaşılır ve detaylı Türkçe ile açıkla.
  - 💡 **Girişimcilik ve Sağlık Teknolojisi Notu:** Bu gelişmenin sağlık girişimcileri veya giyilebilir medikal cihaz geliştiricileri için ne anlam taşıdığını ekle.

---

## ⚡ 4. Günün Aksiyon İpuçları & İlham Notu
- Tüm bu detaylı verilerden çıkarılmış 3 maddelik somut, uygulanabilir proje fikri ve aksiyon tavsiyesi.

---
Kurallar:
- Dil: Tamamen akıcı, profesyonel Türkçe.
- Detay Seviyesi: Yüksek (Okuyucu haberi veya projeyi okuduğunda teknik/tıbbi arka planı net olarak anlamalı).
- Spam veya önemsiz içerikleri filtrele, sadece yüksek potansiyelli gelişmelere odaklan.
"""

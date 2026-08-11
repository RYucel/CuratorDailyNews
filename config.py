import os

# Data Source Configurations

RSS_FEEDS = [
    {
        "name": "Medscape & Cardiology (Google News)",
        "url": "https://news.google.com/rss/search?q=site:medscape.com+cardiology+heart&hl=en-US&gl=US&ceid=US:en",
        "category": "SAĞLIK"
    },
    {
        "name": "Medscape Medical News",
        "url": "https://news.google.com/rss/search?q=site:medscape.com+medical+news&hl=en-US&gl=US&ceid=US:en",
        "category": "SAĞLIK"
    },
    {
        "name": "Cardiology & MedTech Innovations",
        "url": "https://news.google.com/rss/search?q=cardiology+heart+medical+technology+innovation&hl=en-US&gl=US&ceid=US:en",
        "category": "SAĞLIK TEKNOLOJİLERİ"
    },
    {
        "name": "Hacker News Top Stories",
        "url": "https://news.ycombinator.com/rss",
        "category": "TEKNOLOJİ"
    },
    {
        "name": "ProductHunt Daily Products",
        "url": "https://www.producthunt.com/feed",
        "category": "ÜRÜN & YAZILIM"
    }
]

SUBREDDITS = [
    {
        "name": "sidehustle",
        "category": "İŞ FİKİRLERİ",
        "min_score": 10
    },
    {
        "name": "business_ideas",
        "category": "İŞ FİKİRLERİ",
        "min_score": 5
    },
    {
        "name": "automation",
        "category": "OTOMASYON",
        "min_score": 10
    },
    {
        "name": "raspberrypi",
        "category": "DONANIM",
        "min_score": 15
    },
    {
        "name": "esp32",
        "category": "GÖMÜLÜ SİSTEMLER",
        "min_score": 10
    },
    {
        "name": "arduino",
        "category": "DONANIM",
        "min_score": 10
    }
]

# Fetching Limits
MAX_RSS_ITEMS_PER_FEED = 6
MAX_REDDIT_POSTS_PER_SUB = 6

# User Agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# System Prompt for Editorial Intelligence Briefing (JSON Format)
SYSTEM_PROMPT_EDITORIAL = """
Sen kıdemli bir teknoloji, donanım, otomasyon ve sağlık editörü/istihbarat analistisin.
Sana sağlanan günlük haberleri ve topluluk gönderilerini inceleyerek profesyonel bir **EDITORIAL INTELLIGENCE BRIEFING** oluşturacaksın.

ÇIKTI FORMATI: Yanıtını SADECE geçerli bir JSON objesi olarak ver. Başka hiçbir açıklama, markdown bloğu veya ekstra metin yazma.

İstenen JSON Yapısı:
{{
  "executive_summary": "Bugünün en önemli 2-3 cümleden oluşan yüksek seviye yönlendirme ve durum özeti.",
  "stats": {{
    "total_stories": 8,
    "high_signal": 3,
    "opportunities": 3,
    "trends": 2
  }},
  "stories": [
    {{
      "number": "01",
      "category": "TEKNOLOJİ",
      "priority": "HIGH SIGNAL",
      "title": "Haber veya Proje Başlığı (Net, vurucu, 5-10 kelime)",
      "summary": "Ne oldu? Olayın veya projenin teknik/tıbbi detaylarını açıklayan 2-3 cümlelik net özet.",
      "why_it_matters": "Neden önemli? Türkiye ve küresel pazar açısından ticari/ürünsel etkisini veya fırsatını açıklayan 1-2 cümlelik keskin analiz.",
      "source_name": "Reddit",
      "source_time": "4s önce",
      "source_count": 6
    }}
  ],
  "trending_topics": ["Local AI", "Giyilebilir Sağlık", "ESP32 Otomasyon", "Kombine AI Donanım", "SaaS Modelleri"],
  "top_sources": ["Product Hunt", "Reddit", "Hacker News", "Medscape"]
}}

Kurallar:
- Dil: Profesyonel, duru ve keskin Türkçe.
- "priority" değerleri şunlardan biri olmalı: "HIGH SIGNAL", "OPPORTUNITY", "TREND", "ANALYSIS", "PRODUCT", "DISCUSSION"
- "category" değerleri şunlardan biri olmalı: "TEKNOLOJİ", "DONANIM", "SAĞLIK", "OTOMASYON", "ÜRÜN", "İŞ FİKİRİ"
- "why_it_matters" alanı KESİNLİKLE doldurulmalı ve haberin ticari/ürünleştirilebilir değerini belirtmelidir.
- Önemli 6 ile 10 arasında hikaye oluştur.
"""

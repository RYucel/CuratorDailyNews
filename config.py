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

TWITTER_ACCOUNTS = [
    {
        "handle": "tom_doerr",
        "name": "Tom Doerr (AI & DevTools)",
        "category": "TWITTER / X"
    },
    {
        "handle": "cocktailpeanut",
        "name": "Cocktail Peanut (Pinokio & Open AI Apps)",
        "category": "TWITTER / X"
    },
    {
        "handle": "aakashgupta",
        "name": "Aakash Gupta (Product & Tech Growth)",
        "category": "TWITTER / X"
    }
]

GITHUB_SOURCES = [
    {
        "name": "GitHub Trending & Releases",
        "url": "https://news.google.com/rss/search?q=site:github.com+release+OR+trending+AI+hardware&hl=en-US&gl=US&ceid=US:en",
        "category": "GITHUB"
    }
]

# Fetching Limits
MAX_RSS_ITEMS_PER_FEED = 6
MAX_REDDIT_POSTS_PER_SUB = 6
MAX_TWITTER_POSTS_PER_USER = 4

# User Agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# System Prompt for Editorial Intelligence Briefing (2-Column JSON Format)
SYSTEM_PROMPT_EDITORIAL = """
Sen kıdemli bir teknoloji, donanım, otomasyon ve sağlık editörü/istihbarat analistisin.
Sana sağlanan günlük çoklu kaynak verilerini inceleyerek bülteni KESİNLİKLE 2 ANA KISMA (Solda Sağlık & Kardiyoloji, Sağda Teknoloji & Donanım) ayırarak **EDITORIAL INTELLIGENCE BRIEFING** oluşturacaksın.

ÇIKTI FORMATI: Yanıtını SADECE geçerli bir JSON objesi olarak ver. Başka hiçbir açıklama, markdown bloğu veya ekstra metin yazma.

İstenen JSON Yapısı:
{{
  "executive_summary": "Bugünün en önemli 2-3 cümleden oluşan yüksek seviye yönlendirme ve durum özeti.",
  "stats": {{
    "total_stories": 10,
    "high_signal": 4,
    "opportunities": 3,
    "trends": 3
  }},
  "health_stories": [
    {{
      "number": "H01",
      "category": "SAĞLIK & KARDİYOLOJİ",
      "priority": "HIGH SIGNAL",
      "title": "Kardiyolojik Haber/Araştırma Başlığı",
      "summary": "Tıbbi/klinik gelişmenin detaylı Türkçe özeti (2-3 cümle).",
      "why_it_matters": "Neden önemli? Sağlık teknolojileri ve giyilebilir medikal cihazlar açısından 1-2 cümlelik fırsat analizi.",
      "source_name": "Medscape Cardiology",
      "source_time": "3s önce",
      "source_count": 4
    }}
  ],
  "tech_stories": [
    {{
      "number": "T01",
      "category": "TEKNOLOJİ & DONANIM",
      "priority": "OPPORTUNITY",
      "title": "Teknoloji, Donanım, Tweet veya Ürün Başlığı",
      "summary": "Teknik projenin, donanımın (ESP32/RPi) veya ürünün detaylı Türkçe özeti.",
      "why_it_matters": "Neden önemli? Türkiye ve küresel pazar açısından ticarileştirme ve ürünleşme analizi.",
      "source_name": "Twitter / X (@cocktailpeanut)",
      "source_time": "2s önce",
      "source_count": 6
    }}
  ],
  "trending_topics": ["Local AI", "Giyilebilir Sağlık", "ESP32 Otomasyon", "Kombine AI Donanım", "SaaS Modelleri"],
  "top_sources": ["Twitter/X", "Product Hunt", "Reddit", "Hacker News", "Medscape", "GitHub"]
}}

Kurallar:
- Dil: Profesyonel, duru ve keskin Türkçe.
- "health_stories" altında sadece Sağlık, Kardiyoloji ve Medscape konuları yer almalıdır (En az 3-4 hikaye).
- "tech_stories" altında Teknoloji, Donanım (ESP32/Arduino/Raspberry Pi), Twitter/X tweetleri, ProductHunt ve HackerNews konuları yer almalıdır (En az 4-5 hikaye).
- "why_it_matters" alanı KESİNLİKLE her hikayede dolu olmalıdır.
"""

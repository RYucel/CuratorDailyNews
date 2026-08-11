import os
import json
import re
import datetime
import logging
from typing import List, Dict, Any, Tuple
from config import SYSTEM_PROMPT_EDITORIAL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def format_data_for_llm(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]], twitter_posts: List[Dict[str, Any]] = [], github_items: List[Dict[str, Any]] = []) -> str:
    """Formats raw feeds into LLM prompt context."""
    lines = []
    
    lines.append("=== SAĞLIK & KARDİYOLOJİ HABERLERİ (MEDSCAPE / RSS) ===")
    for idx, item in enumerate(rss_articles, 1):
        lines.append(f"[{idx}] Başlık: {item['title']}")
        lines.append(f"    Kaynak: {item['source']} | Kategori: {item['category']}")
        if item.get("summary"):
            lines.append(f"    Özet: {item['summary']}")
        lines.append(f"    Link: {item['link']}\n")
        
    lines.append("\n=== TEKNOLOJİ, DONANIM & İŞ FİKİRLERİ (REDDIT & PRODUCTHUNT & HN) ===")
    for idx, item in enumerate(reddit_posts, 1):
        lines.append(f"[{idx}] Kaynak: {item['subreddit']} (Skor: {item['score']})")
        lines.append(f"    Başlık: {item['title']}")
        if item.get("text"):
            lines.append(f"    İçerik: {item['text']}")
        lines.append(f"    Link: {item['permalink']}\n")
        
    lines.append("\n=== TWITTER / X HESAPLARI (@tom_doerr, @cocktailpeanut, @aakashgupta) ===")
    if not twitter_posts:
        lines.append("Henüz yeni tweet bulunamadı.")
    else:
        for idx, item in enumerate(twitter_posts, 1):
            lines.append(f"[{idx}] Hesap: {item['handle']} ({item['name']})")
            lines.append(f"    Tweet/Gönderi: {item['title']}")
            if item.get("text"):
                lines.append(f"    İçerik: {item['text']}")
            lines.append(f"    Link: {item['url']}\n")

    lines.append("\n=== GITHUB TRENDING & RELEASES ===")
    if not github_items:
        lines.append("Henüz yeni GitHub güncellemesi bulunamadı.")
    else:
        for idx, item in enumerate(github_items, 1):
            lines.append(f"[{idx}] Proje/Release: {item['title']}")
            lines.append(f"    Link: {item['link']}\n")

    return "\n".join(lines)

def parse_json_from_llm_response(text: str) -> Dict[str, Any]:
    """Cleans markdown code blocks and parses JSON safely."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()
    
    try:
        return json.loads(cleaned)
    except Exception as e:
        logging.warning(f"Failed to parse direct JSON response: {e}. Attempting regex search...")
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception as e2:
                logging.error(f"Regex JSON extraction failed: {e2}")
        raise

def generate_mock_editorial_data(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Fallback 2-column editorial data if no LLM key is present."""
    return {
        "executive_summary": "Bugünün bülteninde solda Medscape ve kardiyovasküler sağlık araştırmaları, sağda ise yerel AI çipleri, ESP32 otomasyon ve mikro-donanım girişimleri yer alıyor.",
        "stats": {
            "total_stories": len(rss_articles) + len(reddit_posts),
            "high_signal": 5,
            "opportunities": 4,
            "trends": 3
        },
        "health_stories": [
            {
                "number": "H01",
                "category": "SAĞLIK & KARDİYOLOJİ",
                "priority": "HIGH SIGNAL",
                "title": "Koroner Arter Kalsiyum Skorlaması ile Kalp Riski Tahmini",
                "summary": "Kalsiyum skorlamasının EKG ve kan basıncı ölçümleriyle birleştirilmesi, kardiyak risk tahminlerini rafine ediyor ve erken müdahale şansını artırıyor.",
                "why_it_matters": "Önleyici kardiyoloji alanında kişiselleştirilmiş tanı kitleri ve mobil sağlık analiz platformları için yüksek ticari değer taşır.",
                "source_name": "Medscape Cardiology",
                "source_time": "3s önce",
                "source_count": 5
            },
            {
                "number": "H02",
                "category": "SAĞLIK TEKNOLOJİLERİ",
                "priority": "TREND",
                "title": "Giyilebilir Biyo-Sensörler Sürekli Kan Analizi Sunuyor",
                "summary": "Yeni nesil giyilebilir yamalar, ter ve doku sıvısından glikoz ve laktat seviyelerini eşzamanlı takip ederek mobil uygulamaya aktarıyor.",
                "why_it_matters": "Sporcu sağlığı ve diyabet yönetiminde donanım + SaaS abonelik modeli yaratma fırsatı sunar.",
                "source_name": "MedTech News",
                "source_time": "5s önce",
                "source_count": 4
            }
        ],
        "tech_stories": [
            {
                "number": "T01",
                "category": "DONANIM & AI",
                "priority": "HIGH SIGNAL",
                "title": "Cerebras ve Yerel Çip Mimarisi Cihaz Üstü AI İnferansını Hızlandırıyor",
                "summary": "Tüketici elektroniği ve otomasyon kitleri, bulut bağımlılığını ortadan kaldırarak cihaz üzerinde çalışan yerel yapay zeka modellerine geçiyor.",
                "why_it_matters": "Sıfır gecikmeli ev otomasyonu ve gizlilik odaklı medikal cihazlar için yeni bir ürün kategorisi doğuyor.",
                "source_name": "Hacker News",
                "source_time": "2s önce",
                "source_count": 8
            },
            {
                "number": "T02",
                "category": "ÜRÜN & YAZILIM",
                "priority": "OPPORTUNITY",
                "title": "SecondBrain Note MagSafe İle Ortam Seslerini Nota Dönüştürüyor",
                "summary": "Manyetik olarak telefona tutunan ortam ses kayıt donanımı, toplantıları analiz edip yapılacaklar listesine dönüştürüyor.",
                "why_it_matters": "Donanım + Yazılım bileşimi ile yüksek marjlı profesyonel verimlilik cihazı pazarı sunuyor.",
                "source_name": "Product Hunt",
                "source_time": "4s önce",
                "source_count": 6
            }
        ],
        "trending_topics": ["Local AI", "Giyilebilir Sağlık", "ESP32 Otomasyon", "Kombine AI Donanım", "SaaS Modelleri"],
        "top_sources": ["Twitter/X", "Product Hunt", "Reddit", "Hacker News", "Medscape", "GitHub"]
    }

def generate_digest_with_cerebras(prompt_content: str, api_key: str) -> Dict[str, Any]:
    """Generates structured JSON using Cerebras Cloud API."""
    import openai
    model = os.getenv("CEREBRAS_MODEL", "gemma-4-31b")
    logging.info(f"Generating editorial digest with Cerebras model '{model}'...")
    
    client = openai.OpenAI(api_key=api_key, base_url="https://api.cerebras.ai/v1")
    
    models_to_try = [model, "gemma-4-31b", "gpt-oss-120b", "zai-glm-4.7"]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
    
    for m in models_to_try:
        try:
            logging.info(f"Attempting Cerebras inference with model '{m}'...")
            res = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_EDITORIAL},
                    {"role": "user", "content": f"Aşağıdaki verilerden 2 KISIMLI (Solda Sağlık, Sağda Teknoloji) JSON formatında Editorial Intelligence Briefing oluştur:\n\n{prompt_content}"}
                ],
                temperature=0.4,
                max_tokens=3500
            )
            raw_text = res.choices[0].message.content
            return parse_json_from_llm_response(raw_text)
        except Exception as e:
            logging.warning(f"Cerebras model '{m}' failed: {e}")
            
    raise Exception("All Cerebras models failed.")

def generate_editorial_data(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]], twitter_posts: List[Dict[str, Any]] = [], github_items: List[Dict[str, Any]] = []) -> Dict[str, Any]:
    """Main generation logic returning python dictionary of editorial content."""
    prompt_content = format_data_for_llm(rss_articles, reddit_posts, twitter_posts, github_items)
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if cerebras_key:
        try:
            return generate_digest_with_cerebras(prompt_content, cerebras_key)
        except Exception as e:
            logging.error(f"Cerebras API error: {e}. Falling back...")
            
    if openai_key:
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_EDITORIAL},
                    {"role": "user", "content": prompt_content}
                ],
                response_format={"type": "json_object"}
            )
            return parse_json_from_llm_response(res.choices[0].message.content)
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            
    logging.warning("No valid API keys or inference error. Using fallback mock editorial data.")
    return generate_mock_editorial_data(rss_articles, reddit_posts)

def render_story_item(s: Dict[str, Any]) -> str:
    """Renders single story item HTML."""
    priority_str = s.get('priority', 'HIGH SIGNAL')
    return f"""
    <article class="story-item">
        <div class="story-header">
            <span class="story-num">{s.get('number', '01')}</span>
            <span class="story-cat">{s.get('category', 'KATEGORİ')}</span>
            <span class="story-sep">·</span>
            <span class="story-priority"><span class="priority-dot">●</span> {priority_str}</span>
        </div>
        <h2 class="story-title">{s.get('title', '')}</h2>
        <p class="story-summary">{s.get('summary', '')}</p>
        
        <div class="story-why-box">
            <div class="why-label">WHY IT MATTERS</div>
            <p class="why-text">{s.get('why_it_matters', '')}</p>
        </div>
        
        <div class="story-meta">
            {s.get('source_name', 'Kaynak')} · {s.get('source_time', 'Günün Özeti')} · {s.get('source_count', 4)} kaynak
        </div>
    </article>
    """

def render_editorial_html(data: Dict[str, Any]) -> str:
    """Renders 2-column parallel (Left Health, Right Tech) editorial HTML."""
    stats = data.get("stats", {})
    health_stories = data.get("health_stories", data.get("stories", [])[:4])
    tech_stories = data.get("tech_stories", data.get("stories", [])[4:])
    exec_summary = data.get("executive_summary", "")
    
    health_html_list = [render_story_item(s) for s in health_stories]
    health_combined = '<hr class="story-divider" />\n'.join(health_html_list)
    
    tech_html_list = [render_story_item(s) for s in tech_stories]
    tech_combined = '<hr class="story-divider" />\n'.join(tech_html_list)
    
    total_count = len(health_stories) + len(tech_stories)
    
    return f"""
    <!-- BRIEFING HEADER -->
    <header class="briefing-header">
        <div class="briefing-date">{datetime.date.today().strftime('%d %B %Y').upper()}</div>
        <h1 class="briefing-title">TODAY'S BRIEFING</h1>
        <p class="briefing-exec">{exec_summary}</p>
    </header>

    <!-- AT A GLANCE STATS -->
    <div class="briefing-stats">
        <div class="stat-col">
            <span class="stat-num">{stats.get('total_stories', total_count)}</span>
            <span class="stat-label">STORIES</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-col">
            <span class="stat-num">{stats.get('high_signal', 4)}</span>
            <span class="stat-label">HIGH SIGNAL</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-col">
            <span class="stat-num">{stats.get('opportunities', 3)}</span>
            <span class="stat-label">OPPORTUNITIES</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-col">
            <span class="stat-num">{stats.get('trends', 3)}</span>
            <span class="stat-label">TRENDS</span>
        </div>
    </div>

    <!-- 2-COLUMN PARALLEL FEED: LEFT HEALTH / RIGHT TECH -->
    <div class="editorial-two-columns">
        
        <!-- LEFT COLUMN: KALP & SAĞLIK -->
        <div class="column-health">
            <h3 class="column-title column-title-health">🩺 SAĞLIK & KARDİYOLOJİ</h3>
            <div class="feed-list">
                {health_combined}
            </div>
        </div>

        <!-- RIGHT COLUMN: TEKNOLOJİ & DONANIM -->
        <div class="column-tech">
            <h3 class="column-title column-title-tech">⚡ TEKNOLOJİ & DONANIM</h3>
            <div class="feed-list">
                {tech_combined}
            </div>
        </div>

    </div>
    """

def render_editorial_markdown(data: Dict[str, Any]) -> str:
    """Renders 2-column plain markdown version for Telegram/Email."""
    exec_summary = data.get("executive_summary", "")
    health_stories = data.get("health_stories", [])
    tech_stories = data.get("tech_stories", [])
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    
    lines = [
        f"🗞️ *CURATOR DAILY NEWS — {today_str}*",
        f"_{exec_summary}_\n",
        "====================================",
        "🩺 *SAĞLIK & KARDİYOLOJİ GELİŞMELERİ*",
        "===================================="
    ]
    
    for s in health_stories:
        lines.append(f"\n*{s.get('number', 'H01')} | {s.get('category', 'SAĞLIK')} · {s.get('priority', '')}*")
        lines.append(f"*{s.get('title', '')}*")
        lines.append(f"{s.get('summary', '')}")
        lines.append(f"💡 *WHY IT MATTERS:* {s.get('why_it_matters', '')}")
        lines.append(f"📌 _{s.get('source_name', 'Medscape')} · {s.get('source_count', 4)} kaynak_")
        lines.append("------------------------------------")
        
    lines.append("\n====================================")
    lines.append("⚡ *TEKNOLOJİ, DONANIM & İŞ FİKİRLERİ*")
    lines.append("====================================")
    
    for s in tech_stories:
        lines.append(f"\n*{s.get('number', 'T01')} | {s.get('category', 'TEKNOLOJİ')} · {s.get('priority', '')}*")
        lines.append(f"*{s.get('title', '')}*")
        lines.append(f"{s.get('summary', '')}")
        lines.append(f"💡 *WHY IT MATTERS:* {s.get('why_it_matters', '')}")
        lines.append(f"📌 _{s.get('source_name', 'Twitter/Reddit')} · {s.get('source_count', 4)} kaynak_")
        lines.append("------------------------------------")
        
    return "\n".join(lines)

def generate_digest(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> str:
    """Main pipeline digest generator returning markdown string."""
    data = generate_editorial_data(rss_articles, reddit_posts)
    return render_editorial_markdown(data)

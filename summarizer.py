import os
import json
import re
import datetime
import logging
from typing import List, Dict, Any, Tuple
from config import SYSTEM_PROMPT_EDITORIAL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def format_data_for_llm(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> str:
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
        
    return "\n".join(lines)

def parse_json_from_llm_response(text: str) -> Dict[str, Any]:
    """Cleans markdown code blocks and parses JSON safely."""
    cleaned = text.strip()
    # Remove markdown code block fences if present
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
    """Fallback editorial data if no LLM key is present."""
    return {
        "executive_summary": "Yapay zeka donanımları yerel çip mimarilerine kayarken, giyilebilir medikal cihazlar laboratuvar verileriyle birleşerek kişiselleştirilmiş sağlık takibinde yeni bir dönem başlatıyor.",
        "stats": {
            "total_stories": len(rss_articles) + len(reddit_posts),
            "high_signal": 5,
            "opportunities": 3,
            "trends": 4
        },
        "stories": [
            {
                "number": "01",
                "category": "DONANIM & AI",
                "priority": "HIGH SIGNAL",
                "title": "Cerebras ve Gömülü AI Çipleri Yerel İnferans Dönemini Başlatıyor",
                "summary": "Tüketici elektroniği ve IoT cihazları, bulut bağımlılığını azaltmak için donanım üzerinde doğrudan çalışan ultra-hızlı yapay zeka çiplerine geçiyor.",
                "why_it_matters": "Bulut API maliyetlerini sıfırlarken, gecikmesiz ev otomasyonu ve gizlilik odaklı medikal cihazlar için yeni bir ürün kategorisi yaratıyor.",
                "source_name": "Hacker News",
                "source_time": "2s önce",
                "source_count": 8
            },
            {
                "number": "02",
                "category": "ÜRÜN & VERİMLİLİK",
                "priority": "OPPORTUNITY",
                "title": "SecondBrain Note MagSafe İle Ortam Seslerini Nota Dönüştürüyor",
                "summary": "Akıllı telefonlara manyetik olarak yapışan donanım, ortamdaki toplantı ve konuşmaları ortam dinlemesiyle analiz edip aksiyon öğelerine çeviriyor.",
                "why_it_matters": "Yazılım ve donanımın birleştiği giyilebilir ortam asistanı pazarı, yönetici ve saha çalışanları için yüksek marjlı bir SaaS+Donanım modeli sunuyor.",
                "source_name": "Product Hunt",
                "source_time": "4s önce",
                "source_count": 5
            },
            {
                "number": "03",
                "category": "SAĞLIK & KARDİYOLOJİ",
                "priority": "TREND",
                "title": "Medscape: Giyilebilir Kardiyak Takip Laboratuvar Testleriyle Entegre Oluyor",
                "summary": "Kardiyoloji dünyasındaki son araştırmalar, sürekli EKG ve nabız takibinin biyokimyasal kan testleriyle birleştirilerek erken uyarı sistemi sunduğunu gösteriyor.",
                "why_it_matters": "Sağlık girişimcileri için özel kliniklerle entegre çalışacak kişiselleştirilmiş yaşlanma ve kalp sağlığı platformları ciddi fırsat barındırıyor.",
                "source_name": "Medscape Cardiology",
                "source_time": "5s önce",
                "source_count": 7
            }
        ],
        "trending_topics": ["Local AI", "Giyilebilir Sağlık", "ESP32 Otomasyon", "Kombine AI Donanım", "SaaS Modelleri"],
        "top_sources": ["Product Hunt", "Reddit", "Hacker News", "Medscape"]
    }

def generate_digest_with_cerebras(prompt_content: str, api_key: str) -> Dict[str, Any]:
    """Generates structured JSON using Cerebras Cloud API."""
    import openai
    model = os.getenv("CEREBRAS_MODEL", "gemma-4-31b")
    logging.info(f"Generating editorial digest with Cerebras model '{model}'...")
    
    client = openai.OpenAI(api_key=api_key, base_url="https://api.cerebras.ai/v1")
    today_str = datetime.date.today().strftime("%d %B %Y")
    
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
                    {"role": "user", "content": f"Aşağıdaki verilerden JSON formatında Editorial Intelligence Briefing oluştur:\n\n{prompt_content}"}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            raw_text = res.choices[0].message.content
            return parse_json_from_llm_response(raw_text)
        except Exception as e:
            logging.warning(f"Cerebras model '{m}' failed: {e}")
            
    raise Exception("All Cerebras models failed.")

def generate_editorial_data(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Main generation logic returning python dictionary of editorial content."""
    prompt_content = format_data_for_llm(rss_articles, reddit_posts)
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

def render_editorial_html(data: Dict[str, Any]) -> str:
    """Renders clean, editorial non-card HTML format."""
    stats = data.get("stats", {})
    stories = data.get("stories", [])
    exec_summary = data.get("executive_summary", "")
    
    stories_html = []
    for s in stories:
        priority_str = s.get('priority', 'HIGH SIGNAL')
        story_code = f"""
        <article class="story-item">
            <div class="story-header">
                <span class="story-num">{s.get('number', '01')}</span>
                <span class="story-cat">{s.get('category', 'TEKNOLOJİ')}</span>
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
                {s.get('source_name', 'Reddit')} · {s.get('source_time', 'Günün Özeti')} · {s.get('source_count', 4)} kaynak
            </div>
        </article>
        """
        stories_html.append(story_code)
        
    stories_combined = '<hr class="story-divider" />\n'.join(stories_html)
    
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
            <span class="stat-num">{stats.get('total_stories', len(stories))}</span>
            <span class="stat-label">STORIES</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-col">
            <span class="stat-num">{stats.get('high_signal', 5)}</span>
            <span class="stat-label">HIGH SIGNAL</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-col">
            <span class="stat-num">{stats.get('opportunities', 3)}</span>
            <span class="stat-label">OPPORTUNITIES</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-col">
            <span class="stat-num">{stats.get('trends', 4)}</span>
            <span class="stat-label">TRENDS</span>
        </div>
    </div>

    <!-- MAIN SIGNAL FEED -->
    <section class="signal-feed">
        <h3 class="section-label">TODAY'S SIGNAL</h3>
        <div class="feed-list">
            {stories_combined}
        </div>
    </section>
    """

def render_editorial_markdown(data: Dict[str, Any]) -> str:
    """Renders plain markdown version for Telegram/Email."""
    exec_summary = data.get("executive_summary", "")
    stories = data.get("stories", [])
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    
    lines = [
        f"🗞️ *CURATOR DAILY NEWS — {today_str}*",
        f"_{exec_summary}_\n",
        "------------------------------------"
    ]
    
    for s in stories:
        lines.append(f"\n*{s.get('number', '01')} | {s.get('category', '')} · {s.get('priority', '')}*")
        lines.append(f"*{s.get('title', '')}*")
        lines.append(f"{s.get('summary', '')}")
        lines.append(f"\n💡 *WHY IT MATTERS:* {s.get('why_it_matters', '')}")
        lines.append(f"📌 _{s.get('source_name', 'Kaynak')} · {s.get('source_count', 4)} kaynak_")
        lines.append("------------------------------------")
        
    return "\n".join(lines)

def generate_digest(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> str:
    """Main pipeline digest generator returning markdown string for backwards compatibility."""
    data = generate_editorial_data(rss_articles, reddit_posts)
    return render_editorial_markdown(data)

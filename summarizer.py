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

def generate_mock_editorial_data(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]], twitter_posts: List[Dict[str, Any]] = [], github_items: List[Dict[str, Any]] = []) -> Dict[str, Any]:
    """Fallback 2-column editorial data built from the actually fetched items.

    Used when no LLM key/quota is available. Pulls directly from today's fetched
    RSS/Reddit/Twitter/GitHub items instead of static text, so the digest still
    changes day to day even without an LLM call.
    """
    def clip(text: str, n: int) -> str:
        text = (text or "").strip()
        return text[:n] + "..." if len(text) > n else text

    health_source_items = [a for a in rss_articles if a.get("category") in ("SAĞLIK", "SAĞLIK TEKNOLOJİLERİ")]
    if not health_source_items:
        health_source_items = rss_articles

    tech_source_items = (
        [a for a in rss_articles if a.get("category") not in ("SAĞLIK", "SAĞLIK TEKNOLOJİLERİ")]
        + reddit_posts + twitter_posts + github_items
    )

    health_stories = []
    for idx, item in enumerate(health_source_items[:4], 1):
        health_stories.append({
            "number": f"H0{idx}",
            "category": item.get("category", "SAĞLIK"),
            "priority": "HIGH SIGNAL" if idx == 1 else "TREND",
            "title": item.get("title", ""),
            "summary": clip(item.get("summary", ""), 300) or "Detaylar için kaynak bağlantısını inceleyin.",
            "why_it_matters": "Bu gelişme sağlık/kardiyoloji alanındaki güncel araştırma ve ürün akışını temsil ediyor.",
            "source_name": item.get("source", "Medscape"),
            "source_time": "Bugün",
            "source_count": len(health_source_items),
            "link": item.get("link", "")
        })

    tech_stories = []
    for idx, item in enumerate(tech_source_items[:5], 1):
        title = item.get("title", "")
        text_val = item.get("summary") or item.get("text") or ""
        source_name = item.get("source") or item.get("subreddit") or item.get("handle") or "GitHub Trending"
        link = item.get("link") or item.get("permalink") or item.get("url") or ""
        tech_stories.append({
            "number": f"T0{idx}",
            "category": item.get("category", "TEKNOLOJİ"),
            "priority": "HIGH SIGNAL" if idx == 1 else "OPPORTUNITY",
            "title": title,
            "summary": clip(text_val, 300) or "Detaylar için kaynak bağlantısını inceleyin.",
            "why_it_matters": "Bu içerik teknoloji/donanım/otomasyon gündeminde bugün öne çıkan gelişmelerden biri.",
            "source_name": source_name,
            "source_time": "Bugün",
            "source_count": len(tech_source_items),
            "link": link
        })

    return {
        "executive_summary": "Bugünün bülteninde solda sağlık & kardiyoloji gelişmeleri, sağda teknoloji, donanım ve otomasyon gündemi yer alıyor. (Not: LLM özetleme şu an devre dışı, başlıklar doğrudan kaynaklardan derlendi.)",
        "stats": {
            "total_stories": len(health_stories) + len(tech_stories),
            "high_signal": sum(1 for s in health_stories + tech_stories if s["priority"] == "HIGH SIGNAL"),
            "opportunities": sum(1 for s in tech_stories if s["priority"] == "OPPORTUNITY"),
            "trends": sum(1 for s in health_stories if s["priority"] == "TREND")
        },
        "health_stories": health_stories,
        "tech_stories": tech_stories,
        "trending_topics": list({s["category"] for s in tech_stories + health_stories})[:5],
        "top_sources": list({s["source_name"] for s in tech_stories + health_stories})[:6]
    }

def generate_digest_with_cerebras(prompt_content: str, api_key: str) -> Dict[str, Any]:
    """Generates structured JSON using Cerebras Cloud API."""
    import openai
    model = os.getenv("CEREBRAS_MODEL") or "llama-3.3-70b"
    logging.info(f"Generating editorial digest with Cerebras model '{model}'...")

    client = openai.OpenAI(api_key=api_key, base_url="https://api.cerebras.ai/v1")

    models_to_try = [model, "llama-3.3-70b", "gpt-oss-120b", "qwen-3-32b"]
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
    return generate_mock_editorial_data(rss_articles, reddit_posts, twitter_posts, github_items)

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

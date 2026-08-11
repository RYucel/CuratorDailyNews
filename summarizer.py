import os
import datetime
import logging
from typing import List, Dict, Any, Tuple
from config import SYSTEM_PROMPT_TR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def format_data_for_llm(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> str:
    """Formats collected data into a structured context for the LLM."""
    lines = []
    
    lines.append("=== SAĞLIK & KARDİYOLOJİ HABERLERİ (MEDSCAPE / RSS) ===")
    if not rss_articles:
        lines.append("Bugün henüz yeni sağlık haberi bulunamadı.")
    else:
        for idx, item in enumerate(rss_articles, 1):
            lines.append(f"[{idx}] Başlık: {item['title']}")
            lines.append(f"    Kaynak: {item['source']} | Kategori: {item['category']}")
            if item.get("summary"):
                lines.append(f"    Özet: {item['summary']}")
            lines.append(f"    Link: {item['link']}\n")
            
    lines.append("\n=== TEKNOLOJİ, DONANIM & İŞ FİKİRLERİ (REDDIT) ===")
    if not reddit_posts:
        lines.append("Bugün henüz yeni Reddit gönderisi bulunamadı.")
    else:
        for idx, item in enumerate(reddit_posts, 1):
            lines.append(f"[{idx}] Subreddit: {item['subreddit']} (Skor: {item['score']} | Yorumlar: {item['comments_count']})")
            lines.append(f"    Başlık: {item['title']}")
            if item.get("text"):
                lines.append(f"    İçerik: {item['text']}")
            lines.append(f"    Link: {item['permalink']}\n")
            
    return "\n".join(lines)

def generate_digest_with_openai(prompt_content: str, api_key: str) -> str:
    """Generates digest using OpenAI API."""
    import openai
    client = openai.OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    logging.info(f"Generating summary with OpenAI model '{model}'...")
    
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    system_prompt = SYSTEM_PROMPT_TR.format(date=today_str)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Aşağıdaki verileri incele ve Türkçe bülteni oluştur:\n\n{prompt_content}"}
        ],
        temperature=0.7,
        max_tokens=2500
    )
    return response.choices[0].message.content

def generate_digest_with_gemini(prompt_content: str, api_key: str) -> str:
    """Generates digest using Google Gemini API."""
    logging.info("Generating summary with Google Gemini API...")
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    system_prompt = SYSTEM_PROMPT_TR.format(date=today_str)
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system_prompt}\n\nVeriler:\n{prompt_content}"
        )
        return response.text
    except Exception as e:
        logging.warning(f"google-genai client failed: {e}. Trying legacy google-generativeai...")
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{system_prompt}\n\nVeriler:\n{prompt_content}")
        return response.text

def generate_mock_digest(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> str:
    """Generates a fallback mock digest if no API key is set (for testing)."""
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    return f"""# 🚀 Günlük Teknoloji, Donanım & Sağlık Bülteni
*Tarih: {today_str}* (Test Modu - Deneme Bülteni)

---

## 💡 1. Öne Çıkan Ürün & İş Fikirleri (Side Hustle & Business Ideas)
- **Toplanan Reddit Fikri Sayısı:** {len(reddit_posts)} adet gönderi incelendi.
- **Örnek Fikir (Donanım/Otomasyon):** ESP32 tabanlı enerji takip cihazları veya ev otomasyon kitleri kullanıcılar tarafından yoğun ilgi görüyor.
- **Değerlendirme:** Türkiye pazarında uygun maliyetli IoT enerji sensörleri ve mobil uygulama entegrasyonlu donanım paketleri ciddi bir ticari fırsat sunabilir.

---

## 🛠️ 2. Donanım, IoT & Otomasyon Trendleri (ESP32, Raspberry Pi, Arduino)
- Toplanan subreddit'lerde (`r/esp32`, `r/raspberrypi`, `r/arduino`) otomasyon ve mikrodenetleyici projeleri öne çıkıyor.
- **Proje Fikri:** Raspberry Pi ve Python kullanarak atölye veya ev için akıllı stok/envanter takip terminali oluşturma.

---

## 🩺 3. Sağlık & Medikal Teknolojilerindeki Son Gelişmeler (Medscape & Kardiyoloji)
- **Toplanan Haber Sayısı:** {len(rss_articles)} adet sağlık/kardiyoloji makalesi çekildi.
- Medscape Cardiology kaynaklarında son klinik araştırmalar ve giyilebilir medikal cihazların kardiyak takipte kullanımı inceleniyor.

---

## ⚡ 4. Günün Aksiyon İpuçları & İlham Notu
1. ESP32 veya Arduino ile küçük ölçekli bir sensor otomasyon projesi başlat.
2. Medscape kardiyoloji makalelerinden ilham alarak sağlık teknolojileri dikeyinde içerik veya ürün fikirleri tasarla.
3. r/sidehustle subreddit'indeki gerçek kullanıcı problemlerini otomasyon script'leri ile çözmeyi dene.
"""

def generate_digest_with_cerebras(prompt_content: str, api_key: str) -> str:
    """Generates digest using Cerebras Cloud API (Ultra-fast inference)."""
    import openai
    model = os.getenv("CEREBRAS_MODEL", "gemma-4-31b")
    logging.info(f"Generating summary with Cerebras Cloud model '{model}'...")
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.cerebras.ai/v1"
    )
    
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    system_prompt = SYSTEM_PROMPT_TR.format(date=today_str)
    
    models_to_try = [model, "gemma-4-31b", "gpt-oss-120b", "zai-glm-4.7"]
    # Filter duplicates while maintaining order
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]
    
    for m in models_to_try:
        try:
            logging.info(f"Attempting Cerebras inference with model '{m}'...")
            response = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Aşağıdaki verileri incele ve Türkçe bülteni oluştur:\n\n{prompt_content}"}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.warning(f"Cerebras model '{m}' failed: {e}")
            
    raise Exception("All Cerebras models failed.")

def generate_digest(rss_articles: List[Dict[str, Any]], reddit_posts: List[Dict[str, Any]]) -> str:
    """Main generation logic. Routes to Cerebras, OpenAI, Gemini, or fallback Mock."""
    prompt_content = format_data_for_llm(rss_articles, reddit_posts)
    
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if cerebras_key:
        try:
            return generate_digest_with_cerebras(prompt_content, cerebras_key)
        except Exception as e:
            logging.error(f"Cerebras API error: {e}. Falling back to OpenAI/Gemini...")

    if openai_key:
        try:
            return generate_digest_with_openai(prompt_content, openai_key)
        except Exception as e:
            logging.error(f"OpenAI error: {e}. Falling back to Gemini or Mock...")
            
    if gemini_key:
        try:
            return generate_digest_with_gemini(prompt_content, gemini_key)
        except Exception as e:
            logging.error(f"Gemini error: {e}. Falling back to Mock...")
            
    logging.warning("No valid API keys found. Using fallback test digest.")
    return generate_mock_digest(rss_articles, reddit_posts)

def convert_markdown_to_html(markdown_text: str) -> str:
    """Converts Markdown digest to a premium dark-themed HTML email body."""
    import re
    
    # Basic markdown parsing to styled HTML
    html_body = markdown_text
    
    # Convert Headers
    html_body = re.sub(r"^# (.*?)$", r'<h1 style="color: #6366f1; border-bottom: 2px solid #374151; padding-bottom: 8px; font-size: 24px;">\1</h1>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^## (.*?)$", r'<h2 style="color: #38bdf8; margin-top: 24px; font-size: 18px; font-weight: 600;">\1</h2>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^### (.*?)$", r'<h3 style="color: #f43f5e; margin-top: 16px; font-size: 16px;">\1</h3>', html_body, flags=re.MULTILINE)
    
    # Convert Bold and Italic
    html_body = re.sub(r"\*\*(.*?)\*\*", r'<strong style="color: #f3f4f6;">\1</strong>', html_body)
    html_body = re.sub(r"\*(.*?)\*", r'<em style="color: #9ca3af;">\1</em>', html_body)
    
    # Convert Lists
    html_body = re.sub(r"^- (.*?)$", r'<li style="margin-bottom: 8px; line-height: 1.6; color: #d1d5db;">\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^(\d+)\. (.*?)$", r'<li style="margin-bottom: 8px; line-height: 1.6; color: #d1d5db;">\2</li>', html_body, flags=re.MULTILINE)
    
    # Wrap lists in <ul>
    html_body = re.sub(r'((?:<li style=".*?">.*?</li>\n?)+)', r'<ul style="padding-left: 20px; margin: 12px 0;">\1</ul>', html_body)
    
    # Horizontal rules
    html_body = re.sub(r"^---$", r'<hr style="border: 0; border-top: 1px solid #374151; margin: 20px 0;" />', html_body, flags=re.MULTILINE)
    
    # Paragraph breaks
    paragraphs = html_body.split('\n\n')
    formatted_p = []
    for p in paragraphs:
        if not p.strip().startswith('<') and p.strip():
            formatted_p.append(f'<p style="line-height: 1.6; color: #d1d5db; margin: 10px 0;">{p.strip()}</p>')
        else:
            formatted_p.append(p)
    html_body = '\n'.join(formatted_p)

    template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Curator Daily News - Türkçe Bülten</title>
</head>
<body style="background-color: #0f172a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px; margin: 0;">
    <div style="max-width: 680px; margin: 0 auto; background-color: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
        <div style="text-align: center; padding-bottom: 15px; margin-bottom: 20px; border-bottom: 1px solid #334155;">
            <span style="background: linear-gradient(135deg, #6366f1, #a855f7); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; color: white; letter-spacing: 1px; text-transform: uppercase;">Curator Daily News</span>
        </div>
        
        {html_body}
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #334155; text-align: center; font-size: 12px; color: #64748b;">
            <p>Bu bülten GitHub Actions & AI tarafından otomatik olarak oluşturulmuştur.</p>
            <p>© {datetime.date.today().year} CuratorDailyNews Digest</p>
        </div>
    </div>
</body>
</html>"""
    return template

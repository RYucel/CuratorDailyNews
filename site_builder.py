import os
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_github_pages_site(html_digest: str, output_dir: str = "docs"):
    """Generates a static web portal in docs/index.html for GitHub Pages hosting."""
    os.makedirs(output_dir, exist_ok=True)
    index_path = os.path.join(output_dir, "index.html")
    
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    
    pages_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Curator Daily News | Ryucel</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-main: #0b0f19;
            --bg-card: #151c2c;
            --border-card: #26334d;
            --accent-purple: #8b5cf6;
            --accent-blue: #38bdf8;
            --accent-pink: #f43f5e;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        body {{
            background-color: var(--bg-main);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 40px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .header {{
            max-width: 800px;
            width: 100%;
            text-align: center;
            margin-bottom: 30px;
        }}

        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(56, 189, 248, 0.2));
            border: 1px solid rgba(139, 92, 246, 0.4);
            color: #a78bfa;
            font-size: 13px;
            font-weight: 600;
            padding: 6px 16px;
            border-radius: 30px;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }}

        .title {{
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 15px;
        }}

        .container {{
            max-width: 800px;
            width: 100%;
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }}

        .footer {{
            margin-top: 40px;
            text-align: center;
            color: var(--text-secondary);
            font-size: 13px;
        }}

        .footer a {{
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 500;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>

    <div class="header">
        <span class="badge">AI GÜNLÜK BÜLTEN RADARI</span>
        <h1 class="title">Curator Daily News</h1>
        <p class="subtitle">Teknoloji, Donanım, Otomasyon & Sağlık Gelişmeleri • Güncelleme: {today_str}</p>
    </div>

    <div class="container">
        {html_digest}
    </div>

    <div class="footer">
        <p>CuratorDailyNews &copy; {datetime.date.today().year} • Geliştirici: <a href="https://github.com/Ryucel" target="_blank">Ryucel</a></p>
    </div>

</body>
</html>"""
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(pages_html)
        
    logging.info(f"Built static GitHub Pages portal at '{index_path}'")
    return index_path

if __name__ == "__main__":
    build_github_pages_site("<h1>Test</h1>")

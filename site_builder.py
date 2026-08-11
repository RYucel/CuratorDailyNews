import os
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_github_pages_site(html_digest: str, output_dir: str = "docs"):
    """Generates static Editorial Intelligence Portal in docs/index.html for GitHub Pages."""
    os.makedirs(output_dir, exist_ok=True)
    index_path = os.path.join(output_dir, "index.html")
    
    # Read editorial CSS
    css_path = os.path.join("static", "styles.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
    pages_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Curator Daily News — Daily Intelligence Briefing</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        {css_content}
    </style>
</head>
<body>

    <header class="header-nav">
        <div class="header-left">
            <a href="/" class="header-brand">Curator Daily News</a>
            <span class="header-sub">Daily Intelligence Briefing</span>
        </div>
        <div class="header-right">
            <span class="header-timestamp">Updated {datetime.datetime.now().strftime('%H:%M')}</span>
        </div>
    </header>

    <main class="app-container">
        <div class="editorial-layout">
            <div class="feed-column">
                {html_digest}
            </div>

            <aside class="editorial-sidebar">
                <div class="sidebar-module">
                    <h4 class="sidebar-title">TRENDING</h4>
                    <ul class="sidebar-list">
                        <li class="sidebar-list-item"><span>AI Hardware</span> <span class="count">01</span></li>
                        <li class="sidebar-list-item"><span>Wearable Health</span> <span class="count">02</span></li>
                        <li class="sidebar-list-item"><span>Local Inference</span> <span class="count">03</span></li>
                        <li class="sidebar-list-item"><span>Ambient Audio</span> <span class="count">04</span></li>
                        <li class="sidebar-list-item"><span>ESP32 Automation</span> <span class="count">05</span></li>
                    </ul>
                </div>

                <div class="sidebar-module">
                    <h4 class="sidebar-title">TOP SOURCES</h4>
                    <ul class="sidebar-list">
                        <li class="sidebar-list-item"><span>Reddit</span> <span class="count">11</span></li>
                        <li class="sidebar-list-item"><span>Product Hunt</span> <span class="count">6</span></li>
                        <li class="sidebar-list-item"><span>Hacker News</span> <span class="count">6</span></li>
                        <li class="sidebar-list-item"><span>Medscape</span> <span class="count">7</span></li>
                    </ul>
                </div>
            </aside>
        </div>
    </main>

    <footer>
        <div>Curator Daily News &copy; {datetime.date.today().year} — Daily Intelligence Briefing</div>
        <div>Editor: <a href="https://github.com/Ryucel" target="_blank">Ryucel</a></div>
    </footer>

</body>
</html>"""
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(pages_html)
        
    logging.info(f"Built static Editorial GitHub Pages portal at '{index_path}'")
    return index_path

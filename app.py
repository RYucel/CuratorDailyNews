import os
import glob
import datetime
import logging
from flask import Flask, render_template, jsonify, request

from collectors import fetch_rss_articles, fetch_reddit_posts
from summarizer import generate_digest, convert_markdown_to_html
from notifier import save_local_files, send_email, send_telegram, send_notion
from site_builder import build_github_pages_site

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route("/")
def index():
    """Renders main dashboard."""
    return render_template("index.html")

@app.route("/api/digest/latest")
def get_latest_digest():
    """Returns the latest generated digest."""
    md_path = "digest_output.md"
    html_path = "digest_output.html"
    
    if os.path.exists(md_path) and os.path.exists(html_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(md_path)).strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({
            "status": "success",
            "markdown": md_content,
            "html": html_content,
            "last_updated": mtime
        })
    else:
        return jsonify({
            "status": "empty",
            "message": "Henüz bülten üretilmedi. 'Şimdi Bülten Üret' butonuna basarak yeni bir bülten oluşturabilirsiniz."
        })

@app.route("/api/digest/generate", methods=["POST"])
def generate_fresh_digest():
    """Triggers live data collection and LLM synthesis."""
    try:
        logging.info("Web Dashboard triggered live digest generation...")
        rss_articles = fetch_rss_articles()
        reddit_posts = fetch_reddit_posts()
        
        markdown_digest = generate_digest(rss_articles, reddit_posts)
        html_digest = convert_markdown_to_html(markdown_digest)
        
        md_path, html_path = save_local_files(markdown_digest, html_digest)
        build_github_pages_site(html_digest)
        
        # Automatically dispatch Telegram, Email and Notion if credentials exist
        today_str = datetime.date.today().strftime("%d.%m.%Y")
        subject = f"🚀 Günlük Teknoloji, Donanım & Sağlık Bülteni - {today_str}"
        send_telegram(markdown_digest)
        send_email(subject, html_digest, markdown_digest)
        send_notion(markdown_digest)
            
        return jsonify({
            "status": "success",
            "markdown": markdown_digest,
            "html": html_digest,
            "rss_count": len(rss_articles),
            "reddit_count": len(reddit_posts),
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logging.error(f"Error generating digest via API: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/live-feeds")
def get_live_feeds():
    """Returns raw live fetched feeds for inspect tab."""
    try:
        rss = fetch_rss_articles()
        reddit = fetch_reddit_posts()
        return jsonify({
            "status": "success",
            "rss": rss,
            "reddit": reddit
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/archive")
def get_archive_list():
    """Lists all archived daily digest files."""
    archive_dir = "digests"
    if not os.path.exists(archive_dir):
        return jsonify({"status": "success", "files": []})
        
    files = sorted(glob.glob(os.path.join(archive_dir, "digest_*.html")), reverse=True)
    file_list = []
    for fpath in files:
        fname = os.path.basename(fpath)
        date_part = fname.replace("digest_", "").replace(".html", "")
        file_list.append({
            "filename": fname,
            "date": date_part,
            "path": fpath
        })
    return jsonify({"status": "success", "files": file_list})

@app.route("/archive/<filename>")
def get_archived_digest(filename):
    """Returns content of a specific archived digest."""
    safe_name = os.path.basename(filename)
    filepath = os.path.join("digests", safe_name)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    else:
        return "Bülten bulunamadı", 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

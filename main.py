import os
import sys
import argparse
import datetime
import logging
from dotenv import load_dotenv

from collectors import fetch_rss_articles, fetch_reddit_posts, fetch_twitter_posts, fetch_github_sources
from summarizer import generate_editorial_data, render_editorial_html, render_editorial_markdown
from notifier import send_email, send_telegram, send_notion, save_local_files

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def run_pipeline(dry_run: bool = False):
    logging.info("Starting CuratorDailyNews Digest Pipeline...")
    load_dotenv()
    
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    subject = f"🚀 Curator Daily News Briefing - {today_str}"
    
    # 1. Collect Data across all Horizon sources
    rss_articles = fetch_rss_articles()
    reddit_posts = fetch_reddit_posts()
    twitter_posts = fetch_twitter_posts()
    github_items = fetch_github_sources()
    
    logging.info(f"Collected: {len(rss_articles)} RSS, {len(reddit_posts)} Reddit, {len(twitter_posts)} Twitter/X, {len(github_items)} GitHub.")
    
    # 2. Generate Editorial Digest via LLM
    from summarizer import generate_editorial_data, render_editorial_html, render_editorial_markdown
    editorial_data = generate_editorial_data(rss_articles, reddit_posts, twitter_posts, github_items)
    markdown_digest = render_editorial_markdown(editorial_data)
    html_digest = render_editorial_html(editorial_data)
    
    # 3. Save output to local files & Build GitHub Pages Portal
    md_path, html_path = save_local_files(markdown_digest, html_digest)
    from site_builder import build_github_pages_site
    build_github_pages_site(html_digest)
    
    if dry_run:
        logging.info("DRY-RUN mode enabled. Digest generated and saved to files, skipping notifications.")
        print("\n" + "="*50)
        print(markdown_digest[:800] + "\n...\n[Kısaltıldı. Tam metin digest_output.md ve digest_output.html dosyalarında.]")
        print("="*50 + "\n")
        return
        
    # 4. Dispatch Notifications
    email_sent = send_email(subject, html_digest, markdown_digest)
    telegram_sent = send_telegram(markdown_digest)
    notion_sent = send_notion(markdown_digest)
    
    logging.info(f"Pipeline completed! Email: {email_sent}, Telegram: {telegram_sent}, Notion: {notion_sent}")

def main():
    parser = argparse.ArgumentParser(description="CuratorDailyNews - Automated Turkish Tech & Health Daily Digest")
    parser.add_argument("--dry-run", action="store_true", help="Generate digest and save files without sending notifications")
    args = parser.parse_args()
    
    run_pipeline(dry_run=args.dry_run)

if __name__ == "__main__":
    main()

import os
import smtplib
import logging
import requests
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def send_email(subject: str, html_content: str, markdown_content: str) -> bool:
    """Sends HTML email via SMTP if configured."""
    smtp_server = os.getenv("SMTP_SERVER") or "smtp.gmail.com"
    smtp_port_raw = (os.getenv("SMTP_PORT") or "587").strip()
    smtp_port = int(smtp_port_raw) if smtp_port_raw.isdigit() else 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL") or sender_email
    
    if not sender_email or not sender_password or not receiver_email:
        logging.info("SMTP Email credentials not configured. Skipping email dispatch.")
        return False
        
    try:
        logging.info(f"Sending daily digest email to {receiver_email}...")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Curator Daily News <{sender_email}>"
        msg["To"] = receiver_email
        
        part_text = MIMEText(markdown_content, "plain", "utf-8")
        part_html = MIMEText(html_content, "html", "utf-8")
        
        msg.attach(part_text)
        msg.attach(part_html)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        logging.info("Email sent successfully!")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

def send_telegram(markdown_content: str) -> bool:
    """Sends daily digest message to a Telegram chat/channel via Bot API if configured."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logging.info("Telegram Bot credentials not configured. Skipping Telegram dispatch.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunk_size = 4000
    chunks = [markdown_content[i:i + chunk_size] for i in range(0, len(markdown_content), chunk_size)]
    
    logging.info(f"Sending daily digest to Telegram chat {chat_id} in {len(chunks)} chunk(s)...")
    success = True
    for idx, chunk in enumerate(chunks, 1):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code != 200:
                payload["parse_mode"] = ""
                res = requests.post(url, json=payload, timeout=10)
                
            if res.status_code == 200:
                logging.info(f"Telegram chunk {idx}/{len(chunks)} sent successfully!")
            else:
                logging.error(f"Failed to send Telegram chunk {idx}: {res.status_code}")
                success = False
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            success = False
            
    return success

def send_notion(markdown_content: str) -> bool:
    """Sends daily digest to Notion Database if token and database_id are configured."""
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_token or not database_id:
        logging.info("Notion credentials not configured (NOTION_TOKEN / NOTION_DATABASE_ID). Skipping Notion export.")
        return False
        
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": f"🚀 Daily Digest - {today_str}"}}
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": markdown_content[:2000]}}
                    ]
                }
            }
        ]
    }
    
    try:
        logging.info("Exporting daily digest page to Notion Database...")
        res = requests.post(url, headers=headers, json=payload, timeout=12)
        if res.status_code in [200, 201]:
            logging.info("Notion page created successfully!")
            return True
        else:
            logging.error(f"Notion API error: {res.status_code} {res.text}")
            return False
    except Exception as e:
        logging.error(f"Error exporting to Notion: {e}")
        return False

def save_local_files(markdown_content: str, html_content: str, output_dir: str = ".") -> Tuple[str, str]:
    """Saves generated markdown and HTML to disk and archive folder."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main outputs
    md_path = os.path.join(output_dir, "digest_output.md")
    html_path = os.path.join(output_dir, "digest_output.html")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Save archive entry under digests/
    archive_dir = os.path.join(output_dir, "digests")
    os.makedirs(archive_dir, exist_ok=True)
    today_filename = f"digest_{datetime.date.today().strftime('%Y-%m-%d')}.html"
    archive_path = os.path.join(archive_dir, today_filename)
    
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    logging.info(f"Saved digest local files and archived to '{archive_path}'")
    return md_path, html_path

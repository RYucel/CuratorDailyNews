import logging
import feedparser
import requests
from typing import List, Dict, Any
from config import RSS_FEEDS, SUBREDDITS, MAX_RSS_ITEMS_PER_FEED, MAX_REDDIT_POSTS_PER_SUB, USER_AGENT

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_rss_articles() -> List[Dict[str, Any]]:
    """Fetches latest articles from configured RSS feeds."""
    articles = []
    headers = {"User-Agent": USER_AGENT}
    
    for feed_info in RSS_FEEDS:
        url = feed_info["url"]
        feed_name = feed_info["name"]
        category = feed_info["category"]
        logging.info(f"Fetching RSS feed: {feed_name}...")
        
        try:
            # Fetch feed with headers
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch RSS {url}: HTTP {response.status_code}")
                continue
                
            parsed = feedparser.parse(response.content)
            entries = parsed.entries[:MAX_RSS_ITEMS_PER_FEED]
            
            for entry in entries:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                # Clean up HTML tags if simple
                summary_clean = summary[:300] + "..." if len(summary) > 300 else summary
                link = entry.get("link", "")
                published = entry.get("published", entry.get("updated", ""))
                
                if title:
                    articles.append({
                        "source": feed_name,
                        "category": category,
                        "title": title,
                        "summary": summary_clean,
                        "link": link,
                        "published": published
                    })
        except Exception as e:
            logging.error(f"Error fetching RSS feed '{feed_name}': {e}")
            
    logging.info(f"Total RSS articles fetched: {len(articles)}")
    return articles

def fetch_reddit_posts() -> List[Dict[str, Any]]:
    """Fetches top posts from configured subreddits via Reddit RSS feeds."""
    posts = []
    headers = {"User-Agent": USER_AGENT}
    
    for sub_info in SUBREDDITS:
        import time
        time.sleep(1.5)
        sub_name = sub_info["name"]
        category = sub_info["category"]
        
        rss_url = f"https://www.reddit.com/r/{sub_name}/top/.rss?t=day&limit={MAX_REDDIT_POSTS_PER_SUB}"
        logging.info(f"Fetching Subreddit r/{sub_name} via RSS...")
        
        try:
            res = requests.get(rss_url, headers=headers, timeout=12)
            if res.status_code == 429:
                # Try Google News search RSS for subreddit
                gnews_url = f"https://news.google.com/rss/search?q=site:reddit.com/r/{sub_name}&hl=en-US&gl=US&ceid=US:en"
                res = requests.get(gnews_url, headers=headers, timeout=12)
                
            if res.status_code != 200:
                logging.warning(f"Failed to fetch r/{sub_name} RSS: HTTP {res.status_code}")
                continue
                
            parsed = feedparser.parse(res.content)
            entries = parsed.entries[:MAX_REDDIT_POSTS_PER_SUB]
            
            for entry in entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("content", [{}])[0].get("value", "")).strip()
                
                # Basic text cleanup
                import re
                summary_text = re.sub(r'<[^>]+>', ' ', summary)
                summary_text = ' '.join(summary_text.split())
                summary_clean = summary_text[:400] + "..." if len(summary_text) > 400 else summary_text
                
                if title:
                    posts.append({
                        "subreddit": f"r/{sub_name}",
                        "category": category,
                        "title": title,
                        "text": summary_clean,
                        "score": 10, # RSS entries are top posts of the day
                        "comments_count": 0,
                        "url": link,
                        "permalink": link
                    })
        except Exception as e:
            logging.error(f"Error fetching subreddit 'r/{sub_name}': {e}")
            
    logging.info(f"Total Reddit posts fetched: {len(posts)}")
    return posts

if __name__ == "__main__":
    rss = fetch_rss_articles()
    reddit = fetch_reddit_posts()
    print(f"Sample RSS: {len(rss)} items, Sample Reddit: {len(reddit)} items")

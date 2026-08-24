import logging
import time
import re
import html
import feedparser
import requests
from typing import List, Dict, Any
from config import RSS_FEEDS, SUBREDDITS, TWITTER_ACCOUNTS, GITHUB_SOURCES, MAX_RSS_ITEMS_PER_FEED, MAX_REDDIT_POSTS_PER_SUB, MAX_TWITTER_POSTS_PER_USER, USER_AGENT

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
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch RSS {url}: HTTP {response.status_code}")
                continue
                
            parsed = feedparser.parse(response.content)
            entries = parsed.entries[:MAX_RSS_ITEMS_PER_FEED]
            
            for entry in entries:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                summary_text = re.sub(r'<[^>]+>', ' ', summary)
                summary_text = html.unescape(summary_text)
                summary_text = ' '.join(summary_text.split())
                summary_clean = summary_text[:300] + "..." if len(summary_text) > 300 else summary_text
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
        time.sleep(1.2)
        sub_name = sub_info["name"]
        category = sub_info["category"]
        
        rss_url = f"https://www.reddit.com/r/{sub_name}/top/.rss?t=day&limit={MAX_REDDIT_POSTS_PER_SUB}"
        logging.info(f"Fetching Subreddit r/{sub_name} via RSS...")
        
        try:
            res = requests.get(rss_url, headers=headers, timeout=12)
            if res.status_code == 429:
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
                
                summary_text = re.sub(r'<[^>]+>', ' ', summary)
                summary_text = ' '.join(summary_text.split())
                summary_clean = summary_text[:400] + "..." if len(summary_text) > 400 else summary_text
                
                if title:
                    posts.append({
                        "subreddit": f"r/{sub_name}",
                        "category": category,
                        "title": title,
                        "text": summary_clean,
                        "score": 10,
                        "comments_count": 0,
                        "url": link,
                        "permalink": link
                    })
        except Exception as e:
            logging.error(f"Error fetching subreddit 'r/{sub_name}': {e}")
            
    logging.info(f"Total Reddit posts fetched: {len(posts)}")
    return posts

def fetch_twitter_posts() -> List[Dict[str, Any]]:
    """Fetches latest tweets/posts from configured Twitter/X accounts (@tom_doerr, @cocktailpeanut, @aakashgupta)."""
    tweets = []
    headers = {"User-Agent": USER_AGENT}
    
    nitter_instances = [
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
        "https://nitter.x86-64.net"
    ]
    
    for account in TWITTER_ACCOUNTS:
        handle = account["handle"]
        name = account["name"]
        category = account["category"]
        logging.info(f"Fetching Twitter/X account @{handle}...")
        
        fetched = False
        # Try Nitter RSS instances first
        for instance in nitter_instances:
            rss_url = f"{instance}/{handle}/rss"
            try:
                res = requests.get(rss_url, headers=headers, timeout=6)
                if res.status_code == 200:
                    parsed = feedparser.parse(res.content)
                    entries = parsed.entries[:MAX_TWITTER_POSTS_PER_USER]
                    if entries:
                        for entry in entries:
                            title = entry.get("title", "").strip()
                            link = entry.get("link", f"https://x.com/{handle}")
                            summary = entry.get("summary", "").strip()
                            summary_clean = re.sub(r'<[^>]+>', ' ', summary)
                            
                            if title:
                                tweets.append({
                                    "handle": f"@{handle}",
                                    "name": name,
                                    "category": category,
                                    "title": f"Tweet by @{handle}: {title[:120]}",
                                    "text": summary_clean,
                                    "url": link
                                })
                        fetched = True
                        break
            except Exception:
                continue
                
        # Fallback to Google News Twitter search RSS
        if not fetched:
            logging.info(f"Nitter instances offline for @{handle}. Falling back to Google News search RSS...")
            gnews_url = f"https://news.google.com/rss/search?q=site:x.com/{handle}+OR+site:twitter.com/{handle}&hl=en-US&gl=US&ceid=US:en"
            try:
                res = requests.get(gnews_url, headers=headers, timeout=8)
                if res.status_code == 200:
                    parsed = feedparser.parse(res.content)
                    entries = parsed.entries[:MAX_TWITTER_POSTS_PER_USER]
                    for entry in entries:
                        title = entry.get("title", "").strip()
                        link = entry.get("link", f"https://x.com/{handle}")
                        if title:
                            tweets.append({
                                "handle": f"@{handle}",
                                "name": name,
                                "category": category,
                                "title": f"Tweet by @{handle}: {title}",
                                "text": title,
                                "url": link
                            })
            except Exception as e:
                logging.error(f"Error fetching Twitter @{handle}: {e}")
                
    logging.info(f"Total Twitter/X posts fetched: {len(tweets)}")
    return tweets

def fetch_github_sources() -> List[Dict[str, Any]]:
    """Fetches trending releases and repositories from GitHub."""
    github_items = []
    headers = {"User-Agent": USER_AGENT}
    
    for gsource in GITHUB_SOURCES:
        url = gsource["url"]
        logging.info(f"Fetching GitHub sources: {gsource['name']}...")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                parsed = feedparser.parse(res.content)
                entries = parsed.entries[:5]
                for entry in entries:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "")
                    if title:
                        github_items.append({
                            "source": "GitHub Trending",
                            "category": "GITHUB",
                            "title": title,
                            "summary": title,
                            "link": link
                        })
        except Exception as e:
            logging.error(f"Error fetching GitHub sources: {e}")
            
    logging.info(f"Total GitHub items fetched: {len(github_items)}")
    return github_items

if __name__ == "__main__":
    rss = fetch_rss_articles()
    reddit = fetch_reddit_posts()
    tweets = fetch_twitter_posts()
    gh = fetch_github_sources()
    print(f"RSS: {len(rss)}, Reddit: {len(reddit)}, Twitter: {len(tweets)}, GitHub: {len(gh)}")

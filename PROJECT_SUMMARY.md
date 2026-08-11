# 🗞️ Curator Daily News — Project Architecture & Executive Summary

**Repository:** `https://github.com/RYucel/CuratorDailyNews`  
**Author:** Rüştü Yücel (`github.com/Ryucel`)  
**Product Concept:** Editorial Intelligence Platform (Newspaper + Intelligence Briefing)  

---

## 🏛️ System Architecture

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                            MULTI-SOURCE INGESTION                       │
 │  • Medscape & Cardiology RSS (Google News Search RSS)                   │
 │  • Reddit Subreddits: r/sidehustle, r/business_ideas, r/automation,     │
 │    r/raspberrypi, r/esp32, r/arduino                                    │
 │  • Twitter / X Accounts: @tom_doerr, @cocktailpeanut, @aakashgupta      │
 │  • ProductHunt Daily Products & Hacker News Top Stories                 │
 │  • GitHub Trending & Release Announcements                              │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                          COLLECTOR ENGINE (collectors.py)               │
 │  • Rate-limit protected HTTP client with exponential delay              │
 │  • Nitter RSS with Google News Search RSS fallback for Twitter/X        │
 │  • Feedparser RSS & Reddit RSS fallback handlers                        │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                   CEREBRAS CLOUD AI INFERENCE (summarizer.py)           │
 │  • Primary LLM: Cerebras Cloud API (`gemma-4-31b`) ~3.6s ultra-fast     │
 │  • Fallback LLMs: OpenAI (`gpt-4o-mini`), Google Gemini (`gemini-2.0`) │
 │  • Structured JSON Output Parser (Executive Summary, Stats, Stories)   │
 │  • Deep Technical & Medical Detail Extraction + "WHY IT MATTERS"        │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                     DELIVERY & PORTAL DISTRIBUTION                      │
 │  1. Telegram Bot (@CuratorNewsRYBot -> Chat ID: 6563673916)             │
 │  2. Flask Web Dashboard (app.py -> http://127.0.0.1:5000)                │
 │  3. GitHub Pages Static Portal Generator (site_builder.py -> docs/)     │
 │  4. HTML Email SMTP Dispatcher & Notion API Exporter                    │
 │  5. GitHub Actions Daily CRON Workflow (.github/workflows/)             │
 └─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Map & Module Breakdown

| File Path | Description & Role |
| :--- | :--- |
| `config.py` | Source lists (RSS, Subreddits, Twitter/X, GitHub), fetching limits, and `SYSTEM_PROMPT_EDITORIAL` JSON prompt schema. |
| `collectors.py` | Multi-source ingestion routines (`fetch_rss_articles`, `fetch_reddit_posts`, `fetch_twitter_posts`, `fetch_github_sources`). |
| `summarizer.py` | Cerebras Cloud AI integration, JSON response parser, `render_editorial_html` and `render_editorial_markdown` formatters. |
| `notifier.py` | Delivery dispatchers (`send_telegram`, `send_email`, `send_notion`, `save_local_files`). |
| `site_builder.py` | Static site compiler producing `docs/index.html` for GitHub Pages hosting. |
| `app.py` | Flask Web Dashboard application serving `/`, `/api/digest/latest`, `/api/digest/generate`, `/api/live-feeds`, `/api/archive`. |
| `main.py` | CLI execution entry point (`python main.py` or `python main.py --dry-run`). |
| `test_telegram.py` | Standalone verification script for Telegram Bot notifications. |
| `setup_telegram_chat_id.py` | Auto-detection script for Telegram Chat ID. |
| `templates/index.html` | Editorial Intelligence Platform frontend template (Zero AI-slop, newspaper layout). |
| `static/styles.css` | Editorial design system (Dark mode `#0f1115`, 2-column layout, restrained `2px-4px` borders, no glowing cards). |
| `.github/workflows/daily_digest.yml` | Scheduled CRON job running daily at **08:00 AM TSI (05:00 UTC)**. |
| `.env` | Private environment secrets (`CEREBRAS_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). |
| `README.md` | User documentation and setup guide in Turkish. |

---

## 🎨 Editorial Design System Specifications

1. **Information Architecture:**
   - **Header (56–64px):** Brand title + subtitle (Left), Text-only navigation (*Today*, *Live Feed*, *Archive*) (Center), Timestamp + Actions (*Refresh*, *Generate Briefing*) (Right).
   - **Briefing Header:** Date (`11 AUGUST 2026`), 36px Title (`TODAY'S BRIEFING`), 18-20px Executive Summary (780px max reading width, no container box).
   - **At-a-Glance Stats Strip:** Compact column layout separated by subtle vertical lines (`12 STORIES | 5 HIGH SIGNAL | 3 OPPORTUNITIES | 4 TRENDS`).
   - **Main Feed (`TODAY'S SIGNAL`):** 760-820px reading width, story numbers (`01`, `02`), uppercase category & priority (`SAĞLIK · ● HIGH SIGNAL`), 22-25px semibold title, 16-17px summary, left-bordered `WHY IT MATTERS` section (`border-left: 2px solid #3157d5`), compact source metadata. Divided by thin `<hr class="story-divider">` lines.
   - **Right Sidebar (Desktop):** `TRENDING`, `TOP SOURCES`, `MOST INTERESTING` text modules.
2. **Color Palette (Dark Mode):**
   - Background: `#0f1115`
   - Surface: `#151922`
   - Text Primary: `#f1f2f4`
   - Text Secondary: `#a5aab4`
   - Borders: `#282d36`
   - Accent: Restrained blue `#3157d5`
   - **Zero AI-slop:** No glowing cards, no neon purple gradients, no floating containers, no glassmorphism.

---

## 🔑 Configured Secrets & Environment Variables

```env
CEREBRAS_API_KEY=csk-ynm3dnmxcrr4t55vtvnw9m3wwhytyj589f4kp62hyntk8k8m
CEREBRAS_MODEL=gemma-4-31b
TELEGRAM_BOT_TOKEN=8835416057:AAFDRN9xevdQItvpp-RRmb_ru7hdFCnysLM
TELEGRAM_CHAT_ID=6563673916
```

---

## 🚀 Roadmap for Next Update

1. **User Customization Panel:** Allow adding/removing custom Twitter handles and Subreddits directly from the Web Dashboard.
2. **Search & Tag Filtering:** Add instant client-side keyword search in the Archive tab.
3. **Multi-Model Compare:** Option to run side-by-side comparison between Cerebras `gemma-4-31b` and OpenAI `gpt-4o-mini`.
4. **Enhanced Notion Database Integration:** Map individual stories directly into separate rows in Notion databases with tags.

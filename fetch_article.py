"""
Pulls today's Dawn content:
- the latest editorial (used for the deep-dive summary / vocab / MCQ seed)
- a pool of recent Pakistan + World headlines (used to broaden the daily 50 MCQs
  and the hourly bulletin so they cover more than just one editorial)

Uses Dawn's official RSS feeds instead of scraping the homepage HTML, since
feeds are stable and don't break when Dawn changes its site design.
"""
import feedparser
import requests
from bs4 import BeautifulSoup
import config

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CSSPrepBot/1.0)"}


def _fetch_full_text(url: str) -> str:
    """Best-effort full article text extraction from a Dawn article page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "lxml")

        body = soup.find("div", class_="story__content") or soup.find("article")
        if body:
            paragraphs = [p.get_text(" ", strip=True) for p in body.find_all("p")]
        else:
            paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]

        text = "\n".join(p for p in paragraphs if len(p) > 30)
        return text.strip()
    except Exception as e:
        print(f"[fetch_full_text] failed for {url}: {e}")
        return ""


def get_latest_editorial() -> dict:
    """Returns {'title', 'link', 'summary', 'full_text'} for the newest editorial."""
    feed = feedparser.parse(config.DAWN_EDITORIAL_FEED)
    if not feed.entries:
        raise RuntimeError("No entries found in Dawn editorial feed.")

    entry = feed.entries[0]
    title = entry.get("title", "Untitled")
    link = entry.get("link", "")
    summary = entry.get("summary", "")

    full_text = _fetch_full_text(link) if link else ""
    if not full_text:
        full_text = summary  # fallback so the pipeline never breaks

    return {"title": title, "link": link, "summary": summary, "full_text": full_text}


def get_headline_pool(limit_per_feed: int = 15) -> list:
    """Pulls recent Pakistan + World + Home headlines for MCQ variety."""
    feeds = [config.DAWN_PAKISTAN_FEED, config.DAWN_WORLD_FEED, config.DAWN_HOME_FEED]
    headlines = []
    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries[:limit_per_feed]:
            headlines.append(
                {
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                }
            )
    return headlines


if __name__ == "__main__":
    art = get_latest_editorial()
    print(art["title"])
    print(art["full_text"][:500])

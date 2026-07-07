"""
Fetch Dawn articles safely.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CSSPrepBot/1.0)"
}


def _fetch_full_text(url: str) -> str:
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        body = (
            soup.find("div", class_="story__content")
            or soup.find("article")
        )

        paragraphs = []

        if body:
            paragraphs = body.find_all("p")
        else:
            paragraphs = soup.find_all("p")

        text = "\n".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 30
        )

        return text

    except Exception as e:

        print(f"Article fetch failed: {e}")

        return ""


def _parse_feed(feed_url):

    print(f"Checking RSS: {feed_url}")

    feed = feedparser.parse(feed_url)

    print("Entries:", len(feed.entries))

    return feed


def get_latest_editorial():

    feeds = [

        config.DAWN_EDITORIAL_FEED,

        config.DAWN_HOME_FEED,

        config.DAWN_PAKISTAN_FEED,

        config.DAWN_WORLD_FEED,

    ]

    for url in feeds:

        feed = _parse_feed(url)

        if len(feed.entries) == 0:
            continue

        entry = feed.entries[0]

        title = entry.get("title", "")

        link = entry.get("link", "")

        summary = entry.get("summary", "")

        full_text = ""

        if link:
            full_text = _fetch_full_text(link)

        if not full_text:
            full_text = summary

        return {
            "title": title,
            "link": link,
            "summary": summary,
            "full_text": full_text
        }

    raise RuntimeError(
        "No articles found in any Dawn RSS feed."
    )


def get_headline_pool(limit_per_feed=15):

    headlines = []

    feeds = [

        config.DAWN_HOME_FEED,

        config.DAWN_PAKISTAN_FEED,

        config.DAWN_WORLD_FEED,

    ]

    for feed_url in feeds:

        feed = _parse_feed(feed_url)

        for entry in feed.entries[:limit_per_feed]:

            headlines.append({

                "title": entry.get("title", ""),

                "summary": entry.get("summary", ""),

                "link": entry.get("link", "")

            })

    return headlines


if __name__ == "__main__":

    article = get_latest_editorial()

    print(article["title"])

    print(article["link"])

    print(article["full_text"][:500])

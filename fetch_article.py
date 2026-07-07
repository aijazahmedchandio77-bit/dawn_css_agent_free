"""
Fetch Dawn articles safely.
Works even if the Editorial RSS feed is empty.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CSSPrepBot/1.0)"
}


EDITORIAL_FEEDS = [
    getattr(config, "DAWN_EDITORIAL_FEED", ""),
    "https://www.dawn.com/feeds/editorial",
    "https://www.dawn.com/feeds/home",
    "https://www.dawn.com/feeds/latest",
]


def _fetch_full_text(url):

    if not url:
        return ""

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

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
            if len(p.get_text(strip=True)) > 20
        )

        return text.strip()

    except Exception as e:

        print("Full text failed:", e)

        return ""


def get_latest_editorial():

    for feed_url in EDITORIAL_FEEDS:

        if not feed_url:
            continue

        try:

            print("Trying:", feed_url)

            feed = feedparser.parse(feed_url)

            if not feed.entries:
                continue

            entry = feed.entries[0]

            title = entry.get(
                "title",
                "Untitled",
            )

            link = entry.get(
                "link",
                "",
            )

            summary = entry.get(
                "summary",
                "",
            )

            full_text = _fetch_full_text(link)

            if not full_text:
                full_text = summary

            return {
                "title": title,
                "link": link,
                "summary": summary,
                "full_text": full_text,
            }

        except Exception as e:

            print(
                f"Feed failed {feed_url}: {e}"
            )

    print("No editorial feed available.")

    return {
        "title": "Dawn Editorial Unavailable",
        "link": "",
        "summary": "Editorial feed unavailable today.",
        "full_text": "Editorial feed unavailable today.",
    }


def get_headline_pool(limit_per_feed=15):

    feeds = [
        getattr(config, "DAWN_PAKISTAN_FEED", ""),
        getattr(config, "DAWN_WORLD_FEED", ""),
        getattr(config, "DAWN_HOME_FEED", ""),
        "https://www.dawn.com/feeds/home",
        "https://www.dawn.com/feeds/latest",
    ]

    headlines = []

    seen = set()

    for feed_url in feeds:

        if not feed_url:
            continue

        try:

            parsed = feedparser.parse(feed_url)

            for entry in parsed.entries[:limit_per_feed]:

                title = entry.get("title", "")

                if title in seen:
                    continue

                seen.add(title)

                headlines.append(
                    {
                        "title": title,
                        "summary": entry.get(
                            "summary",
                            "",
                        ),
                        "link": entry.get(
                            "link",
                            "",
                        ),
                    }
                )

        except Exception as e:

            print(
                f"Headline feed failed: {e}"
            )

    return headlines


if __name__ == "__main__":

    article = get_latest_editorial()

    print(article["title"])

    print(article["link"])

    print(article["full_text"][:500])

    print()

    print("Headlines:", len(get_headline_pool()))

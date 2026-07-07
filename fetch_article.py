"""
fetch_article.py
Scrapes Dawn directly instead of using RSS.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

EDITORIAL_PAGE = "https://www.dawn.com/newspaper/editorial"

HOME_PAGE = "https://www.dawn.com/latest-news"


def clean(text):
    if not text:
        return ""
    return " ".join(text.split())


def fetch_html(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    r.raise_for_status()

    return BeautifulSoup(r.text, "html.parser")


def _fetch_full_text(url):

    try:

        soup = fetch_html(url)

        article = soup.find("article")

        if article:

            ps = article.find_all("p")

        else:

            ps = soup.find_all("p")

        text = "\n".join(
            clean(p.get_text())
            for p in ps
            if len(clean(p.get_text())) > 20
        )

        return text

    except Exception as e:

        print(e)

        return ""


def get_latest_editorial():

    try:

        soup = fetch_html(EDITORIAL_PAGE)

        link = soup.find("a", href=True)

        while link:

            href = link["href"]

            if href.startswith("/"):

                href = "https://www.dawn.com" + href

            if "/news/" in href:

                title = clean(link.get_text())

                summary = ""

                full = _fetch_full_text(href)

                if not full:
                    full = summary

                return {
                    "title": title,
                    "link": href,
                    "summary": summary,
                    "full_text": full,
                }

            link = link.find_next("a", href=True)

    except Exception as e:

        print(e)

    return {
        "title": "Editorial unavailable",
        "link": "",
        "summary": "",
        "full_text": "",
    }


def get_headline_pool(limit_per_feed=15):

    news = []

    try:

        soup = fetch_html(HOME_PAGE)

        links = soup.find_all("a", href=True)

        seen = set()

        for a in links:

            href = a["href"]

            title = clean(a.get_text())

            if len(title) < 20:
                continue

            if title in seen:
                continue

            seen.add(title)

            if href.startswith("/"):
                href = "https://www.dawn.com" + href

            if "/news/" not in href:
                continue

            news.append(
                {
                    "title": title,
                    "summary": "",
                    "link": href,
                }
            )

            if len(news) >= limit_per_feed:
                break

    except Exception as e:

        print(e)

    return news


if __name__ == "__main__":

    article = get_latest_editorial()

    print(article["title"])

    print(article["link"])

    print(article["full_text"][:1000])

    print()

    print(get_headline_pool())

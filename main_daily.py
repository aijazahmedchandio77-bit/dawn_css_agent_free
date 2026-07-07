"""
Runs once a day (scheduled by .github/workflows/daily.yml).

Pipeline:
1. Fetch today's Dawn editorial + a headline pool (Pakistan + World).
2. Ask Gemini for: English gist, Urdu gist, full summary, vocabulary, 50 MCQs.
3. Ask Gemini for CSS-relevant resource suggestions.
4. Build a PDF with the summary + vocab + 50 MCQs + answer key.
5. Send everything to Telegram: text package first, then the PDF.
"""
import traceback
import fetch_article
import ai_processor
import pdf_builder
import telegram_bot


def run():
    print("Fetching Dawn editorial + headline pool...")
    article = fetch_article.get_latest_editorial()
    headline_pool = fetch_article.get_headline_pool()

    print("Generating daily package with Gemini...")
    package = ai_processor.make_daily_package(article, headline_pool)

    print("Getting CSS-relevant resource suggestions...")
    css_resources = ai_processor.find_css_relevant_pdfs(article["title"])

    print("Building PDF...")
    pdf_path = pdf_builder.build_daily_pdf(article, package, css_resources)

    print("Sending to Telegram...")
    header = f"📰 DAWN Editorial: {article['title']}\n{article['link']}\n"
    telegram_bot.send_message(header)
    telegram_bot.send_message(f"🇬🇧 50-word gist (English):\n{package['english_gist_50_words']}")
    telegram_bot.send_message(f"🇵🇰 50-word gist (Urdu):\n{package['urdu_gist_50_words']}")
    telegram_bot.send_message(f"📄 Full Summary:\n{package['full_summary']}")

    vocab_lines = "\n".join(
        f"- {v['word']}: {v['meaning_english']} | Urdu: {v['meaning_urdu']}"
        for v in package.get("vocabulary", [])
    )
    telegram_bot.send_message(f"📚 Vocabulary:\n{vocab_lines}")

    if css_resources:
        telegram_bot.send_message(f"🔎 CSS-relevant resource suggestions:\n{css_resources}")

    telegram_bot.send_document(pdf_path, caption="📘 Today's 50 Current Affairs MCQs (Pakistan + International)")
    print("Done.")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        # Surface failures to Telegram too, so a broken run doesn't fail silently.
        err = traceback.format_exc()
        print(err)
        try:
            telegram_bot.send_message(f"⚠️ Daily agent run failed:\n{err[-1500:]}")
        except Exception:
            pass
        raise

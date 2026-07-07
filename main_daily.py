"""
Runs once a day (scheduled by .github/workflows/daily.yml).

Pipeline (deliberately split into small, independent steps so one failure
doesn't take down the whole run):
1. Fetch today's Dawn editorial + a headline pool (Pakistan + World).
2. Ask Gemini for summary + gists + vocabulary (1 small call).
3. Ask Gemini for 25 Pakistan MCQs (1 call).
4. Ask Gemini for 25 International MCQs (1 call).
5. Ask Gemini for CSS-relevant resource suggestions (1 small call).
6. Build a PDF with whatever MCQs succeeded + answer key.
7. Send everything to Telegram: text package first, then the PDF.

If any single step fails, the run keeps going with what it has and reports
the failure in Telegram, instead of crashing silently.
"""
import time
import traceback
import fetch_article
import ai_processor
import pdf_builder
import telegram_bot
import config


def run():
    print("Fetching Dawn editorial + headline pool...")
    article = fetch_article.get_latest_editorial()
    headline_pool = fetch_article.get_headline_pool()

    errors = []

    print("Generating summary + gists + vocabulary...")
    try:
        package = ai_processor.make_summary_and_vocab(article)
    except Exception as e:
        errors.append(f"summary/vocab step failed: {e}")
        package = {
            "english_gist_50_words": "(unavailable this run)",
            "urdu_gist_50_words": "(unavailable this run)",
            "full_summary": article.get("summary", "(unavailable this run)"),
            "vocabulary": [],
        }

    time.sleep(config.SECONDS_BETWEEN_CALLS)

    print("Generating Pakistan MCQs...")
    mcqs = []
    try:
        mcqs += ai_processor.make_mcq_batch("Pakistan", article, headline_pool, count=25)
    except Exception as e:
        errors.append(f"Pakistan MCQ batch failed: {e}")

    time.sleep(config.SECONDS_BETWEEN_CALLS)

    print("Generating International MCQs...")
    try:
        mcqs += ai_processor.make_mcq_batch("International", article, headline_pool, count=25)
    except Exception as e:
        errors.append(f"International MCQ batch failed: {e}")

    time.sleep(config.SECONDS_BETWEEN_CALLS)

    print("Getting CSS-relevant resource suggestions...")
    try:
        css_resources = ai_processor.find_css_relevant_resources(article["title"])
    except Exception as e:
        errors.append(f"resource suggestions failed: {e}")
        css_resources = ""

    print("Sending text package to Telegram...")
    header = f"📰 DAWN Editorial: {article['title']}\n{article['link']}\n"
    telegram_bot.send_message(header)
    telegram_bot.send_message(f"🇬🇧 50-word gist (English):\n{package['english_gist_50_words']}")
    telegram_bot.send_message(f"🇵🇰 50-word gist (Urdu):\n{package['urdu_gist_50_words']}")
    telegram_bot.send_message(f"📄 Full Summary:\n{package['full_summary']}")

    vocab_lines = "\n".join(
        f"- {v['word']}: {v['meaning_english']} | Urdu: {v['meaning_urdu']}"
        for v in package.get("vocabulary", [])
    )
    if vocab_lines:
        telegram_bot.send_message(f"📚 Vocabulary:\n{vocab_lines}")

    if css_resources:
        telegram_bot.send_message(f"🔎 CSS-relevant resource suggestions:\n{css_resources}")

    if mcqs:
        print(f"Building PDF with {len(mcqs)} MCQs...")
        pdf_path = pdf_builder.build_daily_pdf(article, package, mcqs, css_resources)
        telegram_bot.send_document(
            pdf_path,
            caption=f"📘 Today's {len(mcqs)} Current Affairs MCQs (Pakistan + International)",
        )
    else:
        telegram_bot.send_message("⚠️ No MCQs could be generated this run (see error log below).")

    if errors:
        telegram_bot.send_message("⚠️ Some steps had issues today:\n" + "\n".join(errors))

    print("Done.")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        err = traceback.format_exc()
        print(err)
        try:
            telegram_bot.send_message(f"⚠️ Daily agent run failed:\n{err[-1500:]}")
        except Exception:
            pass
        raise

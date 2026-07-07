"""
Runs once a day.

Daily CSS Agent
"""

import time
import traceback

import fetch_article
import ai_processor
import pdf_builder
import telegram_bot
import config


def run():
    errors = []

    print("Fetching Dawn editorial + headline pool...")

    # -------------------------------
    # Fetch article safely
    # -------------------------------
    try:
        article = fetch_article.get_latest_editorial()
    except Exception as e:
        errors.append(f"Editorial fetch failed: {e}")

        article = {
            "title": "Dawn Editorial Unavailable",
            "link": "",
            "summary": (
                "Today's Dawn editorial could not be fetched. "
                "The remaining pipeline will continue."
            ),
        }

    # -------------------------------
    # Fetch headlines safely
    # -------------------------------
    try:
        headline_pool = fetch_article.get_headline_pool()
    except Exception as e:
        errors.append(f"Headline pool failed: {e}")
        headline_pool = []

    print("Generating summary + vocabulary...")

    try:
        package = ai_processor.make_summary_and_vocab(article)

    except Exception as e:

        errors.append(f"Summary/Vocabulary failed: {e}")

        package = {
            "english_gist_50_words": "(Unavailable)",
            "urdu_gist_50_words": "(Unavailable)",
            "full_summary": article.get("summary", ""),
            "vocabulary": [],
        }

    time.sleep(config.SECONDS_BETWEEN_CALLS)

    mcqs = []

    print("Generating Pakistan MCQs...")

    try:
        mcqs.extend(
            ai_processor.make_mcq_batch(
                "Pakistan",
                article,
                headline_pool,
                count=25,
            )
        )

    except Exception as e:
        errors.append(f"Pakistan MCQs failed: {e}")

    time.sleep(config.SECONDS_BETWEEN_CALLS)

    print("Generating International MCQs...")

    try:
        mcqs.extend(
            ai_processor.make_mcq_batch(
                "International",
                article,
                headline_pool,
                count=25,
            )
        )

    except Exception as e:
        errors.append(f"International MCQs failed: {e}")

    time.sleep(config.SECONDS_BETWEEN_CALLS)

    print("Generating CSS resources...")

    try:
        css_resources = ai_processor.find_css_relevant_resources(
            article["title"]
        )

    except Exception as e:

        errors.append(f"CSS resources failed: {e}")
        css_resources = ""

    print("Sending Telegram messages...")

    try:

        telegram_bot.send_message(
            f"📰 DAWN Editorial\n\n"
            f"{article['title']}\n"
            f"{article['link']}"
        )

        telegram_bot.send_message(
            "🇬🇧 English Gist\n\n"
            + package["english_gist_50_words"]
        )

        telegram_bot.send_message(
            "🇵🇰 Urdu Gist\n\n"
            + package["urdu_gist_50_words"]
        )

        telegram_bot.send_message(
            "📄 Summary\n\n"
            + package["full_summary"]
        )

        vocab = package.get("vocabulary", [])

        if vocab:

            lines = []

            for item in vocab:

                lines.append(
                    f"• {item['word']}\n"
                    f"English: {item['meaning_english']}\n"
                    f"Urdu: {item['meaning_urdu']}"
                )

            telegram_bot.send_message(
                "📚 Vocabulary\n\n"
                + "\n\n".join(lines)
            )

        if css_resources:

            telegram_bot.send_message(
                "📖 CSS Resources\n\n"
                + css_resources
            )

    except Exception as e:

        errors.append(f"Telegram text failed: {e}")

    if mcqs:

        try:

            print(f"Building PDF ({len(mcqs)} MCQs)...")

            pdf = pdf_builder.build_daily_pdf(
                article,
                package,
                mcqs,
                css_resources,
            )

            telegram_bot.send_document(
                pdf,
                caption=f"📘 {len(mcqs)} Daily MCQs",
            )

        except Exception as e:

            errors.append(f"PDF failed: {e}")

    else:

        telegram_bot.send_message(
            "⚠️ No MCQs generated today."
        )

    if errors:

        telegram_bot.send_message(
            "⚠️ Daily Agent Report\n\n"
            + "\n".join(errors)
        )

    print("Finished.")


if __name__ == "__main__":

    try:

        run()

    except Exception:

        err = traceback.format_exc()

        print(err)

        try:

            telegram_bot.send_message(
                "⚠️ Daily Agent crashed\n\n"
                + err[-3000:]
            )

        except Exception:
            pass

        raise

"""
Runs every hour, 24x a day (scheduled by .github/workflows/hourly.yml).
Lightweight by design: just a fresh headline pool -> short bulletin -> Telegram.
No MCQ/PDF generation here (that stays in main_daily.py) to keep API usage sane.
"""
import traceback
import datetime
import fetch_article
import ai_processor
import telegram_bot


def run():
    headline_pool = fetch_article.get_headline_pool(limit_per_feed=8)
    bulletin = ai_processor.make_hourly_bulletin(headline_pool)
    now = datetime.datetime.now().strftime("%d %b, %I:%M %p")
    telegram_bot.send_message(f"⏰ Current Affairs Update — {now}\n\n{bulletin}")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        err = traceback.format_exc()
        print(err)
        try:
            telegram_bot.send_message(f"⚠️ Hourly agent run failed:\n{err[-1000:]}")
        except Exception:
            pass
        raise

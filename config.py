"""
Central config. All secrets come from environment variables, which are
injected by GitHub Actions from repo secrets (Settings -> Secrets -> Actions).
Never hardcode real tokens/keys in this file.
"""
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "6345421988")

# IMPORTANT: gemini-2.0-flash was deprecated by Google on 2026-06-01.
# Use gemini-2.5-flash for the daily job (heavier, but only ~4 calls/day)
# and gemini-2.5-flash-lite for the hourly job (light, but runs 24x/day and
# has a much higher free daily-request quota than full Flash).
# If Google renames/deprecates these again, check current free-tier model
# names at https://ai.google.dev/gemini-api/docs/models before swapping in.
MODEL_NAME = "gemini-2.5-flash"
MODEL_NAME_LITE = "gemini-2.5-flash-lite"

# Free tier is rate-limited (requests/minute and requests/day, varies by
# account). These sleeps keep us well under typical per-minute limits even
# on a restricted quota -- cheap insurance against 429 errors.
SECONDS_BETWEEN_CALLS = 6

# Dawn RSS feeds (official, stable, far more reliable than scraping the homepage HTML)
DAWN_EDITORIAL_FEED = "https://www.dawn.com/feeds/editorial"
DAWN_HOME_FEED = "https://www.dawn.com/feeds/home"
DAWN_PAKISTAN_FEED = "https://www.dawn.com/feeds/pakistan"
DAWN_WORLD_FEED = "https://www.dawn.com/feeds/world"

OUTPUT_DIR = "output"

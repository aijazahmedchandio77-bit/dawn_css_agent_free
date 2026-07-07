"""
Central configuration for the CSS AI Agent.

Loads configuration from GitHub Actions Secrets or local
environment variables.

Required GitHub Secrets:

- GEMINI_API_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
"""

import os

# ======================================================
# API KEYS
# ======================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ======================================================
# GEMINI MODEL
# ======================================================

# Change this if required
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

# ======================================================
# DAWN NEWS SOURCES
# ======================================================

# RSS feeds (change if Dawn updates them)
DAWN_FEEDS = [
    "https://www.dawn.com/feeds/home",
    "https://www.dawn.com/feeds/pakistan",
    "https://www.dawn.com/feeds/world",
    "https://www.dawn.com/feeds/business",
]

# ======================================================
# OUTPUT
# ======================================================

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======================================================
# REQUEST SETTINGS
# ======================================================

HTTP_TIMEOUT = 120
MAX_RETRIES = 5
RETRY_DELAY = 20

# ======================================================
# AI SETTINGS
# ======================================================

HOURLY_BULLETIN_TOKENS = 600
DAILY_SUMMARY_TOKENS = 1200
PDF_SEARCH_TOKENS = 400

TEMPERATURE = 0.4

# ======================================================
# VALIDATION
# ======================================================

missing = []

if not GEMINI_API_KEY:
    missing.append("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_CHAT_ID:
    missing.append("TELEGRAM_CHAT_ID")

if missing:
    raise RuntimeError(
        "Missing required environment variables: "
        + ", ".join(missing)
        + "\n\n"
        "Add them as GitHub Secrets:\n"
        "Settings → Secrets and variables → Actions"
    )

# ======================================================
# STARTUP INFO
# ======================================================

print("===================================")
print("CSS AI Agent Configuration Loaded")
print("Model:", MODEL_NAME)
print("Telegram Chat ID:", TELEGRAM_CHAT_ID)
print("Output Directory:", OUTPUT_DIR)
print("Feeds:", len(DAWN_FEEDS))
print("===================================")

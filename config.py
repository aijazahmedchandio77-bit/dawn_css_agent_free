"""
Central configuration for the CSS AI Agent.

Secrets are loaded from GitHub Actions Secrets:
Settings -> Secrets and variables -> Actions
"""

import os

# ======================================================
# API Keys
# ======================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6345421988")

# ======================================================
# Gemini Model
# ======================================================

MODEL_NAME = "gemini-2.0-flash"

# ======================================================
# Dawn RSS Feeds
# ======================================================

# Latest News
DAWN_HOME_FEED = "https://www.dawn.com/feeds/home"

# Pakistan
DAWN_PAKISTAN_FEED = "https://www.dawn.com/feeds/pakistan"

# World
DAWN_WORLD_FEED = "https://www.dawn.com/feeds/world"

# Editorial
DAWN_EDITORIAL_FEED = "https://www.dawn.com/feeds/editorials"

# ======================================================
# Output Directory
# ======================================================

OUTPUT_DIR = "output"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

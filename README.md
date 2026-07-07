# CSS/FIA Daily Dawn Agent (100% Free Version)

Automates daily CSS/FIA prep from Dawn newspaper and delivers it to your Telegram —
using only free services: GitHub Actions (free hosting/scheduling), Google Gemini
(free AI API), and Telegram (free bot).

## What it does

**Daily package (once a day, ~8:00 AM PKT):**
- Fetches today's Dawn editorial
- 50-word gist in English
- 50-word gist in Urdu
- Full ~180-word summary
- 8-10 important vocabulary words (CSS English relevance) with Urdu meanings
- CSS-relevant study resource suggestions
- 50 current affairs MCQs (mixed Pakistan + International), packaged into a
  PDF with an answer key, sent as a Telegram document

**Hourly ping (24x a day):**
- A short 5-6 line current affairs bulletin from the latest Pakistan + World headlines

---

## Step-by-step setup (about 15 minutes, no coding needed)

### Step 1 — Get a free Gemini API key
1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with any Google account
3. Click **Create API Key**
4. Copy the key somewhere safe — you'll paste it into GitHub in Step 6

No credit card, no billing setup required.

### Step 2 — Create your Telegram bot (skip if already done)
1. Open Telegram, search for **@BotFather**
2. Send `/newbot`, follow the prompts, name it anything
3. BotFather gives you a **bot token** — copy it
4. Open a chat with your new bot and send it any message (e.g. "hi") — this is required so the bot is allowed to message you back

### Step 3 — Create a GitHub repository
1. Go to **github.com** → sign up if you don't have an account
2. Click **+** (top right) → **New repository**
3. Repository name: e.g. `css-dawn-agent`
4. Visibility: **Public** (gives unlimited free GitHub Actions minutes)
5. Leave "Add README", "Add .gitignore", "Add license" all **off**
6. Click **Create repository**

### Step 4 — Upload all the files from this zip
On your new repo's page:
1. Click **Add file → Upload files**
2. From the extracted `dawn_css_agent` folder, select and drag in these 9 files:
   `config.py`, `fetch_article.py`, `ai_processor.py`, `pdf_builder.py`,
   `telegram_bot.py`, `main_daily.py`, `main_hourly.py`, `requirements.txt`, `README.md`
3. Click **Commit changes**

### Step 5 — Add the two workflow files
The `.github/workflows/` folder often doesn't drag-and-drop correctly through
the browser, so create these two files directly instead:

1. Click **Add file → Create new file**
2. In the filename box, type exactly: `.github/workflows/daily.yml`
   (typing the `/` makes GitHub create the folders automatically)
3. Open `daily.yml` from your extracted folder in a text editor, copy everything, paste it into the big text box on GitHub
4. Click **Commit changes**
5. Repeat for a second file: filename `.github/workflows/hourly.yml`, paste in the contents of your `hourly.yml`, **Commit changes**

Go back to your repo's main page and confirm you now see all 9 files plus a `.github` folder.

### Step 6 — Add your secrets
1. In your repo, click the **Settings** tab
2. Left sidebar → **Secrets and variables** → **Actions**
3. Click **New repository secret**, and add these one at a time (exact spelling matters):

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | the key from Step 1 |
| `TELEGRAM_BOT_TOKEN` | the token from Step 2 |
| `TELEGRAM_CHAT_ID` | `6345421988` |

### Step 7 — Turn on Actions
Click the **Actions** tab at the top of your repo. If you see a button like
"I understand my workflows, go ahead and enable them," click it.

### Step 8 — Test the daily workflow manually
1. In the **Actions** tab, click **"Daily CSS Current Affairs Package"** in the left list
2. Click **Run workflow** (dropdown) → **Run workflow** (confirm button)
3. Wait ~1-2 minutes, refresh the page — a run will appear; click it to watch the logs
4. Check your Telegram — you should receive the summary, gists, vocabulary, resource suggestions, and finally a PDF with 50 MCQs

### Step 9 — Test the hourly workflow manually
Same as Step 8, but choose **"Hourly Current Affairs Ping"**. Check Telegram for the short bulletin.

### Step 10 — Done, walk away
Once both manual tests succeed, you're finished. The daily workflow fires automatically
at 8 AM PKT, and the hourly one fires every hour, 24/7 — run entirely by GitHub's
servers, with nothing needing to stay on at your end.

---

## Troubleshooting

- **Red ❌ on a run in the Actions tab**: click into it, open the failing step, and read
  the error text. Copy/paste it back to me and I'll fix the code.
- **No Telegram message arrives but the run shows green**: make sure you sent your bot
  at least one message first (Step 2) — Telegram won't let a bot message you until you've
  messaged it.
- **Gemini API errors**: double-check the `GEMINI_API_KEY` secret has no extra spaces,
  and that you copied the full key from Google AI Studio.
- **Free tier limits**: Gemini's free tier has generous but real rate limits (per-minute
  and per-day request caps). 24 hourly calls + 1 heavier daily call comfortably fits
  within the free tier as of this writing — if Google changes the limits later, check
  https://ai.google.dev/gemini-api/docs/rate-limits.
- **GitHub pauses scheduled workflows after 60 days of zero repo activity.** Just make
  any small commit, or manually run a workflow, every couple of months to keep it alive.
- **Cron timing on GitHub is "best effort"** — during high load it can run a few minutes
  late. This is normal GitHub platform behavior.

## File overview

- `config.py` — reads secrets/settings from environment
- `fetch_article.py` — pulls today's editorial + headline pool via Dawn RSS feeds
- `ai_processor.py` — all Gemini API calls (summary, gists, vocab, 50 MCQs, resource suggestions)
- `pdf_builder.py` — builds the daily MCQ PDF
- `telegram_bot.py` — sends text/documents to your Telegram chat
- `main_daily.py` — orchestrates the once-a-day full package
- `main_hourly.py` — orchestrates the lightweight hourly bulletin
- `.github/workflows/daily.yml`, `.github/workflows/hourly.yml` — the schedules

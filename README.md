# CSS/FIA Daily Dawn Agent (Free, Quota-Aware Version)

Automates daily CSS/FIA prep from Dawn newspaper, delivered to Telegram — built
entirely on free services: GitHub Actions, Google Gemini free tier, Telegram bot.

## What changed in this version (fixing the crashes)

1. **Model name fix**: the previous version used `gemini-2.0-flash`, which
   Google deprecated on **June 1, 2026**. Every single call was failing.
   Now uses `gemini-2.5-flash` (daily) and `gemini-2.5-flash-lite` (hourly).
2. **Smaller calls**: asking for all 50 MCQs in one response could hit the
   output token limit mid-generation and produce broken JSON. Now the daily
   job makes 4 small, focused calls instead of 1 giant one:
   summary+vocab → 25 Pakistan MCQs → 25 International MCQs → resource suggestions.
3. **Automatic retry**: a `429` (rate limited) or `5xx` error now waits and
   retries with backoff instead of crashing the whole run.
4. **Partial-failure tolerance**: if one of the 4 steps fails, the run still
   sends you whatever succeeded, plus a note about what didn't — instead of
   sending nothing at all.
5. **Two models, two quota buckets**: the daily job uses `gemini-2.5-flash`
   (~4 calls/day — trivial for any tier). The hourly job uses
   `gemini-2.5-flash-lite`, which has a separate, higher daily quota than
   full Flash, appropriate since it runs 24 times a day.

Google's free-tier request limits change periodically and vary by account —
check your live limits any time at **https://aistudio.google.com** (Projects
→ your project → rate limits) if you want the exact current numbers.

---

## Step-by-step setup

### Step 1 — Get a free Gemini API key
1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with any Google account → **Create API Key** → copy it
3. No credit card needed

### Step 2 — Telegram bot
1. Message **@BotFather** on Telegram → `/newbot` → follow prompts → copy the token
2. Send your new bot any message (e.g. "hi") so it's allowed to message you back

### Step 3 — GitHub repo
1. github.com → **New repository** → name it, e.g. `css-dawn-agent`
2. Visibility: **Public** (unlimited free Actions minutes)
3. Leave README/.gitignore/license off → **Create repository**

### Step 4 — Upload the 9 main files
`Add file → Upload files` → drag in: `config.py`, `fetch_article.py`,
`ai_processor.py`, `pdf_builder.py`, `telegram_bot.py`, `main_daily.py`,
`main_hourly.py`, `requirements.txt`, `README.md` → **Commit changes**

### Step 5 — Create the two workflow files
Browser drag-and-drop often fails on the hidden `.github` folder, so create
these directly instead:
1. `Add file → Create new file` → filename: `.github/workflows/daily.yml`
   → paste in that file's contents → **Commit changes**
2. Repeat for `.github/workflows/hourly.yml`

Confirm on your repo's main page: 9 files + a `.github` folder should be visible.

### Step 6 — Add your secrets
`Settings → Secrets and variables → Actions → New repository secret`:

| Name | Value |
|---|---|
| `GEMINI_API_KEY` | key from Step 1 |
| `TELEGRAM_BOT_TOKEN` | token from Step 2 |
| `TELEGRAM_CHAT_ID` | `6345421988` |

### Step 7 — Enable Actions
**Actions** tab → click "I understand my workflows, go ahead and enable them" if prompted.

### Step 8 — Test both workflows manually
1. **Actions** tab → **"Daily CSS Current Affairs Package"** → **Run workflow** → **Run workflow**
2. Wait 1-3 minutes, refresh, click the run to watch logs live
3. Check Telegram: you should get the summary, gists, vocabulary, resource
   suggestions, and finally a PDF with 50 MCQs
4. Repeat for **"Hourly Current Affairs Ping"** → check Telegram for the short bulletin

### Step 9 — Done
Once both manual tests succeed, the schedules take over automatically —
daily at 8 AM PKT, hourly every hour, forever, run by GitHub's own servers.

---

## Troubleshooting

- **Still see "model not found" errors**: Google occasionally renames/retires
  free models. Open `config.py`, check `MODEL_NAME` / `MODEL_NAME_LITE`
  against the current list at https://ai.google.dev/gemini-api/docs/models,
  and update if needed.
- **A run shows red ❌**: click into it in the Actions tab, open the failing
  step, copy the error text, send it to me — I'll fix the code.
- **Telegram message never arrives but the run is green**: make sure you
  messaged your bot at least once first (Step 2).
- **Frequent 429 errors**: your account's free-tier quota may be lower than
  typical (Google adjusts this periodically). Check your live limits in AI
  Studio; if needed, I can reduce the daily MCQ count further (e.g. 15+15
  instead of 25+25) to fit a tighter quota — just tell me your numbers.
- **GitHub pauses scheduled workflows after 60 days of zero repo activity** —
  a small commit or manual run every couple of months keeps it alive.

## File overview

- `config.py` — secrets, model names, timing settings
- `fetch_article.py` — pulls today's editorial + headline pool via Dawn RSS feeds
- `ai_processor.py` — all Gemini calls: retry/backoff, split MCQ batches, robust JSON parsing
- `pdf_builder.py` — builds the daily MCQ PDF
- `telegram_bot.py` — sends text/documents to your Telegram chat
- `main_daily.py` — orchestrates the once-a-day package, tolerant of partial failures
- `main_hourly.py` — orchestrates the lightweight hourly bulletin
- `.github/workflows/daily.yml`, `.github/workflows/hourly.yml` — the schedules

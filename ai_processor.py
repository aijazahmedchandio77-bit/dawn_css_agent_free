"""
All AI calls, using Google Gemini's free API tier (no billing needed).
Get a free key at https://aistudio.google.com/app/apikey

Note: Gemini's free tier does not include live web-search grounding, so the
"CSS-relevant resources" feature below asks the model to recommend well-known,
stable CSS/FIA resource categories and official sites from its own knowledge,
rather than doing a live web search. This keeps everything on the free tier.
"""
import json
import re
import requests
import config

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{config.MODEL_NAME}:generateContent?key={config.GEMINI_API_KEY}"
)


def _call_gemini(prompt: str, max_tokens: int = 4000) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    resp = requests.post(GEMINI_URL, json=payload, timeout=90)
    if not resp.ok:
        raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text[:500]}")
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response shape: {json.dumps(data)[:500]}")


def make_daily_package(article: dict, headline_pool: list) -> dict:
    """
    One call that returns everything needed for the daily package:
    English gist, Urdu gist, full summary, vocabulary, and 50 MCQs, as JSON.
    """
    headlines_text = "\n".join(f"- {h['title']}: {h['summary']}" for h in headline_pool if h["title"])

    prompt = f"""You are helping a CSS/FIA exam candidate in Pakistan with daily preparation.

TODAY'S DAWN EDITORIAL:
Title: {article['title']}
Text: {article['full_text'][:6000]}

RECENT HEADLINE POOL (Pakistan + International, for MCQ variety):
{headlines_text[:6000]}

Produce a JSON object with EXACTLY these keys, and nothing else (no markdown fences, no preamble, no explanation, just raw JSON):

{{
  "english_gist_50_words": "exactly ~50 words summarizing the editorial's core argument, in English",
  "urdu_gist_50_words": "exactly ~50 words summarizing the same, written in Urdu script",
  "full_summary": "a 150-200 word English summary of the editorial covering its argument, context, and significance for CSS Current Affairs / Pakistan Affairs paper",
  "vocabulary": [
    {{"word": "difficult word from the article", "meaning_english": "concise English meaning", "meaning_urdu": "Urdu meaning"}}
  ],
  "mcqs": [
    {{
      "question": "MCQ text",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "answer": "A",
      "category": "Pakistan" or "International"
    }}
  ]
}}

Rules:
- "vocabulary" should have 8-10 entries of genuinely non-trivial words (CSS-exam level).
- "mcqs" must have EXACTLY 50 items, roughly half tagged "Pakistan" and half "International",
  based on the editorial plus the headline pool above, covering current affairs relevant to
  the CSS/FIA current affairs paper (institutions, policy, treaties, key figures, dates, geography).
- Do not fabricate facts not supported by the text; when unsure, write general-knowledge
  current-affairs MCQs consistent with the headlines given.
- Output must be valid JSON only, starting with {{ and ending with }}.
"""
    raw = _call_gemini(prompt, max_tokens=8000)
    raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def find_css_relevant_pdfs(article_title: str) -> str:
    """
    Free-tier friendly version: asks the model for well-known, stable CSS/FIA
    resource categories tied to the topic (FPSC site, standard reference
    books, official portals) rather than live web search results/links.
    """
    prompt = f"""A CSS/FIA exam candidate in Pakistan wants study resources related to
today's topic: "{article_title}".

List up to 5 well-known, genuinely useful and stable resource categories or
official sources (e.g. FPSC's own syllabus/past papers page, a relevant
ministry or SBP/PBS report page, a standard reference book chapter) that
would help them study this topic further for the CSS/FIA current affairs or
Pakistan affairs paper.

Format as a short plain-text list (max 5 items), each one line:
Resource name - why it's relevant - where to find it (site name, not a
guessed URL, since you don't have live internet access).
No markdown formatting, no extra commentary."""
    return _call_gemini(prompt, max_tokens=800).strip()


def make_hourly_bulletin(headline_pool: list) -> str:
    """Short current-affairs bulletin for the hourly Telegram ping."""
    headlines_text = "\n".join(f"- {h['title']}" for h in headline_pool if h["title"])[:3000]

    prompt = f"""From these recent Dawn headlines, write a compact current-affairs
bulletin for a CSS exam candidate: 5-6 bullet points, each one line, mixing
Pakistan and International news, plain text only (no markdown symbols like * or #).

Headlines:
{headlines_text}
"""
    return _call_gemini(prompt, max_tokens=500).strip()

"""
All AI calls, using Google Gemini's free API tier (no billing needed).
Get a free key at https://aistudio.google.com/app/apikey

Design choices made specifically to survive free-tier limits:
- Uses gemini-2.5-flash / gemini-2.5-flash-lite (gemini-2.0-flash is
  deprecated as of 2026-06-01 and will always fail).
- The old "one giant call for 50 MCQs" approach risked hitting the output
  token cap mid-JSON and crashing the parser. This version splits work into
  several SMALL calls (25 MCQs at a time, summary/vocab separately), each
  far less likely to be truncated.
- Every call goes through _call_gemini(), which retries on 429/5xx with
  exponential backoff instead of crashing the whole run immediately.
- JSON extraction is done by brace-balancing, not a naive regex, so partial
  wrapper text around the JSON doesn't break parsing.
"""
import json
import time
import requests
import config


def _gemini_url(model: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={config.GEMINI_API_KEY}"


def _extract_json_object(text: str) -> str:
    """Finds the first balanced {...} block in text, ignoring braces inside strings."""
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in model output.")
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    raise ValueError("Unbalanced JSON object in model output (likely truncated).")


def _call_gemini(prompt: str, model: str, max_tokens: int = 3000, max_retries: int = 4) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    url = _gemini_url(model)
    last_error = None

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, timeout=90)
        except requests.RequestException as e:
            last_error = e
            time.sleep(2 ** attempt)
            continue

        if resp.status_code == 429:
            # Rate limited -- back off and retry rather than crashing.
            wait = min(60, (2 ** attempt) * 5)
            print(f"[gemini] 429 rate limited, retrying in {wait}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            last_error = RuntimeError(f"429 after retries: {resp.text[:300]}")
            continue

        if resp.status_code >= 500:
            wait = min(30, (2 ** attempt) * 3)
            print(f"[gemini] server error {resp.status_code}, retrying in {wait}s")
            time.sleep(wait)
            last_error = RuntimeError(f"{resp.status_code}: {resp.text[:300]}")
            continue

        if not resp.ok:
            raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text[:500]}")

        data = resp.json()
        try:
            candidate = data["candidates"][0]
        except (KeyError, IndexError):
            raise RuntimeError(f"No candidates in Gemini response: {json.dumps(data)[:500]}")

        finish_reason = candidate.get("finishReason", "")
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)

        if not text.strip():
            raise RuntimeError(f"Empty Gemini response (finishReason={finish_reason}): {json.dumps(data)[:500]}")

        if finish_reason == "MAX_TOKENS":
            print(f"[gemini] warning: response hit MAX_TOKENS, may be truncated")

        return text

    raise RuntimeError(f"Gemini call failed after {max_retries} attempts: {last_error}")


def _call_gemini_json(prompt: str, model: str, max_tokens: int = 3000) -> dict:
    raw = _call_gemini(prompt, model=model, max_tokens=max_tokens)
    json_str = _extract_json_object(raw)
    return json.loads(json_str)


def make_summary_and_vocab(article: dict) -> dict:
    """Small, focused call: gists + summary + vocabulary only (no MCQs)."""
    prompt = f"""You are helping a CSS/FIA exam candidate in Pakistan with daily preparation.

TODAY'S DAWN EDITORIAL:
Title: {article['title']}
Text: {article['full_text'][:5000]}

Produce a JSON object with EXACTLY these keys, nothing else (no markdown fences, no preamble):

{{
  "english_gist_50_words": "exactly ~50 words summarizing the editorial's core argument, in English",
  "urdu_gist_50_words": "exactly ~50 words summarizing the same, written in Urdu script",
  "full_summary": "a 150-200 word English summary of the editorial covering its argument, context, and significance for CSS Current Affairs / Pakistan Affairs paper",
  "vocabulary": [
    {{"word": "difficult word from the article", "meaning_english": "concise English meaning", "meaning_urdu": "Urdu meaning"}}
  ]
}}

"vocabulary" should have 8-10 entries of genuinely non-trivial, CSS-exam-level words.
Output must be valid JSON only, starting with {{ and ending with }}."""
    return _call_gemini_json(prompt, model=config.MODEL_NAME, max_tokens=2500)


def make_mcq_batch(category: str, article: dict, headline_pool: list, count: int = 25) -> list:
    """
    Generates one batch of MCQs for a single category (Pakistan or International).
    Kept small and single-purpose so it's very unlikely to get truncated.
    """
    headlines_text = "\n".join(
        f"- {h['title']}: {h['summary']}" for h in headline_pool if h["title"]
    )[:4000]

    prompt = f"""You are writing {count} current-affairs MCQs for a CSS/FIA exam
candidate in Pakistan, category: {category} current affairs.

CONTEXT (today's editorial + recent headlines):
Editorial title: {article['title']}
Editorial excerpt: {article['full_text'][:1500]}

Recent headlines:
{headlines_text}

Produce a JSON object with EXACTLY this shape, nothing else:

{{
  "mcqs": [
    {{
      "question": "MCQ text",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "answer": "A",
      "category": "{category}"
    }}
  ]
}}

Rules:
- "mcqs" must have EXACTLY {count} items, all category "{category}".
- Base them on the context above plus general CSS/FIA-relevant {category} current
  affairs knowledge (institutions, policy, treaties, key figures, dates, geography).
- Do not fabricate specific facts not supported by the text; for anything not in
  the context, write general-knowledge current-affairs MCQs of the right category.
- Output must be valid JSON only, starting with {{ and ending with }}."""

    result = _call_gemini_json(prompt, model=config.MODEL_NAME, max_tokens=4000)
    return result.get("mcqs", [])


def find_css_relevant_resources(article_title: str) -> str:
    """
    Free-tier friendly version: asks the model for well-known, stable CSS/FIA
    resource categories tied to the topic, rather than live web search.
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
    return _call_gemini(prompt, model=config.MODEL_NAME, max_tokens=600).strip()


def make_hourly_bulletin(headline_pool: list) -> str:
    """Short current-affairs bulletin for the hourly Telegram ping. Uses the
    lighter/higher-quota model since this runs 24x a day."""
    headlines_text = "\n".join(f"- {h['title']}" for h in headline_pool if h["title"])[:2500]

    prompt = f"""From these recent Dawn headlines, write a compact current-affairs
bulletin for a CSS exam candidate: 5-6 bullet points, each one line, mixing
Pakistan and International news, plain text only (no markdown symbols like * or #).

Headlines:
{headlines_text}
"""
    return _call_gemini(prompt, model=config.MODEL_NAME_LITE, max_tokens=400).strip()

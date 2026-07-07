import json
import time
import requests
import config

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{config.MODEL_NAME}:generateContent?key={config.GEMINI_API_KEY}"
)


def _call_gemini(prompt, max_tokens=500):

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": max_tokens
        }
    }

    for attempt in range(3):

        response = requests.post(
            GEMINI_URL,
            json=payload,
            timeout=90
        )

        if response.status_code == 200:

            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"]

        elif response.status_code == 429:

            print(f"Rate limit reached. Waiting 60 seconds... ({attempt+1}/3)")

            time.sleep(60)

            continue

        else:

            raise RuntimeError(
                f"Gemini Error {response.status_code}\n{response.text}"
            )

    raise RuntimeError("Gemini quota exceeded after 3 retries.")


def make_daily_package(article, headline_pool):

    prompt = f"""
Read this article carefully.

Title:
{article['title']}

Article:
{article['full_text'][:800]}

Return ONLY valid JSON:

{{
"english_summary":"",
"vocabulary":[
{{"word":"","english":"","urdu":""}}
],
"mcqs":[
{{"question":"","A":"","B":"","C":"","D":"","answer":""}}
]
}}

Rules:

English Summary:
100 words

Vocabulary:
10 difficult words

MCQs:
10 current affairs MCQs
"""

    text = _call_gemini(prompt, max_tokens=1000)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise RuntimeError("Gemini did not return valid JSON.")

    return json.loads(text[start:end+1])


def make_hourly_bulletin(headline_pool):

    headlines = "\n".join(
        h["title"] for h in headline_pool[:8]
    )

    prompt = f"""
Summarize these headlines into five short bullet points.

{headlines}
"""

    return _call_gemini(prompt, max_tokens=400)


def find_css_relevant_pdfs(topic):

    prompt = f"""
Suggest five official CSS study resources related to:

{topic}

Return plain text only.
"""

    return _call_gemini(prompt, max_tokens=300)

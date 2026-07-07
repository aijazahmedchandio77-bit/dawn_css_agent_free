import json
import requests
import config

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{config.MODEL_NAME}:generateContent?key={config.GEMINI_API_KEY}"
)


def _call_gemini(prompt):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }

    response = requests.post(GEMINI_URL, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(response.text)

    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]


def make_daily_package(article, headline_pool):

    prompt = f"""
Read this article and return JSON only.

Title:
{article['title']}

Article:
{article['full_text'][:2000]}

Return this JSON:

{{
"english_summary":"",
"urdu_summary":"",
"vocabulary":[
{{"word":"","english":"","urdu":""}}
],
"mcqs":[
{{"question":"","A":"","B":"","C":"","D":"","answer":""}}
]
}}

Rules:

- English summary: about 100 words
- Urdu summary: about 100 words
- Vocabulary: 10 words
- MCQs: 10 only
"""

    text = _call_gemini(prompt)

    start = text.find("{")
    end = text.rfind("}")

    return json.loads(text[start:end+1])


def make_hourly_bulletin(headline_pool):

    headlines = "\n".join(
        h["title"] for h in headline_pool[:10]
    )

    prompt = f"""
Summarize these headlines into 5 short bullet points.

{headlines}
"""

    return _call_gemini(prompt)


def find_css_relevant_pdfs(topic):

    prompt = f"""
Suggest five official CSS study resources for:

{topic}
"""

    return _call_gemini(prompt)

"""
Builds a clean PDF containing:
- Today's article title + full summary + vocabulary
- current affairs MCQs (Pakistan + International), with an answer key at the end
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
)
import config


def build_daily_pdf(article: dict, package: dict, mcqs: list, css_resources: str) -> str:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(config.OUTPUT_DIR, f"css_current_affairs_{date_str}.pdf")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["BodyText"], spaceAfter=8, leading=15)
    urdu_body = ParagraphStyle("UrduBody", parent=styles["BodyText"], spaceAfter=8, leading=18)
    mcq_style = ParagraphStyle("MCQ", parent=styles["BodyText"], spaceBefore=6, spaceAfter=2, leading=14)
    option_style = ParagraphStyle("Option", parent=styles["BodyText"], leftIndent=14, spaceAfter=1)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm,
                             leftMargin=2*cm, rightMargin=2*cm)
    story = []

    story.append(Paragraph(f"CSS/FIA Daily Current Affairs — {date_str}", title_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Today's Editorial", h2))
    story.append(Paragraph(article["title"], styles["Heading3"]))
    story.append(Paragraph(package["full_summary"], body))

    story.append(Paragraph("50-Word Gist (English)", h2))
    story.append(Paragraph(package["english_gist_50_words"], body))

    story.append(Paragraph("50-Word Gist (Urdu)", h2))
    story.append(Paragraph(package["urdu_gist_50_words"], urdu_body))

    story.append(Paragraph("Important Vocabulary", h2))
    vocab_items = [
        ListItem(Paragraph(
            f"<b>{v['word']}</b> — {v['meaning_english']} (Urdu: {v['meaning_urdu']})", body))
        for v in package.get("vocabulary", [])
    ]
    if vocab_items:
        story.append(ListFlowable(vocab_items, bulletType="bullet"))

    if css_resources:
        story.append(Paragraph("CSS-Relevant Resource Suggestions", h2))
        for line in css_resources.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), body))

    story.append(PageBreak())
    story.append(Paragraph(f"Current Affairs MCQs — {len(mcqs)} Questions (Pakistan + International)", h2))

    answer_key = []
    for idx, mcq in enumerate(mcqs, start=1):
        story.append(Paragraph(f"{idx}. [{mcq.get('category','')}] {mcq['question']}", mcq_style))
        for key in ["A", "B", "C", "D"]:
            opt = mcq.get("options", {}).get(key, "")
            story.append(Paragraph(f"{key}) {opt}", option_style))
        answer_key.append(f"{idx}-{mcq.get('answer','?')}")

    story.append(PageBreak())
    story.append(Paragraph("Answer Key", h2))
    story.append(Paragraph("   ".join(answer_key), body))

    doc.build(story)
    return filepath

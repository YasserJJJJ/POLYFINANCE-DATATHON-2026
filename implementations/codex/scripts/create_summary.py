#!/usr/bin/env python3
"""Typeset docs/one-page.md as a single-page, text-preserving A4 summary.

Run from the project root with:
    .venv/bin/python scripts/create_summary.py

Dependencies: reportlab, pypdf. Poppler's pdftoppm renders the review image.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from html import escape
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/one-page.md"
OUTPUT = ROOT / "output/pdf/AlphaForge_resume.pdf"
SCREEN = ROOT / "artifacts/screens/resume.png"

PAPER = HexColor("#f5f5ef")
INK = HexColor("#20322c")
DEEP = HexColor("#172b26")
GREEN = HexColor("#2a6b51")
MUTED = HexColor("#617268")
LINE = HexColor("#d8dfd4")
LIME = HexColor("#d8ecaa")


def normalize(text: str) -> str:
    """Preserve source wording; use portable spaces and ASCII hyphens."""
    text = text.replace("\u00a0", " ").replace("\u202f", " ")
    text = re.sub("[\u2010-\u2015\u2212]", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def rich_text(text: str) -> str:
    escaped = escape(normalize(text))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)


def plain_text(text: str) -> str:
    return normalize(text).replace("**", "").removeprefix("# ").strip()


def draw_paragraph(pdf, text, style, x, top, width):
    paragraph = Paragraph(rich_text(text), style)
    _, height = paragraph.wrap(width, A4[1])
    paragraph.drawOn(pdf, x, top - height)
    return top - height


def height_for(text, style, width):
    paragraph = Paragraph(rich_text(text), style)
    return paragraph.wrap(width, A4[1])[1]


def create_pdf():
    blocks = [
        normalize(block)
        for block in re.split(r"\n\s*\n", SOURCE.read_text())
        if block.strip()
    ]
    if len(blocks) != 9 or not blocks[0].startswith("# "):
        raise ValueError("Expected a title, introduction, six paragraphs and conclusion.")
    title = plain_text(blocks[0])
    brand, subtitle = title.split(" - ", 1)
    introduction, *body, conclusion = blocks[1:]

    page_width, page_height = A4
    margin = 44
    width = page_width - 2 * margin
    top = page_height - 50

    intro_style = ParagraphStyle(
        "Intro",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16.5,
        textColor=GREEN,
        alignment=TA_LEFT,
        splitLongWords=False,
    )
    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=12,
        leading=16.7,
        textColor=INK,
        alignment=TA_LEFT,
        splitLongWords=False,
        allowWidows=False,
        allowOrphans=False,
    )
    conclusion_style = ParagraphStyle(
        "Conclusion",
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=PAPER,
        splitLongWords=False,
    )
    title_height = 77
    intro_height = height_for(introduction, intro_style, width)
    paragraph_gap = 12
    body_height = sum(height_for(block, body_style, width) for block in body)
    body_height += paragraph_gap * (len(body) - 1)
    conclusion_height = height_for(conclusion, conclusion_style, width - 36) + 30
    final_bottom = top - title_height - intro_height - 28 - body_height - 22 - conclusion_height
    if final_bottom < 65:
        raise ValueError(
            f"Source does not fit legibly on one page: final bottom {final_bottom:.1f} pt."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    pdf.setTitle(title)
    pdf.setAuthor("AlphaForge")
    pdf.setSubject("Résumé du prototype AlphaForge")
    pdf.setCreator("AlphaForge - ReportLab")

    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, page_width, page_height, stroke=0, fill=1)
    pdf.setFillColor(DEEP)
    pdf.rect(0, page_height - 9, page_width, 9, stroke=0, fill=1)

    pdf.setFillColor(GREEN)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, top, brand)
    pdf.setFillColor(DEEP)
    pdf.setFont("Times-Roman", 29)
    pdf.drawString(margin, top - 37, subtitle[0].upper() + subtitle[1:])
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.6)
    pdf.line(margin, top - 55, page_width - margin, top - 55)

    cursor = top - title_height
    cursor = draw_paragraph(pdf, introduction, intro_style, margin, cursor, width)
    cursor -= 28
    for index, block in enumerate(body):
        cursor = draw_paragraph(pdf, block, body_style, margin, cursor, width)
        if index < len(body) - 1:
            cursor -= paragraph_gap

    cursor -= 22
    pdf.setFillColor(DEEP)
    pdf.roundRect(margin, cursor - conclusion_height, width, conclusion_height, 7, stroke=0, fill=1)
    pdf.setFillColor(LIME)
    pdf.rect(margin, cursor - conclusion_height + 12, 3, conclusion_height - 24, stroke=0, fill=1)
    draw_paragraph(pdf, conclusion, conclusion_style, margin + 18, cursor - 15, width - 36)

    pdf.setStrokeColor(LINE)
    pdf.line(margin, 44, page_width - margin, 44)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(margin, 30, "AlphaForge  /  Résumé du projet")
    pdf.drawRightString(page_width - margin, 30, "1")
    pdf.showPage()
    pdf.save()

    reader = PdfReader(OUTPUT)
    if len(reader.pages) != 1:
        raise AssertionError("The PDF must contain exactly one page.")
    extracted = normalize(reader.pages[0].extract_text())
    for block in blocks[1:]:
        if plain_text(block) not in extracted:
            raise AssertionError(f"Source paragraph missing or altered: {plain_text(block)[:80]}")
    print(f"Created {OUTPUT}; 1 A4 page; complete source paragraphs verified.")
    print(f"Body size: {body_style.fontSize} pt; content bottom: {final_bottom:.1f} pt.")


def render():
    executable = shutil.which("pdftoppm")
    if not executable:
        raise RuntimeError("pdftoppm is required to render the review image.")
    SCREEN.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [executable, "-png", "-r", "150", "-singlefile", str(OUTPUT), str(SCREEN.with_suffix(""))],
        check=True,
    )
    print(f"Rendered {SCREEN}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-render", action="store_true")
    arguments = parser.parse_args()
    create_pdf()
    if not arguments.no_render:
        render()

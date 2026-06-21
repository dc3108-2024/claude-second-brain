#!/usr/bin/env python3
"""
build_8020_pdf.py — render an 80/20 reference PDF from structured JSON content.

Usage:
  python3 build_8020_pdf.py --data content.json --output out.pdf \
      --title "80/20: My Doc" --source "Original: My Doc — Author"

JSON schema (content.json):
{
  "title":  "80/20: ...",
  "source": "Original: ...",
  "sections": [
    {"heading": "...", "type": "prose",    "content": "..."},
    {"heading": "...", "type": "bullets",  "content": ["...", "..."]},
    {"heading": "...", "type": "numbered", "content": ["...", "..."]},
    {"heading": "...", "type": "table",    "headers": [...], "rows": [[...], ...]},
    {"heading": "...", "type": "code",     "content": "..."},
    {"heading": "...", "type": "warning",  "content": "..."}
  ]
}
"""
import sys, json, argparse, textwrap
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Preformatted
)

W, H = A4
ML = MR = 18*mm
MT = MB = 14*mm

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#0F2B5B")
TEAL   = colors.HexColor("#00A9A5")
ORANGE = colors.HexColor("#F7941D")
RED    = colors.HexColor("#C0392B")
GREY   = colors.HexColor("#4A4A4A")
LGREY  = colors.HexColor("#F4F6F9")
DGREY  = colors.HexColor("#DDDDDD")
WHITE  = colors.white
CODE_BG = colors.HexColor("#1E1E2E")
CODE_FG = colors.HexColor("#CDD6F4")

def S(name, **kw):
    return ParagraphStyle(name, **kw)

# ── Styles ────────────────────────────────────────────────────────────────────
cover_title  = S("ct", fontSize=28, textColor=WHITE, fontName="Helvetica-Bold",
                 alignment=TA_CENTER, leading=34)
cover_sub    = S("cs", fontSize=11, textColor=TEAL, fontName="Helvetica",
                 alignment=TA_CENTER, leading=16)
cover_meta   = S("cm", fontSize=8, textColor=colors.HexColor("#8899AA"),
                 fontName="Helvetica", alignment=TA_CENTER, leading=12)
sec_hdr      = S("sh", fontSize=13, textColor=WHITE, fontName="Helvetica-Bold",
                 alignment=TA_LEFT, leading=17)
prose_style  = S("ps", fontSize=9, textColor=GREY, fontName="Helvetica",
                 alignment=TA_LEFT, leading=14, spaceBefore=2)
bullet_style = S("bs", fontSize=9, textColor=GREY, fontName="Helvetica",
                 alignment=TA_LEFT, leading=13, leftIndent=14, firstLineIndent=-8)
num_style    = S("ns", fontSize=9, textColor=GREY, fontName="Helvetica",
                 alignment=TA_LEFT, leading=13, leftIndent=14, firstLineIndent=-8)
warn_style   = S("ws", fontSize=9, textColor=colors.HexColor("#7B1A1A"),
                 fontName="Helvetica", alignment=TA_LEFT, leading=13, leftIndent=8)
tbl_hdr      = S("th", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
                 alignment=TA_LEFT, leading=11)
tbl_cell     = S("tc", fontSize=8, textColor=GREY, fontName="Helvetica",
                 alignment=TA_LEFT, leading=11)
footer_style = S("fs", fontSize=7, textColor=GREY, fontName="Helvetica",
                 alignment=TA_CENTER, leading=10)

def section_banner(text, colour=NAVY):
    data = [[Paragraph(text, sec_hdr)]]
    tbl = Table(data, colWidths=[W - ML - MR])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colour),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    return tbl

def rule(c=TEAL, t=0.8):
    return HRFlowable(width="100%", thickness=t, color=c, spaceBefore=3, spaceAfter=3)

def bullet(text, colour=TEAL):
    hex_col = colour.hexval()[2:]
    return Paragraph(f'<font color="#{hex_col}">&#x25CF;</font>  {text}', bullet_style)

def render_section(sec, story):
    colour_map = {"warning": RED, "code": colors.HexColor("#2D3561")}
    banner_colour = colour_map.get(sec["type"], NAVY)
    story.append(KeepTogether([
        section_banner(sec["heading"], banner_colour),
        Spacer(1, 4*mm),   # guaranteed breathing room below every banner
    ]))

    t = sec["type"]
    content = sec.get("content", "")

    if t == "prose":
        for para in (content if isinstance(content, list) else [content]):
            story.append(Paragraph(str(para), prose_style))
            story.append(Spacer(1, 2*mm))

    elif t == "bullets":
        for item in content:
            story.append(bullet(str(item)))
        story.append(Spacer(1, 3*mm))

    elif t == "numbered":
        for i, item in enumerate(content, 1):
            story.append(Paragraph(f'<font color="#0F2B5B"><b>{i}.</b></font>  {item}', num_style))
        story.append(Spacer(1, 3*mm))

    elif t == "table":
        headers = sec.get("headers", [])
        rows    = sec.get("rows", [])
        col_w   = (W - ML - MR) / max(len(headers), 1)
        col_widths = [col_w] * len(headers)
        # First column wider if 2 columns
        if len(headers) == 2:
            col_widths = [(W - ML - MR) * 0.32, (W - ML - MR) * 0.68]

        hdr_row = [Paragraph(h, tbl_hdr) for h in headers]
        data_rows = [[Paragraph(str(c), tbl_cell) for c in row] for row in rows]
        tbl_data = [hdr_row] + data_rows
        tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  NAVY),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LGREY]),
            ("GRID",          (0,0),(-1,-1), 0.3, DGREY),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 5),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 4*mm))

    elif t == "code":
        lines = str(content).split('\n')
        wrapped = []
        for line in lines:
            if len(line) > 90:
                wrapped.extend(textwrap.wrap(line, 90))
            else:
                wrapped.append(line)
        code_text = '\n'.join(wrapped)
        code_para = Preformatted(code_text, S("cp",
            fontName="Courier", fontSize=8, textColor=CODE_FG,
            backColor=CODE_BG, leading=12,
            leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=4))
        story.append(code_para)
        story.append(Spacer(1, 4*mm))

    elif t == "warning":
        warn_items = content if isinstance(content, list) else [content]
        warn_data = [[
            Paragraph("⚠", S("wi", fontSize=12, textColor=RED, fontName="Helvetica-Bold",
                               alignment=TA_CENTER, leading=14)),
            Paragraph(str(item), warn_style)
        ] for item in warn_items]
        warn_tbl = Table(warn_data, colWidths=[8*mm, W - ML - MR - 10*mm])
        warn_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#FFF5F5")),
            ("LINEABOVE",     (0,0),(-1,0),  1.5, RED),
            ("LINEBELOW",     (0,-1),(-1,-1),0.5, colors.HexColor("#FFB3B3")),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 5),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        story.append(warn_tbl)
        story.append(Spacer(1, 4*mm))

    story.append(Spacer(1, 2*mm))


def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, 26*mm, W, 3, fill=1, stroke=0)
    canvas.restoreState()

def draw_later(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GREY)
    pg_text = f"Page {doc.page}  ·  80/20 Reference  ·  Not a substitute for the original"
    canvas.drawCentredString(W/2, 8*mm, pg_text)
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.4)
    canvas.line(ML, 12*mm, W - MR, 12*mm)
    canvas.restoreState()


def build_pdf(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB
    )
    story = []

    # ── Cover ──
    story.append(Spacer(1, 55*mm))
    story.append(Paragraph(data.get("title", "80/20 Reference"), cover_title))
    story.append(Spacer(1, 6*mm))
    story.append(rule(TEAL, 2))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "The 20% that delivers 80% of the practical value — distilled for action",
        cover_sub))
    story.append(Spacer(1, 25*mm))
    story.append(Paragraph(data.get("source", ""), cover_meta))
    story.append(PageBreak())

    # ── Sections ──
    for sec in data.get("sections", []):
        render_section(sec, story)

    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_later)
    print(f"✅  PDF written to: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",   required=True, help="Path to content JSON")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--title",  default="", help="Override title")
    parser.add_argument("--source", default="", help="Override source line")
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    if args.title:  data["title"]  = args.title
    if args.source: data["source"] = args.source

    build_pdf(data, args.output)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
generate_pptx.py — Generate a professional PPTX presentation for the
Housing Price Predictor MLOps project.

v2 — Fixed code blocks (line-by-line paragraphs) + added visual diagrams.

Usage:
    python3 generate_pptx.py

Output:
    presentation/MLOps_Housing_Price_Predictor.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ============================================================
# Color Palette
# ============================================================
BG_DARK      = RGBColor(0x0F, 0x11, 0x17)
BG_CARD      = RGBColor(0x1C, 0x1F, 0x2E)
BG_SECONDARY = RGBColor(0x16, 0x19, 0x22)
BG_CODE      = RGBColor(0x11, 0x14, 0x1C)
ACCENT       = RGBColor(0x63, 0x66, 0xF1)
ACCENT_LIGHT = RGBColor(0x81, 0x8C, 0xF8)
SUCCESS      = RGBColor(0x10, 0xB9, 0x81)
WARNING      = RGBColor(0xF5, 0x9E, 0x0B)
ERROR        = RGBColor(0xEF, 0x44, 0x44)
INFO         = RGBColor(0x3B, 0x82, 0xF6)
WHITE        = RGBColor(0xF1, 0xF5, 0xF9)
MUTED        = RGBColor(0x94, 0xA3, 0xB8)
DIM          = RGBColor(0x64, 0x74, 0x8B)
BORDER       = RGBColor(0x2A, 0x2D, 0x3E)
PURPLE       = RGBColor(0xA8, 0x55, 0xF7)
CODE_GREEN   = RGBColor(0x4E, 0xC9, 0xB0)
CODE_YELLOW  = RGBColor(0xDC, 0xDC, 0xAA)
CODE_BLUE    = RGBColor(0x9C, 0xDC, 0xFE)

SLIDE_WIDTH  = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)


# ============================================================
# Helpers
# ============================================================
def set_slide_bg(slide, color=BG_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color, border_color=None, rounding=True):
    """Add a rectangle (rounded or flat)."""
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounding else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, left, top, width, height, text, size=18,
             color=WHITE, bold=False, align=PP_ALIGN.LEFT, font="Calibri"):
    """Add a simple text box."""
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font
    p.alignment = align
    return txbox


def add_multiline_text(slide, left, top, width, height, text, size=14,
                       color=MUTED, bold=False, align=PP_ALIGN.LEFT,
                       font="Calibri", spacing=Pt(4)):
    """Add text where \\n actually creates new paragraphs."""
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.font.name = font
        p.alignment = align
        p.space_after = spacing
    return txbox


def add_code_block(slide, left, top, width, height, code_text, font_size=11):
    """Add a code block with each line as a separate paragraph — fixes layout."""
    shape = add_rect(slide, left, top, width, height, BG_CODE, BORDER)
    tf = shape.text_frame
    tf.word_wrap = False
    tf.margin_left = Pt(14)
    tf.margin_right = Pt(14)
    tf.margin_top = Pt(10)
    tf.margin_bottom = Pt(10)

    lines = code_text.strip().split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(font_size)
        p.font.color.rgb = MUTED
        p.font.name = "Consolas"
        p.space_before = Pt(0)
        p.space_after = Pt(1)
    return shape


def add_bullets(slide, items, left, top, width, height,
                size=14, color=MUTED, spacing=Pt(6)):
    """Add bulleted text items."""
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_after = spacing
    return txbox


def add_stat_card(slide, left, top, width, height, label, value, value_color=ACCENT):
    shape = add_rect(slide, left, top, width, height, BG_CARD, BORDER)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(14)
    tf.margin_top = Pt(12)
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(10)
    p.font.color.rgb = DIM
    p.font.bold = True
    p.font.name = "Calibri"
    p2 = tf.add_paragraph()
    p2.text = value
    p2.font.size = Pt(22)
    p2.font.color.rgb = value_color
    p2.font.bold = True
    p2.font.name = "Calibri"
    return shape


def add_table(slide, left, top, width, rows_data, col_widths=None, header=True):
    n_rows = len(rows_data)
    n_cols = len(rows_data[0]) if rows_data else 1
    row_h = Inches(0.38 * n_rows)
    table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, row_h)
    table = table_shape.table
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w
    for r, row_data in enumerate(rows_data):
        for c, cell_text in enumerate(row_data):
            cell = table.cell(r, c)
            cell.text = str(cell_text)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(11)
                paragraph.font.name = "Calibri"
                if r == 0 and header:
                    paragraph.font.bold = True
                    paragraph.font.color.rgb = ACCENT
                else:
                    paragraph.font.color.rgb = MUTED
            cell_fill = cell.fill
            cell_fill.solid()
            if r == 0 and header:
                cell_fill.fore_color.rgb = BG_DARK
            else:
                cell_fill.fore_color.rgb = BG_CARD if r % 2 == 0 else BG_SECONDARY
    return table_shape


def title_bar(slide, text):
    """Slide title + accent bar."""
    add_text(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.6),
             text, size=28, color=WHITE, bold=True)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.15), Inches(1.5), Pt(4)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def slide_num(slide, num, total):
    add_text(slide, Inches(12.2), Inches(7.0), Inches(1), Inches(0.3),
             f"{num}/{total}", size=10, color=DIM, align=PP_ALIGN.RIGHT)


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    return slide


# ── Diagram helpers ──────────────────────────────────────────

def add_arrow_right(slide, x, y, length=Inches(0.8), color=DIM):
    """Horizontal right arrow."""
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.NOTCHED_RIGHT_ARROW, x, y, length, Inches(0.3)
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = color
    arrow.line.fill.background()
    return arrow


def add_arrow_down(slide, x, y, length=Inches(0.6), color=DIM):
    """Vertical down arrow."""
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.DOWN_ARROW, x, y, Inches(0.3), length
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = color
    arrow.line.fill.background()
    return arrow


def add_circle(slide, x, y, size, fill, label="", label_color=WHITE, label_size=12):
    """Circle / oval with centered text."""
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, size, size)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    if label:
        tf = shape.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(label_size)
        p.font.color.rgb = label_color
        p.font.bold = True
        p.font.name = "Calibri"
        p.alignment = PP_ALIGN.CENTER
    return shape


def add_box_node(slide, x, y, w, h, fill, border, title, subtitle="",
                 title_color=WHITE, title_size=13, sub_size=10, sub_color=MUTED):
    """A labeled box node for diagrams."""
    shape = add_rect(slide, x, y, w, h, fill, border)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Pt(8)
    tf.margin_right = Pt(8)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(title_size)
    p.font.color.rgb = title_color
    p.font.bold = True
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(sub_size)
        p2.font.color.rgb = sub_color
        p2.font.name = "Calibri"
        p2.alignment = PP_ALIGN.CENTER
    return shape


def section_header(prs, title, subtitle, speaker, sn, total):
    slide = new_slide(prs)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(2.5), SLIDE_WIDTH, Inches(2.8)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = BG_CARD
    bar.line.fill.background()
    add_text(slide, Inches(1), Inches(2.8), Inches(11), Inches(0.8),
             title, size=36, color=WHITE, bold=True)
    add_text(slide, Inches(1), Inches(3.6), Inches(11), Inches(0.6),
             subtitle, size=18, color=MUTED)
    add_text(slide, Inches(1), Inches(4.3), Inches(11), Inches(0.5),
             f"Presented by {speaker}", size=14, color=ACCENT)
    slide_num(slide, sn, total)
    return slide


# ============================================================
# Build Presentation
# ============================================================
def build_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    TOTAL = 30  # approximate — updated at the end

    sn = 1

    # ================================================================
    # 1 — TITLE
    # ================================================================
    slide = new_slide(prs)
    logo = add_circle(slide, Inches(6.15), Inches(1.4), Inches(1), ACCENT, "HP", WHITE, 28)
    add_text(slide, Inches(2), Inches(2.6), Inches(9.3), Inches(1),
             "Housing Price Predictor", size=44, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), Inches(3.6), Inches(9.3), Inches(0.6),
             "A Complete Local MLOps Pipeline", size=22, color=ACCENT,
             align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), Inches(4.5), Inches(9.3), Inches(0.5),
             "Ralia  •  Cassidy  •  Uriel  •  Cheikh", size=16, color=MUTED,
             align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), Inches(5.1), Inches(9.3), Inches(0.4),
             "Junia School — February 2026", size=12, color=DIM,
             align=PP_ALIGN.CENTER)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # 2 — AGENDA
    # ================================================================
    slide = new_slide(prs)
    title_bar(slide, "Agenda")
    agenda = [
        ("1", "Project Overview & Data Pipeline", "Ralia", ACCENT),
        ("2", "Model Architecture & Training", "Cassidy", SUCCESS),
        ("3", "API, Inference & Docker", "Uriel", WARNING),
        ("4", "Frontend, Logging & CI/CD", "Cheikh", INFO),
    ]
    for i, (num, title, speaker, color) in enumerate(agenda):
        y = Inches(1.7) + Inches(i * 1.2)
        add_rect(slide, Inches(1), y, Inches(11), Inches(0.95), BG_CARD, BORDER)
        add_text(slide, Inches(1.3), y + Pt(12), Inches(0.6), Inches(0.5),
                 num, size=24, color=color, bold=True)
        add_text(slide, Inches(2.3), y + Pt(10), Inches(7), Inches(0.35),
                 title, size=18, color=WHITE, bold=True)
        add_text(slide, Inches(2.3), y + Pt(38), Inches(7), Inches(0.3),
                 speaker, size=13, color=MUTED)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # SECTION 1 — RALIA
    # ================================================================
    section_header(prs, "Part 1: Data & Validation",
                   "Project overview, dataset, and Pandera schema validation",
                   "Ralia", sn, TOTAL); sn += 1

    # ── Architecture DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "System Architecture Diagram")

    # User
    add_circle(slide, Inches(0.5), Inches(2.6), Inches(1.2), BG_CARD, "User\n(Browser)", WHITE, 12)
    add_arrow_right(slide, Inches(1.7), Inches(3.05), Inches(0.7), MUTED)

    # Django container
    dj_x, dj_y = Inches(2.6), Inches(1.5)
    add_rect(slide, dj_x, dj_y, Inches(3.2), Inches(3.8), BG_CARD, SUCCESS, rounding=False)
    add_text(slide, dj_x + Pt(8), dj_y + Pt(4), Inches(3), Inches(0.3),
             "CONTAINER: django-service", size=10, color=SUCCESS, bold=True)
    add_box_node(slide, dj_x + Inches(0.2), dj_y + Inches(0.5), Inches(2.7), Inches(0.6),
                 BG_SECONDARY, BORDER, "Django 4.2", "Port 8080", SUCCESS, 13)
    add_box_node(slide, dj_x + Inches(0.2), dj_y + Inches(1.3), Inches(2.7), Inches(0.55),
                 BG_SECONDARY, BORDER, "Predict Page", "Form + API call", MUTED, 11)
    add_box_node(slide, dj_x + Inches(0.2), dj_y + Inches(2), Inches(2.7), Inches(0.55),
                 BG_SECONDARY, BORDER, "Dashboard", "Live metrics view", MUTED, 11)
    add_box_node(slide, dj_x + Inches(0.2), dj_y + Inches(2.7), Inches(2.7), Inches(0.55),
                 BG_SECONDARY, BORDER, "API Docs", "Endpoint reference", MUTED, 11)

    # Arrow Django -> FastAPI
    add_arrow_right(slide, Inches(5.9), Inches(3.05), Inches(0.9), ACCENT_LIGHT)
    add_text(slide, Inches(5.9), Inches(2.5), Inches(0.9), Inches(0.3),
             "HTTP", size=9, color=ACCENT_LIGHT, align=PP_ALIGN.CENTER, bold=True)

    # FastAPI container
    fa_x, fa_y = Inches(7.0), Inches(1.5)
    add_rect(slide, fa_x, fa_y, Inches(3.2), Inches(3.8), BG_CARD, ACCENT, rounding=False)
    add_text(slide, fa_x + Pt(8), fa_y + Pt(4), Inches(3), Inches(0.3),
             "CONTAINER: training-service", size=10, color=ACCENT, bold=True)
    add_box_node(slide, fa_x + Inches(0.2), fa_y + Inches(0.5), Inches(2.7), Inches(0.6),
                 BG_SECONDARY, BORDER, "FastAPI + Uvicorn", "Port 8000", ACCENT, 13)
    add_box_node(slide, fa_x + Inches(0.2), fa_y + Inches(1.3), Inches(2.7), Inches(0.55),
                 BG_SECONDARY, BORDER, "/predict  /train", "Core endpoints", MUTED, 11)
    add_box_node(slide, fa_x + Inches(0.2), fa_y + Inches(2), Inches(2.7), Inches(0.55),
                 BG_SECONDARY, BORDER, "/health  /metrics", "Monitoring", MUTED, 11)
    add_box_node(slide, fa_x + Inches(0.2), fa_y + Inches(2.7), Inches(2.7), Inches(0.55),
                 BG_SECONDARY, BORDER, "HousingPredictor", "Inference engine", MUTED, 11)

    # Model file
    add_arrow_right(slide, Inches(10.3), Inches(3.05), Inches(0.6), WARNING)
    add_box_node(slide, Inches(11.1), Inches(2.3), Inches(1.7), Inches(1.5),
                 BG_SECONDARY, WARNING, "Model\nFiles", "*.joblib", WARNING, 14)

    # Shared volumes at bottom
    vol_y = Inches(5.8)
    add_rect(slide, Inches(2.6), vol_y, Inches(7.6), Inches(1.2), BG_SECONDARY, BORDER, rounding=False)
    add_text(slide, Inches(2.8), vol_y + Pt(4), Inches(3), Inches(0.25),
             "SHARED DOCKER VOLUMES", size=10, color=DIM, bold=True)
    vols = [("./data", "CSV files"), ("./models", "Joblib"), ("./mlruns", "MLflow"), ("./logs", "Log files")]
    for i, (name, desc) in enumerate(vols):
        vx = Inches(2.8) + Inches(i * 1.85)
        add_box_node(slide, vx, vol_y + Inches(0.35), Inches(1.6), Inches(0.65),
                     BG_CODE, BORDER, name, desc, MUTED, 10, 9, DIM)

    # Arrows down to volumes
    add_arrow_down(slide, Inches(4.0), Inches(5.35), Inches(0.4), SUCCESS)
    add_arrow_down(slide, Inches(8.4), Inches(5.35), Inches(0.4), ACCENT)

    slide_num(slide, sn, TOTAL); sn += 1

    # ── Tech Stack ──
    slide = new_slide(prs)
    title_bar(slide, "Tech Stack")
    stack = [
        ["Component", "Technology", "Purpose"],
        ["ML Model", "scikit-learn (RandomForest)", "Tabular regression"],
        ["Training API", "FastAPI + Uvicorn", "Async REST API"],
        ["Frontend", "Django 4.2", "Web forms, dashboards"],
        ["Containers", "Docker + Compose", "Reproducible deployment"],
        ["Experiment Tracking", "MLflow", "Log params, metrics, models"],
        ["Data Validation", "Pandera", "Schema-based DataFrame checks"],
        ["Serialization", "Joblib", "Fast model save/load"],
        ["CI/CD", "GitHub Actions", "Automated retrain pipeline"],
    ]
    add_table(slide, Inches(0.8), Inches(1.5), Inches(11.5), stack,
              col_widths=[Inches(2.5), Inches(3.5), Inches(5.5)])
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Dataset ──
    slide = new_slide(prs)
    title_bar(slide, "The Dataset")
    add_text(slide, Inches(0.8), Inches(1.4), Inches(11), Inches(0.4),
             "Kaggle House Pricing Dataset — 1,000 rows x 6 columns", size=15, color=MUTED)
    ds = [
        ["Column", "Type", "Description"],
        ["HouseID", "int", "Unique ID (dropped before training)"],
        ["Location", "string", "New York, Los Angeles, Chicago, Houston"],
        ["Bedrooms", "int", "Number of bedrooms (1-10)"],
        ["Bathrooms", "int", "Number of bathrooms (1-5)"],
        ["SquareFeet", "int", "Living area in square feet"],
        ["Price", "float", "Target variable — house price"],
    ]
    add_table(slide, Inches(0.8), Inches(2.0), Inches(11.5), ds,
              col_widths=[Inches(2), Inches(1.5), Inches(8)])
    add_stat_card(slide, Inches(0.8), Inches(5.5), Inches(2.5), Inches(1.2), "ROWS", "1,000", ACCENT)
    add_stat_card(slide, Inches(3.6), Inches(5.5), Inches(2.5), Inches(1.2), "FEATURES", "4", SUCCESS)
    add_stat_card(slide, Inches(6.4), Inches(5.5), Inches(2.5), Inches(1.2), "CITIES", "4", WARNING)
    add_stat_card(slide, Inches(9.2), Inches(5.5), Inches(2.5), Inches(1.2), "TARGET", "Price", INFO)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Data Validation DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "Data Validation Flow")

    # Flow: CSV -> Pandera -> (Pass/Fail)
    add_box_node(slide, Inches(0.6), Inches(2.5), Inches(2), Inches(1.2),
                 BG_CARD, BORDER, "Raw CSV", "house_prices.csv\n1000 rows", MUTED, 13)
    add_arrow_right(slide, Inches(2.7), Inches(2.95), Inches(0.7), MUTED)

    # Pandera box (large, central)
    add_rect(slide, Inches(3.5), Inches(1.8), Inches(4.5), Inches(3.5), BG_CARD, ACCENT, rounding=False)
    add_text(slide, Inches(3.7), Inches(1.9), Inches(4), Inches(0.35),
             "PANDERA SCHEMA VALIDATION", size=11, color=ACCENT, bold=True)
    checks = [
        "HouseID    -> int, > 0",
        "Location   -> str, in {NY, LA, CHI, HOU}",
        "Bedrooms   -> int, range [1, 10]",
        "Bathrooms  -> int, range [1, 5]",
        "SquareFeet -> int, range [100, 10000]",
        "Price      -> float, > 0",
    ]
    add_multiline_text(slide, Inches(3.7), Inches(2.4), Inches(4), Inches(2.5),
                       "\n".join(checks), size=11, color=MUTED, font="Consolas", spacing=Pt(2))

    # Pass arrow
    add_arrow_right(slide, Inches(8.1), Inches(2.4), Inches(0.8), SUCCESS)
    add_box_node(slide, Inches(9.1), Inches(2.0), Inches(3.2), Inches(1.0),
                 BG_CARD, SUCCESS, "PASS", "Continue to preprocessing", SUCCESS, 16)

    # Fail arrow
    add_arrow_right(slide, Inches(8.1), Inches(4.2), Inches(0.8), ERROR)
    add_box_node(slide, Inches(9.1), Inches(3.8), Inches(3.2), Inches(1.0),
                 BG_CARD, ERROR, "FAIL", "Pipeline halts + error logged", ERROR, 16)

    add_text(slide, Inches(0.8), Inches(5.8), Inches(11), Inches(0.6),
             "\"First gate in the pipeline — prevents training on corrupted or malformed data.\"",
             size=14, color=DIM)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Preprocessing ──
    slide = new_slide(prs)
    title_bar(slide, "Data Preprocessing Pipeline")

    # Diagram: 5-step flow
    steps = [
        ("1", "Extract\nTarget", "Price -> y", ACCENT),
        ("2", "Label\nEncode", "Location -> int", SUCCESS),
        ("3", "Select\nFeatures", "4 columns", WARNING),
        ("4", "Handle\nNulls", "median fill", INFO),
        ("5", "Return\nX, y, LE", "ready for split", PURPLE),
    ]
    for i, (num, title, desc, color) in enumerate(steps):
        x = Inches(0.5) + Inches(i * 2.55)
        add_box_node(slide, x, Inches(1.7), Inches(2.0), Inches(1.4),
                     BG_CARD, color, title, desc, color, 14, 10, MUTED)
        add_text(slide, x + Inches(0.7), Inches(1.4), Inches(0.5), Inches(0.3),
                 num, size=18, color=color, bold=True, align=PP_ALIGN.CENTER)
        if i < 4:
            add_arrow_right(slide, x + Inches(2.05), Inches(2.2), Inches(0.45), DIM)

    # Code below the diagram
    preprocess_code = (
        "def preprocess_features(df):\n"
        "    data = df.copy()\n"
        "    y = data[\"Price\"].astype(float)\n"
        "    le = LabelEncoder()\n"
        "    data[\"Location_encoded\"] = le.fit_transform(data[\"Location\"])\n"
        "    feature_cols = [\"Bedrooms\", \"Bathrooms\", \"SquareFeet\", \"Location_encoded\"]\n"
        "    X = data[feature_cols].astype(float)\n"
        "    if X.isnull().any().any():\n"
        "        X = X.fillna(X.median())\n"
        "    return X, y, le"
    )
    add_code_block(slide, Inches(0.8), Inches(3.6), Inches(11.5), Inches(3.4), preprocess_code, font_size=12)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # SECTION 2 — CASSIDY
    # ================================================================
    section_header(prs, "Part 2: Model & Training",
                   "Random Forest architecture, training pipeline, MLflow tracking",
                   "Cassidy", sn, TOTAL); sn += 1

    # ── Random Forest Ensemble DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "Random Forest — Ensemble Diagram")

    # Input data box
    add_box_node(slide, Inches(0.5), Inches(2.8), Inches(2), Inches(1.2),
                 BG_CARD, ACCENT, "Input Data", "4 features\n1000 samples", ACCENT, 14)

    # Arrow to bootstrap
    add_arrow_right(slide, Inches(2.6), Inches(3.2), Inches(0.6), MUTED)

    # Bootstrap sampling label
    add_text(slide, Inches(3.3), Inches(1.6), Inches(2), Inches(0.3),
             "Bootstrap Sampling", size=11, color=DIM, bold=True, align=PP_ALIGN.CENTER)

    # 5 trees (representing 200)
    tree_colors = [ACCENT, SUCCESS, WARNING, INFO, PURPLE]
    tree_labels = ["Tree 1", "Tree 2", "Tree 3", "...", "Tree 200"]
    for i in range(5):
        y = Inches(1.9) + Inches(i * 0.75)
        add_box_node(slide, Inches(3.4), y, Inches(1.8), Inches(0.55),
                     BG_CARD, tree_colors[i % 5], tree_labels[i], "",
                     tree_colors[i % 5], 11)

    # Arrow from trees to averaging
    add_arrow_right(slide, Inches(5.3), Inches(3.2), Inches(0.6), MUTED)

    # Averaging box
    add_box_node(slide, Inches(6.1), Inches(2.5), Inches(2.2), Inches(1.6),
                 BG_CARD, WARNING, "Average\nAll Trees", "Reduces variance\nReduces overfitting",
                 WARNING, 14, 10)

    # Arrow to prediction
    add_arrow_right(slide, Inches(8.4), Inches(3.2), Inches(0.6), MUTED)

    # Prediction output
    add_box_node(slide, Inches(9.2), Inches(2.8), Inches(2.2), Inches(1.2),
                 BG_CARD, SUCCESS, "Prediction", "Estimated price", SUCCESS, 14)

    # Hyperparameters table below
    add_text(slide, Inches(0.8), Inches(5.2), Inches(3), Inches(0.3),
             "Hyperparameters:", size=14, color=WHITE, bold=True)
    hp = [
        ["Parameter", "Value", "Effect"],
        ["n_estimators", "200", "200 trees in the forest"],
        ["max_depth", "20", "Max 20 levels per tree"],
        ["min_samples_split", "5", "Min 5 samples to split"],
        ["min_samples_leaf", "2", "Min 2 samples per leaf"],
        ["n_jobs", "-1", "Parallel on all CPU cores"],
    ]
    add_table(slide, Inches(0.8), Inches(5.55), Inches(11.5), hp,
              col_widths=[Inches(3), Inches(2), Inches(6.5)])
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Model code ──
    slide = new_slide(prs)
    title_bar(slide, "model.py — Model Factory")
    model_code = (
        "# training-service/src/model.py\n"
        "\n"
        "from sklearn.ensemble import RandomForestRegressor\n"
        "\n"
        "def create_model(n_estimators=200, max_depth=20,\n"
        "                 random_state=42, min_samples_split=5,\n"
        "                 min_samples_leaf=2, **kwargs):\n"
        "    return RandomForestRegressor(\n"
        "        n_estimators=n_estimators,\n"
        "        max_depth=max_depth,\n"
        "        random_state=random_state,\n"
        "        min_samples_split=min_samples_split,\n"
        "        min_samples_leaf=min_samples_leaf,\n"
        "        n_jobs=-1\n"
        "    )"
    )
    add_code_block(slide, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.2), model_code, font_size=13)

    # Key points on the right
    points = [
        ("Factory pattern", "create_model() returns a configured estimator"),
        ("Separation", "model.py is pure ML — no API, no I/O"),
        ("**kwargs", "Forward-compatible with new hyperparams"),
        ("n_jobs=-1", "Parallel training on all CPU cores"),
        ("random_state=42", "Reproducible results across runs"),
    ]
    for i, (title, desc) in enumerate(points):
        y = Inches(1.7) + Inches(i * 1.0)
        add_text(slide, Inches(8.8), y, Inches(4), Inches(0.3),
                 f"->  {title}", size=13, color=ACCENT, bold=True)
        add_text(slide, Inches(9.1), y + Pt(20), Inches(3.7), Inches(0.4),
                 desc, size=11, color=MUTED)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Training Pipeline DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "Training Pipeline — Flow Diagram")

    # 8-step pipeline as a 2-row flow with arrows
    pipeline = [
        ("1", "Load CSV", ACCENT),
        ("2", "Validate", SUCCESS),
        ("3", "Preprocess", WARNING),
        ("4", "Train/Test\nSplit", INFO),
    ]
    pipeline2 = [
        ("5", "Start\nMLflow Run", PURPLE),
        ("6", "Train +\nEvaluate", ACCENT),
        ("7", "Log to\nMLflow", SUCCESS),
        ("8", "Save\nJoblib", WARNING),
    ]

    # Row 1
    for i, (num, label, color) in enumerate(pipeline):
        x = Inches(0.5) + Inches(i * 3.1)
        add_box_node(slide, x, Inches(1.7), Inches(2.3), Inches(1.4),
                     BG_CARD, color, label, "", color, 15)
        add_circle(slide, x - Inches(0.15), Inches(1.55), Inches(0.4), color, num, WHITE, 12)
        if i < 3:
            add_arrow_right(slide, x + Inches(2.35), Inches(2.25), Inches(0.7), DIM)

    # Arrow down from row 1 to row 2
    add_arrow_down(slide, Inches(11.65), Inches(3.2), Inches(0.6), DIM)

    # Row 2
    for i, (num, label, color) in enumerate(pipeline2):
        x = Inches(0.5) + Inches(i * 3.1)
        add_box_node(slide, x, Inches(4.1), Inches(2.3), Inches(1.4),
                     BG_CARD, color, label, "", color, 15)
        add_circle(slide, x - Inches(0.15), Inches(3.95), Inches(0.4), color, num, WHITE, 12)
        if i < 3:
            add_arrow_right(slide, x + Inches(2.35), Inches(4.65), Inches(0.7), DIM)

    # Output label
    add_text(slide, Inches(0.8), Inches(5.9), Inches(11), Inches(0.4),
             "Output:  *.joblib model file  +  MLflow experiment run  +  Metrics logged",
             size=14, color=MUTED)

    add_text(slide, Inches(0.8), Inches(6.4), Inches(11), Inches(0.4),
             "All 8 steps happen inside a single POST /train API call.",
             size=12, color=DIM)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Model Versioning ──
    slide = new_slide(prs)
    title_bar(slide, "Model Versioning with Joblib")

    # File tree diagram using shapes
    files = [
        ("models/artifacts/", None, WHITE, True),
        ("  housing_price_predictor_20260215.joblib", "v1 snapshot", MUTED, False),
        ("  housing_price_predictor_20260219.joblib", "v2 snapshot", MUTED, False),
        ("  housing_price_predictor_latest.joblib", "<- API loads this", SUCCESS, False),
        ("  housing_price_predictor_info.joblib", "encoder + metadata", WARNING, False),
    ]
    for i, (name, desc, color, is_bold) in enumerate(files):
        y = Inches(1.7) + Inches(i * 0.6)
        add_text(slide, Inches(1.0), y, Inches(6), Inches(0.35),
                 name, size=13, color=color, bold=is_bold, font="Consolas")
        if desc:
            add_text(slide, Inches(7.5), y, Inches(4), Inches(0.35),
                     desc, size=12, color=DIM)

    # Versioning diagram
    add_text(slide, Inches(0.8), Inches(4.5), Inches(4), Inches(0.3),
             "Versioning Strategy:", size=14, color=WHITE, bold=True)

    # Visual: two model versions -> latest
    add_box_node(slide, Inches(1), Inches(5.0), Inches(2.5), Inches(0.8),
                 BG_CARD, DIM, "v1 — Feb 15", "n_est=100, depth=15", MUTED, 12)
    add_box_node(slide, Inches(1), Inches(6.0), Inches(2.5), Inches(0.8),
                 BG_CARD, ACCENT, "v2 — Feb 19", "n_est=200, depth=20", ACCENT, 12)
    add_arrow_right(slide, Inches(3.6), Inches(6.2), Inches(0.6), ACCENT)
    add_box_node(slide, Inches(4.4), Inches(5.7), Inches(3), Inches(1.2),
                 BG_CARD, SUCCESS, "*_latest.joblib", "Overwritten on each training\nAPI loads at startup", SUCCESS, 13)

    # Info box
    add_box_node(slide, Inches(8.5), Inches(5.0), Inches(3.8), Inches(1.8),
                 BG_CARD, WARNING, "*_info.joblib", "LabelEncoder instance\nFeature column names\nModel hyperparameters\nTraining metrics", WARNING, 13, 10)

    slide_num(slide, sn, TOTAL); sn += 1

    # ── MLflow ──
    slide = new_slide(prs)
    title_bar(slide, "Experiment Tracking with MLflow")

    # Two run comparison cards
    add_rect(slide, Inches(0.8), Inches(1.5), Inches(5.2), Inches(3.6), BG_CARD, ERROR)
    add_text(slide, Inches(1.1), Inches(1.6), Inches(4), Inches(0.35),
             "Run 1 — Feb 15 (FAILED)", size=14, color=ERROR, bold=True)
    add_bullets(slide, [
        "n_estimators: 100",
        "max_depth: 15",
        "Status: CRASHED",
        "Metrics: (none)",
        "Artifacts: (none)",
    ], Inches(1.1), Inches(2.2), Inches(4.5), Inches(2.5), size=12)

    add_rect(slide, Inches(6.5), Inches(1.5), Inches(5.5), Inches(3.6), BG_CARD, SUCCESS)
    add_text(slide, Inches(6.8), Inches(1.6), Inches(4), Inches(0.35),
             "Run 2 — Feb 19 (SUCCESS)", size=14, color=SUCCESS, bold=True)
    add_bullets(slide, [
        "n_estimators: 200",
        "max_depth: 20",
        "RMSE: $140,983",
        "MAE: $119,364",
        "R2: -0.112",
    ], Inches(6.8), Inches(2.2), Inches(5), Inches(2.5), size=12)

    # MLflow vs Joblib comparison diagram
    add_text(slide, Inches(0.8), Inches(5.5), Inches(11), Inches(0.3),
             "MLflow vs Joblib — complementary roles:", size=13, color=WHITE, bold=True)
    add_box_node(slide, Inches(0.8), Inches(5.9), Inches(4.5), Inches(0.9),
                 BG_CODE, ACCENT, "MLflow = Lab Notebook",
                 "Every experiment tracked (even failures)", ACCENT, 13)
    add_text(slide, Inches(5.5), Inches(6.1), Inches(0.8), Inches(0.5),
             "vs", size=14, color=DIM, align=PP_ALIGN.CENTER)
    add_box_node(slide, Inches(6.5), Inches(5.9), Inches(4.5), Inches(0.9),
                 BG_CODE, SUCCESS, "Joblib = Deployed Product",
                 "Only the best model is served by API", SUCCESS, 13)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Metrics ──
    slide = new_slide(prs)
    title_bar(slide, "Model Metrics Explained")
    add_stat_card(slide, Inches(0.8), Inches(1.5), Inches(3.5), Inches(1.5), "R2 SCORE", "-0.112", ERROR)
    add_stat_card(slide, Inches(4.8), Inches(1.5), Inches(3.5), Inches(1.5), "MAE", "$119,364", ACCENT)
    add_stat_card(slide, Inches(8.8), Inches(1.5), Inches(3.5), Inches(1.5), "RMSE", "$140,983", WARNING)
    m = [
        ["Metric", "Value", "Interpretation"],
        ["R2", "-0.112", "Worse than predicting the mean — expected with small dataset"],
        ["MAE", "$119,364", "Average prediction is off by ~$119K"],
        ["RMSE", "$140,983", "Penalizes large errors more heavily than MAE"],
    ]
    add_table(slide, Inches(0.8), Inches(3.5), Inches(11.5), m,
              col_widths=[Inches(2), Inches(2), Inches(7.5)])
    add_multiline_text(slide, Inches(0.8), Inches(5.5), Inches(11), Inches(1),
                       "Goal is not max accuracy — it's demonstrating a complete MLOps pipeline.\n"
                       "MLflow lets us compare: 100->200 estimators improved RMSE from 143K->141K.",
                       size=13, color=DIM)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # SECTION 3 — URIEL
    # ================================================================
    section_header(prs, "Part 3: API & Docker",
                   "FastAPI endpoints, inference pipeline, containerization",
                   "Uriel", sn, TOTAL); sn += 1

    # ── API Endpoints ──
    slide = new_slide(prs)
    title_bar(slide, "FastAPI — 4 Endpoints")
    endpoints = [
        ("GET", "/health", "Service status + model loaded check", SUCCESS),
        ("POST", "/predict", "Takes features -> returns estimated price", INFO),
        ("POST", "/train", "Triggers full retraining pipeline -> reloads model", WARNING),
        ("GET", "/metrics", "R2, MAE, RMSE, model params, features list", ACCENT),
    ]
    for i, (method, path, desc, color) in enumerate(endpoints):
        y = Inches(1.5) + Inches(i * 1.25)
        add_rect(slide, Inches(0.8), y, Inches(11.5), Inches(1), BG_CARD, BORDER)
        badge = add_rect(slide, Inches(1.1), y + Pt(15), Inches(0.9), Inches(0.35), BG_CODE, color)
        tf = badge.text_frame; tf.margin_left = Pt(4)
        p = tf.paragraphs[0]; p.text = method
        p.font.size = Pt(10); p.font.color.rgb = color; p.font.bold = True
        p.font.name = "Consolas"; p.alignment = PP_ALIGN.CENTER
        add_text(slide, Inches(2.2), y + Pt(10), Inches(2), Inches(0.35),
                 path, size=16, color=WHITE, bold=True, font="Consolas")
        add_text(slide, Inches(4.5), y + Pt(12), Inches(7.5), Inches(0.3),
                 desc, size=13, color=MUTED)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Prediction Flow DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "Prediction Flow — /predict")

    # Horizontal flow diagram
    pred_steps = [
        ("Client\nRequest", "JSON body", INFO),
        ("Pydantic\nValidation", "422 if invalid", ACCENT),
        ("Model\nCheck", "503 if missing", ERROR),
        ("Label\nEncode", "Location -> int", WARNING),
        ("Build\nDataFrame", "Column order", MUTED),
        ("model.\npredict()", "RandomForest", SUCCESS),
    ]
    for i, (label, sub, color) in enumerate(pred_steps):
        x = Inches(0.3) + Inches(i * 2.15)
        add_box_node(slide, x, Inches(1.7), Inches(1.7), Inches(1.6),
                     BG_CARD, color, label, sub, color, 13, 9, MUTED)
        if i < 5:
            add_arrow_right(slide, x + Inches(1.75), Inches(2.35), Inches(0.35), DIM)

    # Response example
    add_text(slide, Inches(0.8), Inches(3.8), Inches(3), Inches(0.3),
             "Response example:", size=13, color=WHITE, bold=True)
    resp_code = (
        '{\n'
        '  "prediction": 244900.50,\n'
        '  "model_version": "20260219_110919",\n'
        '  "features_used": [\n'
        '    "Bedrooms", "Bathrooms",\n'
        '    "SquareFeet", "Location_encoded"\n'
        '  ]\n'
        '}'
    )
    add_code_block(slide, Inches(0.8), Inches(4.2), Inches(5), Inches(2.6), resp_code, font_size=12)

    # Error handling on the right
    add_text(slide, Inches(6.5), Inches(3.8), Inches(3), Inches(0.3),
             "Error Handling:", size=13, color=WHITE, bold=True)
    errors = [
        ("422", "Invalid input (Pydantic)", ERROR),
        ("503", "Model not loaded yet", WARNING),
        ("500", "Unexpected server error", DIM),
    ]
    for i, (code, desc, color) in enumerate(errors):
        y = Inches(4.3) + Inches(i * 0.8)
        add_box_node(slide, Inches(6.5), y, Inches(1), Inches(0.6),
                     BG_CODE, color, code, "", color, 16)
        add_text(slide, Inches(7.7), y + Pt(8), Inches(4), Inches(0.4),
                 desc, size=12, color=MUTED)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Inference & Hot Reload ──
    slide = new_slide(prs)
    title_bar(slide, "Inference Engine — HousingPredictor")

    inf_code = (
        "class HousingPredictor:\n"
        "    def __init__(self):\n"
        "        self.model = None\n"
        "        self.label_encoder = None\n"
        "        self.is_loaded = False\n"
        "        self._load()            # Load at startup\n"
        "\n"
        "    def reload(self):           # Called after /train\n"
        "        self._load()            # Zero downtime!\n"
        "\n"
        "    def predict(self, features: dict) -> float:\n"
        "        encoded = self.label_encoder.transform(...)\n"
        "        df = pd.DataFrame(...)  # Same column order\n"
        "        return self.model.predict(df)[0]"
    )
    add_code_block(slide, Inches(0.8), Inches(1.5), Inches(7.5), Inches(4.7), inf_code, font_size=13)

    # Hot reload diagram on the right
    add_text(slide, Inches(8.8), Inches(1.5), Inches(4), Inches(0.3),
             "Hot Reload Flow:", size=14, color=WHITE, bold=True)

    reload_steps = [
        ("POST /train", ACCENT),
        ("train.py runs", SUCCESS),
        ("New .joblib saved", WARNING),
        ("predictor.reload()", INFO),
        ("API serves new model", SUCCESS),
    ]
    for i, (step, color) in enumerate(reload_steps):
        y = Inches(2.1) + Inches(i * 0.85)
        add_box_node(slide, Inches(9.0), y, Inches(3.5), Inches(0.6),
                     BG_CARD, color, step, "", color, 12)
        if i < 4:
            add_arrow_down(slide, Inches(10.6), y + Inches(0.6), Inches(0.2), DIM)

    add_text(slide, Inches(8.8), Inches(6.3), Inches(4), Inches(0.5),
             "Zero downtime — no container restart needed!",
             size=11, color=DIM)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Docker Architecture DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "Docker Architecture")

    # Docker host
    add_rect(slide, Inches(0.5), Inches(1.4), Inches(12.3), Inches(5.5),
             BG_SECONDARY, BORDER, rounding=False)
    add_text(slide, Inches(0.7), Inches(1.45), Inches(3), Inches(0.3),
             "DOCKER HOST", size=10, color=DIM, bold=True)

    # Docker Compose frame
    add_rect(slide, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.8),
             BG_DARK, ACCENT, rounding=False)
    add_text(slide, Inches(1.0), Inches(1.95), Inches(3), Inches(0.3),
             "docker-compose.yml", size=10, color=ACCENT, bold=True)

    # Container 1: training-service
    c1_x, c1_y = Inches(1.3), Inches(2.5)
    add_rect(slide, c1_x, c1_y, Inches(4.8), Inches(3.8), BG_CARD, ACCENT, rounding=False)
    add_text(slide, c1_x + Pt(8), c1_y + Pt(4), Inches(4.5), Inches(0.25),
             "training-service", size=11, color=ACCENT, bold=True)

    add_box_node(slide, c1_x + Inches(0.2), c1_y + Inches(0.45), Inches(4.3), Inches(0.55),
                 BG_SECONDARY, BORDER, "FastAPI + Uvicorn (port 8000)", "", WHITE, 12)
    add_box_node(slide, c1_x + Inches(0.2), c1_y + Inches(1.15), Inches(2), Inches(0.5),
                 BG_CODE, BORDER, "train.py", "", CODE_GREEN, 11)
    add_box_node(slide, c1_x + Inches(2.4), c1_y + Inches(1.15), Inches(2.1), Inches(0.5),
                 BG_CODE, BORDER, "inference.py", "", CODE_BLUE, 11)
    add_box_node(slide, c1_x + Inches(0.2), c1_y + Inches(1.8), Inches(2), Inches(0.5),
                 BG_CODE, BORDER, "model.py", "", CODE_YELLOW, 11)
    add_box_node(slide, c1_x + Inches(2.4), c1_y + Inches(1.8), Inches(2.1), Inches(0.5),
                 BG_CODE, BORDER, "validate_data.py", "", PURPLE, 11)

    # Healthcheck
    add_box_node(slide, c1_x + Inches(0.2), c1_y + Inches(2.6), Inches(4.3), Inches(0.55),
                 BG_SECONDARY, SUCCESS, "healthcheck: curl /health", "", SUCCESS, 10)
    add_text(slide, c1_x + Inches(0.2), c1_y + Inches(3.3), Inches(4.3), Inches(0.3),
             "restart: unless-stopped", size=10, color=DIM)

    # Container 2: django-service
    c2_x, c2_y = Inches(6.8), Inches(2.5)
    add_rect(slide, c2_x, c2_y, Inches(4.8), Inches(3.8), BG_CARD, SUCCESS, rounding=False)
    add_text(slide, c2_x + Pt(8), c2_y + Pt(4), Inches(4.5), Inches(0.25),
             "django-service", size=11, color=SUCCESS, bold=True)

    add_box_node(slide, c2_x + Inches(0.2), c2_y + Inches(0.45), Inches(4.3), Inches(0.55),
                 BG_SECONDARY, BORDER, "Django 4.2 (port 8080)", "", WHITE, 12)
    add_box_node(slide, c2_x + Inches(0.2), c2_y + Inches(1.15), Inches(2), Inches(0.5),
                 BG_CODE, BORDER, "views.py", "", CODE_GREEN, 11)
    add_box_node(slide, c2_x + Inches(2.4), c2_y + Inches(1.15), Inches(2.1), Inches(0.5),
                 BG_CODE, BORDER, "forms.py", "", CODE_BLUE, 11)
    add_box_node(slide, c2_x + Inches(0.2), c2_y + Inches(1.8), Inches(4.3), Inches(0.5),
                 BG_CODE, BORDER, "Templates: predict / dashboard / api_docs", "", MUTED, 10)

    # depends_on
    add_box_node(slide, c2_x + Inches(0.2), c2_y + Inches(2.6), Inches(4.3), Inches(0.55),
                 BG_SECONDARY, WARNING, "depends_on: training-service (healthy)", "", WARNING, 10)

    # Arrow between containers
    add_arrow_right(slide, Inches(6.15), Inches(3.6), Inches(0.6), ACCENT_LIGHT)
    add_text(slide, Inches(6.0), Inches(3.15), Inches(0.9), Inches(0.3),
             "HTTP\nInternal DNS", size=8, color=ACCENT_LIGHT, align=PP_ALIGN.CENTER)

    slide_num(slide, sn, TOTAL); sn += 1

    # ── Docker Compose Code ──
    slide = new_slide(prs)
    title_bar(slide, "docker-compose.yml")
    compose = (
        "services:\n"
        "  training-service:\n"
        "    build: ./training-service\n"
        "    ports:\n"
        "      - \"8000:8000\"\n"
        "    volumes:\n"
        "      - ./data:/app/data\n"
        "      - ./models:/app/models\n"
        "      - ./mlruns:/app/mlruns\n"
        "      - ./logs:/app/logs\n"
        "    healthcheck:\n"
        "      test: curl -f http://localhost:8000/health\n"
        "    restart: unless-stopped\n"
        "\n"
        "  django-service:\n"
        "    build: ./django-service\n"
        "    ports:\n"
        "      - \"8080:8080\"\n"
        "    depends_on:\n"
        "      training-service:\n"
        "        condition: service_healthy"
    )
    add_code_block(slide, Inches(0.8), Inches(1.5), Inches(7), Inches(5.5), compose, font_size=12)

    feats = [
        ("Volumes", "4 shared bind mounts — data persists on host"),
        ("Healthcheck", "Docker pings /health every 30s"),
        ("depends_on", "Django won't start until API is healthy"),
        ("restart", "Auto-recover from crashes"),
        ("Internal DNS", "\"training-service\" resolves to container IP"),
        ("Port mapping", "Host 8000->API, Host 8080->Frontend"),
    ]
    for i, (feat, desc) in enumerate(feats):
        y = Inches(1.7) + Inches(i * 0.85)
        add_text(slide, Inches(8.3), y, Inches(4.5), Inches(0.25),
                 feat, size=13, color=SUCCESS, bold=True)
        add_text(slide, Inches(8.3), y + Pt(18), Inches(4.5), Inches(0.4),
                 desc, size=11, color=MUTED)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # SECTION 4 — CHEIKH
    # ================================================================
    section_header(prs, "Part 4: Frontend & CI/CD",
                   "Django web app, logging, GitHub Actions pipeline",
                   "Cheikh", sn, TOTAL); sn += 1

    # ── Django Frontend ──
    slide = new_slide(prs)
    title_bar(slide, "Django Frontend — 3 Pages")

    pages = [
        ("Predict", "Form with Location, Bedrooms, Bathrooms, SquareFeet.\nSubmits to FastAPI /predict via views.py.\nDisplays estimated price + model version.", ACCENT),
        ("Dashboard", "Live metrics from /metrics endpoint.\nR2, MAE, RMSE stat cards.\nModel parameters + features table.\nSystem status indicator.", SUCCESS),
        ("API Docs", "Interactive reference for all 4 endpoints.\nRequest/response examples.\nSyntax-highlighted code blocks.", INFO),
    ]
    for i, (name, desc, color) in enumerate(pages):
        y = Inches(1.5) + Inches(i * 1.9)
        add_rect(slide, Inches(0.8), y, Inches(11.5), Inches(1.7), BG_CARD, color)
        add_text(slide, Inches(1.2), y + Pt(8), Inches(3), Inches(0.35),
                 f"/{name.lower()}/", size=18, color=color, bold=True, font="Consolas")
        add_multiline_text(slide, Inches(4.5), y + Pt(6), Inches(7.5), Inches(1.4),
                           desc, size=12, color=MUTED, spacing=Pt(2))
    slide_num(slide, sn, TOTAL); sn += 1

    # ── Logging ──
    slide = new_slide(prs)
    title_bar(slide, "Logging & Observability")
    add_text(slide, Inches(0.8), Inches(1.4), Inches(3), Inches(0.3),
             "training.log", size=13, color=SUCCESS, bold=True)
    t_log = (
        "2026-02-19 11:09:15 -- train -- INFO -- STARTING TRAINING PIPELINE\n"
        "2026-02-19 11:09:15 -- train -- INFO -- Loading data from house_prices.csv\n"
        "2026-02-19 11:09:15 -- validate -- INFO -- Data validation passed (1000 rows)\n"
        "2026-02-19 11:09:16 -- train -- INFO -- Metrics: {rmse: 140982, r2: -0.112}\n"
        "2026-02-19 11:09:16 -- train -- INFO -- Model saved to *_20260219.joblib"
    )
    add_code_block(slide, Inches(0.8), Inches(1.8), Inches(11.5), Inches(1.8), t_log, font_size=10)

    add_text(slide, Inches(0.8), Inches(3.8), Inches(3), Inches(0.3),
             "api.log", size=13, color=ACCENT, bold=True)
    a_log = (
        "2026-02-19 11:09:48 -- api.main -- INFO -- FastAPI starting, loading model...\n"
        "2026-02-19 11:09:48 -- api.main -- INFO -- Model loaded and ready\n"
        "2026-02-19 11:10:02 -- api.main -- INFO -- Training triggered via API...\n"
        "2026-02-19 11:10:05 -- api.main -- INFO -- Model reloaded after training"
    )
    add_code_block(slide, Inches(0.8), Inches(4.2), Inches(11.5), Inches(1.5), a_log, font_size=10)

    add_text(slide, Inches(0.8), Inches(6.0), Inches(11), Inches(0.6),
             "Logs mounted via Docker volume — accessible from host even if container stops.",
             size=12, color=DIM)
    slide_num(slide, sn, TOTAL); sn += 1

    # ── CI/CD Pipeline DIAGRAM ──
    slide = new_slide(prs)
    title_bar(slide, "CI/CD Pipeline — GitHub Actions")

    # Trigger sources
    add_text(slide, Inches(0.5), Inches(1.5), Inches(2), Inches(0.3),
             "Triggers:", size=13, color=WHITE, bold=True)
    triggers = [
        ("Push src/**", ACCENT),
        ("Push data/**", SUCCESS),
        ("Manual dispatch", WARNING),
    ]
    for i, (trig, color) in enumerate(triggers):
        y = Inches(1.9) + Inches(i * 0.55)
        add_box_node(slide, Inches(0.5), y, Inches(2.2), Inches(0.45),
                     BG_CARD, color, trig, "", color, 10)

    add_arrow_right(slide, Inches(2.8), Inches(2.5), Inches(0.5), MUTED)

    # Stage 1
    s1_x = Inches(3.5)
    add_rect(slide, s1_x, Inches(1.5), Inches(2.6), Inches(3.5), BG_CARD, ACCENT)
    add_text(slide, s1_x + Pt(8), Inches(1.55), Inches(2.4), Inches(0.25),
             "Stage 1", size=10, color=ACCENT, bold=True)
    add_text(slide, s1_x + Pt(8), Inches(1.85), Inches(2.4), Inches(0.35),
             "Validate\nData", size=18, color=WHITE, bold=True)
    add_bullets(slide, [
        "Checkout code",
        "Install Pandera",
        "Run schema check",
        "Fail -> pipeline stops",
    ], s1_x + Pt(8), Inches(2.7), Inches(2.3), Inches(2), size=10, color=MUTED)

    add_arrow_right(slide, Inches(6.2), Inches(3.0), Inches(0.4), MUTED)

    # Stage 2
    s2_x = Inches(6.8)
    add_rect(slide, s2_x, Inches(1.5), Inches(2.6), Inches(3.5), BG_CARD, SUCCESS)
    add_text(slide, s2_x + Pt(8), Inches(1.55), Inches(2.4), Inches(0.25),
             "Stage 2", size=10, color=SUCCESS, bold=True)
    add_text(slide, s2_x + Pt(8), Inches(1.85), Inches(2.4), Inches(0.35),
             "Train\nModel", size=18, color=WHITE, bold=True)
    add_bullets(slide, [
        "Build Docker image",
        "Start training-service",
        "POST /train",
        "Save model + metrics",
    ], s2_x + Pt(8), Inches(2.7), Inches(2.3), Inches(2), size=10, color=MUTED)

    add_arrow_right(slide, Inches(9.5), Inches(3.0), Inches(0.4), MUTED)

    # Stage 3
    s3_x = Inches(10.1)
    add_rect(slide, s3_x, Inches(1.5), Inches(2.6), Inches(3.5), BG_CARD, WARNING)
    add_text(slide, s3_x + Pt(8), Inches(1.55), Inches(2.4), Inches(0.25),
             "Stage 3", size=10, color=WARNING, bold=True)
    add_text(slide, s3_x + Pt(8), Inches(1.85), Inches(2.4), Inches(0.35),
             "Deploy\nLocally", size=18, color=WHITE, bold=True)
    add_bullets(slide, [
        "docker compose down",
        "docker compose up",
        "Wait for healthcheck",
        "E2E prediction test",
    ], s3_x + Pt(8), Inches(2.7), Inches(2.3), Inches(2), size=10, color=MUTED)

    # Self-hosted runner note
    add_rect(slide, Inches(0.5), Inches(5.5), Inches(12.3), Inches(1.2), BG_CARD, BORDER)
    add_text(slide, Inches(0.8), Inches(5.6), Inches(2), Inches(0.3),
             "Self-Hosted Runner", size=13, color=INFO, bold=True)
    add_multiline_text(slide, Inches(0.8), Inches(5.95), Inches(11.5), Inches(0.6),
                       "Pipeline runs on our local machine (not GitHub cloud) because it needs Docker access.\n"
                       "GitHub triggers the workflow -> self-hosted runner executes all 3 stages locally.",
                       size=11, color=MUTED, spacing=Pt(2))
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # FULL LIFECYCLE DIAGRAM
    # ================================================================
    slide = new_slide(prs)
    title_bar(slide, "The Full MLOps Lifecycle")

    # Circular-ish lifecycle with 6 stages
    lifecycle = [
        ("CODE", "model.py\ndata/", ACCENT),
        ("VALIDATE", "Pandera\nchecks", SUCCESS),
        ("TRAIN", "train.py\nMLflow", WARNING),
        ("SERVE", "FastAPI\nDocker", INFO),
        ("MONITOR", "Logs\n/metrics", PURPLE),
        ("RETRAIN", "CI/CD\nAuto-trigger", ERROR),
    ]
    # Layout as a hexagonal cycle
    positions = [
        (Inches(2.5), Inches(1.6)),   # CODE - top left
        (Inches(5.5), Inches(1.6)),   # VALIDATE - top center
        (Inches(8.5), Inches(1.6)),   # TRAIN - top right
        (Inches(8.5), Inches(3.8)),   # SERVE - bottom right
        (Inches(5.5), Inches(3.8)),   # MONITOR - bottom center
        (Inches(2.5), Inches(3.8)),   # RETRAIN - bottom left
    ]
    for i, ((title, sub, color), (x, y)) in enumerate(zip(lifecycle, positions)):
        add_box_node(slide, x, y, Inches(2.2), Inches(1.6),
                     BG_CARD, color, title, sub, color, 18, 11, MUTED)

    # Arrows connecting them (clockwise)
    # Top row: right
    add_arrow_right(slide, Inches(4.75), Inches(2.25), Inches(0.7), DIM)
    add_arrow_right(slide, Inches(7.75), Inches(2.25), Inches(0.7), DIM)
    # Right side: down
    add_arrow_down(slide, Inches(9.45), Inches(3.3), Inches(0.45), DIM)
    # Bottom row: left (text arrows)
    add_text(slide, Inches(7.75), Inches(4.55), Inches(0.7), Inches(0.3),
             "<--", size=16, color=DIM, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(4.75), Inches(4.55), Inches(0.7), Inches(0.3),
             "<--", size=16, color=DIM, align=PP_ALIGN.CENTER)
    # Left side: up
    add_text(slide, Inches(3.15), Inches(3.3), Inches(0.5), Inches(0.5),
             "^", size=22, color=DIM, align=PP_ALIGN.CENTER, bold=True)

    add_text(slide, Inches(0.8), Inches(5.8), Inches(11.5), Inches(0.5),
             "Developer pushes code -> Pipeline validates -> Retrains -> Deploys -> Monitors -> Loop continues",
             size=14, color=MUTED, align=PP_ALIGN.CENTER)

    add_text(slide, Inches(0.8), Inches(6.4), Inches(11.5), Inches(0.4),
             "Automated by GitHub Actions — every push to src/ or data/ triggers the full cycle.",
             size=12, color=DIM, align=PP_ALIGN.CENTER)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # SUMMARY
    # ================================================================
    slide = new_slide(prs)
    title_bar(slide, "Project Summary")
    summary = [
        ["Component", "Owner", "What We Built", "Key Takeaway"],
        ["Data Pipeline", "Ralia", "Pandera validation + preprocessing", "Validate before you train"],
        ["Training + Tracking", "Cassidy", "RandomForest + MLflow + Joblib", "Track every experiment"],
        ["API + Containers", "Uriel", "FastAPI + Docker Compose", "Containerize for reproducibility"],
        ["Frontend + CI/CD", "Cheikh", "Django UI + GitHub Actions", "Automate the full cycle"],
    ]
    add_table(slide, Inches(0.5), Inches(1.5), Inches(12.3), summary,
              col_widths=[Inches(2.5), Inches(1.5), Inches(4.3), Inches(4)])

    add_multiline_text(slide, Inches(0.8), Inches(4.5), Inches(11), Inches(2),
                       "\"MLOps is about the system, not just the model.\n"
                       "A model in a notebook is useful to one person.\n"
                       "A model inside a pipeline — validated, versioned, served,\n"
                       "monitored, and automatically retrained — is useful to everyone.\"",
                       size=16, color=MUTED, align=PP_ALIGN.CENTER)
    slide_num(slide, sn, TOTAL); sn += 1

    # ================================================================
    # THANK YOU
    # ================================================================
    slide = new_slide(prs)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(2), SLIDE_WIDTH, Inches(3.5)
    )
    bar.fill.solid(); bar.fill.fore_color.rgb = BG_CARD; bar.line.fill.background()
    add_text(slide, Inches(2), Inches(2.4), Inches(9.3), Inches(0.9),
             "Thank You!", size=48, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), Inches(3.4), Inches(9.3), Inches(0.6),
             "Questions?", size=24, color=ACCENT, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), Inches(4.3), Inches(9.3), Inches(0.5),
             "Ralia  •  Cassidy  •  Uriel  •  Cheikh", size=16, color=MUTED,
             align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), Inches(5.7), Inches(9.3), Inches(0.4),
             "Junia School — Housing Price Predictor MLOps Project — Feb 2026",
             size=12, color=DIM, align=PP_ALIGN.CENTER)
    slide_num(slide, sn, TOTAL)

    return prs


# ============================================================
if __name__ == "__main__":
    import os
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentation")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "MLOps_Housing_Price_Predictor.pptx")
    prs = build_presentation()
    prs.save(out_path)
    print(f"Presentation saved to: {out_path}")
    print(f"Total slides: {len(prs.slides)}")

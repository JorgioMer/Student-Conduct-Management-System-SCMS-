# =============================================================================
#  PDF Export Module — SCMS Document Generation with CCIS ISO Header/Footer
# =============================================================================
"""
Handles PDF generation for reports and slip records with the official CCIS
ISO 9001:2015 header banner and CCIS footer (logo + program list + divider).

SETUP: Place these two image files alongside this script (or update the paths
below to wherever you store them in your project):
  - header_banner.jpg  (the Cor Jesu / ISO wide banner from the Word template)
  - footer_logo.png    (the CCIS circuit-board logo from the Word template)
"""

from reportlab.lib import pagesizes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate,
    BaseDocTemplate, Frame, PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path
import os
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from collections import Counter

# ── Image paths ───────────────────────────────────────────────────────────────
# Resolve image paths: look in backend directory first (development), then in 
# assets directory (PyInstaller bundle). Works both from source and built executable.
def _get_asset_path(filename):
    """Resolve asset path, checking multiple locations for flexibility."""
    # Check in backend directory first (development setup)
    backend_path = Path(__file__).parent / filename
    if backend_path.exists():
        return str(backend_path)
    
    # Check in assets directory (PyInstaller bundle and project structure)
    assets_path = Path(__file__).parent.parent / "assets" / filename
    if assets_path.exists():
        return str(assets_path)
    
    # Fallback to assets for runtime warning purposes
    return str(assets_path)

HEADER_BANNER_PATH = _get_asset_path("header_banner.jpg")   # full-width ISO banner
FOOTER_LOGO_PATH   = _get_asset_path("footer_logo.png")     # CCIS square logo

# ── Document Styling Constants ────────────────────────────────────────────────
NAVY             = HexColor("#1a3a52")
GOLD             = HexColor("#d4af37")
BLUE_CJC         = HexColor("#0070C0")
TAN_CJC          = HexColor("#948A54")
WHITE            = HexColor("#ffffff")
LIGHT_GRAY       = HexColor("#f5f5f5")
DARK_GRAY        = HexColor("#333333")
GREEN_SLIP_COLOR = HexColor("#4CAF50")
PINK_SLIP_COLOR  = HexColor("#E91E63")
BLUE_SLIP_COLOR  = HexColor("#2196F3")

# Page margins
MARGIN_TOP    = 1.65 * inch
MARGIN_BOTTOM = 1.10 * inch
MARGIN_LEFT   = 0.75 * inch
MARGIN_RIGHT  = 0.75 * inch

PAGE_W, PAGE_H = pagesizes.LETTER
BANNER_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
BANNER_H = BANNER_W * (247 / 1883)
LOGO_SIZE = 0.45 * inch
CONTENT_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT


# ── Helper ────────────────────────────────────────────────────────────────────
def _safe(text):
    """Encode to latin-1, replacing unmappable chars (e.g. em-dash). Never returns None."""
    if text is None:
        return '-'
    text = str(text)
    # Replace Unicode characters that can't be encoded in latin-1 with ASCII equivalents
    text = text.replace('—', '-')  # Em-dash → hyphen
    text = text.replace('–', '-')  # En-dash → hyphen
    text = text.replace('"', '"')  # Left double quote → regular quote
    text = text.replace('"', '"')  # Right double quote → regular quote
    text = text.replace(''', "'")  # Left single quote → apostrophe
    text = text.replace(''', "'")  # Right single quote → apostrophe
    return text.encode('latin-1', errors='replace').decode('latin-1')


def _wrap_text_for_table(text, is_header=False):
    """Wrap table cell text in a Paragraph object to enable text wrapping.
    
    Args:
        text: String to wrap
        is_header: True for header cells, False for data cells
    
    Returns:
        Paragraph object with appropriate styling for text wrapping
    """
    if text is None:
        text = '-'
    text = _safe(text)
    
    if is_header:
        style = ParagraphStyle(
            'TableHeader',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=WHITE,
            alignment=TA_CENTER
        )
    else:
        style = ParagraphStyle(
            'TableCell',
            fontName='Helvetica',
            fontSize=9,
            textColor=DARK_GRAY,
            alignment=TA_LEFT
        )
    
    return Paragraph(text, style)


def _wrap_table_row(row, is_header=False):
    """Wrap all cells in a table row with Paragraph objects for text wrapping.
    
    Args:
        row: List of cell values
        is_header: True for header row, False for data rows
    
    Returns:
        List of Paragraph-wrapped cells
    """
    return [_wrap_text_for_table(cell, is_header) for cell in row]


# ── Chart Generation Functions ────────────────────────────────────────────────
def _create_college_distribution_chart(college_data):
    """Create a bar chart showing slip distribution by college.
    
    Args:
        college_data: Dict with college codes as keys and slip counts as values
    
    Returns:
        BytesIO object containing the chart image
    """
    fig = Figure(figsize=(8, 5), dpi=90, facecolor='white')
    ax = fig.add_subplot(111)
    
    college_colors = {
        "CEDAS": "#FF6B6B",
        "CABE": "#4ECDC4",
        "CCIS": "#95E1D3",
        "COE": "#F9CA24",
        "CHS": "#6C5CE7",
        "CSP": "#A29BFE"
    }
    
    colleges = []
    green_counts = []
    pink_counts = []
    blue_counts = []
    colors = []
    
    for college_code in sorted(college_data.keys()):
        data = college_data[college_code]
        if data["total"] > 0:
            colleges.append(college_code)
            green_counts.append(data["green"])
            pink_counts.append(data["pink"])
            blue_counts.append(data["blue"])
            colors.append(college_colors.get(college_code, "#999999"))
    
    if colleges:
        x = range(len(colleges))
        width = 0.25
        
        bars1 = ax.bar([i - width for i in x], green_counts, width, label='Green Slips', color='#4CAF50', edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x, pink_counts, width, label='Pink Slips', color='#E91E63', edgecolor='black', linewidth=0.5)
        bars3 = ax.bar([i + width for i in x], blue_counts, width, label='Blue Slips', color='#2196F3', edgecolor='black', linewidth=0.5)
        
        ax.set_ylabel('Number of Slips', fontsize=10, fontweight='bold')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel('College', fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(colleges, fontsize=9)
        ax.legend(fontsize=9)
        ax.set_title('Slip Distribution by College', fontsize=12, fontweight='bold', pad=15)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
    else:
        ax.text(0.5, 0.5, 'No College Data Available', ha='center', va='center', fontsize=12, color='gray')
    
    fig.tight_layout()
    
    # Save to BytesIO buffer
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=90)
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer


def _create_slip_distribution_chart(green_count, pink_count, blue_count):
    """Create a pie chart showing overall slip distribution.
    
    Args:
        green_count: Number of green slips
        pink_count: Number of pink slips
        blue_count: Number of blue slips
    
    Returns:
        BytesIO object containing the chart image
    """
    fig = Figure(figsize=(6, 5), dpi=90, facecolor='white')
    ax = fig.add_subplot(111)
    
    sizes = [green_count, pink_count, blue_count]
    labels = [f'Green Slips\n({green_count})', f'Pink Slips\n({pink_count})', f'Blue Slips\n({blue_count})']
    colors = ['#4CAF50', '#E91E63', '#2196F3']
    explode = (0.05, 0.05, 0.05)
    
    if sum(sizes) > 0:
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90,
               explode=explode, shadow=True, textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax.set_title('Overall Slip Distribution', fontsize=12, fontweight='bold', pad=15)
    else:
        ax.text(0.5, 0.5, 'No Slip Data Available', ha='center', va='center', fontsize=12, color='gray')
    
    fig.tight_layout()
    
    # Save to BytesIO buffer
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=90)
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer


# ── Header and Footer ─────────────────────────────────────────────────────────
class CorJesuHeaderFooter(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self._ccis_title = _safe(kw.pop('title', 'SCMS Report') or 'SCMS Report')
        self.report_date = datetime.now().strftime("%B %d, %Y")
        BaseDocTemplate.__init__(
            self, filename,
            pagesize=pagesizes.LETTER,
            rightMargin=MARGIN_RIGHT,
            leftMargin=MARGIN_LEFT,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
            **kw
        )
        self.addPageTemplates(self._create_page_template())

    def _create_page_template(self):
        frame = Frame(
            MARGIN_LEFT, MARGIN_BOTTOM,
            PAGE_W - MARGIN_LEFT - MARGIN_RIGHT,
            PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
            id='normal'
        )
        return PageTemplate(id='default', frames=[frame], onPage=self._on_page)

    def _on_page(self, c, doc):
        c.saveState()
        c.setFont("Helvetica", 10)

        # ── HEADER ────────────────────────────────────────────────────
        banner_y = PAGE_H - MARGIN_LEFT - BANNER_H
        if os.path.exists(HEADER_BANNER_PATH):
            c.drawImage(HEADER_BANNER_PATH, MARGIN_LEFT, banner_y,
                        width=BANNER_W, height=BANNER_H,
                        preserveAspectRatio=True, mask='auto')
        else:
            c.setFillColor(NAVY)
            c.rect(MARGIN_LEFT, banner_y, BANNER_W, BANNER_H, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(PAGE_W / 2, banner_y + BANNER_H * 0.6, "Cor Jesu College")
            c.setFillColor(WHITE)
            c.setFont("Helvetica", 9)
            c.drawCentredString(PAGE_W / 2, banner_y + BANNER_H * 0.3,
                                "ISO 9001:2015 Certified | CHED Accredited")

        title_y = banner_y - 0.38 * inch
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(NAVY)
        c.drawString(MARGIN_LEFT, title_y, self._ccis_title)
        c.setFont("Helvetica", 8)
        c.setFillColor(DARK_GRAY)
        c.drawRightString(PAGE_W - MARGIN_RIGHT, title_y,
                          f"Generated: {self.report_date}")

        # ── FOOTER ────────────────────────────────────────────────────
        footer_top = MARGIN_BOTTOM - 0.08 * inch

        c.setStrokeColor(BLUE_CJC)
        c.setLineWidth(2.5)
        c.line(MARGIN_LEFT, footer_top + 0.55 * inch,
               PAGE_W - MARGIN_RIGHT, footer_top + 0.55 * inch)
        c.setLineWidth(0.75)
        c.line(MARGIN_LEFT, footer_top + 0.52 * inch,
               PAGE_W - MARGIN_RIGHT, footer_top + 0.52 * inch)

        if os.path.exists(FOOTER_LOGO_PATH):
            c.drawImage(FOOTER_LOGO_PATH, MARGIN_LEFT, footer_top,
                        width=LOGO_SIZE, height=LOGO_SIZE,
                        preserveAspectRatio=True, mask='auto')
        logo_right = MARGIN_LEFT + LOGO_SIZE + 0.10 * inch

        c.setFont("Helvetica-BoldOblique", 10)
        c.setFillColor(BLUE_CJC)
        c.drawString(logo_right, footer_top + 0.30 * inch,
                     "College of Computing & Information Sciences (CCIS)")
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(TAN_CJC)
        c.drawString(logo_right, footer_top + 0.16 * inch,
                     "Contact: (+63)(82) 553-2433 Loc. 169")
        c.drawString(logo_right, footer_top + 0.06 * inch,
                     "Email: computerstudies@g.cjc.edu.ph  |  FB: CJC - College of Computing and Information Sciences")

        prog_x = PAGE_W - MARGIN_RIGHT
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(TAN_CJC)
        c.drawRightString(prog_x, footer_top + 0.30 * inch,
                          "| Bachelor of Science in Computer Science")
        c.drawRightString(prog_x, footer_top + 0.18 * inch,
                          "| Bachelor of Science in Information Technology")
        c.drawRightString(prog_x, footer_top + 0.06 * inch,
                          "| Bachelor of Library and Information Science")

        c.restoreState()


# ── Style Definitions ─────────────────────────────────────────────────────────
def get_document_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=16, textColor=NAVY, spaceAfter=12,
        alignment=TA_CENTER, fontName='Helvetica-Bold'
    )
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'],
        fontSize=13, textColor=GOLD, spaceAfter=10,
        spaceBefore=10, fontName='Helvetica-Bold'
    )
    subsection_style = ParagraphStyle(
        'Subsection', parent=styles['Heading3'],
        fontSize=11, textColor=NAVY, spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['BodyText'],
        fontSize=10, textColor=DARK_GRAY,
        alignment=TA_JUSTIFY, spaceAfter=6
    )
    return {
        'title':      title_style,
        'section':    section_style,
        'subsection': subsection_style,
        'normal':     normal_style,
    }


# ── Table Styling ─────────────────────────────────────────────────────────────
def create_table_style(slip_type='mixed'):
    accent = {
        'green': GREEN_SLIP_COLOR,
        'pink':  PINK_SLIP_COLOR,
        'blue':  BLUE_SLIP_COLOR,
    }.get(slip_type, NAVY)
    return TableStyle([
        ('BACKGROUND',    (0, 0), (-1,  0), accent),
        ('TEXTCOLOR',     (0, 0), (-1,  0), WHITE),
        ('FONTNAME',      (0, 0), (-1,  0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1,  0), 10),
        ('ALIGN',         (0, 0), (-1,  0), 'CENTER'),
        ('VALIGN',        (0, 0), (-1,  0), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1,  0), 8),
        ('BOTTOMPADDING', (0, 0), (-1,  0), 8),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 9),
        ('TEXTCOLOR',     (0, 1), (-1, -1), DARK_GRAY),
        ('ALIGN',         (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 1), (-1, -1), 'TOP'),  # Changed from MIDDLE to TOP for wrapped text
        ('LEFTPADDING',   (0, 1), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 1), (-1, -1), 8),
        ('TOPPADDING',    (0, 1), (-1, -1), 8),     # Increased from 6 to 8
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),     # Increased from 6 to 8
        ('GRID',          (0, 0), (-1, -1), 0.5, grey),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
    ])


def _info_table_style():
    return TableStyle([
        ('FONTNAME',      (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',      (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 0), (-1, -1), 10),
        ('TEXTCOLOR',     (0, 0), (0, -1), NAVY),
        ('TEXTCOLOR',     (1, 0), (1, -1), DARK_GRAY),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),  # Changed from MIDDLE to TOP for wrapped text
        ('ALIGN',         (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN',         (1, 0), (1, -1), 'LEFT'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),     # Increased from 6 to 8
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),     # Increased from 6 to 8
        ('GRID',          (0, 0), (-1, -1), 0.5, grey),
        ('ROWBACKGROUNDS',(0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
    ])


# ── PDF Export Functions ──────────────────────────────────────────────────────
def generate_overview_report(output_path, records_data, period=None):
    current_month = period if period else datetime.now().strftime("%B %Y")
    doc = CorJesuHeaderFooter(
        output_path,
        title=f"Monthly Overview Report - {current_month}",
        docTitle="SCMS Monthly Overview"
    )
    story  = []
    styles = get_document_styles()

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"<b>Report Period:</b> {current_month}", styles['normal']))
    story.append(Spacer(1, 0.15 * inch))

    green_count = len(records_data.get('green', []))
    pink_count  = len(records_data.get('pink',  []))
    blue_count  = len(records_data.get('blue',  []))
    total       = green_count + pink_count + blue_count

    stats_data = [
        ['Metric', 'Count'],
        ['Green Slips (Dispensation/Excuse)', str(green_count)],
        ['Pink Slips (Penalty)',              str(pink_count)],
        ['Blue Slips (Violations)',           str(blue_count)],
        ['Total Records',                     str(total)],
    ]
    # Wrap header and data rows for text wrapping support
    stats_data = [_wrap_table_row(stats_data[0], is_header=True)] + [_wrap_table_row(row) for row in stats_data[1:]]
    stats_table = Table(stats_data, colWidths=[3.5 * inch, 1.5 * inch], splitByRow=True)
    stats_table.setStyle(create_table_style('mixed'))
    story.append(Paragraph("<b>Summary Statistics</b>", styles['section']))
    story.append(stats_table)
    story.append(Spacer(1, 0.25 * inch))

    if records_data.get('green'):
        story.append(Paragraph("Green Slips Report", styles['section']))
        headers    = ['Student No.', 'Name', 'Year', 'Type', 'Date', 'Status']
        green_data = [headers] + [
            [
                _safe(r[4] if len(r) > 4 else None),
                _safe(r[0] if len(r) > 0 else None),
                _safe(r[2] if len(r) > 2 else None),
                'Excuse' if (r[5] is False if len(r) > 5 else False) else 'Dispensation',
                _safe(str(r[6])[:10] if len(r) > 6 else None),
                _safe(r[8] if len(r) > 8 else 'Active'),
            ]
            for r in records_data['green'][:10]
        ]
        # Wrap header and data rows for text wrapping support
        green_data = [_wrap_table_row(green_data[0], is_header=True)] + [_wrap_table_row(row) for row in green_data[1:]]
        t = Table(green_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch], splitByRow=True)
        t.setStyle(create_table_style('green'))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    if records_data.get('pink'):
        story.append(PageBreak())
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("Pink Slips Report", styles['section']))
        headers   = ['Student No.', 'Name', 'Year', 'Course', 'Violation', 'Date Issued']
        pink_data = [headers] + [
            [
                _safe(r[4] if len(r) > 4 else None),
                _safe(r[0] if len(r) > 0 else None),
                _safe(r[2] if len(r) > 2 else None),
                _safe(r[1] if len(r) > 1 else None),
                _safe(r[6] if len(r) > 6 else None),
                _safe(str(r[5])[:10] if len(r) > 5 else None),
            ]
            for r in records_data['pink'][:10]
        ]
        # Wrap header and data rows for text wrapping support
        pink_data = [_wrap_table_row(pink_data[0], is_header=True)] + [_wrap_table_row(row) for row in pink_data[1:]]
        t = Table(pink_data, colWidths=[1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 1.2*inch, 0.9*inch], splitByRow=True)
        t.setStyle(create_table_style('pink'))
        story.append(t)
        story.append(Spacer(1, 0.4 * inch))

    if records_data.get('blue'):
        story.append(PageBreak())
        story.append(Spacer(1, 0.4 * inch))
        story.append(Paragraph("Blue Slips Report", styles['section']))
        headers   = ['Student No.', 'Name', 'Year', 'Violation', 'Severity', 'Date', 'Status']
        blue_data = [headers] + [
            [
                _safe(r[4] if len(r) > 4 else None),
                _safe(r[0] if len(r) > 0 else None),
                _safe(r[2] if len(r) > 2 else None),
                _safe(r[5] if len(r) > 5 else None),
                _safe(r[6] if len(r) > 6 else None),
                _safe(str(r[7])[:10] if len(r) > 7 else None),
                _safe(r[8] if len(r) > 8 else 'Active'),
            ]
            for r in records_data['blue'][:10]
        ]
        # Wrap header and data rows for text wrapping support
        blue_data = [_wrap_table_row(blue_data[0], is_header=True)] + [_wrap_table_row(row) for row in blue_data[1:]]
        t = Table(blue_data, colWidths=[1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch, 0.8*inch], splitByRow=True)
        t.setStyle(create_table_style('blue'))
        story.append(t)
        story.append(Spacer(1, 0.4 * inch))

    # ── Charts and College Summary ────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Visual Summary", styles['section']))
    story.append(Spacer(1, 0.15 * inch))
    
    # Overall slip distribution chart
    try:
        chart_buffer = _create_slip_distribution_chart(green_count, pink_count, blue_count)
        story.append(RLImage(chart_buffer, width=4.5*inch, height=3.75*inch))
        story.append(Spacer(1, 0.3 * inch))
    except Exception as e:
        story.append(Paragraph(f"<i>Chart unavailable: {str(e)}</i>", styles['normal']))
    
    # Build college data
    all_slips = records_data.get('green', []) + records_data.get('pink', []) + records_data.get('blue', [])
    college_data = {}
    for slip in all_slips:
        try:
            course = slip[1] if len(slip) > 1 else ""
            from backend.config import get_course_college, COLLEGES
            college_code = get_course_college(course) if course else None
            
            if college_code is None:
                continue
            
            if college_code not in college_data:
                college_data[college_code] = {"green": 0, "pink": 0, "blue": 0, "total": 0}
            
            if slip in records_data.get('green', []):
                college_data[college_code]["green"] += 1
            elif slip in records_data.get('pink', []):
                college_data[college_code]["pink"] += 1
            elif slip in records_data.get('blue', []):
                college_data[college_code]["blue"] += 1
            college_data[college_code]["total"] += 1
        except:
            pass
    
    # College distribution chart
    if college_data:
        story.append(PageBreak())
        story.append(Spacer(1, 0.5 * inch))
        
        try:
            chart_buffer = _create_college_distribution_chart(college_data)
            story.append(RLImage(chart_buffer, width=6*inch, height=3.75*inch))
            story.append(Spacer(1, 0.3 * inch))
        except Exception as e:
            story.append(Paragraph(f"<i>Chart unavailable: {str(e)}</i>", styles['normal']))
        
        # College summary table
        story.append(PageBreak())
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("College Summary", styles['section']))
        story.append(Spacer(1, 0.15 * inch))
        
        college_summary = [['College', 'Green', 'Pink', 'Blue', 'Total']]
        for college_code in sorted(college_data.keys()):
            data = college_data[college_code]
            college_summary.append([
                college_code,
                str(data['green']),
                str(data['pink']),
                str(data['blue']),
                str(data['total'])
            ])
        
        # Wrap header and data rows
        college_summary = [_wrap_table_row(college_summary[0], is_header=True)] + [_wrap_table_row(row) for row in college_summary[1:]]
        college_table = Table(college_summary, colWidths=[2.0*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch], splitByRow=True)
        college_table.setStyle(create_table_style('mixed'))
        story.append(college_table)

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "<b>Document Information:</b> This report contains confidential student conduct "
        "records. Authorized personnel only. Managed by the Office of the Prefect.",
        styles['normal']
    ))
    doc.build(story)
    return output_path


def generate_slip_report(output_path, slip_type, records_data, subtitle="", period=None):
    current_month = period if period else datetime.now().strftime("%B %Y")
    type_map = {
        'green': 'Green Slip Report',
        'pink':  'Pink Slip Report',
        'blue':  'Blue Slip Report',
    }
    report_title = type_map.get(slip_type, 'Green Slip Report')

    doc = CorJesuHeaderFooter(
        output_path,
        title=f"{report_title} - {current_month}",
        docTitle=report_title
    )
    story  = []
    styles = get_document_styles()

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(report_title, styles['section']))
    if subtitle:
        story.append(Paragraph(_safe(subtitle), styles['subsection']))
    story.append(Spacer(1, 0.15 * inch))

    if slip_type == 'green':
        headers    = ['Student No.', 'Name', 'Year', 'Type', 'Date', 'Days/Reason', 'Status']
        table_data = [headers] + [
            [
                _safe(r[4] if len(r) > 4 else None),
                _safe(r[0] if len(r) > 0 else None),
                _safe(r[2] if len(r) > 2 else None),
                'Excuse' if (r[5] is False if len(r) > 5 else False) else 'Dispensation',
                _safe(str(r[6])[:10] if len(r) > 6 else None),
                _safe(r[7] if len(r) > 7 else None),
                _safe(r[8] if len(r) > 8 else 'Active'),
            ]
            for r in records_data[:20]
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.9*inch, 1.0*inch, 0.8*inch]
    elif slip_type == 'pink':
        headers    = ['Student No.', 'Name', 'Year', 'Course', 'Violation', 'Date Issued']
        table_data = [headers] + [
            [
                _safe(r[4] if len(r) > 4 else None),
                _safe(r[0] if len(r) > 0 else None),
                _safe(r[2] if len(r) > 2 else None),
                _safe(r[1] if len(r) > 1 else None),
                _safe(r[6] if len(r) > 6 else None),
                _safe(str(r[5])[:10] if len(r) > 5 else None),
            ]
            for r in records_data[:20]
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 1.2*inch, 0.9*inch]
    else:  # blue
        headers    = ['Student No.', 'Name', 'Year', 'Violation', 'Severity', 'Date', 'Status']
        table_data = [headers] + [
            [
                _safe(r[4] if len(r) > 4 else None),
                _safe(r[0] if len(r) > 0 else None),
                _safe(r[2] if len(r) > 2 else None),
                _safe(r[5] if len(r) > 5 else None),
                _safe(r[6] if len(r) > 6 else None),
                _safe(str(r[7])[:10] if len(r) > 7 else None),
                _safe(r[8] if len(r) > 8 else 'Active'),
            ]
            for r in records_data[:20]
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.8*inch, 0.8*inch, 0.8*inch]

    # Wrap header and data rows for text wrapping support
    table_data = [_wrap_table_row(table_data[0], is_header=True)] + [_wrap_table_row(row) for row in table_data[1:]]
    t = Table(table_data, colWidths=col_widths, splitByRow=True)
    t.setStyle(create_table_style(slip_type))
    story.append(t)
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        f"<b>Total Records:</b> {len(records_data)}  "
        f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['normal']
    ))
    doc.build(story)
    return output_path


def generate_student_conduct_summary(output_path, student_data):
    current_month = datetime.now().strftime("%B %Y")
    doc = CorJesuHeaderFooter(
        output_path,
        title=f"Student Conduct Summary - {current_month}",
        docTitle="Student Conduct Summary"
    )
    story  = []
    styles = get_document_styles()

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Student Conduct Summary", styles['section']))
    story.append(Paragraph("Students with Most Recorded Slips This Semester",
                            styles['subsection']))
    story.append(Spacer(1, 0.15 * inch))

    headers    = ['Rank', 'Student No.', 'Student Name', 'Year',
                  'Green', 'Pink', 'Blue', 'Total']
    table_data = [headers] + [[_safe(c) for c in row] for row in student_data[:15]]
    
    # Wrap header and data rows for text wrapping support
    table_data = [_wrap_table_row(table_data[0], is_header=True)] + [_wrap_table_row(row) for row in table_data[1:]]
    
    t = Table(table_data,
              colWidths=[0.6*inch, 1.0*inch, 1.8*inch, 0.7*inch,
                         0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch],
              splitByRow=True)
    t.setStyle(create_table_style('mixed'))
    story.append(t)
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        "<b>Note:</b> This list helps the Office of the Prefect identify students who may need "
        "additional counseling, guidance, or follow-up actions. Data shown is for the current "
        "semester only.",
        styles['normal']
    ))
    doc.build(story)
    return output_path


def generate_individual_student_report(output_path, student_number,
                                        student_info, green_slips, pink_slips,
                                        blue_slips, get_course_college_fn,
                                        colleges_dict):
    """
    Generate a comprehensive individual student conduct report.

    IMPORTANT — the function signature has changed. Instead of fetching DB data
    internally, the caller now passes the already-fetched data in.  Update your
    call-site like this:

        from .db_blue_slip  import get_blue_slips
        from .db_pink_slip  import get_pink_slips
        from .db_green_slip import get_green_slips
        from .db_students   import get_student
        from .config        import get_course_college, COLLEGES

        pdf_path = generate_individual_student_report(
            output_path     = "/tmp/student_123.pdf",
            student_number  = "2023-001",
            student_info    = get_student("2023-001"),
            green_slips     = get_green_slips("2023-001"),
            pink_slips      = get_pink_slips("2023-001"),
            blue_slips      = get_blue_slips("2023-001"),
            get_course_college_fn = get_course_college,
            colleges_dict   = COLLEGES,
        )

    Args:
        output_path           : Destination PDF path
        student_number        : Student ID string
        student_info          : Tuple (stud_num, stud_name, stud_course,
                                       stud_year, school_yr, stud_status)
        green_slips           : List of green slip tuples
        pink_slips            : List of pink slip tuples
        blue_slips            : List of blue slip tuples
        get_course_college_fn : Callable(course_str) -> college_code_str
        colleges_dict         : Dict {college_code: college_full_name}

    Returns:
        output_path on success, None if student_info is falsy
    """
    if not student_info:
        return None

    stud_num, stud_name, stud_course, stud_year, school_yr, stud_status = student_info

    college_code = get_course_college_fn(stud_course) if stud_course else None
    college_name = colleges_dict.get(college_code, college_code or 'Unknown College')

    # Collect colleges that issued slips — ordered, deduped
    colleges_seen = {}
    for slip_list in (green_slips, pink_slips, blue_slips):
        for slip in slip_list:
            course = slip[1] if len(slip) > 1 else None
            code   = get_course_college_fn(course) if course else None
            if code and code not in colleges_seen:
                colleges_seen[code] = colleges_dict.get(code, code)

    doc = CorJesuHeaderFooter(
        output_path,
        title=f"Student Conduct Report - {_safe(stud_num)}",
        docTitle="Individual Student Conduct Report"
    )
    story  = []
    styles = get_document_styles()

    story.append(Spacer(1, 0.25 * inch))

    # ── PAGE 1: Student Info + Summary + Colleges ─────────────────────────────

    # Student Information
    story.append(Paragraph("Student Information", styles['section']))
    story.append(Spacer(1, 0.10 * inch))

    info_rows = [
        ['Student Number:', _safe(stud_num)],
        ['Full Name:',      _safe(stud_name)],
        ['Course:',         _safe(stud_course)],
        ['Year Level:',     _safe(stud_year)],
        ['College:',        _safe(college_name)],
        ['School Year:',    _safe(school_yr)],
        ['Status:',         _safe(stud_status) if stud_status else 'Active'],
    ]
    # Wrap rows for text wrapping support
    info_rows = [_wrap_table_row(row) for row in info_rows]
    info_table = Table(info_rows, colWidths=[1.6 * inch, CONTENT_W - 1.6 * inch])
    info_table.setStyle(_info_table_style())
    story.append(info_table)
    story.append(Spacer(1, 0.30 * inch))

    # Conduct Summary
    story.append(Paragraph("Conduct Summary", styles['section']))
    story.append(Spacer(1, 0.10 * inch))

    total_slips = len(green_slips) + len(pink_slips) + len(blue_slips)
    summary_rows = [
        ['Slip Type',                           'Count'],
        ['Green Slips (Dispensation / Excuse)', str(len(green_slips))],
        ['Pink Slips (Penalty)',                str(len(pink_slips))],
        ['Blue Slips (Violations)',             str(len(blue_slips))],
        ['Total Slips',                         str(total_slips)],
    ]
    # Wrap header and data rows for text wrapping support
    summary_rows = [_wrap_table_row(summary_rows[0], is_header=True)] + [_wrap_table_row(row) for row in summary_rows[1:]]
    summary_table = Table(summary_rows, colWidths=[3.5 * inch, 1.5 * inch], splitByRow=True)
    summary_table.setStyle(create_table_style('mixed'))
    story.append(summary_table)
    story.append(Spacer(1, 0.30 * inch))

    # Colleges Where Slips Were Availed
    story.append(Paragraph("Colleges Where Slips Were Availed", styles['section']))
    story.append(Spacer(1, 0.10 * inch))

    if colleges_seen:
        col_rows = [['#', 'College / Office']]
        for i, (code, name) in enumerate(colleges_seen.items(), 1):
            col_rows.append([str(i), _safe(code)])

        # Wrap header and data rows for text wrapping support
        col_rows = [_wrap_table_row(col_rows[0], is_header=True)] + [_wrap_table_row(row) for row in col_rows[1:]]

        col_table = Table(
            col_rows,
            colWidths=[0.40 * inch, CONTENT_W - 0.40 * inch]
        )
        col_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND',    (0, 0), (-1, 0),  BLUE_CJC),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  WHITE),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0),  10),
            ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
            ('VALIGN',        (0, 0), (-1, 0),  'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, 0),  8),
            ('BOTTOMPADDING', (0, 0), (-1, 0),  8),
            # Data rows
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 9),
            ('TEXTCOLOR',     (0, 1), (-1, -1), DARK_GRAY),
            ('ALIGN',         (0, 1), (0, -1),  'CENTER'),
            ('ALIGN',         (1, 1), (1, -1),  'LEFT'),
            ('VALIGN',        (0, 1), (-1, -1), 'TOP'),  # Changed from MIDDLE to TOP for wrapped text
            ('LEFTPADDING',   (0, 1), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 1), (-1, -1), 8),
            ('TOPPADDING',    (0, 1), (-1, -1), 8),     # Increased from 6 to 8
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),     # Increased from 6 to 8
            ('GRID',          (0, 0), (-1, -1), 0.5, grey),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ]))
        story.append(col_table)
    else:
        story.append(Paragraph(
            "No college data available for this student's recorded slips.",
            styles['normal']
        ))
    story.append(Spacer(1, 0.30 * inch))

    # ── Detailed Slip Pages ───────────────────────────────────────────────────

    def _college_label(slip):
        course = slip[1] if len(slip) > 1 else None
        code   = get_course_college_fn(course) if course else None
        return _safe(code if code else 'Unknown')

    # Green Slips detail
    if green_slips:
        story.append(PageBreak())
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Green Slips - Dispensation / Excuse", styles['section']))
        story.append(Spacer(1, 0.10 * inch))

        # slip indices: name[0] course[1] year[2] recordID[3] studNum[4]
        #               isExcuse[5] date[6] daysOrReason[7] status[8]
        g_headers = ['#', 'Date', 'Type', 'Days / Reason', 'Status', 'College']
        g_col_w   = [0.30*inch, 0.90*inch, 1.00*inch, 2.20*inch, 0.80*inch, 0.90*inch]
        g_rows    = [g_headers]
        for i, slip in enumerate(green_slips, 1):
            g_rows.append([
                str(i),
                _safe(str(slip[6])[:10] if len(slip) > 6 and slip[6] else None),
                'Excuse' if (slip[5] is False if len(slip) > 5 else False) else 'Dispensation',
                _safe(slip[7] if len(slip) > 7 else None),
                _safe(slip[8] if len(slip) > 8 else 'Active'),
                _college_label(slip),
            ])
        # Wrap header and data rows for text wrapping support
        g_rows = [_wrap_table_row(g_rows[0], is_header=True)] + [_wrap_table_row(row) for row in g_rows[1:]]
        g_table = Table(g_rows, colWidths=g_col_w, splitByRow=True)
        g_table.setStyle(create_table_style('green'))
        g_table.setStyle(TableStyle([
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Ensure wrapped text aligns to top
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),
        ]))
        story.append(g_table)
        story.append(Spacer(1, 0.25 * inch))

    # Pink Slips detail
    if pink_slips:
        story.append(PageBreak())
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Pink Slips - Penalty", styles['section']))
        story.append(Spacer(1, 0.10 * inch))

        # slip indices: name[0] course[1] year[2] recordID[3] studNum[4]
        #               violationType[5] dateOfIncident[6] actionTaken[7] status[8]
        p_headers = ['#', 'Date', 'Violation', 'Action Taken', 'Status', 'College']
        p_col_w   = [0.30*inch, 0.90*inch, 1.30*inch, 1.90*inch, 0.80*inch, 0.90*inch]
        p_rows    = [p_headers]
        for i, slip in enumerate(pink_slips, 1):
            p_rows.append([
                str(i),
                _safe(str(slip[6])[:10] if len(slip) > 6 and slip[6] else None),
                _safe(slip[5] if len(slip) > 5 else None),
                _safe(slip[7] if len(slip) > 7 else None),
                _safe(slip[8] if len(slip) > 8 else 'Active'),
                _college_label(slip),
            ])
        # Wrap header and data rows for text wrapping support
        p_rows = [_wrap_table_row(p_rows[0], is_header=True)] + [_wrap_table_row(row) for row in p_rows[1:]]
        p_table = Table(p_rows, colWidths=p_col_w, splitByRow=True)
        p_table.setStyle(create_table_style('pink'))
        p_table.setStyle(TableStyle([
            ('ALIGN', (2, 1), (3, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Ensure wrapped text aligns to top
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),
        ]))
        story.append(p_table)
        story.append(Spacer(1, 0.25 * inch))

    # Blue Slips detail
    if blue_slips:
        story.append(PageBreak())
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Blue Slips - Violations", styles['section']))
        story.append(Spacer(1, 0.10 * inch))

        # slip indices: name[0] course[1] year[2] recordID[3] studNum[4]
        #               violationType[5] severityLevel[6] actionTaken[7]
        #               date[7] status[8/9] — adjust if your tuple differs
        b_headers = ['#', 'Date', 'Violation', 'Severity', 'Action Taken', 'Status', 'College']
        b_col_w   = [0.30*inch, 0.85*inch, 1.15*inch, 0.80*inch, 1.45*inch, 0.75*inch, 0.90*inch]
        b_rows    = [b_headers]
        for i, slip in enumerate(blue_slips, 1):
            b_rows.append([
                str(i),
                _safe(str(slip[7])[:10] if len(slip) > 7 and slip[7] else None),
                _safe(slip[5] if len(slip) > 5 else None),
                _safe(slip[6] if len(slip) > 6 else None),
                _safe(slip[8] if len(slip) > 8 else None),
                _safe(slip[9] if len(slip) > 9 else 'Active'),
                _college_label(slip),
            ])
        # Wrap header and data rows for text wrapping support
        b_rows = [_wrap_table_row(b_rows[0], is_header=True)] + [_wrap_table_row(row) for row in b_rows[1:]]
        b_table = Table(b_rows, colWidths=b_col_w, splitByRow=True)
        b_table.setStyle(create_table_style('blue'))
        b_table.setStyle(TableStyle([
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Ensure wrapped text aligns to top
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            ('ALIGN', (6, 1), (6, -1), 'LEFT'),
        ]))
        story.append(b_table)
        story.append(Spacer(1, 0.25 * inch))

    # No records fallback
    if not (green_slips or pink_slips or blue_slips):
        story.append(Spacer(1, 0.20 * inch))
        story.append(Paragraph(
            "<b>No records found:</b> This student has no slip records in the system.",
            styles['normal']
        ))

    # Closing note
    story.append(Spacer(1, 0.30 * inch))
    story.append(Paragraph(
        f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
        "<b>Confidentiality Notice:</b> This report contains confidential student conduct "
        "records. For authorised personnel only.",
        styles['normal']
    ))

    doc.build(story)
    return output_path
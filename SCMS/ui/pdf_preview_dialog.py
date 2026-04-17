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

# ── Image paths ───────────────────────────────────────────────────────────────
# Resolve relative to this file's directory so imports from anywhere work.
_HERE = Path(__file__).parent
HEADER_BANNER_PATH = str(_HERE / "header_banner.jpg")   # full-width ISO banner
FOOTER_LOGO_PATH   = str(_HERE / "footer_logo.png")     # CCIS square logo

# ── Document Styling Constants ────────────────────────────────────────────────
NAVY       = HexColor("#1a3a52")
GOLD       = HexColor("#d4af37")
BLUE_CJC   = HexColor("#0070C0")   # matches the Word template CCIS blue
TAN_CJC    = HexColor("#948A54")   # matches the Word template program-list tan
WHITE      = HexColor("#ffffff")
LIGHT_GRAY = HexColor("#f5f5f5")
DARK_GRAY  = HexColor("#333333")
GREEN_SLIP_COLOR = HexColor("#4CAF50")
PINK_SLIP_COLOR  = HexColor("#E91E63")
BLUE_SLIP_COLOR  = HexColor("#2196F3")

# Page margins
MARGIN_TOP    = 1.45 * inch   # extra room for the tall banner
MARGIN_BOTTOM = 1.10 * inch   # room for footer
MARGIN_LEFT   = 0.75 * inch
MARGIN_RIGHT  = 0.75 * inch

# Header / footer geometry (Letter: 8.5 × 11 inches)
PAGE_W, PAGE_H = pagesizes.LETTER

# Banner: full content width, proportional height
BANNER_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
BANNER_H = BANNER_W * (247 / 1883)   # original image aspect ratio

# Footer logo: small square on the left
LOGO_SIZE = 0.45 * inch


# ── Header and Footer Functions ────────────────────────────────────────────────
class CorJesuHeaderFooter(BaseDocTemplate):
    """
    Custom PDF document using the official CCIS ISO header banner and
    CCIS footer (logo + CCIS name/contact + program list + rule line).
    """

    def __init__(self, filename, **kw):
        self._ccis_title = str(kw.pop('title', 'SCMS Report') or 'SCMS Report')
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

    # ------------------------------------------------------------------
    def _on_page(self, c, doc):
        c.saveState()
        c.setFont("Helvetica", 10)   # ensure a font is active before any text ops

        # ── HEADER ────────────────────────────────────────────────────
        # Draw the ISO/Cor Jesu banner image
        banner_y = PAGE_H - MARGIN_LEFT - BANNER_H   # top of page minus margin
        if os.path.exists(HEADER_BANNER_PATH):
            c.drawImage(
                HEADER_BANNER_PATH,
                MARGIN_LEFT, banner_y,
                width=BANNER_W, height=BANNER_H,
                preserveAspectRatio=True, mask='auto'
            )
        else:
            # Fallback text header if image is missing
            c.setFillColor(NAVY)
            c.rect(MARGIN_LEFT, banner_y, BANNER_W, BANNER_H, fill=1, stroke=0)
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(PAGE_W / 2, banner_y + BANNER_H * 0.6,
                                "Cor Jesu College")
            c.setFillColor(WHITE)
            c.setFont("Helvetica", 9)
            c.drawCentredString(PAGE_W / 2, banner_y + BANNER_H * 0.3,
                                "ISO 9001:2015 Certified | CHED Accredited")

        # Report title & date just below the banner
        title_y = banner_y - 0.18 * inch
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(NAVY)
        # Encode to latin-1, replacing any unmappable characters (e.g. em-dash -> hyphen)
        safe_title = self._ccis_title.encode('latin-1', errors='replace').decode('latin-1')
        c.drawString(MARGIN_LEFT, title_y, safe_title)
        c.setFont("Helvetica", 8)
        c.setFillColor(DARK_GRAY)
        c.drawRightString(PAGE_W - MARGIN_RIGHT, title_y,
                          f"Generated: {self.report_date}")

        # ── FOOTER ────────────────────────────────────────────────────
        footer_top = MARGIN_BOTTOM - 0.08 * inch   # just inside bottom margin

        # Horizontal rule (thick-thin style matching the Word template)
        c.setStrokeColor(BLUE_CJC)
        c.setLineWidth(2.5)
        c.line(MARGIN_LEFT, footer_top + 0.55 * inch,
               PAGE_W - MARGIN_RIGHT, footer_top + 0.55 * inch)
        c.setLineWidth(0.75)
        c.line(MARGIN_LEFT, footer_top + 0.52 * inch,
               PAGE_W - MARGIN_RIGHT, footer_top + 0.52 * inch)

        # CCIS logo
        if os.path.exists(FOOTER_LOGO_PATH):
            c.drawImage(
                FOOTER_LOGO_PATH,
                MARGIN_LEFT, footer_top,
                width=LOGO_SIZE, height=LOGO_SIZE,
                preserveAspectRatio=True, mask='auto'
            )
        logo_right = MARGIN_LEFT + LOGO_SIZE + 0.10 * inch

        # Left block: CCIS name + contact
        c.setFont("Helvetica-BoldOblique", 10)
        c.setFillColor(BLUE_CJC)
        c.drawString(logo_right, footer_top + 0.30 * inch,
                     "College of Computing & Information Sciences (CCIS)")
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(TAN_CJC)
        c.drawString(logo_right, footer_top + 0.16 * inch,
                     "Contact: (+63)(82) 553-2433 Loc. 169")
        c.drawString(logo_right, footer_top + 0.06 * inch,
                     "Email: computerstudies@g.cjc.edu.ph  |  FB: CJC – College of Computing and Information Sciences")

        # Right block: programs
        prog_x = PAGE_W - MARGIN_RIGHT
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(TAN_CJC)
        c.drawRightString(prog_x, footer_top + 0.30 * inch,
                          "| Bachelor of Science in Computer Science")
        c.drawRightString(prog_x, footer_top + 0.18 * inch,
                          "| Bachelor of Science in Information Technology")
        c.drawRightString(prog_x, footer_top + 0.06 * inch,
                          "| Bachelor of Library and Information Science")

        # Page number centred below footer rule
        c.setFont("Helvetica", 7.5)
        c.setFillColor(DARK_GRAY)
        c.drawCentredString(PAGE_W / 2, 0.20 * inch, f"Page {doc.page}")

        c.restoreState()


# ── Style Definitions ─────────────────────────────────────────────────────────
def get_document_styles():
    """Return a dictionary of custom paragraph styles."""
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
        'title': title_style,
        'section': section_style,
        'subsection': subsection_style,
        'normal': normal_style,
    }


# ── Table Styling ─────────────────────────────────────────────────────────────
def create_table_style(slip_type='mixed'):
    accent = {
        'green': GREEN_SLIP_COLOR,
        'pink':  PINK_SLIP_COLOR,
        'blue':  BLUE_SLIP_COLOR,
    }.get(slip_type, NAVY)

    return TableStyle([
        ('BACKGROUND',   (0, 0), (-1,  0), accent),
        ('TEXTCOLOR',    (0, 0), (-1,  0), WHITE),
        ('FONTNAME',     (0, 0), (-1,  0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1,  0), 10),
        ('ALIGN',        (0, 0), (-1,  0), 'CENTER'),
        ('VALIGN',       (0, 0), (-1,  0), 'MIDDLE'),
        ('BOTTOMPADDING',(0, 0), (-1,  0), 8),
        ('FONTNAME',     (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1), 9),
        ('TEXTCOLOR',    (0, 1), (-1, -1), DARK_GRAY),
        ('ALIGN',        (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 1), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 1), (-1, -1), 6),
        ('RIGHTPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING',   (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 1), (-1, -1), 6),
        ('GRID',         (0, 0), (-1, -1), 0.5, grey),
        ('ROWBACKGROUNDS',(0,1), (-1, -1), [WHITE, LIGHT_GRAY]),
    ])


# ── PDF Export Functions ──────────────────────────────────────────────────────
def generate_overview_report(output_path, records_data):
    """
    Generate an overview report PDF with statistics and summaries.

    Args:
        output_path : Path where the PDF will be saved
        records_data: Dict with 'green', 'pink', 'blue' slip record lists
    Returns:
        Path to the generated PDF
    """
    doc = CorJesuHeaderFooter(
        output_path,
        title="Monthly Overview Report — November 2024",
        docTitle="SCMS Monthly Overview"
    )
    story  = []
    styles = get_document_styles()

    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("<b>Report Period:</b> November 2024", styles['normal']))
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
    stats_table = Table(stats_data, colWidths=[3.5 * inch, 1.5 * inch])
    stats_table.setStyle(create_table_style('mixed'))
    story.append(Paragraph("<b>Summary Statistics</b>", styles['section']))
    story.append(stats_table)
    story.append(Spacer(1, 0.25 * inch))

    if records_data.get('green'):
        story.append(Paragraph("Green Slips Report", styles['section']))
        headers    = ['Student No.', 'Name', 'Year', 'Type', 'Date', 'Status']
        green_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                'Excuse' if (r[5] is False if len(r) > 5 else False) else 'Dispensation',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data['green'][:10]
        ]
        t = Table(green_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch])
        t.setStyle(create_table_style('green'))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    if records_data.get('pink'):
        story.append(PageBreak())
        story.append(Paragraph("Pink Slips Report", styles['section']))
        headers   = ['Student No.', 'Name', 'Year', 'Violation', 'Date', 'Status']
        pink_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                str(r[5]) if len(r) > 5 else 'N/A',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data['pink'][:10]
        ]
        t = Table(pink_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1.2*inch, 0.9*inch, 0.8*inch])
        t.setStyle(create_table_style('pink'))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    if records_data.get('blue'):
        story.append(PageBreak())
        story.append(Paragraph("Blue Slips Report", styles['section']))
        headers   = ['Student No.', 'Name', 'Year', 'Violation', 'Severity', 'Date', 'Status']
        blue_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                str(r[5]) if len(r) > 5 else 'N/A',
                str(r[6]) if len(r) > 6 else 'N/A',
                str(r[7])[:10] if len(r) > 7 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data['blue'][:10]
        ]
        t = Table(blue_data, colWidths=[1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch, 0.8*inch])
        t.setStyle(create_table_style('blue'))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "<b>Document Information:</b> This report contains confidential student conduct "
        "records. Authorized personnel only. Managed by the Office of the Prefect.",
        styles['normal']
    ))
    doc.build(story)
    return output_path


def generate_slip_report(output_path, slip_type, records_data, subtitle=""):
    """
    Generate a single slip-type report PDF.

    Args:
        output_path : Path where the PDF will be saved
        slip_type   : 'green', 'pink', or 'blue'
        records_data: List of record tuples
        subtitle    : Optional subtitle for the report
    Returns:
        Path to the generated PDF
    """
    type_map = {
        'green': 'Green Slip Report',
        'pink':  'Pink Slip Report',
        'blue':  'Blue Slip Report',
    }
    report_title = type_map.get(slip_type, 'Green Slip Report')

    doc = CorJesuHeaderFooter(
        output_path,
        title=f"{report_title} — November 2024",
        docTitle=report_title
    )
    story  = []
    styles = get_document_styles()

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(report_title, styles['section']))
    if subtitle:
        story.append(Paragraph(subtitle, styles['subsection']))
    story.append(Spacer(1, 0.15 * inch))

    if slip_type == 'green':
        headers    = ['Student No.', 'Name', 'Year', 'Type', 'Date', 'Days/Reason', 'Status']
        table_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                'Excuse' if (r[5] is False if len(r) > 5 else False) else 'Dispensation',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[7]) if len(r) > 7 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data[:20]
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.9*inch, 1.0*inch, 0.8*inch]

    elif slip_type == 'pink':
        headers    = ['Student No.', 'Name', 'Year', 'Violation', 'Date Issued', 'Action Taken', 'Status']
        table_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                str(r[5]) if len(r) > 5 else 'N/A',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[7]) if len(r) > 7 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data[:20]
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.2*inch, 0.9*inch, 0.9*inch, 0.8*inch]

    else:  # blue
        headers    = ['Student No.', 'Name', 'Year', 'Violation', 'Severity', 'Date', 'Status']
        table_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                str(r[5]) if len(r) > 5 else 'N/A',
                str(r[6]) if len(r) > 6 else 'N/A',
                str(r[7])[:10] if len(r) > 7 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data[:20]
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.8*inch, 0.8*inch, 0.8*inch]

    t = Table(table_data, colWidths=col_widths)
    t.setStyle(create_table_style(slip_type))
    story.append(t)

    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        f"<b>Total Records:</b> {len(records_data)} — "
        f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['normal']
    ))
    doc.build(story)
    return output_path


def generate_student_conduct_summary(output_path, student_data):
    """
    Generate a student conduct summary report.

    Args:
        output_path : Path where the PDF will be saved
        student_data: List of tuples (rank, student_no, name, year, green, pink, blue, total)
    Returns:
        Path to the generated PDF
    """
    doc = CorJesuHeaderFooter(
        output_path,
        title="Student Conduct Summary — November 2024",
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
    table_data = [headers] + student_data[:15]
    t = Table(table_data,
              colWidths=[0.6*inch, 1.0*inch, 1.8*inch, 0.7*inch,
                         0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
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
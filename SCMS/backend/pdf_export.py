# =============================================================================
#  PDF Export Module — SCMS Document Generation with Cor Jesu Header
# =============================================================================
"""
Handles PDF generation for reports and slip records with professional branding,
header/footer templates, and filter-based exports.
"""

from reportlab.lib import pagesizes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate,
    BaseDocTemplate, Frame, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path
import os


# ── Document Styling Constants ────────────────────────────────────────────────
NAVY = HexColor("#1a3a52")
GOLD = HexColor("#d4af37")
WHITE = HexColor("#ffffff")
LIGHT_GRAY = HexColor("#f5f5f5")
DARK_GRAY = HexColor("#333333")
GREEN_SLIP_COLOR = HexColor("#4CAF50")
PINK_SLIP_COLOR = HexColor("#E91E63")
BLUE_SLIP_COLOR = HexColor("#2196F3")

# Page margins
MARGIN_TOP = 1.2 * inch
MARGIN_BOTTOM = 1.0 * inch
MARGIN_LEFT = 0.75 * inch
MARGIN_RIGHT = 0.75 * inch


# ── Header and Footer Functions ────────────────────────────────────────────────
class CorJesuHeaderFooter(BaseDocTemplate):
    """
    Custom PDF document with Cor Jesu College header and CCIS footer.
    """
    
    def __init__(self, filename, **kw):
        self.title = kw.get('title', 'SCMS Report')
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
        """Create page template with header and footer frames."""
        frame = Frame(
            MARGIN_LEFT, MARGIN_BOTTOM,
            pagesizes.LETTER[0] - MARGIN_LEFT - MARGIN_RIGHT,
            pagesizes.LETTER[1] - MARGIN_TOP - MARGIN_BOTTOM,
            id='normal'
        )
        
        template = PageTemplate(
            id='default',
            frames=[frame],
            onPage=self._on_page
        )
        return template

    def _on_page(self, canvas_obj, doc):
        """Draw header and footer on each page."""
        # Save canvas state
        canvas_obj.saveState()
        
        # Set font for header/footer
        canvas_obj.setFont("Helvetica-Bold", 10)
        
        # ── HEADER ────────────────────────────────────────────────────────
        # Header background
        canvas_obj.setFillColor(NAVY)
        canvas_obj.rect(
            MARGIN_LEFT - 0.2*inch,
            pagesizes.LETTER[1] - 1.15*inch,
            pagesizes.LETTER[0] - MARGIN_LEFT - MARGIN_RIGHT + 0.4*inch,
            1.1*inch,
            fill=1,
            stroke=0
        )
        
        # College Name (Top Center)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawCentredString(
            pagesizes.LETTER[0] / 2,
            pagesizes.LETTER[1] - 0.45*inch,
            "Cor Jesu College"
        )
        
        # Accreditation text (Center)
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.setFillColor(WHITE)
        canvas_obj.drawCentredString(
            pagesizes.LETTER[0] / 2,
            pagesizes.LETTER[1] - 0.65*inch,
            "ISO 9001:2015 Certified | CHED Accredited | Regional Educational Institution"
        )
        
        # Document Title (Right side)
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.drawString(
            MARGIN_LEFT,
            pagesizes.LETTER[1] - 0.85*inch,
            self.title
        )
        
        # Date (Right side, below title)
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.setFillColor(WHITE)
        canvas_obj.drawString(
            MARGIN_LEFT,
            pagesizes.LETTER[1] - 1.0*inch,
            f"Generated: {self.report_date}"
        )
        
        # ── FOOTER ────────────────────────────────────────────────────────
        # Footer background
        canvas_obj.setFillColor(LIGHT_GRAY)
        canvas_obj.rect(
            MARGIN_LEFT - 0.2*inch,
            0.1*inch,
            pagesizes.LETTER[0] - MARGIN_LEFT - MARGIN_RIGHT + 0.4*inch,
            0.75*inch,
            fill=1,
            stroke=0
        )
        
        # College of Computing & Information Sciences (Left)
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.setFillColor(NAVY)
        canvas_obj.drawString(
            MARGIN_LEFT,
            0.65*inch,
            "College of Computing & Information Sciences (CCIS)"
        )
        
        # Courses (Left, secondary)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(DARK_GRAY)
        canvas_obj.drawString(
            MARGIN_LEFT,
            0.50*inch,
            "Programs: BS Information Technology | BS Computer Science | BS Information Systems"
        )
        
        # Contact Information (Right)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(DARK_GRAY)
        canvas_obj.drawRightString(
            pagesizes.LETTER[0] - MARGIN_RIGHT,
            0.65*inch,
            "Office: +63 (0)2 8842-3600 ext. CCIS"
        )
        canvas_obj.drawRightString(
            pagesizes.LETTER[0] - MARGIN_RIGHT,
            0.50*inch,
            "Email: ccis@cjc.edu.ph | Web: www.cjc.edu.ph"
        )
        
        # Page number (Center, bottom)
        canvas_obj.setFont("Helvetica", 8)
        page_num = f"Page {doc.page}"
        canvas_obj.drawCentredString(
            pagesizes.LETTER[0] / 2,
            0.25*inch,
            page_num
        )
        
        # Restore canvas state
        canvas_obj.restoreState()


# ── Style Definitions ─────────────────────────────────────────────────────────
def get_document_styles():
    """Return a dictionary of custom paragraph styles."""
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=NAVY,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Section header style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=GOLD,
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    # Subsection style
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=NAVY,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    # Normal text
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=DARK_GRAY,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    return {
        'title': title_style,
        'section': section_style,
        'subsection': subsection_style,
        'normal': normal_style,
    }


# ── Table Styling ─────────────────────────────────────────────────────────────
def create_table_style(slip_type='mixed'):
    """
    Create table style based on slip type.
    slip_type: 'green', 'pink', 'blue', or 'mixed'
    """
    if slip_type == 'green':
        accent_color = GREEN_SLIP_COLOR
    elif slip_type == 'pink':
        accent_color = PINK_SLIP_COLOR
    elif slip_type == 'blue':
        accent_color = BLUE_SLIP_COLOR
    else:
        accent_color = NAVY
    
    return TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), accent_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), DARK_GRAY),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 1), (-1, -1), 6),
        ('RIGHTPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Borders
        ('GRID', (0, 0), (-1, -1), 0.5, grey),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
    ])


# ── PDF Export Functions ──────────────────────────────────────────────────────
def generate_overview_report(output_path, records_data):
    """
    Generate an overview report PDF with statistics and summaries.
    
    Args:
        output_path: Path where the PDF will be saved
        records_data: Dict with 'green', 'pink', 'blue' slip counts and records
    
    Returns:
        Path to the generated PDF
    """
    doc = CorJesuHeaderFooter(
        output_path,
        title="Monthly Overview Report — November 2024",
        docTitle="SCMS Monthly Overview"
    )
    
    story = []
    styles = get_document_styles()
    
    # Add spacing for header
    story.append(Spacer(1, 0.3*inch))
    
    # Report period
    period_para = Paragraph(
        "<b>Report Period:</b> November 2024",
        styles['normal']
    )
    story.append(period_para)
    story.append(Spacer(1, 0.15*inch))
    
    # Summary statistics
    green_count = len(records_data.get('green', []))
    pink_count = len(records_data.get('pink', []))
    blue_count = len(records_data.get('blue', []))
    total = green_count + pink_count + blue_count
    
    stats_data = [
        ['Metric', 'Count'],
        ['Green Slips (Dispensation/Excuse)', str(green_count)],
        ['Pink Slips (Penalty)', str(pink_count)],
        ['Blue Slips (Violations)', str(blue_count)],
        ['Total Records', str(total)],
    ]
    
    stats_table = Table(stats_data, colWidths=[3.5*inch, 1.5*inch])
    stats_table.setStyle(create_table_style('mixed'))
    story.append(Paragraph("<b>Summary Statistics</b>", styles['section']))
    story.append(stats_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Green slips section
    if records_data.get('green'):
        story.append(Paragraph("Green Slips Report", styles['section']))
        green_records = records_data['green'][:10]  # Limit to 10 for preview
        headers = ['Student No.', 'Name', 'Year', 'Type', 'Date', 'Status']
        green_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                'Excuse' if (r[5] == False if len(r) > 5 else False) else 'Dispensation',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in green_records
        ]
        green_table = Table(green_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch])
        green_table.setStyle(create_table_style('green'))
        story.append(green_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Pink slips section
    if records_data.get('pink'):
        story.append(PageBreak())
        story.append(Paragraph("Pink Slips Report", styles['section']))
        pink_records = records_data['pink'][:10]
        headers = ['Student No.', 'Name', 'Year', 'Violation', 'Date', 'Status']
        pink_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                str(r[5]) if len(r) > 5 else 'N/A',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in pink_records
        ]
        pink_table = Table(pink_data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 1.2*inch, 0.9*inch, 0.8*inch])
        pink_table.setStyle(create_table_style('pink'))
        story.append(pink_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Blue slips section
    if records_data.get('blue'):
        story.append(PageBreak())
        story.append(Paragraph("Blue Slips Report", styles['section']))
        blue_records = records_data['blue'][:10]
        headers = ['Student No.', 'Name', 'Year', 'Violation', 'Severity', 'Date', 'Status']
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
            for r in blue_records
        ]
        blue_table = Table(blue_data, colWidths=[1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.9*inch, 0.8*inch, 0.8*inch])
        blue_table.setStyle(create_table_style('blue'))
        story.append(blue_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Footer note
    story.append(Spacer(1, 0.3*inch))
    footer_text = (
        "<b>Document Information:</b> This report contains confidential student conduct records. "
        "Authorized personnel only. Managed by the Office of the Prefect."
    )
    story.append(Paragraph(footer_text, styles['normal']))
    
    # Build PDF
    doc.build(story)
    return output_path


def generate_slip_report(output_path, slip_type, records_data, subtitle=""):
    """
    Generate a single slip type report PDF.
    
    Args:
        output_path: Path where the PDF will be saved
        slip_type: 'green', 'pink', or 'blue'
        records_data: List of record tuples
        subtitle: Optional subtitle for the report
    
    Returns:
        Path to the generated PDF
    """
    type_map = {
        'green': {'title': 'Green Slip Report', 'color': 'green'},
        'pink': {'title': 'Pink Slip Report', 'color': 'pink'},
        'blue': {'title': 'Blue Slip Report', 'color': 'blue'},
    }
    
    type_info = type_map.get(slip_type, type_map['green'])
    doc = CorJesuHeaderFooter(
        output_path,
        title=f"{type_info['title']} — November 2024",
        docTitle=type_info['title']
    )
    
    story = []
    styles = get_document_styles()
    
    # Add spacing for header
    story.append(Spacer(1, 0.3*inch))
    
    # Title and subtitle
    story.append(Paragraph(type_info['title'], styles['section']))
    if subtitle:
        story.append(Paragraph(subtitle, styles['subsection']))
    story.append(Spacer(1, 0.15*inch))
    
    # Build table based on slip type
    if slip_type == 'green':
        headers = ['Student No.', 'Name', 'Year', 'Type', 'Date', 'Days/Reason', 'Status']
        table_data = [headers] + [
            [
                str(r[4]) if len(r) > 4 else 'N/A',
                str(r[0]) if len(r) > 0 else 'N/A',
                str(r[2]) if len(r) > 2 else 'N/A',
                'Excuse' if (r[5] == False if len(r) > 5 else False) else 'Dispensation',
                str(r[6])[:10] if len(r) > 6 else 'N/A',
                str(r[7]) if len(r) > 7 else 'N/A',
                str(r[8]) if len(r) > 8 else 'Active',
            ]
            for r in records_data[:20]  # Show max 20 records
        ]
        col_widths = [1.0*inch, 1.3*inch, 0.8*inch, 1.0*inch, 0.9*inch, 1.0*inch, 0.8*inch]
    
    elif slip_type == 'pink':
        headers = ['Student No.', 'Name', 'Year', 'Violation', 'Date Issued', 'Action Taken', 'Status']
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
        headers = ['Student No.', 'Name', 'Year', 'Violation', 'Severity', 'Date', 'Status']
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
    
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(create_table_style(slip_type))
    story.append(table)
    
    # Summary info
    story.append(Spacer(1, 0.25*inch))
    summary_text = f"<b>Total Records:</b> {len(records_data)} — <b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    story.append(Paragraph(summary_text, styles['normal']))
    
    # Build PDF
    doc.build(story)
    return output_path


def generate_student_conduct_summary(output_path, student_data):
    """
    Generate a student conduct summary report with top offenders.
    
    Args:
        output_path: Path where the PDF will be saved
        student_data: List of tuples (rank, student_no, name, year, green, pink, blue, total)
    
    Returns:
        Path to the generated PDF
    """
    doc = CorJesuHeaderFooter(
        output_path,
        title="Student Conduct Summary — November 2024",
        docTitle="Student Conduct Summary"
    )
    
    story = []
    styles = get_document_styles()
    
    # Add spacing for header
    story.append(Spacer(1, 0.3*inch))
    
    # Title
    story.append(Paragraph("Student Conduct Summary", styles['section']))
    story.append(Paragraph("Students with Most Recorded Slips This Semester", styles['subsection']))
    story.append(Spacer(1, 0.15*inch))
    
    # Build student table
    headers = ['Rank', 'Student No.', 'Student Name', 'Year', 'Green', 'Pink', 'Blue', 'Total']
    table_data = [headers] + student_data[:15]  # Show max 15 students
    
    student_table = Table(table_data, colWidths=[0.6*inch, 1.0*inch, 1.8*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
    student_table.setStyle(create_table_style('mixed'))
    story.append(student_table)
    
    # Guidance note
    story.append(Spacer(1, 0.25*inch))
    note_text = (
        "<b>Note:</b> This list helps the Office of the Prefect identify students who may need additional "
        "counseling, guidance, or follow-up actions. Data shown is for the current semester only."
    )
    story.append(Paragraph(note_text, styles['normal']))
    
    # Build PDF
    doc.build(story)
    return output_path

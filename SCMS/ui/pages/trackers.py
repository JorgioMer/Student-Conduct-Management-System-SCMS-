# =============================================================================
#  SCMS — Record Trackers Page  (Combined Monthly Overview)
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QWidget, QFrame, QGridLayout,
    QDialog, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import (
    NAVY, GOLD, WHITE, OFF_WHITE, LIGHT_GRAY,
    MID_GRAY, TEXT_DARK, GREEN_SLIP, PINK_SLIP, BLUE_SLIP,
    btn_primary, btn_outline, btn_gold
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    StatTile, add_shadow, InfoDialog
)
from ui.pages.base_page import BasePage, page_header, build_record_table
from ui.data_events import data_events
from ui.pdf_preview_dialog import PDFPreviewDialog
from backend.pdf_export import generate_slip_report, generate_individual_student_report
from backend.db_activity_log import log_export, log_report_generated, log_batch_operation
import tempfile
import os
from datetime import datetime


def _apply_table_selection_style(table: QTableWidget, accent_color: str):
    """Apply row highlight + hover effect consistent with system theme."""
    table.setStyleSheet(table.styleSheet() + f"""
        QTableWidget::item:selected {{
            background: {accent_color};
            color: {WHITE};
        }}
        QTableWidget::item:selected:active {{
            background: {accent_color};
            color: {WHITE};
        }}
        QTableWidget::item:hover {{
            background: {accent_color}44;
            color: {TEXT_DARK};
        }}
    """)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)


# =============================================================================
#  Shared Record Detail Dialog
# =============================================================================
class RecordDetailDialog(QDialog):
    """
    Generic detail dialog for any slip record.
    Pass a list of (label, value) pairs and a slip_type colour key.
    Optionally pass slip_summary={slip_key: count} to show a summary strip.
    """
    SLIP_META = {
        "green":  {"colour": GREEN_SLIP, "bg": "#E8F5E9", "emoji": "🟢", "title": "Green Slip Record"},
        "pink":   {"colour": PINK_SLIP,  "bg": "#FCE4EC", "emoji": "🔴", "title": "Pink Slip Record"},
        "blue":   {"colour": BLUE_SLIP,  "bg": "#E3F2FD", "emoji": "🔵", "title": "Blue Slip Record"},
        "mixed":  {"colour": NAVY,       "bg": "#F0F4FF", "emoji": "📋", "title": "Slip Record Details"},
    }

    def __init__(self, fields: list, slip_type: str = "mixed",
                 slip_summary: dict = None, student_number: str = None, parent=None):
        super().__init__(parent)
        self.student_number = student_number
        meta = self.SLIP_META.get(slip_type, self.SLIP_META["mixed"])
        self.setWindowTitle(meta["title"])
        self.setMinimumWidth(520)
        self.setMaximumWidth(640)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(f"QDialog {{ background: {WHITE}; }}")
        self._slip_summary = slip_summary
        self._build(fields, meta)

    def _build(self, fields, meta):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Coloured header banner ────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"""
            QFrame {{
                background: {meta['colour']};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(20, 0, 20, 0)

        emoji_lbl = QLabel(meta["emoji"])
        emoji_lbl.setFont(QFont("Segoe UI Emoji", 22))
        emoji_lbl.setStyleSheet("color: white; background: transparent; border: none;")

        title_lbl = QLabel(meta["title"])
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_lbl.setStyleSheet("color: white; background: transparent; border: none;")

        h_lay.addWidget(emoji_lbl)
        h_lay.addSpacing(10)
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()
        outer.addWidget(header)

        # ── Slip Summary strip ────────────────────────────────────────────────
        if self._slip_summary:
            summary_frame = QFrame()
            summary_frame.setStyleSheet(f"""
                QFrame {{
                    background: #F8F9FA;
                    border-bottom: 1px solid {LIGHT_GRAY};
                }}
            """)
            s_lay = QHBoxLayout(summary_frame)
            s_lay.setContentsMargins(24, 10, 24, 10)
            s_lay.setSpacing(24)

            summary_title = QLabel("Slip Summary:")
            summary_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
            summary_title.setStyleSheet(
                f"color: {NAVY}; background: transparent; border: none;")
            s_lay.addWidget(summary_title)

            INDICATOR_MAP = {
                "green": (GREEN_SLIP, "Green Slip"),
                "pink":  (PINK_SLIP,  "Pink Slip"),
                "blue":  (BLUE_SLIP,  "Blue Slip"),
            }
            for slip_key, count in self._slip_summary.items():
                color, label_text = INDICATOR_MAP.get(
                    slip_key, (NAVY, slip_key.title() + " Slip"))
                item_lbl = QLabel()
                item_lbl.setFont(QFont("Segoe UI", 11))
                item_lbl.setTextFormat(Qt.RichText)
                item_lbl.setText(
                    f"<span style='color:{color}; font-size:15px;'>●</span> "
                    f"<span style='color:{TEXT_DARK};'>{label_text}:</span> "
                    f"<b style='color:{NAVY};'>{count}</b>"
                )
                item_lbl.setStyleSheet("background: transparent; border: none;")
                s_lay.addWidget(item_lbl)

            s_lay.addStretch()
            outer.addWidget(summary_frame)

        # ── Scrollable body ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        body = QWidget()
        body.setStyleSheet(f"background: {WHITE};")
        grid = QGridLayout(body)
        grid.setContentsMargins(24, 20, 24, 16)
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)

        for row_idx, (label, value) in enumerate(fields):
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet(f"""
                color: {NAVY};
                background: transparent;
                border: none;
                padding: 2px 0;
            """)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setFixedWidth(160)

            val = QLabel(str(value) if value else "—")
            val.setFont(QFont("Segoe UI", 11))
            val.setWordWrap(True)
            val.setStyleSheet(f"""
                color: {TEXT_DARK};
                background: {OFF_WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 6px;
                padding: 5px 10px;
            """)
            val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            grid.addWidget(lbl, row_idx, 0, alignment=Qt.AlignRight | Qt.AlignTop)
            grid.addWidget(val, row_idx, 1)

        scroll.setWidget(body)
        outer.addWidget(scroll)

        # ── Footer buttons ────────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border-top: 1px solid {LIGHT_GRAY};
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 10, 20, 10)
        f_lay.addStretch()

        # Export PDF button (if student number is available)
        if self.student_number:
            export_btn = QPushButton("  📄 Export as PDF  ")
            export_btn.setFixedHeight(36)
            export_btn.setCursor(Qt.PointingHandCursor)
            export_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #2196F3;
                    color: {WHITE};
                    border: none;
                    border-radius: 7px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 20px;
                }}
                QPushButton:hover {{
                    background: #1976D2;
                }}
            """)
            export_btn.clicked.connect(self._export_student_pdf)
            f_lay.addWidget(export_btn)

        close_btn = QPushButton("  Close ")
        close_btn.setFixedHeight(36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {NAVY};
                color: {GOLD};
                border: none;
                border-radius: 7px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {GOLD};
                color: {NAVY};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        f_lay.addWidget(close_btn)
        outer.addWidget(footer)

    def _export_student_pdf(self):
        """Export individual student conduct report as PDF."""
        try:
            temp_pdf = os.path.join(tempfile.gettempdir(), 
                                    f"StudentReport_{self.student_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            result = generate_individual_student_report(temp_pdf, self.student_number)
            if result:
                PDFPreviewDialog(temp_pdf, title="Student Conduct Report", parent=self).exec_()
            else:
                InfoDialog("Error", f"Student {self.student_number} not found in database.", 
                          success=False, parent=self).exec_()
        except Exception as e:
            InfoDialog("Error", f"Failed to generate report:\n{str(e)}", 
                      success=False, parent=self).exec_()


# =============================================================================
#  Helper: show warning or open dialog for a table + slip_type
# =============================================================================
def _view_selected_row(table: QTableWidget, slip_type: str, parent=None,
                       slip_summary: dict = None):
    """
    Read the currently selected row from *table*, build a field list,
    and open RecordDetailDialog.  Shows InfoDialog if nothing is selected.
    """
    selected = table.selectedItems()
    if not selected:
        InfoDialog(
            "No Record Selected",
            "Please select a student by clicking the Name or ID Number in the table.",
            success=False, parent=parent
        ).exec_()
        return

    row = table.currentRow()
    headers = [table.horizontalHeaderItem(c).text()
               for c in range(table.columnCount())]
    fields = []
    student_number = None
    
    for col, header in enumerate(headers):
        item = table.item(row, col)
        field_value = item.text() if item else "—"
        fields.append((header, field_value))
        
        # Try to extract student number from "Student No." column
        if header.lower() in ("student no.", "student number") and field_value != "—":
            student_number = field_value

    dlg = RecordDetailDialog(fields, slip_type=slip_type,
                             slip_summary=slip_summary, 
                             student_number=student_number, parent=parent)
    dlg.exec_()


# =============================================================================
#  TrackersPage
# =============================================================================
class TrackersPage(BasePage):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.staff_id = self.current_user.get("username", "UNKNOWN")
        self._combined_tiles = {}
        self._combined_table = None
        self._combined_layout = None
        self._combined_table_index = 2
        self._monthly_tiles = {}
        self._monthly_chart = None
        data_events.slips_changed.connect(self._on_slips_changed)
        self._build()

    def _build(self):
        header = QFrame()
        header.setFixedHeight(82)
        header.setStyleSheet(f"""
            QFrame {{
                background: #FFF8E1;
                border-radius: 12px;
                border: 1px solid {GOLD}40;
                border-left: 6px solid {GOLD};
            }}
        """)
        add_shadow(header, blur=12, y=3, color=(0, 0, 0, 18))

        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)

        h_left = QVBoxLayout()
        h_left.setSpacing(2)

        t_lbl = QLabel("   Record Trackers — Monthly Overview")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none; padding: 0;")

        s_lbl = QLabel("View and filter all slip records — Green, Pink, and Blue — in one place")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none; padding: 0;")

        h_left.addWidget(t_lbl)
        h_left.addWidget(s_lbl)
        h_lay.addLayout(h_left)
        h_lay.addStretch()

        self.main_layout.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(self._build_combined_tab(), "   All Records ")
        tabs.addTab(self._build_student_tab(),  "   Student Lookup ")
        tabs.addTab(self._build_monthly_tab(),  "   Monthly Summary ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Combined Records tab ──────────────────────────────────────────────────
    def _build_combined_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        green_slips = get_green_slips(None) or []
        pink_slips  = get_pink_slips(None)  or []
        blue_slips  = get_blue_slips(None)  or []

        green_count   = len(green_slips)
        pink_count    = len(pink_slips)
        blue_count    = len(blue_slips)
        total_records = green_count + pink_count + blue_count

        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            if len(r) > 1:
                all_students.add(r[1])
        students_tracked = len(all_students)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        self._combined_tiles = {}
        for label, val, colour in [
            ("Green Slips",      str(green_count),      GREEN_SLIP),
            ("Pink Slips",       str(pink_count),       PINK_SLIP),
            ("Blue Slips",       str(blue_count),       BLUE_SLIP),
            ("Total Records",    str(total_records),    NAVY),
            ("Students Tracked", str(students_tracked), GOLD),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self._combined_tiles[label] = tile
        lay.addLayout(tiles_row)

        # ── Filter Row ─────────────────────────────────────────────────────
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        add_shadow(filter_frame, blur=8, y=2, color=(0, 0, 0, 14))
        filter_outer = QHBoxLayout(filter_frame)
        filter_outer.setContentsMargins(12, 8, 12, 8)
        filter_outer.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("   Search by student name or number...")
        search.setFixedHeight(38)
        search.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                color: {TEXT_DARK};
                background: {OFF_WHITE};
            }}
            QLineEdit:focus {{
                border-color: {NAVY};
                background: {WHITE};
            }}
        """)
        filter_outer.addWidget(search, 2)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background: {LIGHT_GRAY}; border: none;")
        filter_outer.addWidget(sep)

        def make_filter_pair(items, width=150):
            pair = QFrame()
            pair.setStyleSheet("QFrame { border: none; background: transparent; }")
            p_lay = QHBoxLayout(pair)
            p_lay.setContentsMargins(0, 0, 0, 0)
            p_lay.setSpacing(0)

            combo = QComboBox()
            combo.addItems(items)
            combo.setFixedHeight(38)
            combo.setFixedWidth(width)
            combo.setStyleSheet(f"""
                QComboBox {{
                    border: 1.5px solid {LIGHT_GRAY};
                    border-right: none;
                    border-top-left-radius: 8px;
                    border-bottom-left-radius: 8px;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 0 10px;
                    font-size: 12px;
                    color: {TEXT_DARK};
                    background: {OFF_WHITE};
                }}
                QComboBox:hover {{
                    border-color: {NAVY};
                    border-right: none;
                }}
                QComboBox::drop-down {{ border: none; width: 0px; }}
                QComboBox::down-arrow {{ width: 0; height: 0; }}
                QComboBox QAbstractItemView {{
                    border: 1.5px solid {NAVY};
                    border-radius: 6px;
                    background: {WHITE};
                    selection-background-color: {NAVY};
                    selection-color: {GOLD};
                    padding: 4px;
                    font-size: 12px;
                }}
            """)

            ind_btn = QPushButton("■")
            ind_btn.setFixedSize(30, 38)
            ind_btn.setCursor(Qt.PointingHandCursor)
            ind_btn.setToolTip("Click to expand")
            ind_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {NAVY};
                    color: {GOLD};
                    border: 1.5px solid {NAVY};
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                    border-top-left-radius: 0px;
                    border-bottom-left-radius: 0px;
                    font-size: 9px;
                    font-weight: bold;
                    padding: 0;
                }}
                QPushButton:hover {{
                    background: {GOLD};
                    color: {NAVY};
                    border-color: {GOLD};
                }}
            """)
            ind_btn.clicked.connect(combo.showPopup)

            p_lay.addWidget(combo)
            p_lay.addWidget(ind_btn)
            return pair, combo

        slip_pair, slip_filter   = make_filter_pair(
            ["All Slip Types", "Green Slip", "Pink Slip", "Blue Slip"], width=145)
        month_pair, month_filter = make_filter_pair(
            ["This Month", "All Months", "Custom Range"], width=185)
        year_pair, year_filter   = make_filter_pair(
            ["All Years", "1st", "2nd", "3rd", "4th", "5th"], width=110)

        filter_outer.addWidget(slip_pair)
        filter_outer.addWidget(month_pair)
        filter_outer.addWidget(year_pair)

        # ── Custom Range Row ──────────────────────────────────────────────────
        custom_range_frame = QFrame()
        custom_range_frame.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
            }}
        """)
        custom_range_frame.setVisible(False)
        custom_lay = QHBoxLayout(custom_range_frame)
        custom_lay.setContentsMargins(12, 8, 12, 8)
        custom_lay.setSpacing(10)

        from_lbl = QLabel("From:")
        from_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        custom_lay.addWidget(from_lbl)

        month_combo_style = f"""
            QComboBox {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 6px;
                padding: 0 8px;
                font-size: 12px;
                color: {TEXT_DARK};
                background: {WHITE};
            }}
            QComboBox:hover {{ border-color: {NAVY}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                border: 1.5px solid {NAVY};
                background: {WHITE};
                selection-background-color: {NAVY};
                selection-color: {GOLD};
            }}
        """

        from_month = QComboBox()
        from_month.addItems([
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ])
        from_month.setFixedHeight(34); from_month.setFixedWidth(130)
        from_month.setStyleSheet(month_combo_style)
        custom_lay.addWidget(from_month)

        from_year = QComboBox()
        from_year.addItems(["2022","2023","2024","2025"])
        from_year.setCurrentText("2024")
        from_year.setFixedHeight(34); from_year.setFixedWidth(80)
        from_year.setStyleSheet(month_combo_style)
        custom_lay.addWidget(from_year)

        to_lbl = QLabel("To:")
        to_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        custom_lay.addWidget(to_lbl)

        to_month = QComboBox()
        to_month.addItems([
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ])
        to_month.setCurrentIndex(10)
        to_month.setFixedHeight(34); to_month.setFixedWidth(130)
        to_month.setStyleSheet(month_combo_style)
        custom_lay.addWidget(to_month)

        to_year = QComboBox()
        to_year.addItems(["2022","2023","2024","2025"])
        to_year.setCurrentText("2024")
        to_year.setFixedHeight(34); to_year.setFixedWidth(80)
        to_year.setStyleSheet(month_combo_style)
        custom_lay.addWidget(to_year)

        custom_lay.addStretch()

        apply_range_btn = QPushButton("Apply Range")
        apply_range_btn.setFixedHeight(34)
        apply_range_btn.setCursor(Qt.PointingHandCursor)
        apply_range_btn.setStyleSheet(f"""
            QPushButton {{
                background: {NAVY}; color: {GOLD};
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: bold; padding: 0 14px;
            }}
            QPushButton:hover {{ background: {GOLD}; color: {NAVY}; }}
        """)
        custom_lay.addWidget(apply_range_btn)

        def on_month_filter_changed(index):
            custom_range_frame.setVisible(month_filter.currentText() == "Custom Range")
        month_filter.currentIndexChanged.connect(on_month_filter_changed)

        lay.addWidget(filter_frame)
        lay.addWidget(custom_range_frame)

        # ── Apply Filter button ───────────────────────────────────────────────
        filter_btn = QPushButton(" Apply Filter")
        filter_btn.setFixedHeight(38)
        filter_btn.setFixedWidth(130)
        filter_btn.setCursor(Qt.PointingHandCursor)
        filter_btn.setStyleSheet(f"""
            QPushButton {{
                background: {NAVY}; color: {GOLD};
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: bold;
                padding: 0 14px; letter-spacing: 0.3px;
            }}
            QPushButton:hover {{ background: {GOLD}; color: {NAVY}; }}
            QPushButton:pressed {{
                background: {GOLD}; color: {NAVY};
                border: 1.5px solid {NAVY};
            }}
        """)
        filter_outer.addWidget(filter_btn)
        lay.addWidget(filter_frame)

        headers = ["#", "Student No.", "Student Name", "Year", "Course",
                   "Slip Type", "Date Filed", "Details", "Status"]
        sample = self._build_combined_sample()
        self._combined_table = build_record_table(headers, sample)
        _apply_table_selection_style(self._combined_table, NAVY)
        self._apply_combined_colors(self._combined_table)
        self._combined_table.setMinimumHeight(320)
        lay.addWidget(self._combined_table)
        self._combined_layout = lay
        self._combined_table_index = 2

        # ── Action Row — View button now wired ────────────────────────────────
        action_row = QHBoxLayout()
        action_row.addStretch()

        view_btn = QPushButton("   View")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(self._view_combined_record)

        export_btn = QPushButton("   Export")
        export_btn.setStyleSheet(btn_gold())
        export_btn.setFixedHeight(38)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self._export_combined_records)

        action_row.addWidget(view_btn)
        action_row.addWidget(export_btn)
        lay.addLayout(action_row)
        lay.addStretch()
        return w

    # ── View handler: All Records tab ─────────────────────────────────────────
    def _view_combined_record(self):
        """Determine slip type from the Slip Type column, build summary, open detail dialog."""
        if self._combined_table is None:
            return

        selected = self._combined_table.selectedItems()
        if not selected:
            InfoDialog(
                "No Record Selected",
                "Please select a student by clicking the Name or ID Number in the table.",
                success=False, parent=self
            ).exec_()
            return

        row = self._combined_table.currentRow()
        slip_cell = self._combined_table.item(row, 5)
        slip_text = slip_cell.text() if slip_cell else ""

        if "Green" in slip_text:
            slip_type = "green"
        elif "Pink" in slip_text:
            slip_type = "pink"
        elif "Blue" in slip_text:
            slip_type = "blue"
        else:
            slip_type = "mixed"

        stud_num_cell = self._combined_table.item(row, 1)
        stud_num = stud_num_cell.text() if stud_num_cell else ""
        slip_summary = self._get_student_slip_summary(stud_num)

        _view_selected_row(self._combined_table, slip_type, parent=self,
                           slip_summary=slip_summary)

    def _get_student_slip_summary(self, stud_num: str) -> dict:
        """Return {slip_key: count} for a given student number."""
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        summary = {}
        try:
            green = [r for r in (get_green_slips(None) or [])
                     if len(r) > 4 and str(r[4]).strip() == stud_num.strip()]
            if green:
                summary["green"] = len(green)
            pink = [r for r in (get_pink_slips(None) or [])
                    if len(r) > 4 and str(r[4]).strip() == stud_num.strip()]
            if pink:
                summary["pink"] = len(pink)
            blue = [r for r in (get_blue_slips(None) or [])
                    if len(r) > 4 and str(r[4]).strip() == stud_num.strip()]
            if blue:
                summary["blue"] = len(blue)
        except Exception:
            pass
        return summary if summary else None

    def _build_combined_sample(self):
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        sample = []
        all_records = []
        try:
            for record in (get_blue_slips(None)  or []): all_records.append(("blue",  record))
            for record in (get_green_slips(None) or []): all_records.append(("green", record))
            for record in (get_pink_slips(None)  or []): all_records.append(("pink",  record))
        except Exception:
            pass

        for i, (slip_type, record) in enumerate(all_records[:8], 1):
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                course    = record[1] if len(record) > 1 else "N/A"

                if slip_type == "blue":
                    slip_label = "🔵 Blue Slip"
                    details    = record[5] if len(record) > 5 else "N/A"
                    date       = str(record[6])[:10] if len(record) > 6 else "N/A"
                    status     = record[10] if len(record) > 10 else "Open / Pending"
                elif slip_type == "green":
                    is_disp    = record[5] == False if len(record) > 5 else False
                    slip_label = "🟢 Green (Disp.)" if is_disp else "🟢 Green (Excuse)"
                    details    = str(record[7]) if len(record) > 7 else "N/A"
                    date       = str(record[6])[:10] if len(record) > 6 else "N/A"
                    status     = record[8] if len(record) > 8 else "Active"
                else:
                    slip_label = "🔴 Pink Slip"
                    details    = record[6] if len(record) > 6 else "N/A"
                    date       = str(record[5])[:10] if len(record) > 5 else "N/A"
                    status     = "Completed"

                sample.append((str(i), stud_num, stud_name, year, course,
                               slip_label, date, details, status))
            except Exception:
                pass

        if not sample:
            sample = [("1", "No records", "Add records to see them here",
                       "-", "-", "-", "-", "-", "-")]
        return sample

    def _apply_combined_colors(self, table):
        SLIP_COLORS = {
            "🟢 Green (Disp.)":  (GREEN_SLIP, "#E8F5E9"),
            "🟢 Green (Excuse)": (GREEN_SLIP, "#E8F5E9"),
            "🔴 Pink Slip":      (PINK_SLIP,  "#FCE4EC"),
            "🔵 Blue Slip":      (BLUE_SLIP,  "#E3F2FD"),
        }
        for r in range(table.rowCount()):
            slip_val = table.item(r, 5).text() if table.item(r, 5) else ""
            if slip_val in SLIP_COLORS:
                fg, _ = SLIP_COLORS[slip_val]
                table.item(r, 5).setForeground(QColor(fg))

    def _refresh_combined_records(self):
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        green_slips = get_green_slips(None) or []
        pink_slips  = get_pink_slips(None)  or []
        blue_slips  = get_blue_slips(None)  or []

        green_count   = len(green_slips)
        pink_count    = len(pink_slips)
        blue_count    = len(blue_slips)
        total_records = green_count + pink_count + blue_count

        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            if len(r) > 1:
                all_students.add(r[1])
        students_tracked = len(all_students)

        if self._combined_tiles:
            self._combined_tiles["Green Slips"].set_value(green_count)
            self._combined_tiles["Pink Slips"].set_value(pink_count)
            self._combined_tiles["Blue Slips"].set_value(blue_count)
            self._combined_tiles["Total Records"].set_value(total_records)
            self._combined_tiles["Students Tracked"].set_value(students_tracked)

        if self._combined_table and self._combined_layout:
            headers = ["#", "Student No.", "Student Name", "Year", "Course",
                       "Slip Type", "Date Filed", "Details", "Status"]
            for i in range(self._combined_layout.count()):
                item = self._combined_layout.itemAt(i)
                if item and item.widget() is self._combined_table:
                    self._combined_layout.removeWidget(self._combined_table)
                    self._combined_table.deleteLater()
                    break
            self._combined_table = build_record_table(headers, self._build_combined_sample())
            _apply_table_selection_style(self._combined_table, NAVY)
            self._apply_combined_colors(self._combined_table)
            self._combined_table.setMinimumHeight(320)
            self._combined_layout.insertWidget(self._combined_table_index, self._combined_table)

    # ── Student Lookup tab ────────────────────────────────────────────────────
    def _build_student_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Student Record Lookup"))
        lay.addWidget(SubTitle("Search for a specific student and view all their slip records"))

        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        s_lay = QHBoxLayout(search_frame)
        s_lay.setContentsMargins(16, 12, 16, 12)
        s_lay.setSpacing(10)

        lbl = QLabel("Student Number:")
        lbl.setStyleSheet("border: none; background: transparent;")
        s_lay.addWidget(lbl)

        self.stud_search_edit = QLineEdit()
        self.stud_search_edit.setPlaceholderText("Type student number to search...")
        self.stud_search_edit.setFixedHeight(40)

        search_btn = QPushButton("   Search ")
        search_btn.setStyleSheet(btn_gold())
        search_btn.setFixedHeight(40)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)

        search_btn.clicked.connect(self._search_student)
        clear_btn.clicked.connect(self._clear_student_search)

        s_lay.addWidget(self.stud_search_edit, 1)
        s_lay.addWidget(search_btn)
        s_lay.addWidget(clear_btn)
        lay.addWidget(search_frame)

        self.profile_frame = QFrame()
        self.profile_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        self.profile_layout = QVBoxLayout(self.profile_frame)
        self.profile_layout.setContentsMargins(20, 14, 20, 14)
        self.profile_layout.setSpacing(8)

        profile_lbl = QLabel("Student Profile")
        profile_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        profile_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        self.profile_layout.addWidget(profile_lbl)

        divider = Divider()
        divider.setStyleSheet("border: none; background: #E0E0E0; max-height: 1px;")
        self.profile_layout.addWidget(divider)

        self.profile_empty = QLabel("Search for a student number to view their profile")
        self.profile_empty.setAlignment(Qt.AlignCenter)
        self.profile_empty.setStyleSheet(
            f"color: {MID_GRAY}; background: transparent; border: none; padding: 30px;"
        )
        self.profile_layout.addWidget(self.profile_empty)
        lay.addWidget(self.profile_frame)

        lay.addWidget(SectionTitle("Slip History"))
        self.history_table_container = QVBoxLayout()
        self.slip_history_empty = QLabel("Perform a search to view slip history")
        self.slip_history_empty.setAlignment(Qt.AlignCenter)
        self.slip_history_empty.setStyleSheet(f"color: {MID_GRAY}; padding: 30px; border: none;")
        self.history_table_container.addWidget(self.slip_history_empty)
        lay.addLayout(self.history_table_container)

        lay.addStretch()
        return w

    def _clear_profile_layout(self):
        while self.profile_layout.count() > 2:
            item = self.profile_layout.takeAt(2)
            widget = item.widget()
            if widget is not None:
                if widget is self.profile_empty:
                    widget.setParent(None)
                else:
                    widget.deleteLater()
                continue
            nested = item.layout()
            if nested is not None:
                while nested.count():
                    child = nested.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

    def _clear_history_layout(self):
        while self.history_table_container.count() > 0:
            item = self.history_table_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                if widget is self.slip_history_empty:
                    widget.setParent(None)
                else:
                    widget.deleteLater()

    def _search_student(self):
        from backend.db_students import get_student
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        search_term = self.stud_search_edit.text().strip()
        if not search_term:
            InfoDialog("Input Required", "Please enter a student number or name to search.",
                       success=False, parent=self).exec_()
            return

        student_info = get_student(search_term)
        if not student_info:
            InfoDialog("Not Found", f"No student found with number/name: {search_term}",
                       success=False, parent=self).exec_()
            return

        self._clear_profile_layout()

        stud_num    = student_info[0] if len(student_info) > 0 else "N/A"
        stud_name   = student_info[1] if len(student_info) > 1 else "N/A"
        stud_course = student_info[2] if len(student_info) > 2 else "N/A"
        stud_year   = student_info[3] if len(student_info) > 3 else "N/A"

        profile_grid = QGridLayout()
        profile_grid.setSpacing(12)

        for i, (label, value) in enumerate([
            ("Student Number:", stud_num),
            ("Student Name:",   stud_name),
            ("Year Level:",     stud_year),
            ("Course:",         stud_course),
        ]):
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")

            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 11))
            val.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")

            profile_grid.addWidget(lbl, i, 0, alignment=Qt.AlignRight)
            profile_grid.addWidget(val, i, 1, alignment=Qt.AlignLeft)

        self.profile_layout.addLayout(profile_grid)

        history_records = []
        try:
            for record in get_blue_slips(stud_num) or []:
                try:
                    violation = record[5] if len(record) > 5 else "N/A"
                    date      = str(record[6])[:10] if len(record) > 6 else "N/A"
                    status    = record[10] if len(record) > 10 else "Open"
                    history_records.append(("Blue Slip", violation, date, status))
                except:
                    pass

            for record in get_green_slips(stud_num) or []:
                try:
                    slip_type = "Dispensation" if (record[5] is True if len(record) > 5 else False) else "Excuse"
                    date      = str(record[6])[:10] if len(record) > 6 else "N/A"
                    status    = record[8] if len(record) > 8 else "Active"
                    history_records.append(("Green (" + slip_type + ")", date, status, "-"))
                except:
                    pass

            for record in get_pink_slips(stud_num) or []:
                try:
                    violation = record[6] if len(record) > 6 else "N/A"
                    date      = str(record[5])[:10] if len(record) > 5 else "N/A"
                    history_records.append(("Pink Slip", violation, date, "Completed"))
                except:
                    pass
        except:
            pass

        self._clear_history_layout()

        if not history_records:
            no_records = QLabel(f"No slip records found for {stud_name} ({stud_num})")
            no_records.setAlignment(Qt.AlignCenter)
            no_records.setStyleSheet(f"color: {MID_GRAY}; padding: 20px; border: none;")
            self.history_table_container.addWidget(no_records)
        else:
            headers = ["Slip Type", "Details", "Date", "Status"]
            history_table = build_record_table(headers, history_records)
            history_table.setMinimumHeight(280)
            self.history_table_container.addWidget(history_table)

    def _clear_student_search(self):
        self.stud_search_edit.clear()
        self._clear_profile_layout()
        self.profile_layout.addWidget(self.profile_empty)
        self._clear_history_layout()
        self.history_table_container.addWidget(self.slip_history_empty)

    # ── Monthly Summary tab ───────────────────────────────────────────────────
    def _build_monthly_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Monthly Record Summary"))
        lay.addWidget(SubTitle("Overview of all slip records grouped by month"))

        period_row = QHBoxLayout()
        lbl = QLabel("Select Month:")
        lbl.setStyleSheet("border: none; background: transparent;")
        period_row.addWidget(lbl)

        period = QComboBox()
        period.addItems(["December 2026","November 2026", "October 2026", "September 2026", "August 2026", "July 2026", "June 2026","May 2026","April 2026", "March 2026", "February 2026", "January 2026"])
        period.setFixedHeight(36)
        period.setFixedWidth(200)
        period_row.addWidget(period)
        period_row.addStretch()

        export_btn = QPushButton("   Export Monthly Report ")
        export_btn.setStyleSheet(btn_gold())
        export_btn.setFixedHeight(36)
        export_btn.clicked.connect(self._export_monthly_summary)
        period_row.addWidget(export_btn)
        lay.addLayout(period_row)

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        green_slips = get_green_slips(None) or []
        pink_slips  = get_pink_slips(None)  or []
        blue_slips  = get_blue_slips(None)  or []

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        for label, val, colour in [
            ("Green Slips", str(len(green_slips)), GREEN_SLIP),
            ("Pink Slips",  str(len(pink_slips)),  PINK_SLIP),
            ("Blue Slips",  str(len(blue_slips)),  BLUE_SLIP),
            ("Total",       str(len(green_slips) + len(pink_slips) + len(blue_slips)), NAVY),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self._monthly_tiles[label] = tile
        lay.addLayout(tiles_row)

        from ui.chart_widgets import CombinedAllSlipsChart
        self._monthly_chart = CombinedAllSlipsChart(w)
        self._monthly_chart.setMinimumHeight(380)
        lay.addWidget(self._monthly_chart)

        self._refresh_monthly_summary()
        lay.addStretch()
        return w

    def _refresh_monthly_chart(self, chart_widget):
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        blue_slips  = get_blue_slips(None)  or []
        green_slips = get_green_slips(None) or []
        pink_slips  = get_pink_slips(None)  or []
        chart_widget.update_data(len(green_slips), len(pink_slips), len(blue_slips))

    def _refresh_monthly_summary(self):
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        green_slips = get_green_slips(None) or []
        pink_slips  = get_pink_slips(None)  or []
        blue_slips  = get_blue_slips(None)  or []

        if self._monthly_tiles:
            self._monthly_tiles["Green Slips"].set_value(len(green_slips))
            self._monthly_tiles["Pink Slips"].set_value(len(pink_slips))
            self._monthly_tiles["Blue Slips"].set_value(len(blue_slips))
            self._monthly_tiles["Total"].set_value(len(green_slips) + len(pink_slips) + len(blue_slips))

        if self._monthly_chart:
            self._monthly_chart.update_data(len(green_slips), len(pink_slips), len(blue_slips))

    def _on_slips_changed(self):
        try:
            self._refresh_combined_records()
            self._refresh_monthly_summary()
        except Exception:
            pass

    # ── PDF Export Methods ────────────────────────────────────────────────────
    def _export_combined_records(self):
        """Export combined records from all slip types as PDF."""
        try:
            from backend.db_blue_slip import get_blue_slips
            from backend.db_green_slip import get_green_slips
            from backend.db_pink_slip import get_pink_slips
            
            green_slips = get_green_slips(None) or []
            pink_slips = get_pink_slips(None) or []
            blue_slips = get_blue_slips(None) or []
            
            # Combine all records
            all_records = green_slips + pink_slips + blue_slips
            
            if not all_records:
                InfoDialog(
                    "No Data",
                    "No records available to export.",
                    success=False,
                    parent=self
                ).exec_()
                return
            
            # Generate PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_pdf = os.path.join(tempfile.gettempdir(), f'SCMS_Combined_Records_{timestamp}.pdf')
            generate_slip_report(temp_pdf, 'mixed', all_records, 
                               "All Slip Types Combined - Monthly Overview")
            
            # Log the export action
            log_export(self.staff_id, "Combined Records Report", len(all_records))
            
            # Show preview dialog
            PDFPreviewDialog(temp_pdf, "All Records Export", parent=self).exec_()
        except Exception as e:
            InfoDialog(
                "Export Error",
                f"Failed to export records:\n{str(e)}",
                success=False,
                parent=self
            ).exec_()

    def _export_monthly_summary(self):
        """Export monthly summary report as PDF."""
        try:
            from backend.db_blue_slip import get_blue_slips
            from backend.db_green_slip import get_green_slips
            from backend.db_pink_slip import get_pink_slips
            from backend.db_students import get_student
            
            green_slips = get_green_slips(None) or []
            pink_slips = get_pink_slips(None) or []
            blue_slips = get_blue_slips(None) or []
            
            # Count slips per student for summary
            student_counts = {}
            for record in green_slips:
                stud_num = record[4] if len(record) > 4 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["green"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)
            
            for record in pink_slips:
                stud_num = record[4] if len(record) > 4 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["pink"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)
            
            for record in blue_slips:
                stud_num = record[4] if len(record) > 4 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["blue"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)
            
            # Build student data for export
            sorted_students = sorted(
                student_counts.items(),
                key=lambda x: x[1]["green"] + x[1]["pink"] + x[1]["blue"],
                reverse=True
            )
            
            student_data = []
            for rank, (stud_num, counts) in enumerate(sorted_students[:20], 1):
                try:
                    info = counts["info"]
                    stud_name = info[1] if info and len(info) > 1 else "Unknown"
                    year = info[3] if info and len(info) > 3 else "N/A"
                    total = counts["green"] + counts["pink"] + counts["blue"]
                    student_data.append((
                        str(rank), stud_num, stud_name, year,
                        str(counts["green"]), str(counts["pink"]),
                        str(counts["blue"]), str(total)
                    ))
                except:
                    pass
            
            if not student_data:
                InfoDialog(
                    "No Data",
                    "No student records available to export.",
                    success=False,
                    parent=self
                ).exec_()
                return
            
            # Generate PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            from backend.pdf_export import generate_student_conduct_summary
            temp_pdf = os.path.join(tempfile.gettempdir(), f'SCMS_Monthly_Summary_{timestamp}.pdf')
            generate_student_conduct_summary(temp_pdf, student_data)
            
            # Log the export action
            log_report_generated(self.staff_id, "Monthly Summary Report")
            
            # Show preview dialog
            PDFPreviewDialog(temp_pdf, "Monthly Summary Report", parent=self).exec_()
        except Exception as e:
            InfoDialog(
                "Export Error",
                f"Failed to export monthly summary:\n{str(e)}",
                success=False,
                parent=self
            ).exec_()


from ui.components import Divider
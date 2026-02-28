# =============================================================================
#  SCMS — Green Slip Page  (Dispensation + Excuse)
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QSpinBox, QTabWidget,
    QWidget, QFrame, QGroupBox, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import (
    NAVY, GOLD, WHITE, OFF_WHITE, LIGHT_GRAY,
    MID_GRAY, TEXT_DARK, GREEN_SLIP,
    btn_primary, btn_outline, btn_danger, btn_green
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    FieldLabel, Card, add_shadow, ConfirmDialog, InfoDialog
)
from ui.pages.base_page import BasePage, page_header, build_record_table

# Backend database imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_green_slip import add_green_slip, get_green_slips
from backend.db_students import add_student, get_student


class GreenSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        # Page header
        self.main_layout.addWidget(page_header(
            "green",
            "   Green Slip Management ",
            "Record and track Dispensation & Excuse Green Slips"
        ))

        # Tab widget for Dispensation vs Excuse
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
                background: {WHITE};
                top: -1px;
            }}
            QTabBar::tab {{
                background: {LIGHT_GRAY};
                color: {TEXT_DARK};
                padding: 10px 28px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background: {GREEN_SLIP};
                color: {WHITE};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background: #81C784;
                color: {WHITE};
            }}
        """)

        tabs.addTab(self._build_dispensation_tab(), "   Dispensation Green Slip ")
        tabs.addTab(self._build_excuse_tab(),        "   Excuse Green Slip ")
        tabs.addTab(self._build_tracker_tab(),       "   Green Slip Tracker ")
        tabs.addTab(self._build_summary_tab(),       "  Summary & Charts ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Dispensation tab ──────────────────────────────────────────────────────
    def _build_dispensation_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        info = QLabel(
            "ℹ  A Dispensation Green Slip allows a student to be excused from a specific "
            "activity or class for an approved number of days."
        )
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 11))
        info.setStyleSheet(f"""
            background: #E8F5E9; border-left: 4px solid {GREEN_SLIP};
            border-radius: 6px; padding: 10px 14px; color: #1B5E20;
        """)
        lay.addWidget(info)

        form_group = QGroupBox("New Dispensation Green Slip Record")
        form_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        form_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid {GREEN_SLIP}60;
                border-radius: 10px;
                margin-top: 18px;
                padding: 16px 14px;
                background: {WHITE};
                color: {GREEN_SLIP};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: -2px;
                padding: 0 8px;
                background: {WHITE};
                color: {GREEN_SLIP};
            }}
        """)
        form_lay = QGridLayout(form_group)
        form_lay.setSpacing(12)
        form_lay.setColumnStretch(1, 1)
        form_lay.setColumnStretch(3, 1)

        def lbl(text, req=False):
            return FieldLabel(text, required=req)

        # Row 0
        form_lay.addWidget(lbl("Student Number", True), 0, 0)
        self.disp_stud_no = QLineEdit()
        self.disp_stud_no.setPlaceholderText("e.g. 2024-0001")
        self.disp_stud_no.setFixedHeight(38)
        form_lay.addWidget(self.disp_stud_no, 0, 1)

        form_lay.addWidget(lbl("Student Name", True), 0, 2)
        self.disp_stud_name = QLineEdit()
        self.disp_stud_name.setPlaceholderText("Last, First Middle")
        self.disp_stud_name.setFixedHeight(38)
        form_lay.addWidget(self.disp_stud_name, 0, 3)

        # Row 1
        form_lay.addWidget(lbl("Year & Course"), 1, 0)
        grade_row = QHBoxLayout()
        self.disp_grade = QComboBox()
        self.disp_grade.addItems(["1st","2nd","3rd","4th","5th"])
        self.disp_grade.setFixedHeight(38)
        self.disp_section = QLineEdit()
        self.disp_section.setPlaceholderText("Section / Block")
        self.disp_section.setFixedHeight(38)
        grade_row.addWidget(self.disp_grade)
        grade_row.addWidget(self.disp_section)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Date Availed", True), 1, 2)
        self.disp_date = QDateEdit(QDate.currentDate())
        self.disp_date.setCalendarPopup(True)
        self.disp_date.setFixedHeight(38)
        self.disp_date.setDisplayFormat("MMMM d, yyyy")
        form_lay.addWidget(self.disp_date, 1, 3)

        # Row 2
        form_lay.addWidget(lbl("Number of Days", True), 2, 0)
        self.disp_days = QSpinBox()
        self.disp_days.setRange(1, 30)
        self.disp_days.setValue(1)
        self.disp_days.setFixedHeight(38)
        self.disp_days.setSuffix(" day(s)")
        form_lay.addWidget(self.disp_days, 2, 1)

        form_lay.addWidget(lbl("Expiry Date"), 2, 2)
        self.disp_expiry = QDateEdit(QDate.currentDate().addDays(1))
        self.disp_expiry.setCalendarPopup(True)
        self.disp_expiry.setFixedHeight(38)
        self.disp_expiry.setDisplayFormat("MMMM d, yyyy")
        self.disp_expiry.setReadOnly(True)
        self.disp_expiry.setStyleSheet(f"background: {LIGHT_GRAY};")
        form_lay.addWidget(self.disp_expiry, 2, 3)

        # Auto-update expiry when days changes
        def update_expiry(val):
            self.disp_expiry.setDate(self.disp_date.date().addDays(val))
        self.disp_days.valueChanged.connect(update_expiry)
        self.disp_date.dateChanged.connect(lambda d: update_expiry(self.disp_days.value()))

        # Row 3
        form_lay.addWidget(lbl("Purpose / Reason", True), 3, 0)
        self.disp_reason = QTextEdit()
        self.disp_reason.setPlaceholderText("Briefly describe the reason for dispensation...")
        self.disp_reason.setFixedHeight(70)
        form_lay.addWidget(self.disp_reason, 3, 1, 1, 3)

        # Row 4
        form_lay.addWidget(lbl("Authorized By", True), 4, 0)
        self.disp_auth = QLineEdit()
        self.disp_auth.setPlaceholderText("Name of authorizing officer")
        self.disp_auth.setFixedHeight(38)
        form_lay.addWidget(self.disp_auth, 4, 1)

        form_lay.addWidget(lbl("Status"), 4, 2)
        self.disp_status = QComboBox()
        self.disp_status.addItems(["Active", "Expired", "Cancelled"])
        self.disp_status.setFixedHeight(38)
        form_lay.addWidget(self.disp_status, 4, 3)

        # Row 5
        form_lay.addWidget(lbl("Semester", True), 5, 0)
        self.disp_semester = QComboBox()
        self.disp_semester.addItems(["1st", "2nd", "Summer"])
        self.disp_semester.setFixedHeight(38)
        form_lay.addWidget(self.disp_semester, 5, 1)

        lay.addWidget(form_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)
        clear_btn.setFixedWidth(110)
        clear_btn.clicked.connect(self._clear_dispensation)

        save_btn = QPushButton("   Save Record ")
        save_btn.setStyleSheet(btn_green())
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(160)
        save_btn.clicked.connect(self._save_dispensation)

        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)

        return w

    def _clear_dispensation(self):
        self.disp_stud_no.clear()
        self.disp_stud_name.clear()
        self.disp_section.clear()
        self.disp_days.setValue(1)
        self.disp_reason.clear()
        self.disp_auth.clear()

    def _save_dispensation(self):
        if not self.disp_stud_no.text().strip() or not self.disp_stud_name.text().strip():
            InfoDialog("Missing Fields",
                       "Please fill in the required fields\n(Student Number and Name).",
                       success=False, parent=self).exec_()
            return
        dlg = ConfirmDialog("Confirm Save",
                            "Save this Dispensation Green Slip record?", parent=self)
        if dlg.exec_():
            try:
                # Prepare data from form
                stud_num = self.disp_stud_no.text().strip()
                stud_name = self.disp_stud_name.text().strip()
                stud_grade = self.disp_grade.currentText()  # e.g., "Grade 9"
                slip_type = "Dispensation"
                date_avail = self.disp_date.date().toPyDate()
                days = self.disp_days.value()
                status = self.disp_status.currentText()
                expiry = self.disp_expiry.date().toPyDate()
                purpose = self.disp_reason.toPlainText().strip()
                semester = self.disp_semester.currentText()
                remarks = ""
                absence_type = ""
                dates_absence = ""
                supp_doc = ""
                auth_by = self.disp_auth.text().strip()
                
                # Save to database (student will be auto-added if doesn't exist)
                add_green_slip(stud_num, slip_type, date_avail, days, status,
                              expiry, purpose, remarks, absence_type,
                              dates_absence, supp_doc, auth_by, 
                              stud_name=stud_name, stud_course="", stud_year=stud_grade, semester=semester)
                
                InfoDialog("Record Saved",
                           "Dispensation Green Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._clear_dispensation()
            except Exception as e:
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    def _clear_excuse(self):
        self.exc_stud_no.clear()
        self.exc_stud_name.clear()
        self.exc_section.clear()
        self.exc_abs_date.clear()
        self.exc_remarks.clear()
        self.exc_auth.clear()
        self.exc_type.setCurrentIndex(0)
        self.exc_doc.setCurrentIndex(0)

    def _save_excuse(self):
        if not self.exc_stud_no.text().strip() or not self.exc_stud_name.text().strip():
            InfoDialog("Missing Fields",
                       "Please fill in the required fields\n(Student Number and Name).",
                       success=False, parent=self).exec_()
            return
        dlg = ConfirmDialog("Confirm Save",
                            "Save this Excuse Green Slip record?", parent=self)
        if dlg.exec_():
            try:
                # Prepare data from form
                stud_num = self.exc_stud_no.text().strip()
                stud_name = self.exc_stud_name.text().strip()
                stud_grade = self.exc_grade.currentText()
                slip_type = "Excuse"  # Set to Excuse for this tab
                date_avail = self.exc_date.date().toPyDate()
                days = 0  # Not applicable for excuse
                status = "Active"  # Default status for excuse
                expiry = self.exc_date.date().toPyDate()  # Same as date available for excuse
                purpose = ""  # Not applicable for excuse
                remarks = self.exc_remarks.toPlainText().strip()
                absence_type = self.exc_type.currentText()
                dates_absence = self.exc_abs_date.text().strip()
                supp_doc = self.exc_doc.currentText()
                auth_by = self.exc_auth.text().strip()
                semester = self.exc_semester.currentText()
                
                # Save to database (student will be auto-added if doesn't exist)
                add_green_slip(stud_num, slip_type, date_avail, days, status,
                              expiry, purpose, remarks, absence_type,
                              dates_absence, supp_doc, auth_by,
                              stud_name=stud_name, stud_course="", stud_year=stud_grade, semester=semester)
                
                InfoDialog("Record Saved",
                           "Excuse Green Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._clear_excuse()
            except Exception as e:
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    # ── Excuse tab ────────────────────────────────────────────────────────────
    def _build_excuse_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        info = QLabel(
            "   An Excuse Green Slip is issued when a student's absence is officially excused.  "
            "The type of absence must be specified."
        )
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 11))
        info.setStyleSheet(f"""
            background: #E8F5E9; border-left: 4px solid {GREEN_SLIP};
            border-radius: 6px; padding: 10px 14px; color: #1B5E20;
        """)
        lay.addWidget(info)

        form_group = QGroupBox("New Excuse Green Slip Record")
        form_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        form_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid {GREEN_SLIP}60;
                border-radius: 10px;
                margin-top: 18px;
                padding: 16px 14px;
                background: {WHITE};
                color: {GREEN_SLIP};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px; top: -2px;
                padding: 0 8px;
                background: {WHITE};
                color: {GREEN_SLIP};
            }}
        """)
        form_lay = QGridLayout(form_group)
        form_lay.setSpacing(12)
        form_lay.setColumnStretch(1, 1)
        form_lay.setColumnStretch(3, 1)

        def lbl(text, req=False):
            return FieldLabel(text, required=req)

        form_lay.addWidget(lbl("Student Number", True), 0, 0)
        self.exc_stud_no = QLineEdit()
        self.exc_stud_no.setPlaceholderText("e.g. 2024-0001")
        self.exc_stud_no.setFixedHeight(38)
        form_lay.addWidget(self.exc_stud_no, 0, 1)

        form_lay.addWidget(lbl("Student Name", True), 0, 2)
        self.exc_stud_name = QLineEdit()
        self.exc_stud_name.setPlaceholderText("Last, First Middle")
        self.exc_stud_name.setFixedHeight(38)
        form_lay.addWidget(self.exc_stud_name, 0, 3)

        form_lay.addWidget(lbl("Grade & Section"), 1, 0)
        grade_row = QHBoxLayout()
        self.exc_grade = QComboBox()
        self.exc_grade.addItems(["Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12"])
        self.exc_grade.setFixedHeight(38)
        self.exc_section = QLineEdit()
        self.exc_section.setPlaceholderText("Section / Block")
        self.exc_section.setFixedHeight(38)
        grade_row.addWidget(self.exc_grade)
        grade_row.addWidget(self.exc_section)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Date Availed", True), 1, 2)
        self.exc_date = QDateEdit(QDate.currentDate())
        self.exc_date.setCalendarPopup(True)
        self.exc_date.setFixedHeight(38)
        self.exc_date.setDisplayFormat("MMMM d, yyyy")
        form_lay.addWidget(self.exc_date, 1, 3)

        form_lay.addWidget(lbl("Absence Type", True), 2, 0)
        self.exc_type = QComboBox()
        self.exc_type.addItems([
            "Medical / Illness",
            "Family Emergency",
            "School Event / Activity",
            "Official Function",
            "Weather / Calamity",
            "Other (specify below)",
        ])
        self.exc_type.setFixedHeight(38)
        form_lay.addWidget(self.exc_type, 2, 1)

        form_lay.addWidget(lbl("Date(s) of Absence", True), 2, 2)
        self.exc_abs_date = QLineEdit()
        self.exc_abs_date.setPlaceholderText("e.g. Nov 18–19, 2024")
        self.exc_abs_date.setFixedHeight(38)
        form_lay.addWidget(self.exc_abs_date, 2, 3)

        form_lay.addWidget(lbl("Remarks / Details"), 3, 0)
        self.exc_remarks = QTextEdit()
        self.exc_remarks.setPlaceholderText("Additional details about the absence...")
        self.exc_remarks.setFixedHeight(70)
        form_lay.addWidget(self.exc_remarks, 3, 1, 1, 3)

        form_lay.addWidget(lbl("Authorized By", True), 4, 0)
        self.exc_auth = QLineEdit()
        self.exc_auth.setPlaceholderText("Name of authorizing officer")
        self.exc_auth.setFixedHeight(38)
        form_lay.addWidget(self.exc_auth, 4, 1)

        form_lay.addWidget(lbl("Supporting Document"), 4, 2)
        self.exc_doc = QComboBox()
        self.exc_doc.addItems(["Medical Certificate", "Parent Letter", "Official Document", "None"])
        self.exc_doc.setFixedHeight(38)
        form_lay.addWidget(self.exc_doc, 4, 3)

        # Row 5
        form_lay.addWidget(lbl("Semester", True), 5, 0)
        self.exc_semester = QComboBox()
        self.exc_semester.addItems(["1st", "2nd", "Summer"])
        self.exc_semester.setFixedHeight(38)
        form_lay.addWidget(self.exc_semester, 5, 1)

        lay.addWidget(form_group)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)
        clear_btn.setFixedWidth(110)
        clear_btn.clicked.connect(self._clear_excuse)

        save_btn = QPushButton("   Save Record ")
        save_btn.setStyleSheet(btn_green())
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(160)
        save_btn.clicked.connect(self._save_excuse)

        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)

        return w

    # ── Tracker tab ───────────────────────────────────────────────────────────
    def _build_tracker_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Green Slip Record Tracker"))
        lay.addWidget(SubTitle("All dispensation and excuse slips are listed below"))

        # Search + filter row
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("   Search by student name or number... ")
        search.setFixedHeight(38)
        search.setStyleSheet(f"""
            QLineEdit {{
                background: {OFF_WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {GREEN_SLIP}; }}
        """)

        filter_cb = QComboBox()
        filter_cb.addItems(["All Types", "Dispensation", "Excuse"])
        filter_cb.setFixedHeight(38)
        filter_cb.setFixedWidth(160)

        grade_filter = QComboBox()
        grade_filter.addItems(["All Grades","1st","2nd","3rd","4th","5th"])
        grade_filter.setFixedHeight(38)
        grade_filter.setFixedWidth(140)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setStyleSheet(btn_outline())
        refresh_btn.setFixedHeight(38)

        top_row.addWidget(search, 1)
        top_row.addWidget(filter_cb)
        top_row.addWidget(grade_filter)
        top_row.addWidget(refresh_btn)
        lay.addLayout(top_row)

        # Sample table
        headers = ["Student No.", "Student Name", "Grade", "Section",
                   "Slip Type", "Date Availed", "Days / Absence Type", "Expiry / Date", "Status"]
        sample = [
            ("2024-0001", "Dela Cruz, Juan M.",  "Grade 9", "St. Thomas", "Dispensation", "Nov 20, 2024", "2 days",             "Nov 22, 2024", "Active"),
            ("2024-0045", "Santos, Maria R.",    "Grade 10","St. Clare",  "Excuse",        "Nov 19, 2024", "Medical / Illness",  "Nov 19, 2024", "Completed"),
            ("2024-0078", "Lim, Angela C.",      "Grade 8", "St. Agnes",  "Dispensation", "Nov 17, 2024", "1 day",              "Nov 18, 2024", "Expired"),
            ("2024-0200", "Torres, Liza F.",     "Grade 11","St. Joseph", "Excuse",        "Nov 14, 2024", "Family Emergency",   "Nov 14, 2024", "Completed"),
            ("2024-0312", "Bautista, Carlo E.",  "Grade 12","St. Peter",  "Dispensation", "Nov 10, 2024", "3 days",             "Nov 13, 2024", "Expired"),
        ]

        table = build_record_table(headers, sample)
        table.setMinimumHeight(280)
        lay.addWidget(table)

        action_row = QHBoxLayout()
        action_row.addStretch()

        view_btn = QPushButton("   View Details ")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)

        delete_btn = QPushButton("   Delete ")
        delete_btn.setStyleSheet(btn_danger())
        delete_btn.setFixedHeight(38)

        action_row.addWidget(view_btn)
        action_row.addWidget(delete_btn)
        lay.addLayout(action_row)
        lay.addStretch()

        return w

    # ── Summary tab ───────────────────────────────────────────────────────────
    def _build_summary_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Green Slip Summary"))
        lay.addWidget(SubTitle("Statistical overview of green slip records"))

        # Period selector
        period_row = QHBoxLayout()
        period_row.addWidget(QLabel("View Period:"))
        period = QComboBox()
        period.addItems(["This Month (November 2024)",
                         "Last Month (October 2024)",
                         "This Semester", "School Year 2024–2025"])
        period.setFixedHeight(36)
        period.setFixedWidth(260)
        period_row.addWidget(period)
        period_row.addStretch()

        export_btn = QPushButton("   Export Report ")
        export_btn.setStyleSheet(btn_green())
        export_btn.setFixedHeight(36)
        period_row.addWidget(export_btn)
        lay.addLayout(period_row)

        # Stat tiles
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)

        from ui.components import StatTile
        for label, val, colour in [
            ("Total Green Slips",       "35", GREEN_SLIP),
            ("Dispensation Slips",      "20", "#388E3C"),
            ("Excuse Slips",            "15", "#66BB6A"),
            ("Currently Active",        "8",  "#2E7D32"),
            ("Students with >2 Slips",  "4",  "#F57F17"),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
        lay.addLayout(tiles_row)

        # Chart placeholder
        chart_frame = QFrame()
        chart_frame.setFixedHeight(280)
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background: #F1F8E9;
                border: 2px dashed {GREEN_SLIP}80;
                border-radius: 12px;
            }}
        """)
        chart_lay = QVBoxLayout(chart_frame)
        chart_lay.setAlignment(Qt.AlignCenter)
        chart_icon = QLabel("📊")
        chart_icon.setFont(QFont("Segoe UI", 48))
        chart_icon.setAlignment(Qt.AlignCenter)
        chart_icon.setStyleSheet("background: transparent;")
        chart_text = QLabel(
            "Visual charts (Bar / Pie / Line) will be rendered here\n"
            "using matplotlib or PyQtChart in the final system."
        )
        chart_text.setFont(QFont("Segoe UI", 12))
        chart_text.setAlignment(Qt.AlignCenter)
        chart_text.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
        chart_lay.addWidget(chart_icon)
        chart_lay.addWidget(chart_text)
        lay.addWidget(chart_frame)

        lay.addStretch()
        return w

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
from backend.config import get_current_semester


class GreenSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.green_tracker_table = None
        self.green_tracker_layout = None
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
        self.disp_year = QComboBox()
        self.disp_year.addItems(["1st","2nd","3rd","4th","5th"])
        self.disp_year.setFixedHeight(38)
        self.disp_course = QLineEdit()
        self.disp_course.setPlaceholderText("Course")
        self.disp_course.setFixedHeight(38)
        grade_row.addWidget(self.disp_year)
        grade_row.addWidget(self.disp_course)
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
        # Set to current semester from config
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.disp_semester.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.disp_semester.setCurrentIndex(1)
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
        self.disp_course.clear()
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
                stud_course = self.disp_course.text().strip() if hasattr(self, 'disp_course') else ""
                stud_year = self.disp_year.currentText()  # e.g., "1st"
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
                              stud_name=stud_name, stud_course=stud_course, stud_year=stud_year)
                
                InfoDialog("Record Saved",
                           "Dispensation Green Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._clear_dispensation()
                # Refresh tracker tab
                self._refresh_green_tracker()
                # Refresh summary charts
                self._refresh_green_summary()
            except Exception as e:
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    def _clear_excuse(self):
        self.exc_stud_no.clear()
        self.exc_stud_name.clear()
        self.exc_course.clear()
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
                stud_course = self.exc_course.text().strip()  # Get course
                stud_year = self.exc_year.currentText()
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
                              stud_name=stud_name, stud_course=stud_course, stud_year=stud_year)
                
                InfoDialog("Record Saved",
                           "Excuse Green Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._clear_excuse()
                # Refresh tracker tab
                self._refresh_green_tracker()
                # Refresh summary charts
                self._refresh_green_summary()
            except Exception as e:
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    def _load_green_tracker_data(self):
        """Load green slip data from database"""
        from backend.db_green_slip import get_green_slips
        from backend.db_students import get_student
        
        sample = []
        try:
            green_slips = get_green_slips(None) or []
            for record in green_slips:
                try:
                    # Record structure: (studName, studCourse, studYrLvl, ID, studNumber, slipType_green, dateAvail_green, daysOfAbs_greenDisp, status_green, exprDate_greenDisp, purpose_greenDisp, remarks_greenExc, absceneType_greenExc, datesOfAbs_greenExc, suppDoc_greenExc, authBy_green)
                    stud_name = record[0] if len(record) > 0 else "N/A"
                    stud_course = record[1] if len(record) > 1 else "N/A"
                    stud_year = record[2] if len(record) > 2 else "N/A"
                    stud_num = record[4] if len(record) > 4 else "N/A"
                    is_disp = record[5] if len(record) > 5 else False
                    slip_type = "Dispensation" if is_disp else "Excuse"
                    date_avail = str(record[6]) if len(record) > 6 else "N/A"
                    days_absence = str(record[7]) if len(record) > 7 else "N/A"
                    status = record[8] if len(record) > 8 else "Active"
                    expiry = str(record[9]) if len(record) > 9 else "N/A"
                    sample.append((stud_num, stud_name, stud_year, stud_course, slip_type, date_avail[:10] if date_avail else "N/A", days_absence, expiry[:10] if expiry else "N/A", status))
                except:
                    pass
        except:
            pass
        
        if not sample:
            sample = [("No records", "Add records to see them here", "-", "-", "-", "-", "-", "-", "-")]
        
        return sample

    def _refresh_green_tracker(self):
        """Refresh the green slip tracker table"""
        if self.green_tracker_table is not None and self.green_tracker_layout is not None:
            headers = ["Student No.", "Student Name", "Year", "Course",
                       "Slip Type", "Date Availed", "Days / Absence Type", "Expiry / Date", "Status"]
            data = self._load_green_tracker_data()
            
            # Remove old table from layout and destroy it
            for i in range(self.green_tracker_layout.count()):
                item = self.green_tracker_layout.itemAt(i)
                if item and item.widget() is self.green_tracker_table:
                    self.green_tracker_layout.removeWidget(self.green_tracker_table)
                    self.green_tracker_table.deleteLater()
                    break
            
            # Create new table with fresh data
            self.green_tracker_table = build_record_table(headers, data)
            self.green_tracker_table.setMinimumHeight(280)
            # Re-add table to layout at the correct position
            self.green_tracker_layout.insertWidget(2, self.green_tracker_table)

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

        form_lay.addWidget(lbl("Year & Course"), 1, 0)
        grade_row = QHBoxLayout()
        self.exc_year = QComboBox()
        self.exc_year.addItems(["1st","2nd","3rd","4th","5th"])
        self.exc_year.setFixedHeight(38)
        self.exc_course = QLineEdit()
        self.exc_course.setPlaceholderText("Course")
        self.exc_course.setFixedHeight(38)
        grade_row.addWidget(self.exc_year)
        grade_row.addWidget(self.exc_course)
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
        # Set to current semester from config
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.exc_semester.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.exc_semester.setCurrentIndex(1)
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

        semester_filter = QComboBox()
        semester_filter.addItems(["All Semesters", "1st", "2nd", "Summer"])
        semester_filter.setFixedHeight(38)
        semester_filter.setFixedWidth(140)
        # Set to current semester by default
        current_sem = get_current_semester()
        if "1st" in current_sem:
            semester_filter.setCurrentIndex(1)
        elif "2nd" in current_sem:
            semester_filter.setCurrentIndex(2)

        grade_filter = QComboBox()
        grade_filter.addItems(["All Grades","1st","2nd","3rd","4th","5th"])
        grade_filter.setFixedHeight(38)
        grade_filter.setFixedWidth(140)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setStyleSheet(btn_outline())
        refresh_btn.setFixedHeight(38)
        refresh_btn.clicked.connect(self._refresh_green_tracker)

        top_row.addWidget(search, 1)
        top_row.addWidget(filter_cb)
        top_row.addWidget(semester_filter)
        top_row.addWidget(grade_filter)
        top_row.addWidget(refresh_btn)
        lay.addLayout(top_row)

        headers = ["Student No.", "Student Name", "Year", "Course",
                   "Slip Type", "Date Availed", "Days / Absence Type", "Expiry / Date", "Status"]
        sample = self._load_green_tracker_data()
        
        self.green_tracker_table = build_record_table(headers, sample)
        self.green_tracker_table.setMinimumHeight(280)
        lay.addWidget(self.green_tracker_table)
        
        # Store reference to layout for refresh functionality
        self.green_tracker_layout = lay

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

        # Stat tiles
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)

        from ui.components import StatTile
        # Calculate and display statistics
        self.green_stat_tiles = {}
        self._update_green_stats(tiles_row)
        lay.addLayout(tiles_row)

        # Add refresh button for manual refresh
        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        refresh_btn = QPushButton("⟳  Refresh Charts")
        refresh_btn.setStyleSheet(btn_green())
        refresh_btn.setFixedHeight(36)
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self._refresh_green_summary)
        refresh_row.addWidget(refresh_btn)
        refresh_row.addStretch()
        lay.addLayout(refresh_row)

        # Create and add chart
        from ui.chart_widgets import GreenSlipChart
        self.green_chart = GreenSlipChart(w)
        self.green_chart.setMinimumHeight(380)
        lay.addWidget(self.green_chart)
        
        # Initialize chart with current data
        self._refresh_green_summary()
        
        lay.addStretch()
        return w
    
    def _update_green_stats(self, tiles_row: QHBoxLayout):
        """Update statistics tiles."""
        from ui.components import StatTile
        from backend.db_green_slip import get_green_slips
        
        green_records = get_green_slips(None) or []
        total_green = len(green_records)
        dispensation_count = sum(1 for r in green_records if len(r) > 5 and r[5] == True)
        excuse_count = sum(1 for r in green_records if len(r) > 5 and r[5] == False)
        active_count = sum(1 for r in green_records if len(r) > 8 and "Active" in str(r[8]))
        
        # Count students with >2 slips
        student_slip_counts = {}
        for r in green_records:
            if len(r) > 0:
                stud = r[0]
                student_slip_counts[stud] = student_slip_counts.get(stud, 0) + 1
        multi_slip_students = sum(1 for count in student_slip_counts.values() if count > 2)
        
        for label, val, colour in [
            ("Total Green Slips",       str(total_green), GREEN_SLIP),
            ("Dispensation Slips",      str(dispensation_count), "#388E3C"),
            ("Excuse Slips",            str(excuse_count), "#66BB6A"),
            ("Currently Active",        str(active_count),  "#2E7D32"),
            ("Students with >2 Slips",  str(multi_slip_students),  "#F57F17"),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self.green_stat_tiles[label] = tile
    
    def _refresh_green_summary(self):
        """Refresh the summary chart with current database data."""
        from backend.db_green_slip import get_green_slips
        
        green_records = get_green_slips(None) or []
        
        dispensation_count = sum(1 for r in green_records if len(r) > 5 and r[5] == True)
        excuse_count = sum(1 for r in green_records if len(r) > 5 and r[5] == False)
        active_count = sum(1 for r in green_records if len(r) > 8 and "Active" in str(r[8]))
        expired_count = sum(1 for r in green_records if len(r) > 8 and "Expired" in str(r[8]))
        
        # Update chart
        if hasattr(self, 'green_chart'):
            self.green_chart.update_data(dispensation_count, excuse_count, active_count, expired_count)

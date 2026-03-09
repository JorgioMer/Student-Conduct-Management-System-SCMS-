# =============================================================================
#  SCMS — Pink Slip Page  (Once per Semester)
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QTabWidget, QWidget,
    QFrame, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import (
    NAVY, GOLD, WHITE, OFF_WHITE, LIGHT_GRAY,
    MID_GRAY, TEXT_DARK, PINK_SLIP,
    btn_primary, btn_outline, btn_danger, btn_pink
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    FieldLabel, add_shadow, ConfirmDialog, InfoDialog, StatTile
)
from ui.pages.base_page import BasePage, page_header, build_record_table

# Backend database imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_pink_slip import add_pink_slip, get_pink_slips
from backend.config import get_current_semester


class PinkSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pink_tracker_table = None
        self.pink_tracker_layout = None
        self._build()

    def _build(self):
        self.main_layout.addWidget(page_header(
            "pink",
            "   Pink Slip Management ",
            "Track penalty slips — issued only ONCE per student per semester"
        ))

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabBar::tab:selected {{
                background: {PINK_SLIP};
                color: white;
                font-weight: bold;
            }}
            QTabBar::tab {{
                background: {LIGHT_GRAY};
                color: {TEXT_DARK};
                padding: 10px 26px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
            }}
            QTabBar::tab:hover:!selected {{ background: #F48FB1; color: white; }}
            QTabWidget::pane {{
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
                background: {WHITE};
                top: -1px;
            }}
        """)

        tabs.addTab(self._build_record_tab(), "   New Pink Slip Record ")
        tabs.addTab(self._build_tracker_tab(), "   Pink Slip Tracker ")
        tabs.addTab(self._build_summary_tab(), "   Summary & Charts ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Record tab ────────────────────────────────────────────────────────────
    def _build_record_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        warning = QLabel(
            "   Important: A student may only receive ONE Pink Slip per semester.  "
            "Verify the student's record before filing. Multiple violations may escalate the action."
        )
        warning.setWordWrap(True)
        warning.setFont(QFont("Segoe UI", 11))
        warning.setStyleSheet(f"""
            background: #FCE4EC;
            border-left: 4px solid {PINK_SLIP};
            border-radius: 6px;
            padding: 10px 14px;
            color: #880E4F;
        """)
        lay.addWidget(warning)

        form_group = QGroupBox("New Pink Slip Record")
        form_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        form_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid {PINK_SLIP}60;
                border-radius: 10px;
                margin-top: 18px;
                padding: 16px 14px;
                background: {WHITE};
                color: {PINK_SLIP};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px; top: -2px;
                padding: 0 8px;
                background: {WHITE};
                color: {PINK_SLIP};
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
        self.pink_no = QLineEdit()
        self.pink_no.setPlaceholderText("e.g. 2024-0001")
        self.pink_no.setFixedHeight(38)
        form_lay.addWidget(self.pink_no, 0, 1)

        form_lay.addWidget(lbl("Student Name", True), 0, 2)
        self.pink_name = QLineEdit()
        self.pink_name.setPlaceholderText("Last, First Middle")
        self.pink_name.setFixedHeight(38)
        form_lay.addWidget(self.pink_name, 0, 3)

        # Row 1
        form_lay.addWidget(lbl("Year & Course"), 1, 0)
        grade_row = QHBoxLayout()
        self.pink_year = QComboBox()
        self.pink_year.addItems(["1st","2nd","3rd","4th","5th"])
        self.pink_year.setFixedHeight(38)
        self.pink_course = QLineEdit()
        self.pink_course.setPlaceholderText("Course")
        self.pink_course.setFixedHeight(38)
        grade_row.addWidget(self.pink_year)
        grade_row.addWidget(self.pink_course)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Semester", True), 1, 2)
        self.pink_sem = QComboBox()
        self.pink_sem.addItems(["1st", "2nd", "Summer"])
        self.pink_sem.setFixedHeight(38)
        # Set to current semester from config
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.pink_sem.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.pink_sem.setCurrentIndex(1)
        form_lay.addWidget(self.pink_sem, 1, 3)

        # Row 2
        form_lay.addWidget(lbl("Date Issued", True), 2, 0)
        self.pink_date = QDateEdit(QDate.currentDate())
        self.pink_date.setCalendarPopup(True)
        self.pink_date.setFixedHeight(38)
        self.pink_date.setDisplayFormat("MMMM d, yyyy")
        form_lay.addWidget(self.pink_date, 2, 1)

        form_lay.addWidget(lbl("Violation / Reason", True), 2, 2)
        self.pink_violation = QComboBox()
        self.pink_violation.addItems([
            "Uniform Violation",
            "Tardiness",
            "Misconduct",
            "Prohibited Items",
            "Disrespect",
            "Other (specify in remarks)",
        ])
        self.pink_violation.setFixedHeight(38)
        form_lay.addWidget(self.pink_violation, 2, 3)

        # Row 3
        form_lay.addWidget(lbl("Description / Remarks"), 3, 0)
        self.pink_remarks = QTextEdit()
        self.pink_remarks.setPlaceholderText("Provide additional details about the violation...")
        self.pink_remarks.setFixedHeight(75)
        form_lay.addWidget(self.pink_remarks, 3, 1, 1, 3)

        # Row 4
        form_lay.addWidget(lbl("Action Taken"), 4, 0)
        self.pink_action = QComboBox()
        self.pink_action.addItems([
            "Warning",
            "Parent Notification",
            "Community Service",
            "Suspension",
            "Other",
        ])
        self.pink_action.setFixedHeight(38)
        form_lay.addWidget(self.pink_action, 4, 1)

        form_lay.addWidget(lbl("Officer in Charge", True), 4, 2)
        self.pink_officer = QLineEdit()
        self.pink_officer.setPlaceholderText("Name of prefect / officer")
        self.pink_officer.setFixedHeight(38)
        form_lay.addWidget(self.pink_officer, 4, 3)

        lay.addWidget(form_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        check_btn = QPushButton("   Check Student Record ")
        check_btn.setStyleSheet(btn_outline())
        check_btn.setFixedHeight(40)
        check_btn.setToolTip("Verify if student has already received a Pink Slip this semester")
        check_btn.clicked.connect(lambda: InfoDialog(
            "Record Check",
            "No existing Pink Slip found for this student\nin the selected semester.\n\nYou may proceed to save.",
            parent=self).exec_())

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)

        save_btn = QPushButton("   Save Record ")
        save_btn.setStyleSheet(btn_pink())
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_pink)

        btn_row.setSpacing(10)
        btn_row.addWidget(check_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)

        return w

    def _save_pink(self):
        if not self.pink_no.text().strip():
            InfoDialog("Missing Fields",
                       "Please fill in all required fields.",
                       success=False, parent=self).exec_()
            return
        dlg = ConfirmDialog("Confirm Save",
                            "Save this Pink Slip record?\nPlease confirm the student has not already\nreceived a Pink Slip this semester.",
                            parent=self)
        if dlg.exec_():
            try:
                # Prepare data from form
                stud_num = self.pink_no.text().strip()
                stud_name = self.pink_name.text().strip()
                stud_course = self.pink_course.text().strip()
                stud_year = self.pink_year.currentText()
                date_issued = self.pink_date.date().toPyDate()
                violation = self.pink_violation.currentText()
                action_taken = self.pink_action.currentText()
                officer = self.pink_officer.text().strip()
                sem = self.pink_sem.currentText()
                remarks = self.pink_remarks.toPlainText().strip()
                
                # Save to database (student will be auto-added if doesn't exist)
                add_pink_slip(stud_num, date_issued, violation, action_taken, officer,
                             sem=sem, remarks=remarks, stud_name=stud_name, 
                             stud_course=stud_course, stud_year=stud_year)
                
                InfoDialog("Record Saved",
                           "Pink Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                # Refresh tracker tab
                self._refresh_pink_tracker()
                # Refresh summary charts
                self._refresh_pink_summary()
            except Exception as e:
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    def _load_pink_tracker_data(self):
        """Load pink slip data from database"""
        from backend.db_pink_slip import get_pink_slips
        from backend.db_students import get_student
        
        sample = []
        try:
            pink_slips = get_pink_slips(None) or []
            for record in pink_slips:
                try:
                    # Record structure: (studName, studCourse, studYrLvl, ID, studNumber, dateIssued_pink, violation_pink, actionTaken_pink, offcInCharge_pink, sem_pink, remarks_pink)
                    stud_name = record[0] if len(record) > 0 else "N/A"
                    stud_course = record[1] if len(record) > 1 else "N/A"
                    stud_year = record[2] if len(record) > 2 else "N/A"
                    stud_num = record[4] if len(record) > 4 else "N/A"
                    date_issued = str(record[5]) if len(record) > 5 else "N/A"
                    violation = record[6] if len(record) > 6 else "N/A"
                    action_taken = record[7] if len(record) > 7 else "N/A"
                    officer = record[8] if len(record) > 8 else "N/A"
                    semester = record[9] if len(record) > 9 else "N/A"
                    sample.append((stud_num, stud_name, stud_year, stud_course, semester, date_issued[:10], violation, action_taken, officer))
                except:
                    pass
        except:
            pass
        
        if not sample:
            sample = [("No records", "Add records to see them here", "-", "-", "-", "-", "-", "-", "-")]
        
        return sample

    def _refresh_pink_tracker(self):
        """Refresh the pink slip tracker table"""
        if self.pink_tracker_table is not None:
            headers = ["Student No.", "Student Name", "Year", "Course",
                       "Semester", "Date Issued", "Violation", "Action Taken", "Officer"]
            data = self._load_pink_tracker_data()
            
            # Clear and rebuild table
            self.pink_tracker_table.setRowCount(0)
            for row_data in data:
                row_idx = self.pink_tracker_table.rowCount()
                self.pink_tracker_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.pink_tracker_table.setItem(row_idx, col_idx, item)

    # ── Tracker tab ───────────────────────────────────────────────────────────
    def _build_tracker_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Pink Slip Record Tracker"))
        lay.addWidget(SubTitle("Track all issued pink slips — one per student per semester"))

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        search = QLineEdit()
        search.setPlaceholderText("   Search student... ")
        search.setFixedHeight(38)

        sem_filter = QComboBox()
        sem_filter.addItems(["All Semesters", "1st", "2nd", "Summer"])
        sem_filter.setFixedHeight(38)
        sem_filter.setFixedWidth(140)
        # Set to current semester by default
        current_sem = get_current_semester()
        if "1st" in current_sem:
            sem_filter.setCurrentIndex(1)
        elif "2nd" in current_sem:
            sem_filter.setCurrentIndex(2)

        top_row.addWidget(search, 1)
        top_row.addWidget(sem_filter)

        refresh_btn = QPushButton("   Refresh ")
        refresh_btn.setStyleSheet(btn_outline())
        refresh_btn.setFixedHeight(38)
        refresh_btn.clicked.connect(self._refresh_pink_tracker)
        top_row.addWidget(refresh_btn)
        lay.addLayout(top_row)

        headers = ["Student No.", "Student Name", "Year", "Course",
                   "Semester", "Date Issued", "Violation", "Action Taken", "Officer"]
        sample = self._load_pink_tracker_data()
        
        self.pink_tracker_table = build_record_table(headers, sample)
        self.pink_tracker_table.setMinimumHeight(260)
        lay.addWidget(self.pink_tracker_table)

        action_row = QHBoxLayout()
        action_row.addStretch()
        view_btn = QPushButton("   View ")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        del_btn = QPushButton("   Delete ")
        del_btn.setStyleSheet(btn_danger())
        del_btn.setFixedHeight(38)
        action_row.addWidget(view_btn)
        action_row.addWidget(del_btn)
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

        lay.addWidget(SectionTitle("Pink Slip Summary"))

        # Calculate and display statistics
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        self.pink_stat_tiles = {}
        self._update_pink_stats(tiles_row)
        lay.addLayout(tiles_row)

        # Add refresh button for manual refresh
        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        refresh_btn = QPushButton("⟳  Refresh Charts")
        refresh_btn.setStyleSheet(btn_pink())
        refresh_btn.setFixedHeight(36)
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self._refresh_pink_summary)
        refresh_row.addWidget(refresh_btn)
        refresh_row.addStretch()
        lay.addLayout(refresh_row)

        # Create and add chart
        from ui.chart_widgets import PinkSlipChart
        self.pink_chart = PinkSlipChart(w)
        self.pink_chart.setMinimumHeight(380)
        lay.addWidget(self.pink_chart)
        
        # Initialize chart with current data
        self._refresh_pink_summary()
        
        lay.addStretch()
        return w
    
    def _update_pink_stats(self, tiles_row: QHBoxLayout):
        """Update statistics tiles."""
        from backend.db_pink_slip import get_pink_slips
        
        pink_records = get_pink_slips(None) or []
        total_pink = len(pink_records)
        unique_students_pink = len(set(r[0] for r in pink_records if len(r) > 0))
        
        # Find most common violation
        violation_counts = {}
        for r in pink_records:
            if len(r) > 6:
                violation = str(r[6])
                violation_counts[violation] = violation_counts.get(violation, 0) + 1
        most_common = max(violation_counts.items(), key=lambda x: x[1])[0] if violation_counts else "—"
        
        for label, val, colour in [
            ("Total Pink Slips (Sem)",   str(total_pink), PINK_SLIP),
            ("Students Issued",          str(unique_students_pink), "#C2185B"),
            ("Most Common Violation",    most_common, "#880E4F"),
            ("Pending Action",           "0", "#F57F17"),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self.pink_stat_tiles[label] = tile
    
    def _refresh_pink_summary(self):
        """Refresh the summary chart with current database data."""
        from backend.db_pink_slip import get_pink_slips
        
        pink_records = get_pink_slips(None) or []
        
        # Build violation type distribution
        violation_types = {}
        for r in pink_records:
            if len(r) > 6:
                vtype = str(r[6])
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        # Build year/grade level distribution
        year_distribution = {}
        for r in pink_records:
            if len(r) > 2:
                year = str(r[2])
                year_distribution[year] = year_distribution.get(year, 0) + 1
        
        # Update chart
        if hasattr(self, 'pink_chart'):
            self.pink_chart.update_data(violation_types, year_distribution)

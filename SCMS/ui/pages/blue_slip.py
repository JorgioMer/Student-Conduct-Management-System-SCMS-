# =============================================================================
#  SCMS — Blue Slip Page  (Violation Tracking + Escalation)
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QTabWidget, QWidget,
    QFrame, QGroupBox, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import (
    NAVY, GOLD, WHITE, OFF_WHITE, LIGHT_GRAY,
    MID_GRAY, TEXT_DARK, BLUE_SLIP, RED_ERR,
    btn_primary, btn_outline, btn_danger, btn_blue
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    FieldLabel, add_shadow, ConfirmDialog, InfoDialog, StatTile
)
from ui.pages.base_page import BasePage, page_header, build_record_table

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_blue_slip import add_blue_slip, get_blue_slips
from backend.config import get_current_semester


# ── Filter-panel shared styles ────────────────────────────────────────────────
def _filter_panel_style(accent):
    """Clean, borderless panel — soft neutral background only."""
    return f"""
        QFrame {{
            background: #F8F9FA;
            border: none;
            border-radius: 8px;
        }}
    """

def _date_edit_style(accent):
    """QDateEdit styled to match system inputs; calendar popup is always on."""
    return f"""
        QDateEdit {{
            background: {WHITE};
            border: 1px solid #D0D5DD;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 13px;
            font-family: "Segoe UI";
            color: {TEXT_DARK};
        }}
        QDateEdit:focus {{
            border: 1.5px solid {accent};
        }}
        QDateEdit:disabled {{
            background: #F2F4F7;
            color: #9CA3AF;
            border: 1px solid #E5E7EB;
        }}
        QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: right center;
            width: 28px;
            border-left: 1px solid #E5E7EB;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
    """

def _combo_style(accent):
    """QComboBox styled to match system inputs."""
    return f"""
        QComboBox {{
            background: {WHITE};
            border: 1px solid #D0D5DD;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 13px;
            font-family: "Segoe UI";
            color: {TEXT_DARK};
        }}
        QComboBox:focus {{
            border: 1.5px solid {accent};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background: {WHITE};
            border: 1px solid #D0D5DD;
            selection-background-color: {accent}20;
            selection-color: {TEXT_DARK};
            font-size: 13px;
            font-family: "Segoe UI";
        }}
    """

def _search_style(accent):
    """Search QLineEdit — slightly larger font, clean border."""
    return f"""
        QLineEdit {{
            background: {WHITE};
            border: 1px solid #D0D5DD;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 13px;
            font-family: "Segoe UI";
            color: {TEXT_DARK};
        }}
        QLineEdit:focus {{
            border: 1.5px solid {accent};
        }}
    """


class BlueSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blue_tracker_table = None
        self.blue_tracker_layout = None
        self._all_blue_records = []    # cache for client-side filtering
        self._blue_table_index = 3     # position in lay for table widget
        self._build()

    def _build(self):
        self.main_layout.addWidget(page_header(
            "blue",
            "  Blue Slip Management ",
            "Record student violations — repeated offenses trigger escalated disciplinary action"
        ))

        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabBar::tab:selected {{
                background: {BLUE_SLIP};
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
            QTabBar::tab:hover:!selected {{ background: #64B5F6; color: white; }}
            QTabWidget::pane {{
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
                background: {WHITE};
                top: -1px;
            }}
        """)

        tabs.addTab(self._build_record_tab(),   "  File Blue Slip ")
        tabs.addTab(self._build_tracker_tab(),  "  Blue Slip Tracker ")
        tabs.addTab(self._build_progress_tab(), "   Violation Progress")
        tabs.addTab(self._build_summary_tab(),  "   Summary & Charts ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # =========================================================================
    # Record form tab  (UNCHANGED)
    # =========================================================================
    def _build_record_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        escalation_notice = QLabel(
            "   Escalation Policy: A student who receives the SAME violation multiple times  "
            "will automatically be subject to a higher level of disciplinary action. "
            "The system will track and flag repeated violations."
        )
        escalation_notice.setWordWrap(True)
        escalation_notice.setFont(QFont("Segoe UI", 11))
        escalation_notice.setStyleSheet(f"""
            background: #E3F2FD;
            border-left: 4px solid {BLUE_SLIP};
            border-radius: 6px;
            padding: 10px 14px;
            color: #0D47A1;
        """)
        lay.addWidget(escalation_notice)

        form_group = QGroupBox("New Blue Slip Violation Record")
        form_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        form_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1.5px solid {BLUE_SLIP}60;
                border-radius: 10px;
                margin-top: 18px;
                padding: 16px 14px;
                background: {WHITE};
                color: {BLUE_SLIP};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px; top: -2px;
                padding: 0 8px;
                background: {WHITE};
                color: {BLUE_SLIP};
            }}
        """)
        form_lay = QGridLayout(form_group)
        form_lay.setSpacing(12)
        form_lay.setColumnStretch(1, 1)
        form_lay.setColumnStretch(3, 1)

        def lbl(text, req=False):
            return FieldLabel(text, required=req)

        form_lay.addWidget(lbl("Student Number", True), 0, 0)
        self.blue_no = QLineEdit()
        self.blue_no.setPlaceholderText("e.g. 2024-0001")
        self.blue_no.setFixedHeight(38)
        form_lay.addWidget(self.blue_no, 0, 1)

        form_lay.addWidget(lbl("Student Name", True), 0, 2)
        self.blue_name = QLineEdit()
        self.blue_name.setPlaceholderText("Last, First Middle")
        self.blue_name.setFixedHeight(38)
        form_lay.addWidget(self.blue_name, 0, 3)

        form_lay.addWidget(lbl("Year & Course"), 1, 0)
        grade_row = QHBoxLayout()
        self.blue_year = QComboBox()
        self.blue_year.addItems(["1st","2nd","3rd","4th"])
        self.blue_year.setFixedHeight(38)
        self.blue_course = QLineEdit()
        self.blue_course.setPlaceholderText("Course")
        self.blue_course.setFixedHeight(38)
        grade_row.addWidget(self.blue_year)
        grade_row.addWidget(self.blue_course)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Date of Violation", True), 1, 2)
        self.blue_date = QDateEdit(QDate.currentDate())
        self.blue_date.setCalendarPopup(True)
        self.blue_date.setFixedHeight(38)
        self.blue_date.setDisplayFormat("MMMM d, yyyy")
        form_lay.addWidget(self.blue_date, 1, 3)

        form_lay.addWidget(lbl("Violation Type", True), 2, 0)
        self.blue_vtype = QComboBox()
        self.blue_vtype.addItems([
            "Bullying / Harassment",
            "Physical Altercation / Fighting",
            "Damage to Property",
            "Theft / Stealing",
            "Cheating / Academic Dishonesty",
            "Possession of Prohibited Items",
            "Skipping Class / Cutting",
            "Vandalism",
            "Disrespect to Authority",
            "Use of Mobile Phone (Prohibited)",
            "Other (specify in description)",
        ])
        self.blue_vtype.setFixedHeight(38)
        form_lay.addWidget(self.blue_vtype, 2, 1)

        form_lay.addWidget(lbl("Severity Level", True), 2, 2)
        self.blue_severity = QComboBox()
        self.blue_severity.addItems([
            "Level 1 — Minor",
            "Level 2 — Moderate",
            "Level 3 — Major",
            "Level 4 — Grave / Serious",
        ])
        self.blue_severity.setFixedHeight(38)
        form_lay.addWidget(self.blue_severity, 2, 3)

        form_lay.addWidget(lbl("Violation Description", True), 3, 0)
        self.blue_desc = QTextEdit()
        self.blue_desc.setPlaceholderText("Provide a detailed account of the violation incident...")
        self.blue_desc.setFixedHeight(75)
        form_lay.addWidget(self.blue_desc, 3, 1, 1, 3)

        form_lay.addWidget(lbl("Action Taken"), 4, 0)
        self.blue_action = QComboBox()
        self.blue_action.addItems([
            "Verbal Warning", "Written Warning", "Parent Meeting",
            "Community Service", "Suspension (specify days)",
            "Endorsement to Guidance", "Probation", "Other",
        ])
        self.blue_action.setFixedHeight(38)
        form_lay.addWidget(self.blue_action, 4, 1)

        form_lay.addWidget(lbl("Officer in Charge", True), 4, 2)
        self.blue_officer = QLineEdit()
        self.blue_officer.setPlaceholderText("Name of prefect / officer")
        self.blue_officer.setFixedHeight(38)
        form_lay.addWidget(self.blue_officer, 4, 3)

        form_lay.addWidget(lbl("Status"), 5, 0)
        self.blue_status = QComboBox()
        self.blue_status.addItems([
            "Open / Pending", "Under Investigation",
            "Action Taken", "Resolved", "Escalated",
        ])
        self.blue_status.setFixedHeight(38)
        form_lay.addWidget(self.blue_status, 5, 1)

        form_lay.addWidget(lbl("Witnesses / Notes"), 5, 2)
        self.blue_witnesses = QLineEdit()
        self.blue_witnesses.setPlaceholderText("Names of witnesses (optional)")
        self.blue_witnesses.setFixedHeight(38)
        form_lay.addWidget(self.blue_witnesses, 5, 3)

        form_lay.addWidget(lbl("Semester", True), 6, 0)
        self.blue_semester = QComboBox()
        self.blue_semester.addItems(["1st", "2nd", "Summer"])
        self.blue_semester.setFixedHeight(38)
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.blue_semester.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.blue_semester.setCurrentIndex(1)
        form_lay.addWidget(self.blue_semester, 6, 1)

        self.blue_escalate_chk = QCheckBox(
            "    Flag as ESCALATED (repeated same violation)")
        self.blue_escalate_chk.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.blue_escalate_chk.setStyleSheet(
            f"color: {RED_ERR}; background: transparent;")
        form_lay.addWidget(self.blue_escalate_chk, 7, 0, 1, 4)

        lay.addWidget(form_group)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        history_btn = QPushButton("  Check Violation History ")
        history_btn.setStyleSheet(btn_outline())
        history_btn.setFixedHeight(40)
        history_btn.setToolTip("Check if this student has prior violations of the same type")
        history_btn.clicked.connect(self._check_history)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)

        save_btn = QPushButton("   Save Violation Record ")
        save_btn.setStyleSheet(btn_blue())
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_blue)

        btn_row.addWidget(history_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)
        return w

    def _check_history(self):
        InfoDialog(
            "Violation History Check",
            "Student: (enter student number first)\n\n"
            "Prior violations found:\n"
            "  Nov 1, 2024 — Disrespect to Authority (Resolved)\n\n "
            "   This student has 1 prior violation of a similar type.\n "
            "Consider escalating the action if this is a repeat offense.",
            success=True, parent=self
        ).exec_()

    def _save_blue(self):
        if not self.blue_no.text().strip():
            InfoDialog("Missing Fields", "Please fill in all required fields.",
                       success=False, parent=self).exec_()
            return
        dlg = ConfirmDialog("Confirm Save",
                            "Save this Blue Slip violation record?", parent=self)
        if dlg.exec_():
            try:
                stud_num        = self.blue_no.text().strip()
                stud_name       = self.blue_name.text().strip()
                stud_course     = self.blue_course.text().strip()
                stud_year       = self.blue_year.currentText()
                semester        = self.blue_semester.currentText()
                violation_type  = self.blue_vtype.currentText()
                date_of_violation = self.blue_date.date().toPyDate()
                severity        = self.blue_severity.currentText()
                action_taken    = self.blue_action.currentText()
                status          = self.blue_status.currentText()
                violation_desc  = self.blue_desc.toPlainText().strip()
                witnesses       = self.blue_witnesses.text().strip()
                add_blue_slip(stud_num, violation_type, date_of_violation, severity,
                              action_taken, status=status, violation_desc=violation_desc,
                              witnesses=witnesses, stud_name=stud_name,
                              stud_course=stud_course, stud_year=stud_year)
                InfoDialog("Record Saved",
                           "Blue Slip violation record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._refresh_blue_tracker()
                self._refresh_blue_summary()
            except Exception as e:
                InfoDialog("Error", f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    # =========================================================================
    # Tracker tab — NEW: fully wired search / semester / status / date filters
    # =========================================================================
    def _load_blue_tracker_data(self):
        """Fetch all records from DB and cache them."""
        from backend.db_blue_slip import get_blue_slips
        sample = []
        try:
            for record in (get_blue_slips(None) or []):
                try:
                    stud_name      = record[0]  if len(record) > 0  else "N/A"
                    stud_year      = record[2]  if len(record) > 2  else "N/A"
                    stud_num       = record[4]  if len(record) > 4  else "N/A"
                    violation_type = record[5]  if len(record) > 5  else "N/A"
                    date_vio       = str(record[6]) if len(record) > 6  else "N/A"
                    severity       = record[8]  if len(record) > 8  else "N/A"
                    action         = record[9]  if len(record) > 9  else "N/A"
                    status         = record[10] if len(record) > 10 else "Open / Pending"
                    sample.append((
                        stud_num, stud_name, stud_year,
                        violation_type, severity,
                        date_vio[:10] if date_vio != "N/A" else "N/A",
                        action, status
                    ))
                except Exception:
                    pass
        except Exception:
            pass
        self._all_blue_records = sample
        return sample if sample else [
            ("No records", "Add records to see them here",
             "-", "-", "-", "-", "-", "-")
        ]

    def _apply_blue_filters(self):
        """Re-filter cached records and rebuild table."""
        search_text    = self._blue_search.text().strip().lower()
        sem_val        = self._blue_sem_filter.currentText()
        status_val     = self._blue_status_filter.currentText()
        severity_val   = self._blue_severity_filter.currentText()
        use_date       = self._blue_date_toggle.currentText() == "Filter by Date Range"
        date_from      = self._blue_date_from.date()
        date_to        = self._blue_date_to.date()

        filtered = []
        for row in self._all_blue_records:
            stud_num, stud_name, year, vtype, severity, date_str, action, status = row

            if search_text and (
                search_text not in stud_num.lower()
                and search_text not in stud_name.lower()
                and search_text not in vtype.lower()
            ):
                continue

            if status_val != "All Status" and status != status_val:
                continue

            if severity_val != "All Levels":
                level_num = severity_val.split()[-1]   # "Level 1" → "1"
                if f"Level {level_num}" not in str(severity):
                    continue

            if use_date and date_str not in ("-", "N/A"):
                try:
                    parts = date_str.split("-")
                    rec_date = QDate(int(parts[0]), int(parts[1]), int(parts[2]))
                    if rec_date < date_from or rec_date > date_to:
                        continue
                except Exception:
                    pass

            filtered.append(row)

        if not filtered:
            filtered = [("No results",
                         "No records match the selected filters",
                         "-", "-", "-", "-", "-", "-")]

        self._rebuild_blue_table(filtered)

    STATUS_COLORS = {
        "Under Investigation": ("#FFF3CD", "#856404"),
        "Resolved":            ("#D4EDDA", "#155724"),
        "Action Taken":        ("#CCE5FF", "#004085"),
        "Open / Pending":      ("#F8D7DA", "#721C24"),
        "Escalated":           ("#F8D7DA", "#721C24"),
    }

    def _rebuild_blue_table(self, data):
        if self.blue_tracker_table is None or self.blue_tracker_layout is None:
            return
        headers = ["Student No.", "Student Name", "Year", "Violation Type",
                   "Severity", "Date", "Action Taken", "Status"]
        for i in range(self.blue_tracker_layout.count()):
            item = self.blue_tracker_layout.itemAt(i)
            if item and item.widget() is self.blue_tracker_table:
                self.blue_tracker_layout.removeWidget(self.blue_tracker_table)
                self.blue_tracker_table.deleteLater()
                break
        self.blue_tracker_table = build_record_table(headers, data)
        self.blue_tracker_table.setMinimumHeight(260)
        # Colour-code status column
        for r in range(self.blue_tracker_table.rowCount()):
            cell = self.blue_tracker_table.item(r, 7)
            if cell and cell.text() in self.STATUS_COLORS:
                bg, fg = self.STATUS_COLORS[cell.text()]
                cell.setBackground(QColor(bg))
                cell.setForeground(QColor(fg))
        self.blue_tracker_layout.insertWidget(self._blue_table_index,
                                              self.blue_tracker_table)

    def _refresh_blue_tracker(self):
        """Reload from DB then re-apply active filters."""
        self._load_blue_tracker_data()
        self._apply_blue_filters()

    def _build_tracker_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Blue Slip Record Tracker"))
        lay.addWidget(SubTitle("All filed violations and their current status"))

        # ── Filter Panel ──────────────────────────────────────────────────────
        filter_panel = QFrame()
        filter_panel.setStyleSheet(_filter_panel_style(BLUE_SLIP))
        panel_lay = QVBoxLayout(filter_panel)
        panel_lay.setContentsMargins(16, 14, 16, 14)
        panel_lay.setSpacing(10)

        # Row 1 — Search + Semester + Status + Severity + Refresh
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self._blue_search = QLineEdit()
        self._blue_search.setPlaceholderText(
            "Search by student name, number, or violation type...")
        self._blue_search.setFixedHeight(38)
        self._blue_search.setStyleSheet(_search_style(BLUE_SLIP))
        self._blue_search.textChanged.connect(self._apply_blue_filters)

        self._blue_sem_filter = QComboBox()
        self._blue_sem_filter.addItems(["All Semesters", "1st", "2nd", "Summer"])
        self._blue_sem_filter.setFixedHeight(38)
        self._blue_sem_filter.setFixedWidth(145)
        self._blue_sem_filter.setToolTip("Filter by semester")
        self._blue_sem_filter.setStyleSheet(_combo_style(BLUE_SLIP))
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self._blue_sem_filter.setCurrentIndex(1)
        elif "2nd" in current_sem:
            self._blue_sem_filter.setCurrentIndex(2)
        self._blue_sem_filter.currentIndexChanged.connect(self._apply_blue_filters)

        self._blue_status_filter = QComboBox()
        self._blue_status_filter.addItems([
            "All Status", "Open / Pending", "Under Investigation",
            "Action Taken", "Resolved", "Escalated"
        ])
        self._blue_status_filter.setFixedHeight(38)
        self._blue_status_filter.setFixedWidth(190)
        self._blue_status_filter.setToolTip("Filter by case status")
        self._blue_status_filter.setStyleSheet(_combo_style(BLUE_SLIP))
        self._blue_status_filter.currentIndexChanged.connect(self._apply_blue_filters)

        self._blue_severity_filter = QComboBox()
        self._blue_severity_filter.addItems(
            ["All Levels", "Level 1", "Level 2", "Level 3", "Level 4"])
        self._blue_severity_filter.setFixedHeight(38)
        self._blue_severity_filter.setFixedWidth(120)
        self._blue_severity_filter.setToolTip("Filter by severity level")
        self._blue_severity_filter.setStyleSheet(_combo_style(BLUE_SLIP))
        self._blue_severity_filter.currentIndexChanged.connect(self._apply_blue_filters)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setStyleSheet(btn_blue())
        refresh_btn.setFixedHeight(38)
        refresh_btn.setFixedWidth(110)
        refresh_btn.setToolTip("Reload all records from the database")
        refresh_btn.clicked.connect(self._refresh_blue_tracker)

        row1.addWidget(self._blue_search, 1)
        row1.addWidget(self._blue_sem_filter)
        row1.addWidget(self._blue_status_filter)
        row1.addWidget(self._blue_severity_filter)
        row1.addWidget(refresh_btn)
        panel_lay.addLayout(row1)

        # Row 2 — Date Range filter
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        date_lbl = QLabel("Date Range:")
        date_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        date_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._blue_date_toggle = QComboBox()
        self._blue_date_toggle.addItems(["All Dates", "Filter by Date Range"])
        self._blue_date_toggle.setFixedHeight(38)
        self._blue_date_toggle.setFixedWidth(185)
        self._blue_date_toggle.setToolTip("Toggle date range filtering")
        self._blue_date_toggle.setStyleSheet(_combo_style(BLUE_SLIP))

        self._blue_from_lbl = QLabel("From:")
        self._blue_from_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._blue_from_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._blue_date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self._blue_date_from.setCalendarPopup(True)
        self._blue_date_from.setFixedHeight(38)
        self._blue_date_from.setFixedWidth(165)
        self._blue_date_from.setDisplayFormat("MMM d, yyyy")
        self._blue_date_from.setStyleSheet(_date_edit_style(BLUE_SLIP))
        self._blue_date_from.setEnabled(False)

        self._blue_to_lbl = QLabel("To:")
        self._blue_to_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._blue_to_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._blue_date_to = QDateEdit(QDate.currentDate())
        self._blue_date_to.setCalendarPopup(True)
        self._blue_date_to.setFixedHeight(38)
        self._blue_date_to.setFixedWidth(165)
        self._blue_date_to.setDisplayFormat("MMM d, yyyy")
        self._blue_date_to.setStyleSheet(_date_edit_style(BLUE_SLIP))
        self._blue_date_to.setEnabled(False)

        def _toggle_blue_dates(idx):
            on = (idx == 1)
            self._blue_date_from.setEnabled(on)
            self._blue_date_to.setEnabled(on)
            self._blue_from_lbl.setEnabled(on)
            self._blue_to_lbl.setEnabled(on)
            self._apply_blue_filters()

        self._blue_date_toggle.currentIndexChanged.connect(_toggle_blue_dates)
        self._blue_date_from.dateChanged.connect(self._apply_blue_filters)
        self._blue_date_to.dateChanged.connect(self._apply_blue_filters)

        row2.addWidget(date_lbl)
        row2.addWidget(self._blue_date_toggle)
        row2.addWidget(self._blue_from_lbl)
        row2.addWidget(self._blue_date_from)
        row2.addWidget(self._blue_to_lbl)
        row2.addWidget(self._blue_date_to)
        row2.addStretch()
        panel_lay.addLayout(row2)

        lay.addWidget(filter_panel)

        # ── Table ─────────────────────────────────────────────────────────────
        headers = ["Student No.", "Student Name", "Year", "Violation Type",
                   "Severity", "Date", "Action Taken", "Status"]
        sample = self._load_blue_tracker_data()
        self.blue_tracker_table = build_record_table(headers, sample)
        # Apply initial status colours
        for r in range(self.blue_tracker_table.rowCount()):
            cell = self.blue_tracker_table.item(r, 7)
            if cell and cell.text() in self.STATUS_COLORS:
                bg, fg = self.STATUS_COLORS[cell.text()]
                cell.setBackground(QColor(bg))
                cell.setForeground(QColor(fg))
        self.blue_tracker_table.setMinimumHeight(260)
        lay.addWidget(self.blue_tracker_table)

        self.blue_tracker_layout = lay
        # lay indices: 0=SectionTitle, 1=SubTitle, 2=filter_panel, 3=table
        self._blue_table_index = 3

        action_row = QHBoxLayout()
        action_row.addStretch()
        view_btn   = QPushButton("  View Details ")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        update_btn = QPushButton("  Update Status")
        update_btn.setStyleSheet(btn_blue())
        update_btn.setFixedHeight(38)
        del_btn    = QPushButton("   Delete ")
        del_btn.setStyleSheet(btn_danger())
        del_btn.setFixedHeight(38)
        action_row.addWidget(view_btn)
        action_row.addWidget(update_btn)
        action_row.addWidget(del_btn)
        lay.addLayout(action_row)
        lay.addStretch()
        return w

    # =========================================================================
    # Violation Progress tab  (UNCHANGED)
    # =========================================================================
    def _build_progress_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("Violation Progress Tracker"))
        lay.addWidget(SubTitle("Monitor the disciplinary progress of individual students"))

        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background: #E3F2FD;
                border: 1px solid {BLUE_SLIP}40;
                border-radius: 10px;
                padding: 6px;
            }}
        """)
        s_lay = QHBoxLayout(search_frame)
        s_lay.setContentsMargins(14, 10, 14, 10)

        s_lay.addWidget(QLabel("Student Number:"))
        stud_search = QLineEdit()
        stud_search.setPlaceholderText(
            "Enter student number to view their full violation history")
        stud_search.setFixedHeight(38)
        stud_search.setFixedWidth(380)
        search_go = QPushButton("   Load History ")
        search_go.setStyleSheet(btn_blue())
        search_go.setFixedHeight(38)

        s_lay.addWidget(stud_search)
        s_lay.addWidget(search_go)
        s_lay.addStretch()
        lay.addWidget(search_frame)

        prog_frame = QFrame()
        prog_frame.setStyleSheet(f"QFrame {{ background: {WHITE}; border: none; }}")
        p_lay = QVBoxLayout(prog_frame)
        p_lay.setContentsMargins(0, 0, 0, 0)
        p_lay.setSpacing(8)

        name_lbl = QLabel(
            "Search for a student to view their violation escalation progress")
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_lbl.setStyleSheet(f"""
            color: {MID_GRAY};
            background: #F8F9FA;
            border: 1px solid {LIGHT_GRAY};
            border-radius: 8px;
            padding: 10px 14px;
        """)
        p_lay.addWidget(name_lbl)

        steps = [
            ("1st Offense", "Verbal Warning",                        "", False, False),
            ("2nd Offense", "Written Warning",                       "", False, False),
            ("3rd Offense", "Parent Meeting + Community Service",    "", False, False),
            ("4th Offense", "Suspension",                            "", False, False),
            ("5th Offense", "Endorsement / Probation",               "", False, False),
        ]

        for step_name, action, date, done, current in steps:
            s_frame = QFrame()
            if current:
                bg, border_color, text_color = "#FFF3E0", RED_ERR, "#B71C1C"
            elif done:
                bg, border_color, text_color = "#F1F8E9", "#43A047", "#1B5E20"
            else:
                bg, border_color, text_color = "#FAFAFA", LIGHT_GRAY, MID_GRAY

            s_frame.setStyleSheet(f"""
                QFrame {{
                    background: {bg};
                    border-left: 4px solid {border_color};
                    border-top: 1px solid {border_color}40;
                    border-bottom: 1px solid {border_color}40;
                    border-right: 1px solid {border_color}40;
                    border-radius: 8px;
                }}
            """)
            s_frame.setFixedHeight(48)

            s_inner = QHBoxLayout(s_frame)
            s_inner.setContentsMargins(14, 0, 14, 0)
            s_inner.setSpacing(10)

            dot_lbl = QLabel()
            dot_lbl.setFixedSize(22, 22)
            if current:
                dot_lbl.setStyleSheet(f"background: {RED_ERR}; border-radius: 11px; border: none;")
            elif done:
                dot_lbl.setStyleSheet(f"background: #43A047; border-radius: 11px; border: none;")
            else:
                dot_lbl.setStyleSheet(
                    f"background: {LIGHT_GRAY}; border-radius: 11px; border: none;")

            step_lbl = QLabel(f"<b>{step_name}</b> &nbsp;—&nbsp; {action}")
            step_lbl.setFont(QFont("Segoe UI", 12))
            step_lbl.setTextFormat(Qt.RichText)
            step_lbl.setStyleSheet(
                f"background: transparent; color: {text_color}; border: none;")

            s_inner.addWidget(dot_lbl)
            s_inner.addWidget(step_lbl, 1)

            if current:
                curr_badge = QLabel("CURRENT")
                curr_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
                curr_badge.setAlignment(Qt.AlignCenter)
                curr_badge.setFixedHeight(22)
                curr_badge.setMinimumWidth(64)
                curr_badge.setStyleSheet(f"""
                    background: {RED_ERR}; color: white;
                    border-radius: 4px; padding: 0px 8px; border: none;
                """)
                s_inner.addWidget(curr_badge)

            date_lbl = QLabel(date if date else "—")
            date_lbl.setFont(QFont("Segoe UI", 11))
            date_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            date_lbl.setFixedWidth(100)
            date_lbl.setStyleSheet(
                f"color: {MID_GRAY}; background: transparent; border: none;")
            s_inner.addWidget(date_lbl)

            p_lay.addWidget(s_frame)

        lay.addWidget(prog_frame)
        lay.addStretch()
        return w

    # =========================================================================
    # Summary tab  (UNCHANGED — refresh button already exists)
    # =========================================================================
    def _build_summary_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Blue Slip Summary"))

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        self.blue_stat_tiles = {}
        self._update_blue_stats(tiles_row)
        lay.addLayout(tiles_row)

        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        refresh_btn = QPushButton("⟳  Refresh Charts")
        refresh_btn.setStyleSheet(btn_blue())
        refresh_btn.setFixedHeight(36)
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self._refresh_blue_summary)
        refresh_row.addWidget(refresh_btn)
        refresh_row.addStretch()
        lay.addLayout(refresh_row)

        from ui.chart_widgets import BlueSlipChart
        self.blue_chart = BlueSlipChart(w)
        self.blue_chart.setMinimumHeight(380)
        lay.addWidget(self.blue_chart)

        self._refresh_blue_summary()
        lay.addStretch()
        return w

    def _update_blue_stats(self, tiles_row: QHBoxLayout):
        from backend.db_blue_slip import get_blue_slips
        blue_records    = get_blue_slips(None) or []
        total           = len(blue_records)
        pending_count   = sum(1 for r in blue_records if len(r) > 10 and "Pending"  in str(r[10]))
        open_count      = sum(1 for r in blue_records if len(r) > 10 and "Open"     in str(r[10]))
        escalated_count = sum(1 for r in blue_records if len(r) > 10 and "Escalat"  in str(r[10]))
        resolved_count  = sum(1 for r in blue_records if len(r) > 10 and "Resolved" in str(r[10]))
        for label, val, colour in [
            ("Total Violations (Sem)", str(total),                        BLUE_SLIP),
            ("Pending / Open",         str(pending_count + open_count),   "#F57F17"),
            ("Escalated Cases",        str(escalated_count),              RED_ERR),
            ("Resolved",               str(resolved_count),               "#2E7D32"),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self.blue_stat_tiles[label] = tile

    def _refresh_blue_summary(self):
        from backend.db_blue_slip import get_blue_slips
        blue_records    = get_blue_slips(None) or []
        violation_types = {}
        for r in blue_records:
            if len(r) > 5:
                vtype = str(r[5])
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
        pending_count   = sum(1 for r in blue_records if len(r) > 10 and "Pending"  in str(r[10]))
        open_count      = sum(1 for r in blue_records if len(r) > 10 and "Open"     in str(r[10]))
        escalated_count = sum(1 for r in blue_records if len(r) > 10 and "Escalat"  in str(r[10]))
        resolved_count  = sum(1 for r in blue_records if len(r) > 10 and "Resolved" in str(r[10]))
        if hasattr(self, 'blue_chart'):
            self.blue_chart.update_data(violation_types,
                                        pending_count + open_count,
                                        escalated_count, resolved_count)


# ── Helper import ─────────────────────────────────────────────────────────────
from ui.components import Divider
from ui.pages.base_page import build_record_table
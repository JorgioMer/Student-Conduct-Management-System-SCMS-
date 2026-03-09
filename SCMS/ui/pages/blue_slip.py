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

# Backend database imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_blue_slip import add_blue_slip, get_blue_slips
from backend.config import get_current_semester


class BlueSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blue_tracker_table = None
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

        tabs.addTab(self._build_record_tab(), "  File Blue Slip ")
        tabs.addTab(self._build_tracker_tab(), "  Blue Slip Tracker ")
        tabs.addTab(self._build_progress_tab(), "   Violation Progress")
        tabs.addTab(self._build_summary_tab(), "   Summary & Charts ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Record form tab ───────────────────────────────────────────────────────
    def _build_record_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        # Escalation warning
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

        # Row 0
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

        # Row 1
        form_lay.addWidget(lbl("Course & Year"), 1, 0)
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

        # Row 2
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

        # Row 3
        form_lay.addWidget(lbl("Violation Description", True), 3, 0)
        self.blue_desc = QTextEdit()
        self.blue_desc.setPlaceholderText("Provide a detailed account of the violation incident...")
        self.blue_desc.setFixedHeight(75)
        form_lay.addWidget(self.blue_desc, 3, 1, 1, 3)

        # Row 4
        form_lay.addWidget(lbl("Action Taken"), 4, 0)
        self.blue_action = QComboBox()
        self.blue_action.addItems([
            "Verbal Warning",
            "Written Warning",
            "Parent Meeting",
            "Community Service",
            "Suspension (specify days)",
            "Endorsement to Guidance",
            "Probation",
            "Other",
        ])
        self.blue_action.setFixedHeight(38)
        form_lay.addWidget(self.blue_action, 4, 1)

        form_lay.addWidget(lbl("Officer in Charge", True), 4, 2)
        self.blue_officer = QLineEdit()
        self.blue_officer.setPlaceholderText("Name of prefect / officer")
        self.blue_officer.setFixedHeight(38)
        form_lay.addWidget(self.blue_officer, 4, 3)

        # Row 5
        form_lay.addWidget(lbl("Status"), 5, 0)
        self.blue_status = QComboBox()
        self.blue_status.addItems([
            "Open / Pending",
            "Under Investigation",
            "Action Taken",
            "Resolved",
            "Escalated",
        ])
        self.blue_status.setFixedHeight(38)
        form_lay.addWidget(self.blue_status, 5, 1)

        form_lay.addWidget(lbl("Witnesses / Notes"), 5, 2)
        self.blue_witnesses = QLineEdit()
        self.blue_witnesses.setPlaceholderText("Names of witnesses (optional)")
        self.blue_witnesses.setFixedHeight(38)
        form_lay.addWidget(self.blue_witnesses, 5, 3)

        # Row 6
        form_lay.addWidget(lbl("Semester", True), 6, 0)
        self.blue_semester = QComboBox()
        self.blue_semester.addItems(["1st", "2nd", "Summer"])
        self.blue_semester.setFixedHeight(38)
        # Set to current semester from config
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.blue_semester.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.blue_semester.setCurrentIndex(1)
        form_lay.addWidget(self.blue_semester, 6, 1)

        # Escalation flag
        self.blue_escalate_chk = QCheckBox(
            "    Flag as ESCALATED (repeated same violation)")
        self.blue_escalate_chk.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.blue_escalate_chk.setStyleSheet(f"color: {RED_ERR}; background: transparent;")
        form_lay.addWidget(self.blue_escalate_chk, 7, 0, 1, 4)

        lay.addWidget(form_group)

        # Buttons
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
        dlg = ConfirmDialog("Confirm Save", "Save this Blue Slip violation record?", parent=self)
        if dlg.exec_():
            try:
                stud_num = self.blue_no.text().strip()
                stud_name = self.blue_name.text().strip()
                stud_course = self.blue_course.text().strip()
                stud_year = self.blue_year.currentText()
                semester = self.blue_semester.currentText()
                violation_type = self.blue_vtype.currentText()
                date_of_violation = self.blue_date.date().toPyDate()
                severity = self.blue_severity.currentText()
                action_taken = self.blue_action.currentText()
                status = self.blue_status.currentText()
                violation_desc = self.blue_desc.toPlainText().strip()
                witnesses = self.blue_witnesses.text().strip()

                add_blue_slip(stud_num, violation_type, date_of_violation, severity,
                             action_taken, status=status, violation_desc=violation_desc,
                             witnesses=witnesses, stud_name=stud_name,
                             stud_course=stud_course, stud_year=stud_year)

                InfoDialog("Record Saved",
                           "Blue Slip violation record has been saved successfully!",
                           success=True, parent=self).exec_()
                # Refresh tracker tab
                self._refresh_blue_tracker()
                # Refresh summary charts
                self._refresh_blue_summary()
            except Exception as e:
                InfoDialog("Error",
                           f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    def _load_blue_tracker_data(self):
        """Load blue slip data from database"""
        from backend.db_blue_slip import get_blue_slips
        from backend.db_students import get_student
        
        sample = []
        try:
            blue_slips = get_blue_slips(None) or []
            for record in blue_slips:
                try:
                    # Record structure: (studName, studCourse, studYrLvl, ID, studNumber, violationType_blue, dateOfViolation_blue, confiscatedBy_blue, severityLvl_blue, actionTaken_blue, status_blue, violationDesc_blue, witnesses_blue)
                    stud_name = record[0] if len(record) > 0 else "N/A"
                    stud_year = record[2] if len(record) > 2 else "N/A"
                    stud_num = record[4] if len(record) > 4 else "N/A"
                    violation_type = record[5] if len(record) > 5 else "N/A"
                    date_vio = str(record[6]) if len(record) > 6 else "N/A"
                    severity = record[8] if len(record) > 8 else "N/A"
                    action = record[9] if len(record) > 9 else "N/A"
                    status = record[10] if len(record) > 10 else "Open / Pending"
                    sample.append((stud_num, stud_name, stud_year, violation_type, severity, date_vio[:10], action, status))
                except:
                    pass
        except:
            pass
        
        if not sample:
            sample = [("No records", "Add records to see them here", "-", "-", "-", "-", "-", "-")]
        
        return sample

    def _refresh_blue_tracker(self):
        """Refresh the blue slip tracker table"""
        if self.blue_tracker_table is not None:
            data = self._load_blue_tracker_data()
            
            self.blue_tracker_table.setRowCount(0)
            STATUS_COLORS = {
                "Under Investigation": ("#FFF3CD", "#856404"),
                "Resolved":            ("#D4EDDA", "#155724"),
                "Action Taken":        ("#CCE5FF", "#004085"),
                "Open / Pending":      ("#F8D7DA", "#721C24"),
                "Escalated":           ("#F8D7DA", "#721C24"),
            }
            for row_data in data:
                row_idx = self.blue_tracker_table.rowCount()
                self.blue_tracker_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.blue_tracker_table.setItem(row_idx, col_idx, item)
                
                status_val = str(row_data[7]) if len(row_data) > 7 else ""
                if status_val in STATUS_COLORS:
                    bg, fg = STATUS_COLORS[status_val]
                    self.blue_tracker_table.item(row_idx, 7).setBackground(QColor(bg))
                    self.blue_tracker_table.item(row_idx, 7).setForeground(QColor(fg))

    # ── Tracker tab ───────────────────────────────────────────────────────────
    def _build_tracker_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Blue Slip Record Tracker"))
        lay.addWidget(SubTitle("All filed violations and their current status"))

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        search = QLineEdit()
        search.setPlaceholderText("   Search by student name, number, or violation type... ")
        search.setFixedHeight(38)

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

        status_filter = QComboBox()
        status_filter.addItems(["All Status","Open / Pending","Under Investigation",
                                "Action Taken","Resolved","Escalated"])
        status_filter.setFixedHeight(38)
        status_filter.setFixedWidth(190)

        severity_filter = QComboBox()
        severity_filter.addItems(["All Levels","Level 1","Level 2","Level 3","Level 4"])
        severity_filter.setFixedHeight(38)
        severity_filter.setFixedWidth(130)

        top_row.addWidget(search, 1)
        top_row.addWidget(semester_filter)
        top_row.addWidget(status_filter)
        top_row.addWidget(severity_filter)
        refresh_btn = QPushButton("   Refresh ")
        refresh_btn.setStyleSheet(btn_outline())
        refresh_btn.setFixedHeight(38)
        refresh_btn.clicked.connect(self._refresh_blue_tracker)
        top_row.addWidget(refresh_btn)
        lay.addLayout(top_row)

        headers = ["Student No.", "Student Name", "Year", "Violation Type",
                   "Severity", "Date", "Action Taken", "Status"]
        
        sample = self._load_blue_tracker_data()
        
        self.blue_tracker_table = build_record_table(headers, sample)

        STATUS_COLORS = {
            "Under Investigation": ("#FFF3CD", "#856404"),
            "Resolved":            ("#D4EDDA", "#155724"),
            "Action Taken":        ("#CCE5FF", "#004085"),
            "Open / Pending":      ("#F8D7DA", "#721C24"),
            "Escalated":           ("#F8D7DA", "#721C24"),
        }
        for r in range(self.blue_tracker_table.rowCount()):
            status_val = self.blue_tracker_table.item(r, 7).text() if self.blue_tracker_table.item(r, 7) else ""
            if status_val in STATUS_COLORS:
                bg, fg = STATUS_COLORS[status_val]
                self.blue_tracker_table.item(r, 7).setBackground(QColor(bg))
                self.blue_tracker_table.item(r, 7).setForeground(QColor(fg))
        
        self.blue_tracker_table.setMinimumHeight(260)
        lay.addWidget(self.blue_tracker_table)

        action_row = QHBoxLayout()
        action_row.addStretch()
        view_btn = QPushButton("  View Details ")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        update_btn = QPushButton("  Update Status")
        update_btn.setStyleSheet(btn_blue())
        update_btn.setFixedHeight(38)
        del_btn = QPushButton("   Delete ")
        del_btn.setStyleSheet(btn_danger())
        del_btn.setFixedHeight(38)
        action_row.addWidget(view_btn)
        action_row.addWidget(update_btn)
        action_row.addWidget(del_btn)
        lay.addLayout(action_row)
        lay.addStretch()
        return w

    # ── Violation Progress tab ────────────────────────────────────────────────
    def _build_progress_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("Violation Progress Tracker"))
        lay.addWidget(SubTitle("Monitor the disciplinary progress of individual students"))

        # Student search
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
        stud_search.setPlaceholderText("Enter student number to view their full violation history")
        stud_search.setFixedHeight(38)
        stud_search.setFixedWidth(380)
        search_go = QPushButton("   Load History ")
        search_go.setStyleSheet(btn_blue())
        search_go.setFixedHeight(38)

        s_lay.addWidget(stud_search)
        s_lay.addWidget(search_go)
        s_lay.addStretch()
        lay.addWidget(search_frame)

        # Progress display — FIX: removed outer border from prog_frame,
        # each step row (s_frame) already has its own clean border
        prog_frame = QFrame()
        prog_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: none;
            }}
        """)
        p_lay = QVBoxLayout(prog_frame)
        p_lay.setContentsMargins(0, 0, 0, 0)
        p_lay.setSpacing(8)

        # Student profile header
        name_lbl = QLabel("Search for a student to view their violation escalation progress")
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_lbl.setStyleSheet(f"""
            color: {MID_GRAY};
            background: #F8F9FA;
            border: 1px solid {LIGHT_GRAY};
            border-radius: 8px;
            padding: 10px 14px;
        """)
        p_lay.addWidget(name_lbl)

        # Steps definition: (label, action, date, done, current)
        steps = [
            ("1st Offense", "Verbal Warning",                        "",  False, False),
            ("2nd Offense", "Written Warning",                       "", False,  False),
            ("3rd Offense", "Parent Meeting + Community Service",    "",  False, False),
            ("4th Offense", "Suspension",                            "",  False, False),
            ("5th Offense", "Endorsement / Probation",               "",  False, False),
        ]

        for step_name, action, date, done, current in steps:
            s_frame = QFrame()

            if current:
                bg           = "#FFF3E0"
                border_color = RED_ERR
                text_color   = "#B71C1C"
            elif done:
                bg           = "#F1F8E9"
                border_color = "#43A047"
                text_color   = "#1B5E20"
            else:
                bg           = "#FAFAFA"
                border_color = LIGHT_GRAY
                text_color   = MID_GRAY

            # FIX: single border only — removed the double-border by using
            # one unified border style instead of border + border-left override
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

            # Dot indicator
            dot_lbl = QLabel()
            dot_lbl.setFixedSize(22, 22)
            if current:
                dot_lbl.setStyleSheet(f"""
                    background: {RED_ERR};
                    border-radius: 11px;
                    color: white;
                    border: none;
                """)
            elif done:
                dot_lbl.setStyleSheet(f"""
                    background: #43A047;
                    border-radius: 11px;
                    color: white;
                    border: none;
                """)
            else:
                dot_lbl.setStyleSheet(f"""
                    background: {LIGHT_GRAY};
                    border-radius: 11px;
                    color: {MID_GRAY};
                    border: none;
                """)

            # Step name bold + action
            step_lbl = QLabel(f"<b>{step_name}</b> &nbsp;—&nbsp; {action}")
            step_lbl.setFont(QFont("Segoe UI", 12))
            step_lbl.setTextFormat(Qt.RichText)
            step_lbl.setStyleSheet(f"background: transparent; color: {text_color}; border: none;")

            s_inner.addWidget(dot_lbl)
            s_inner.addWidget(step_lbl, 1)

            # CURRENT badge
            if current:
                curr_badge = QLabel("CURRENT")
                curr_badge.setFont(QFont("Segoe UI", 9, QFont.Bold))
                curr_badge.setAlignment(Qt.AlignCenter)
                curr_badge.setFixedHeight(22)
                curr_badge.setMinimumWidth(64)
                curr_badge.setStyleSheet(f"""
                    background: {RED_ERR};
                    color: white;
                    border-radius: 4px;
                    padding: 0px 8px;
                    border: none;
                """)
                s_inner.addWidget(curr_badge)

            # Date label (right-aligned)
            date_lbl = QLabel(date if date else "—")
            date_lbl.setFont(QFont("Segoe UI", 11))
            date_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            date_lbl.setFixedWidth(100)
            date_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")
            s_inner.addWidget(date_lbl)

            p_lay.addWidget(s_frame)

        lay.addWidget(prog_frame)
        lay.addStretch()
        return w

    # ── Summary tab ───────────────────────────────────────────────────────────
    def _build_summary_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Blue Slip Summary"))

        # Calculate and display statistics
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        self.blue_stat_tiles = {}
        self._update_blue_stats(tiles_row)
        lay.addLayout(tiles_row)

        # Add refresh button for manual refresh
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

        # Create and add chart
        from ui.chart_widgets import BlueSlipChart
        self.blue_chart = BlueSlipChart(w)
        self.blue_chart.setMinimumHeight(380)
        lay.addWidget(self.blue_chart)
        
        # Initialize chart with current data
        self._refresh_blue_summary()
        
        lay.addStretch()
        return w
    
    def _update_blue_stats(self, tiles_row: QHBoxLayout):
        """Update statistics tiles."""
        from backend.db_blue_slip import get_blue_slips
        
        blue_records = get_blue_slips(None) or []
        total_violations = len(blue_records)
        pending_count = sum(1 for r in blue_records if len(r) > 10 and "Pending" in str(r[10]))
        open_count = sum(1 for r in blue_records if len(r) > 10 and "Open" in str(r[10]))
        escalated_count = sum(1 for r in blue_records if len(r) > 10 and "Escalat" in str(r[10]))
        resolved_count = sum(1 for r in blue_records if len(r) > 10 and "Resolved" in str(r[10]))

        for label, val, colour in [
            ("Total Violations (Sem)", str(total_violations), BLUE_SLIP),
            ("Pending / Open",         str(pending_count + open_count),    "#F57F17"),
            ("Escalated Cases",        str(escalated_count),  RED_ERR),
            ("Resolved",               str(resolved_count),   "#2E7D32"),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self.blue_stat_tiles[label] = tile
    
    def _refresh_blue_summary(self):
        """Refresh the summary chart with current database data."""
        from backend.db_blue_slip import get_blue_slips
        
        blue_records = get_blue_slips(None) or []
        
        # Build violation type distribution
        violation_types = {}
        for r in blue_records:
            if len(r) > 5:
                vtype = str(r[5])
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        # Count statuses
        pending_count = sum(1 for r in blue_records if len(r) > 10 and "Pending" in str(r[10]))
        open_count = sum(1 for r in blue_records if len(r) > 10 and "Open" in str(r[10]))
        escalated_count = sum(1 for r in blue_records if len(r) > 10 and "Escalat" in str(r[10]))
        resolved_count = sum(1 for r in blue_records if len(r) > 10 and "Resolved" in str(r[10]))
        
        # Update chart
        if hasattr(self, 'blue_chart'):
            self.blue_chart.update_data(violation_types, pending_count + open_count, escalated_count, resolved_count)


# ── Helper import ─────────────────────────────────────────────────────────────
from ui.components import Divider
from ui.pages.base_page import build_record_table
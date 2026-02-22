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


class BlueSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.main_layout.addWidget(page_header(
            "blue",
            "📘  Blue Slip Management",
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

        tabs.addTab(self._build_record_tab(), "📋  File Blue Slip")
        tabs.addTab(self._build_tracker_tab(), "📊  Blue Slip Tracker")
        tabs.addTab(self._build_progress_tab(), "🔄  Violation Progress")
        tabs.addTab(self._build_summary_tab(), "📈  Summary & Charts")

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
            "⚠  Escalation Policy: A student who receives the SAME violation multiple times "
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
        form_lay.addWidget(lbl("Grade & Section"), 1, 0)
        grade_row = QHBoxLayout()
        self.blue_grade = QComboBox()
        self.blue_grade.addItems(["Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12"])
        self.blue_grade.setFixedHeight(38)
        self.blue_section = QLineEdit()
        self.blue_section.setPlaceholderText("Section")
        self.blue_section.setFixedHeight(38)
        grade_row.addWidget(self.blue_grade)
        grade_row.addWidget(self.blue_section)
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

        # Escalation flag
        self.blue_escalate_chk = QCheckBox(
            " ⚠  Flag as ESCALATED (repeated same violation)")
        self.blue_escalate_chk.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.blue_escalate_chk.setStyleSheet(f"color: {RED_ERR}; background: transparent;")
        form_lay.addWidget(self.blue_escalate_chk, 6, 0, 1, 4)

        lay.addWidget(form_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        history_btn = QPushButton("📋  Check Violation History")
        history_btn.setStyleSheet(btn_outline())
        history_btn.setFixedHeight(40)
        history_btn.setToolTip("Check if this student has prior violations of the same type")
        history_btn.clicked.connect(self._check_history)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)

        save_btn = QPushButton("💾  Save Violation Record")
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
            "• Nov 1, 2024 — Disrespect to Authority (Resolved)\n\n"
            "⚠  This student has 1 prior violation of a similar type.\n"
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
            InfoDialog("Record Saved",
                       "Blue Slip violation record has been saved successfully!",
                       parent=self).exec_()

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
        search.setPlaceholderText("🔍  Search by student name, number, or violation type...")
        search.setFixedHeight(38)

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
        top_row.addWidget(status_filter)
        top_row.addWidget(severity_filter)
        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setStyleSheet(btn_outline())
        refresh_btn.setFixedHeight(38)
        top_row.addWidget(refresh_btn)
        lay.addLayout(top_row)

        headers = ["Student No.", "Student Name", "Grade", "Violation Type",
                   "Severity", "Date", "Action Taken", "Status"]
        sample = [
            ("2024-0045", "Santos, Maria R.",    "Grade 10", "Bullying",                  "Level 3", "Nov 19, 2024", "Parent Meeting",       "Under Investigation"),
            ("2024-0033", "Garcia, Paolo B.",    "Grade 11", "Skipping Class",             "Level 1", "Nov 15, 2024", "Verbal Warning",       "Resolved"),
            ("2024-0199", "Mendoza, Lara K.",    "Grade 9",  "Disrespect to Authority",   "Level 2", "Nov 12, 2024", "Written Warning",      "Action Taken"),
            ("2024-0310", "Villanueva, R. A.",   "Grade 12", "Cheating",                  "Level 3", "Nov 8, 2024",  "Endorsement Guidance", "Escalated"),
            ("2024-0060", "Cruz, Miguel P.",     "Grade 8",  "Possession Prohibited Item","Level 2", "Nov 5, 2024",  "Suspension (1 day)",   "Action Taken"),
        ]

        table = build_record_table(headers, sample)

        # Color-code Status column
        STATUS_COLORS = {
            "Under Investigation": ("#FFF3CD", "#856404"),
            "Resolved":            ("#D4EDDA", "#155724"),
            "Action Taken":        ("#CCE5FF", "#004085"),
            "Open / Pending":      ("#F8D7DA", "#721C24"),
            "Escalated":           ("#F8D7DA", "#721C24"),
        }
        for r in range(table.rowCount()):
            status_val = table.item(r, 7).text() if table.item(r, 7) else ""
            if status_val in STATUS_COLORS:
                bg, fg = STATUS_COLORS[status_val]
                table.item(r, 7).setBackground(QColor(bg))
                table.item(r, 7).setForeground(QColor(fg))

        table.setMinimumHeight(280)
        lay.addWidget(table)

        action_row = QHBoxLayout()
        action_row.addStretch()
        view_btn = QPushButton("👁  View Details")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        update_btn = QPushButton("✏  Update Status")
        update_btn.setStyleSheet(btn_blue())
        update_btn.setFixedHeight(38)
        del_btn = QPushButton("🗑  Delete")
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
        stud_search.setFixedWidth(280)
        search_go = QPushButton("🔍  Load History")
        search_go.setStyleSheet(btn_blue())
        search_go.setFixedHeight(38)

        s_lay.addWidget(stud_search)
        s_lay.addWidget(search_go)
        s_lay.addStretch()
        lay.addWidget(search_frame)

        # Progress display
        prog_frame = QFrame()
        prog_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        p_lay = QVBoxLayout(prog_frame)
        p_lay.setContentsMargins(20, 16, 20, 16)
        p_lay.setSpacing(10)

        # Sample student profile
        name_lbl = QLabel("Student: Santos, Maria R. — Grade 10, St. Clare  |  Student No. 2024-0045")
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {NAVY}; background: transparent;")

        # Progress steps
        steps = [
            ("1st Offense", "Verbal Warning", "Nov 5, 2024", True,  False),
            ("2nd Offense", "Written Warning", "Nov 12, 2024", True,  False),
            ("3rd Offense", "Parent Meeting + Community Service", "Nov 19, 2024", True,  True),
            ("4th Offense", "Suspension", "—", False, False),
            ("5th Offense", "Endorsement / Probation", "—", False, False),
        ]

        p_lay.addWidget(name_lbl)
        p_lay.addWidget(Divider())

        for step_name, action, date, done, current in steps:
            s_frame = QFrame()
            bg = "#E3F2FD" if current else ("#F1F8E9" if done else OFF_WHITE)
            border_color = RED_ERR if current else (BLUE_SLIP if done else LIGHT_GRAY)
            s_frame.setStyleSheet(f"""
                QFrame {{
                    background: {bg};
                    border-left: 4px solid {border_color};
                    border-radius: 6px;
                    padding: 2px 4px;
                }}
            """)
            s_inner = QHBoxLayout(s_frame)
            s_inner.setContentsMargins(12, 8, 12, 8)

            status_icon = "✅" if (done and not current) else ("🔴" if current else "⬜")
            icon_lbl = QLabel(status_icon)
            icon_lbl.setFont(QFont("Segoe UI", 14))
            icon_lbl.setFixedWidth(28)
            icon_lbl.setStyleSheet("background: transparent;")

            step_lbl = QLabel(f"<b>{step_name}</b> — {action}")
            step_lbl.setFont(QFont("Segoe UI", 12))
            step_lbl.setTextFormat(Qt.RichText)
            step_lbl.setStyleSheet("background: transparent;")

            date_lbl = QLabel(date)
            date_lbl.setFont(QFont("Segoe UI", 11))
            date_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")

            if current:
                curr_badge = QLabel("  ◀ CURRENT  ")
                curr_badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
                curr_badge.setStyleSheet(f"""
                    background: {RED_ERR};
                    color: white;
                    border-radius: 4px;
                    padding: 2px 6px;
                """)
                s_inner.addWidget(curr_badge)

            s_inner.addWidget(icon_lbl)
            s_inner.addWidget(step_lbl, 1)
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

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        for label, val, colour in [
            ("Total Violations (Sem)", "8",  BLUE_SLIP),
            ("Pending / Open",         "3",  "#F57F17"),
            ("Escalated Cases",        "1",  RED_ERR),
            ("Resolved",               "4",  "#2E7D32"),
            ("Unique Students",        "5",  NAVY),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
        lay.addLayout(tiles_row)

        chart_frame = QFrame()
        chart_frame.setFixedHeight(280)
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background: #E3F2FD;
                border: 2px dashed {BLUE_SLIP}80;
                border-radius: 12px;
            }}
        """)
        c_lay = QVBoxLayout(chart_frame)
        c_lay.setAlignment(Qt.AlignCenter)
        c_icon = QLabel("📊")
        c_icon.setFont(QFont("Segoe UI", 48))
        c_icon.setAlignment(Qt.AlignCenter)
        c_icon.setStyleSheet("background: transparent;")
        c_text = QLabel(
            "Blue Slip charts will appear here\n"
            "(Violations by type, Grade level breakdown, Status pie chart)"
        )
        c_text.setFont(QFont("Segoe UI", 12))
        c_text.setAlignment(Qt.AlignCenter)
        c_text.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
        c_lay.addWidget(c_icon)
        c_lay.addWidget(c_text)
        lay.addWidget(chart_frame)
        lay.addStretch()
        return w


# ── Helper import ─────────────────────────────────────────────────────────────
from ui.components import Divider
from ui.pages.base_page import build_record_table

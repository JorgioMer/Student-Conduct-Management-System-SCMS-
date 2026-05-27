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
    FieldLabel, add_shadow, ConfirmDialog, InfoDialog, StatTile,
    AutoCompleteLineEdit
)
from ui.pages.base_page import BasePage, page_header, build_record_table
from ui.data_events import data_events
from ui.pages.trackers import _apply_table_selection_style

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_blue_slip import add_blue_slip, get_blue_slips
from backend.config import get_current_semester
from backend.db_accounts import get_officer_names
from backend.db_activity_log import log_slip_created

# ── Column index constants ────────────────────────────────────────────────────
# Query: SELECT s.studName, s.studCourse, s.studYrLvl, b.*
# b.* expands to: ID, studNumber, violationType_blue, dateOfViolation_blue,
#                 confiscatedBy_blue, severityLvl_blue, actionTaken_blue,
#                 status_blue, violationDesc_blue, witnesses_blue
_COL_STUD_NAME      = 0
_COL_STUD_COURSE    = 1
_COL_STUD_YEAR      = 2
_COL_SLIP_ID        = 3
_COL_STUD_NUM       = 4
_COL_VTYPE          = 5
_COL_DATE           = 6
_COL_CONFISCATED_BY = 7
_COL_SEVERITY       = 8
_COL_ACTION         = 9
_COL_STATUS         = 10
_COL_DESC           = 11
_COL_WITNESSES      = 12


class CalendarDateEdit(QDateEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCalendarPopup(True)
        svg_data = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>'''

        import tempfile, os
        self._icon_file = tempfile.NamedTemporaryFile(
            suffix=".svg", delete=False, mode='w', encoding='utf-8'
        )
        self._icon_file.write(svg_data)
        self._icon_file.flush()
        self._icon_path = self._icon_file.name.replace("\\", "/")
        self._icon_file.close()

    def apply_icon_style(self, base_style):
        icon_style = base_style + f"""
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 36px;
                background: {BLUE_SLIP};
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QDateEdit::drop-down:hover {{
                background: #1565C0;
            }}
            QDateEdit::drop-down:disabled {{
                background: #B0BEC5;
            }}
            QDateEdit::down-arrow {{
                image: url("{self._icon_path}");
                width: 18px;
                height: 18px;
            }}
        """
        self.setStyleSheet(icon_style)

    def __del__(self):
        import os
        try:
            os.unlink(self._icon_path)
        except Exception:
            pass


# ── Filter-panel shared styles ────────────────────────────────────────────────
def _filter_panel_style(accent):
    return f"""
        QFrame {{
            background: #F8F9FA;
            border: none;
            border-radius: 8px;
        }}
    """

def _date_edit_style(accent):
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
    return f"""
        QComboBox {{
            background: {WHITE};
            border: 1px solid #D0D5DD;
            border-radius: 6px;
            padding: 4px 10px;
            padding-right: 42px;
            font-size: 13px;
            font-family: "Segoe UI";
            color: {TEXT_DARK};
        }}
        QComboBox:focus {{
            border: 1.5px solid {accent};
        }}
        QComboBox:hover {{
            border: 1.5px solid {accent};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: right center;
            width: 36px;
            background: {accent};
            border-left: none;
            border-top-right-radius: 5px;
            border-bottom-right-radius: 5px;
        }}
        QComboBox::drop-down:hover {{
            background: #1565C0;
        }}
        QComboBox::down-arrow {{
            width: 0px;
            height: 0px;
            border-style: solid;
            border-width: 5px 4px 0px 4px;
            border-color: white transparent transparent transparent;
        }}
        QComboBox QAbstractItemView {{
            background: {WHITE};
            border: 1px solid #D0D5DD;
            border-radius: 4px;
            selection-background-color: {accent}30;
            selection-color: {TEXT_DARK};
            font-size: 13px;
            font-family: "Segoe UI";
            padding: 2px;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 6px 10px;
            min-height: 28px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: {accent}20;
        }}
    """

def _search_style(accent):
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


def _build_officer_combo(accent: str) -> QComboBox:
    """
    Build a QComboBox pre-populated with active officer names from the
    Accounts table.  Falls back gracefully if the DB is unavailable.
    """
    combo = QComboBox()
    combo.setFixedHeight(38)
    combo.setStyleSheet(_combo_style(accent))
    combo.addItem("— Select Officer —")          # placeholder / index 0
    for name in get_officer_names():
        combo.addItem(name)
    return combo


class BlueSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blue_tracker_table = None
        self.blue_tracker_layout = None
        self._all_blue_records = []
        self._blue_table_index = 3
        self.blue_stat_tiles = {}
        self.blue_chart = None
        self._summary_built = False
        self._tabs = None
        data_events.slips_changed.connect(self._on_slips_changed)
        self._build()

    def _build(self):
        self.main_layout.addWidget(page_header(
            "blue",
            "  Blue Slip Management ",
            "Record student violations — repeated offenses trigger escalated disciplinary action"
        ))

        tabs = QTabWidget()
        self._tabs = tabs
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
        tabs.addTab(self._build_summary_placeholder(), "   Summary & Charts ")
        tabs.currentChanged.connect(self._on_tab_changed)

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # =========================================================================
    # Record form tab
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
        self.blue_year.addItems(["1st", "2nd", "3rd", "4th"])
        self.blue_year.setFixedHeight(38)
        self.blue_year.setStyleSheet(_combo_style(BLUE_SLIP))
        self.blue_course = AutoCompleteLineEdit()
        grade_row.addWidget(self.blue_year)
        grade_row.addWidget(self.blue_course)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Date of Violation", True), 1, 2)
        self.blue_date = CalendarDateEdit(QDate.currentDate())
        self.blue_date.setFixedHeight(38)
        self.blue_date.setDisplayFormat("MMMM d, yyyy")
        self.blue_date.apply_icon_style(_date_edit_style(BLUE_SLIP))
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
        self.blue_vtype.setStyleSheet(_combo_style(BLUE_SLIP))
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
        self.blue_severity.setStyleSheet(_combo_style(BLUE_SLIP))
        form_lay.addWidget(self.blue_severity, 2, 3)

        _lbl_vd = lbl("Violation Description", True)
        _lbl_vd.setContentsMargins(0, 8, 0, 0)
        form_lay.addWidget(_lbl_vd, 3, 0, Qt.AlignTop)
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
        self.blue_action.setStyleSheet(_combo_style(BLUE_SLIP))
        form_lay.addWidget(self.blue_action, 4, 1)

        form_lay.addWidget(lbl("Officer in Charge", True), 4, 2)
        self.blue_officer = _build_officer_combo(BLUE_SLIP)
        form_lay.addWidget(self.blue_officer, 4, 3)

        form_lay.addWidget(lbl("Status"), 5, 0)
        self.blue_status = QComboBox()
        self.blue_status.addItems([
            "Open / Pending", "Under Investigation",
            "Action Taken", "Resolved", "Escalated",
        ])
        self.blue_status.setFixedHeight(38)
        self.blue_status.setStyleSheet(_combo_style(BLUE_SLIP))
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
        self.blue_semester.setStyleSheet(_combo_style(BLUE_SLIP))
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
        clear_btn.clicked.connect(self._clear_blue_form)

        save_btn = QPushButton("   Save Violation Record ")
        save_btn.setStyleSheet(btn_blue())
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_blue)

        btn_row.addWidget(history_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)
        
        # Connect auto-fill on student number entry
        self.blue_no.editingFinished.connect(self._auto_fill_blue)
        
        return w

    def _auto_fill_blue(self):
        """Auto-fill blue slip form when student number exists in database."""
        stud_no = self.blue_no.text().strip()
        if not stud_no:
            return
        
        try:
            from backend.db_students import get_student
            student = get_student(stud_no)
            if student:
                # student = (studNumber, studName, studCourse, studYrLvl, schoolYr, studStatus)
                self.blue_name.setText(student[1] or "")
                self.blue_course.setText(student[2] or "")
                
                # Set year if available
                year = student[3] or ""
                if year:
                    index = self.blue_year.findText(year)
                    if index >= 0:
                        self.blue_year.setCurrentIndex(index)
        except Exception as e:
            # Silently fail - user can fill manually
            pass

    def _clear_blue_form(self):
        self.blue_no.clear()
        self.blue_name.clear()
        self.blue_course.clear()
        self.blue_desc.clear()
        self.blue_officer.setCurrentIndex(0)
        self.blue_witnesses.clear()
        self.blue_year.setCurrentIndex(0)
        self.blue_vtype.setCurrentIndex(0)
        self.blue_severity.setCurrentIndex(0)
        self.blue_action.setCurrentIndex(0)
        self.blue_status.setCurrentIndex(0)
        self.blue_date.setDate(QDate.currentDate())
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.blue_semester.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.blue_semester.setCurrentIndex(1)
        else:
            self.blue_semester.setCurrentIndex(0)
        self.blue_escalate_chk.setChecked(False)

    def _check_history(self):
        stud_num  = self.blue_no.text().strip()
        stud_name = self.blue_name.text().strip()

        if not stud_num and not stud_name:
            InfoDialog(
                "Missing Information",
                "Please enter at least a Student Number or Student Name "
                "before checking violation history.",
                success=False, parent=self
            ).exec_()
            return
        
        try:
            all_records = get_blue_slips(None) or []
        except Exception:
            all_records = []

        matches = []
        for record in all_records:
            rec_name = str(record[_COL_STUD_NAME]).strip().lower() if len(record) > _COL_STUD_NAME else ""
            rec_num  = str(record[_COL_STUD_NUM]).strip().lower()  if len(record) > _COL_STUD_NUM  else ""
            if (stud_num  and stud_num.lower()  == rec_num) or \
               (stud_name and stud_name.lower() in rec_name):
                matches.append(record)

        current_vtype = self.blue_vtype.currentText()

        if not matches:
            InfoDialog(
                "Violation History Check",
                f"Student: {stud_name or stud_num}\n\n"
                "No prior violations found for this student.\n"
                "This would be their first recorded offense.\n\n"
                "No escalation will be triggered.",
                success=True, parent=self
            ).exec_()
            return

        lines = [
            f"Student: {stud_name or stud_num}\n",
            f"Total violations on record: {len(matches)}\n",
            "Prior violations:"
        ]

        same_type_count = 0
        for r in matches:
            vtype  = str(r[_COL_VTYPE])       if len(r) > _COL_VTYPE   else "N/A"
            date   = str(r[_COL_DATE])[:10]   if len(r) > _COL_DATE    else "N/A"
            status = str(r[_COL_STATUS])       if len(r) > _COL_STATUS  else "N/A"
            lines.append(f"  • {date}  —  {vtype}  ({status})")
            if current_vtype and current_vtype in vtype:
                same_type_count += 1

        lines.append("")  # blank line for spacing
        
        if same_type_count >= 2:
            lines.append(
                f"🔴 AUTOMATIC ESCALATION TRIGGERED:\n"
                f"This student has {same_type_count} prior violation(s) of:\n"
                f"{current_vtype}\n\n"
                f"Per escalation policy, this record will automatically\n"
                f"be marked as ESCALATED when saved."
            )
            self.blue_escalate_chk.setChecked(True)  # Auto-check the escalation box
            success = False  # Show as warning
        elif same_type_count == 1:
            lines.append(
                f"⚠ ESCALATION AVAILABLE:\n"
                f"This student has {same_type_count} prior violation of:\n"
                f"{current_vtype}\n\n"
                f"You may manually flag this as ESCALATED if you believe\n"
                f"this warrants higher disciplinary action."
            )
            success = False  # Show as warning
        else:
            lines.append(
                f"✓ No prior violations of type: {current_vtype}\n"
                f"This will be a first offense of this type.\n"
                f"No escalation will be triggered."
            )
            self.blue_escalate_chk.setChecked(False)  # Uncheck escalation
            success = True

        InfoDialog(
            "Violation History & Escalation Check",
            "\n".join(lines),
            success=success, parent=self
        ).exec_()

    def closeEvent(self, event):
        """Clean up signal connections when page is closed"""
        try:
            data_events.slips_changed.disconnect(self._on_slips_changed)
        except Exception:
            pass
        super().closeEvent(event)

    def _save_blue(self):
        if not self.blue_no.text().strip():
            InfoDialog("Missing Fields", "Please fill in all required fields.",
                       success=False, parent=self).exec_()
            return
        dlg = ConfirmDialog("Confirm Save",
                            "Save this Blue Slip violation record?", parent=self)
        if dlg.exec_():
            try:
                stud_num          = self.blue_no.text().strip()
                stud_name         = self.blue_name.text().strip()
                stud_course       = self.blue_course.text().strip()
                stud_year         = self.blue_year.currentText()
                semester          = self.blue_semester.currentText()
                violation_type    = self.blue_vtype.currentText()
                date_of_violation = self.blue_date.date().toPyDate()
                severity          = self.blue_severity.currentText()
                action_taken      = self.blue_action.currentText()
                status            = self.blue_status.currentText()
                violation_desc    = self.blue_desc.toPlainText().strip()
                witnesses         = self.blue_witnesses.text().strip()
                is_manual_escalation = self.blue_escalate_chk.isChecked()
                
                # ── Determine if this should be escalated ────────────────────
                from backend.db_blue_slip import should_escalate_violation
                should_escalate = should_escalate_violation(stud_num, violation_type, is_manual_escalation)
                
                # ── If escalation detected, update status ────────────────────
                if should_escalate and status not in ("Escalated", "Resolved"):
                    status = "Escalated"
                
                record_id = add_blue_slip(stud_num, violation_type, date_of_violation, severity,
                              action_taken, status=status, violation_desc=violation_desc,
                              witnesses=witnesses, stud_name=stud_name,
                              stud_course=stud_course, stud_year=stud_year)
                # Log the action
                log_slip_created("SYSTEM", "Blue", stud_name, record_id=record_id)
                
                # ── Show escalation warning if applicable ────────────────────
                if should_escalate and not is_manual_escalation:
                    from backend.db_blue_slip import count_violations_by_type
                    prior_count = count_violations_by_type(stud_num, violation_type)
                    InfoDialog("Record Saved & Escalated",
                               f"Blue Slip violation record has been saved.\n\n"
                               f"⚠ ESCALATION TRIGGERED:\n"
                               f"Student has {prior_count} prior violations of type:\n"
                               f"{violation_type}\n\n"
                               f"This record has been marked as ESCALATED for higher disciplinary action.",
                               success=True, parent=self).exec_()
                else:
                    InfoDialog("Record Saved",
                               "Blue Slip violation record has been saved successfully!",
                               success=True, parent=self).exec_()
                data_events.slips_changed.emit()
                self._clear_blue_form()
            except Exception as e:
                print(f"[ERROR] Failed to save blue slip: {str(e)}")
                import traceback
                traceback.print_exc()
                InfoDialog("Error", f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    # =========================================================================
    # Tracker tab
    # =========================================================================
    def _load_blue_tracker_data(self):
        sample = []
        try:
            blue_records = get_blue_slips(None) or []
            print(f"[DEBUG] Loaded {len(blue_records)} blue slip records from database")
            for record in blue_records:
                try:
                    # Query returns: ID(0), studNumber(1), studName(2), studYear(3),
                    #                violationType(4), severity(5), dateOfViolation(6),
                    #                actionTaken(7), status(8)
                    slip_id      = record[0]   # ID for deletion
                    stud_num     = record[1]   # Student Number
                    stud_name    = record[2]   # Student Name
                    stud_year    = record[3]   # Year
                    vtype        = record[4]   # Violation Type
                    severity     = record[5]   # Severity
                    date_str     = str(record[6])[:10] if len(record) > 6 else "N/A"
                    action       = str(record[7]) if len(record) > 7 else "N/A"
                    status       = str(record[8]) if len(record) > 8 else "Open / Pending"
                    sample.append((
                        slip_id,  # Hidden ID for deletion
                        stud_num, stud_name, stud_year, vtype, severity,
                        date_str, action, status,
                    ))
                except Exception as e:
                    print(f"[ERROR] Failed to parse blue slip record: {str(e)}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[ERROR] Failed to load blue slips: {str(e)}")
            import traceback
            traceback.print_exc()

        self._all_blue_records = sample
        print(f"[DEBUG] Blue tracker showing {len(sample)} records")
        return sample if sample else [
            (None, "No records", "Add records to see them here",
             "-", "-", "-", "-", "-", "-")
        ]

    def _apply_blue_filters(self):
        search_text  = self._blue_search.text().strip().lower()
        sem_val      = self._blue_sem_filter.currentText()
        status_val   = self._blue_status_filter.currentText()
        severity_val = self._blue_severity_filter.currentText()
        use_date     = self._blue_date_toggle.currentText() == "Filter by Date Range"
        date_from    = self._blue_date_from.date()
        date_to      = self._blue_date_to.date()

        filtered = []
        for row in self._all_blue_records:
            slip_id, stud_num, stud_name, year, vtype, severity, date_str, action, status = row

            if search_text and (
                    search_text not in stud_num.lower()
                    and search_text not in stud_name.lower()
                    and search_text not in vtype.lower()
            ):
                continue

            if status_val != "All Status" and status != status_val:
                continue

            if severity_val != "All Levels":
                level_num = severity_val.split()[-1]
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
            filtered = [(None, "No results",
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
        if self.blue_tracker_layout is None:
            print("[WARNING] Blue tracker layout not initialized yet")
            return
        headers = ["Student No.", "Student Name", "Year", "Violation Type",
                   "Severity", "Date", "Action Taken", "Status"]
        # Remove old table if it exists
        if self.blue_tracker_table is not None:
            for i in range(self.blue_tracker_layout.count()):
                item = self.blue_tracker_layout.itemAt(i)
                if item and item.widget() is self.blue_tracker_table:
                    self.blue_tracker_layout.removeWidget(self.blue_tracker_table)
                    self.blue_tracker_table.deleteLater()
                    break
        # Strip the ID from each row before passing to build_record_table
        display_data = []
        for row in data:
            # row[0] is slip_id, row[1:] is the display data
            display_data.append(row[1:])
        # Create and add new table
        self.blue_tracker_table = build_record_table(headers, display_data)
        _apply_table_selection_style(self.blue_tracker_table, BLUE_SLIP)
        self.blue_tracker_table.setMinimumHeight(260)
        for r in range(self.blue_tracker_table.rowCount()):
            cell = self.blue_tracker_table.item(r, 7)
            if cell and cell.text() in self.STATUS_COLORS:
                bg, fg = self.STATUS_COLORS[cell.text()]
                cell.setBackground(QColor(bg))
                cell.setForeground(QColor(fg))
        self.blue_tracker_layout.insertWidget(self._blue_table_index,
                                              self.blue_tracker_table)

    def _refresh_blue_tracker(self):
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

        filter_panel = QFrame()
        filter_panel.setStyleSheet(_filter_panel_style(BLUE_SLIP))
        panel_lay = QVBoxLayout(filter_panel)
        panel_lay.setContentsMargins(16, 14, 16, 14)
        panel_lay.setSpacing(10)

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
        self._blue_status_filter.setStyleSheet(_combo_style(BLUE_SLIP))
        self._blue_status_filter.currentIndexChanged.connect(self._apply_blue_filters)

        self._blue_severity_filter = QComboBox()
        self._blue_severity_filter.addItems(
            ["All Levels", "Level 1", "Level 2", "Level 3", "Level 4"])
        self._blue_severity_filter.setFixedHeight(38)
        self._blue_severity_filter.setFixedWidth(120)
        self._blue_severity_filter.setStyleSheet(_combo_style(BLUE_SLIP))
        self._blue_severity_filter.currentIndexChanged.connect(self._apply_blue_filters)

        refresh_btn = QPushButton("  Refresh ")
        refresh_btn.setStyleSheet(btn_blue())
        refresh_btn.setFixedHeight(38)
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self._refresh_blue_tracker)

        row1.addWidget(self._blue_search, 1)
        row1.addWidget(self._blue_sem_filter)
        row1.addWidget(self._blue_status_filter)
        row1.addWidget(self._blue_severity_filter)
        row1.addWidget(refresh_btn)
        panel_lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        date_lbl = QLabel("Date Range:")
        date_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        date_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._blue_date_toggle = QComboBox()
        self._blue_date_toggle.addItems(["All Dates", "Filter by Date Range"])
        self._blue_date_toggle.setFixedHeight(38)
        self._blue_date_toggle.setFixedWidth(185)
        self._blue_date_toggle.setStyleSheet(_combo_style(BLUE_SLIP))

        self._blue_from_lbl = QLabel("From:")
        self._blue_from_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._blue_from_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._blue_date_from = CalendarDateEdit(QDate.currentDate().addMonths(-1))
        self._blue_date_from.setFixedHeight(38)
        self._blue_date_from.setFixedWidth(165)
        self._blue_date_from.setDisplayFormat("MMM d, yyyy")
        self._blue_date_from.apply_icon_style(_date_edit_style(BLUE_SLIP))
        self._blue_date_from.setEnabled(False)

        self._blue_to_lbl = QLabel("To:")
        self._blue_to_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._blue_to_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._blue_date_to = CalendarDateEdit(QDate.currentDate())
        self._blue_date_to.setFixedHeight(38)
        self._blue_date_to.setFixedWidth(165)
        self._blue_date_to.setDisplayFormat("MMM d, yyyy")
        self._blue_date_to.apply_icon_style(_date_edit_style(BLUE_SLIP))
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

        headers = ["Student No.", "Student Name", "Year", "Violation Type",
                   "Severity", "Date", "Action Taken", "Status"]
        sample = self._load_blue_tracker_data()
        self.blue_tracker_table = build_record_table(headers, sample)
        _apply_table_selection_style(self.blue_tracker_table, BLUE_SLIP)
        for r in range(self.blue_tracker_table.rowCount()):
            cell = self.blue_tracker_table.item(r, 7)
            if cell and cell.text() in self.STATUS_COLORS:
                bg, fg = self.STATUS_COLORS[cell.text()]
                cell.setBackground(QColor(bg))
                cell.setForeground(QColor(fg))
        self.blue_tracker_table.setMinimumHeight(260)
        lay.addWidget(self.blue_tracker_table)

        self.blue_tracker_layout = lay
        self._blue_table_index = 3

        # ── Action Row ────────────────────────────────────────────────────────
        action_row = QHBoxLayout()
        action_row.addStretch()

        view_btn = QPushButton("  View Details ")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(self._view_blue_record)

        update_btn = QPushButton("  Update Status")
        update_btn.setStyleSheet(btn_blue())
        update_btn.setFixedHeight(38)
        update_btn.clicked.connect(self._update_blue_status)

        del_btn = QPushButton("   Delete ")
        del_btn.setStyleSheet(btn_danger())
        del_btn.setFixedHeight(38)
        del_btn.clicked.connect(self._delete_blue_record)

        action_row.addWidget(view_btn)
        action_row.addWidget(update_btn)
        action_row.addWidget(del_btn)
        lay.addLayout(action_row)
        lay.addStretch()
        return w

    # ── View handler for Blue Slip Tracker ───────────────────────────────────
    def _view_blue_record(self):
        """Open detail dialog for the selected row in the Blue Slip tracker."""
        if self.blue_tracker_table is None:
            return

        selected = self.blue_tracker_table.selectedItems()
        if not selected:
            InfoDialog(
                "No Record Selected",
                "Please select a student by clicking the Name or ID Number in the table.",
                success=False, parent=self
            ).exec_()
            return

        row = self.blue_tracker_table.currentRow()
        headers = [
            self.blue_tracker_table.horizontalHeaderItem(c).text()
            for c in range(self.blue_tracker_table.columnCount())
        ]
        fields = []
        for col, header in enumerate(headers):
            item = self.blue_tracker_table.item(row, col)
            fields.append((header, item.text() if item else "—"))

        from ui.pages.trackers import RecordDetailDialog
        dlg = RecordDetailDialog(fields, slip_type="blue", parent=self)
        dlg.exec_()

    def _update_blue_status(self):
        """Update the status of a selected blue slip record."""
        if self.blue_tracker_table is None:
            return
        selected = self.blue_tracker_table.selectedItems()
        if not selected:
            InfoDialog(
                "No Record Selected",
                "Please select a record to update.",
                success=False, parent=self
            ).exec_()
            return
        
        row = self.blue_tracker_table.currentRow()
        stud_num_item = self.blue_tracker_table.item(row, 0)  # Student No. is column 0
        if not stud_num_item:
            return
        
        stud_num = stud_num_item.text()
        if stud_num == "No records":
            return
        
        # Show status update dialog
        from PyQt5.QtWidgets import QComboBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton
        from PyQt5.QtCore import Qt
        dlg = QDialog(self)
        dlg.setWindowTitle("Update Blue Slip Status")
        dlg.setFixedWidth(350)
        dlg.setStyleSheet(f"background: {WHITE};")
        
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        
        lbl = QLabel("Update status for student: " + stud_num)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lay.addWidget(lbl)
        
        lay.addWidget(QLabel("New Status:"))
        status_combo = QComboBox()
        status_combo.addItems([
            "Open / Pending",
            "Under Investigation",
            "Action Taken",
            "Resolved",
            "Dismissed"
        ])
        lay.addWidget(status_combo)
        
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        
        ok_btn = QPushButton("Update")
        ok_btn.setStyleSheet(btn_blue())
        ok_btn.setFixedHeight(38)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(btn_outline())
        cancel_btn.setFixedHeight(38)
        
        btn_lay.addWidget(ok_btn)
        btn_lay.addWidget(cancel_btn)
        lay.addLayout(btn_lay)
        
        def on_update():
            try:
                new_status = status_combo.currentText()
                from backend.db_blue_slip import update_blue_slip_status
                print(f"[DEBUG] Updating blue slip status for student {stud_num} to {new_status}")
                update_blue_slip_status(stud_num, new_status)
                print(f"[DEBUG] Blue slip status updated successfully")
                dlg.accept()
                InfoDialog(
                    "Status Updated",
                    f"Blue slip status updated to: {new_status}",
                    success=True, parent=self
                ).exec_()
                data_events.slips_changed.emit()
            except Exception as e:
                print(f"[ERROR] Failed to update blue slip status: {str(e)}")
                import traceback
                traceback.print_exc()
                InfoDialog(
                    "Error",
                    f"Failed to update status: {str(e)}",
                    success=False, parent=self
                ).exec_()
        
        ok_btn.clicked.connect(on_update)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec_()

    def _delete_blue_record(self):
        """Delete selected blue slip record from database."""
        if self.blue_tracker_table is None:
            return
        selected = self.blue_tracker_table.selectedItems()
        if not selected:
            InfoDialog(
                "No Record Selected",
                "Please select a record to delete.",
                success=False, parent=self
            ).exec_()
            return
        
        row = self.blue_tracker_table.currentRow()
        
        # Get the row data from _all_blue_records (which includes the ID)
        if row < 0 or row >= len(self._all_blue_records):
            return
        
        row_data = self._all_blue_records[row]
        slip_id = row_data[0]  # First element is the ID
        stud_num = row_data[1]  # Second element is the student number
        
        if slip_id is None or stud_num == "No records":
            return
        
        dlg = ConfirmDialog(
            "Confirm Delete",
            f"Delete blue slip record for student {stud_num}?\nThis action cannot be undone.",
            parent=self
        )
        if dlg.exec_():
            try:
                from backend.db_blue_slip import delete_blue_slip
                print(f"[DEBUG] Deleting blue slip ID {slip_id} for student {stud_num}")
                delete_blue_slip(slip_id)
                print(f"[DEBUG] Blue slip deleted successfully")
                InfoDialog(
                    "Record Deleted",
                    "Blue slip record has been deleted.",
                    success=True, parent=self
                ).exec_()
                data_events.slips_changed.emit()
            except Exception as e:
                print(f"[ERROR] Failed to delete blue slip: {str(e)}")
                import traceback
                traceback.print_exc()
                InfoDialog(
                    "Error",
                    f"Failed to delete record: {str(e)}",
                    success=False, parent=self
                ).exec_()

    # =========================================================================
    # Violation Progress tab
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
        self._prog_stud_search = QLineEdit()
        self._prog_stud_search.setPlaceholderText(
            "Enter student number to view their full violation history")
        self._prog_stud_search.setFixedHeight(38)
        self._prog_stud_search.setFixedWidth(380)
        self._prog_stud_search.setStyleSheet(_search_style(BLUE_SLIP))
        self._prog_stud_search.returnPressed.connect(self._load_student_history)

        search_go = QPushButton("   Load History ")
        search_go.setStyleSheet(btn_blue())
        search_go.setFixedHeight(38)
        search_go.clicked.connect(self._load_student_history)

        s_lay.addWidget(self._prog_stud_search)
        s_lay.addWidget(search_go)
        s_lay.addStretch()
        lay.addWidget(search_frame)

        # ── Student name / status banner ──────────────────────────────────────
        self._prog_name_lbl = QLabel(
            "Search for a student to view their violation escalation progress")
        self._prog_name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._prog_name_lbl.setStyleSheet(f"""
            color: {MID_GRAY};
            background: #F8F9FA;
            border: 1px solid {LIGHT_GRAY};
            border-radius: 8px;
            padding: 10px 14px;
        """)
        lay.addWidget(self._prog_name_lbl)

        # ── Progress steps container ──────────────────────────────────────────
        self._prog_steps_frame = QFrame()
        self._prog_steps_frame.setStyleSheet(
            f"QFrame {{ background: {WHITE}; border: none; }}")
        self._prog_steps_layout = QVBoxLayout(self._prog_steps_frame)
        self._prog_steps_layout.setContentsMargins(0, 0, 0, 0)
        self._prog_steps_layout.setSpacing(8)

        # Render the default empty ladder on first load
        self._build_progress_steps([], current_offense=0)
        lay.addWidget(self._prog_steps_frame)

        lay.addStretch()
        return w

    def _build_progress_steps(self, student_violations: list, current_offense: int):
        """
        Rebuild the 5-step escalation ladder.
        student_violations : list of (vtype, date_str) tuples, one per recorded offense.
        current_offense    : total offenses capped at 5 — drives which step is highlighted.
        """
        # Clear any previously rendered steps
        while self._prog_steps_layout.count():
            child = self._prog_steps_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        escalation_steps = [
            ("1st Offense", "Verbal Warning"),
            ("2nd Offense", "Written Warning"),
            ("3rd Offense", "Parent Meeting + Community Service"),
            ("4th Offense", "Suspension"),
            ("5th Offense", "Endorsement / Probation"),
        ]

        for i, (step_name, action) in enumerate(escalation_steps):
            offense_num = i + 1
            done    = offense_num <  current_offense
            current = offense_num == current_offense

            # Use the actual violation date for this step slot if available
            date = ""
            if i < len(student_violations):
                date = student_violations[i][1]

            if current:
                bg, border_color, text_color = "#FFF3E0", RED_ERR, "#B71C1C"
            elif done:
                bg, border_color, text_color = "#F1F8E9", "#43A047", "#1B5E20"
            else:
                bg, border_color, text_color = "#FAFAFA", LIGHT_GRAY, MID_GRAY

            s_frame = QFrame()
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
                dot_lbl.setStyleSheet(
                    f"background: {RED_ERR}; border-radius: 11px; border: none;")
            elif done:
                dot_lbl.setStyleSheet(
                    f"background: #43A047; border-radius: 11px; border: none;")
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

            self._prog_steps_layout.addWidget(s_frame)

    def _load_student_history(self):
        """Load and display a student's violation escalation progress."""
        stud_num = self._prog_stud_search.text().strip()
        if not stud_num:
            InfoDialog(
                "Missing Input",
                "Please enter a student number to load their violation history.",
                success=False, parent=self
            ).exec_()
            return

        try:
            matches = get_blue_slips(stud_num) or []
        except Exception as e:
            InfoDialog("Error", f"Could not load records: {e}",
                       success=False, parent=self).exec_()
            return

        if not matches:
            self._prog_name_lbl.setText(
                f"No violation records found for student number: {stud_num}")
            self._prog_name_lbl.setStyleSheet(f"""
                color: {RED_ERR};
                background: #FFF3F3;
                border: 1px solid {RED_ERR}40;
                border-radius: 8px;
                padding: 10px 14px;
            """)
            self._build_progress_steps([], current_offense=0)
            return

        # Sort ascending by date so the earliest offense = step 1
        matches.sort(key=lambda r: str(r[_COL_DATE]) if len(r) > _COL_DATE else "")

        stud_name       = str(matches[0][_COL_STUD_NAME]) if matches else stud_num
        offense_count   = len(matches)
        current_offense = min(offense_count, 5)

        # Build (vtype, date) pairs for up to 5 step slots
        violations_for_steps = []
        for r in matches[:5]:
            vtype    = str(r[_COL_VTYPE])[:28] if len(r) > _COL_VTYPE else "N/A"
            date_str = str(r[_COL_DATE])[:10]  if len(r) > _COL_DATE  else ""
            violations_for_steps.append((vtype, date_str))

        extra = f" (+{offense_count - 5} more beyond step 5)" if offense_count > 5 else ""
        self._prog_name_lbl.setText(
            f"Student: {stud_name}  ({stud_num})  —  "
            f"{offense_count} violation(s) on record{extra}"
        )
        self._prog_name_lbl.setStyleSheet(f"""
            color: {'#B71C1C' if offense_count >= 3 else '#1B5E20'};
            background: {'#FFF3E0' if offense_count >= 3 else '#F1F8E9'};
            border: 1px solid {'#FFCCBC' if offense_count >= 3 else '#C8E6C9'};
            border-radius: 8px;
            padding: 10px 14px;
        """)

        self._build_progress_steps(violations_for_steps, current_offense)

    # =========================================================================
    # Summary tab
    # =========================================================================
    def _build_summary_placeholder(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)
        lay.addWidget(SectionTitle("Blue Slip Summary"))
        lay.addWidget(SubTitle("Loading summary..."))
        lay.addStretch()
        return w

    def _on_tab_changed(self, idx: int):
        if idx == 3 and not self._summary_built:
            self._summary_built = True
            summary = self._build_summary_tab()
            self._tabs.removeTab(3)
            self._tabs.insertTab(3, summary, "   Summary & Charts ")
            self._tabs.setCurrentIndex(3)

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
        self._init_blue_stat_tiles(tiles_row)
        lay.addLayout(tiles_row)

        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        refresh_btn = QPushButton("  Refresh Chart  ")
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

    def _init_blue_stat_tiles(self, tiles_row: QHBoxLayout):
        for label, colour in [
            ("Total Violations (Sem)", BLUE_SLIP),
            ("Pending / Open",         "#F57F17"),
            ("Escalated Cases",        RED_ERR),
            ("Resolved",               "#2E7D32"),
        ]:
            tile = StatTile(label, "0", colour)
            tiles_row.addWidget(tile)
            self.blue_stat_tiles[label] = tile

    def _refresh_blue_summary(self):
        blue_records = get_blue_slips(None) or []

        total           = len(blue_records)
        pending_count   = sum(1 for r in blue_records
                              if len(r) > _COL_STATUS and "Open / Pending" in str(r[_COL_STATUS]))
        escalated_count = sum(1 for r in blue_records
                              if len(r) > _COL_STATUS and "Escalated"      in str(r[_COL_STATUS]))
        resolved_count  = sum(1 for r in blue_records
                              if len(r) > _COL_STATUS and "Resolved"       in str(r[_COL_STATUS]))

        violation_types: dict = {}
        for r in blue_records:
            if len(r) > _COL_VTYPE:
                vtype = str(r[_COL_VTYPE])
                violation_types[vtype] = violation_types.get(vtype, 0) + 1

        if self.blue_stat_tiles:
            self.blue_stat_tiles["Total Violations (Sem)"].set_value(total)
            self.blue_stat_tiles["Pending / Open"].set_value(pending_count)
            self.blue_stat_tiles["Escalated Cases"].set_value(escalated_count)
            self.blue_stat_tiles["Resolved"].set_value(resolved_count)

        if self.blue_chart is not None:
            self.blue_chart.update_data(
                violation_types, pending_count, escalated_count, resolved_count)

    # =========================================================================
    # Event handlers
    # =========================================================================
    def _on_slips_changed(self):
        print("[DEBUG] Blue slip page: _on_slips_changed() called")
        try:
            self._refresh_blue_tracker()
            print("[DEBUG] Blue slip tracker refreshed successfully")
        except Exception as e:
            print(f"[ERROR] Failed to refresh blue tracker: {str(e)}")
            import traceback
            traceback.print_exc()
        try:
            self._refresh_blue_summary()
            print("[DEBUG] Blue slip summary refreshed successfully")
        except Exception as e:
            print(f"[ERROR] Failed to refresh blue summary: {str(e)}")
            import traceback
            traceback.print_exc()


from ui.components import Divider
from ui.pages.base_page import build_record_table
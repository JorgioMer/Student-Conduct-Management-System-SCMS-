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
    FieldLabel, add_shadow, ConfirmDialog, InfoDialog, StatTile,
    AutoCompleteLineEdit
)
from ui.pages.base_page import BasePage, page_header, build_record_table
from ui.data_events import data_events
from ui.pages.trackers import _apply_table_selection_style

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_pink_slip import add_pink_slip, get_pink_slips
from backend.config import get_current_semester
from backend.db_accounts import get_officer_names          # ← NEW
from backend.db_activity_log import log_slip_created

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
                background: {PINK_SLIP};
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QDateEdit::drop-down:hover {{
                background: #C2185B;
            }}
            QDateEdit::drop-down:disabled {{
                background: #E0BFC9;
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
            background: #C2185B;
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


class PinkSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pink_tracker_table = None
        self.pink_tracker_layout = None
        self._all_pink_records = []
        self._pink_table_index = 3
        self.pink_stat_tiles = {}
        self.pink_chart = None          # always initialise to None
        self._summary_built = False
        self._tabs = None
        data_events.slips_changed.connect(self._on_slips_changed)
        self._build()

    def _build(self):
        self.main_layout.addWidget(page_header(
            "pink",
            "   Pink Slip Management ",
            "Track penalty slips — issued only ONCE per student per semester"
        ))

        tabs = QTabWidget()
        self._tabs = tabs
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
        tabs.addTab(self._build_summary_placeholder(), "   Summary & Charts ")
        tabs.currentChanged.connect(self._on_tab_changed)

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # =========================================================================
    # Record tab
    # =========================================================================
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

        form_lay.addWidget(lbl("Year & Course"), 1, 0)
        grade_row = QHBoxLayout()
        self.pink_year = QComboBox()
        self.pink_year.addItems(["1st","2nd","3rd","4th","5th"])
        self.pink_year.setFixedHeight(38)
        self.pink_year.setStyleSheet(_combo_style(PINK_SLIP))
        self.pink_course = AutoCompleteLineEdit()
        grade_row.addWidget(self.pink_year)
        grade_row.addWidget(self.pink_course)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Semester", True), 1, 2)
        self.pink_sem = QComboBox()
        self.pink_sem.addItems(["1st", "2nd", "Summer"])
        self.pink_sem.setFixedHeight(38)
        self.pink_sem.setStyleSheet(_combo_style(PINK_SLIP))
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.pink_sem.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.pink_sem.setCurrentIndex(1)
        form_lay.addWidget(self.pink_sem, 1, 3)

        form_lay.addWidget(lbl("Date Issued", True), 2, 0)
        self.pink_date = CalendarDateEdit(QDate.currentDate())
        self.pink_date.setFixedHeight(38)
        self.pink_date.setDisplayFormat("MMMM d, yyyy")
        self.pink_date.apply_icon_style(_date_edit_style(PINK_SLIP))
        form_lay.addWidget(self.pink_date, 2, 1)

        form_lay.addWidget(lbl("Violation / Reason", True), 2, 2)
        self.pink_violation = QComboBox()
        self.pink_violation.addItems([
            "Uniform Violation", "Tardiness", "Misconduct",
            "Prohibited Items", "Disrespect",
            "Other (specify in remarks)",
        ])
        self.pink_violation.setFixedHeight(38)
        self.pink_violation.setStyleSheet(_combo_style(PINK_SLIP))
        form_lay.addWidget(self.pink_violation, 2, 3)

        _lbl_dr = lbl("Description / Remarks")
        _lbl_dr.setContentsMargins(0, 8, 0, 0)
        form_lay.addWidget(_lbl_dr, 3, 0, Qt.AlignTop)
        self.pink_remarks = QTextEdit()
        self.pink_remarks.setPlaceholderText("Provide additional details about the violation...")
        self.pink_remarks.setFixedHeight(75)
        form_lay.addWidget(self.pink_remarks, 3, 1, 1, 3)

        form_lay.addWidget(lbl("Action Taken"), 4, 0)
        self.pink_action = QComboBox()
        self.pink_action.addItems([
            "Warning", "Parent Notification",
            "Community Service", "Suspension", "Other",
        ])
        self.pink_action.setFixedHeight(38)
        self.pink_action.setStyleSheet(_combo_style(PINK_SLIP))
        form_lay.addWidget(self.pink_action, 4, 1)

        # ── Officer in Charge — QComboBox populated from Accounts ─────────────
        form_lay.addWidget(lbl("Officer in Charge", True), 4, 2)
        self.pink_officer = _build_officer_combo(PINK_SLIP)  # ← CHANGED (was QLineEdit)
        form_lay.addWidget(self.pink_officer, 4, 3)

        lay.addWidget(form_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        check_btn = QPushButton("   Check Student Record ")
        check_btn.setStyleSheet(btn_outline())
        check_btn.setFixedHeight(40)
        check_btn.clicked.connect(lambda: InfoDialog(
            "Record Check",
            "No existing Pink Slip found for this student\nin the selected semester.\n\nYou may proceed to save.",
            parent=self).exec_())

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)
        clear_btn.clicked.connect(self._clear_pink_form)

        save_btn = QPushButton("   Save Record ")
        save_btn.setStyleSheet(btn_pink())
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_pink)

        btn_row.setSpacing(10)
        btn_row.addWidget(check_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(save_btn)
        lay.addLayout(btn_row)
        
        # Connect auto-fill on student number entry
        self.pink_no.editingFinished.connect(self._auto_fill_pink)
        
        return w

    def _auto_fill_pink(self):
        """Auto-fill pink slip form when student number exists in database."""
        stud_no = self.pink_no.text().strip()
        if not stud_no:
            return
        
        try:
            from backend.db_students import get_student
            student = get_student(stud_no)
            if student:
                # student = (studNumber, studName, studCourse, studYrLvl, schoolYr, studStatus)
                self.pink_name.setText(student[1] or "")
                self.pink_course.setText(student[2] or "")
                
                # Set year if available
                year = student[3] or ""
                if year:
                    index = self.pink_year.findText(year)
                    if index >= 0:
                        self.pink_year.setCurrentIndex(index)
        except Exception as e:
            # Silently fail - user can fill manually
            pass

    def _clear_pink_form(self):
        self.pink_no.clear()
        self.pink_name.clear()
        self.pink_course.clear()
        self.pink_violation.setCurrentIndex(0)
        self.pink_action.setCurrentIndex(0)
        self.pink_officer.setCurrentIndex(0)       # ← CHANGED (was .clear())
        self.pink_remarks.clear()
        self.pink_date.setDate(QDate.currentDate())
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.pink_sem.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.pink_sem.setCurrentIndex(1)
        else:
            self.pink_sem.setCurrentIndex(0)
        self.pink_year.setCurrentIndex(0)

    def closeEvent(self, event):
        """Clean up signal connections when page is closed"""
        try:
            data_events.slips_changed.disconnect(self._on_slips_changed)
        except Exception:
            pass
        super().closeEvent(event)

    def _save_pink(self):
        if not self.pink_no.text().strip():
            InfoDialog("Missing Fields",
                       "Please fill in all required fields.",
                       success=False, parent=self).exec_()
            return

        # ── Validate officer selection ────────────────────────────────────────
        officer = self.pink_officer.currentText()
        if officer == "— Select Officer —":
            InfoDialog("Missing Fields",
                       "Please select an Officer in Charge.",
                       success=False, parent=self).exec_()
            return

        # ── Check for existing Pink Slip in this semester ────────────────────
        stud_num = self.pink_no.text().strip()
        sem = self.pink_sem.currentText()
        
        try:
            from backend.db_pink_slip import has_pink_slip_for_semester
            if has_pink_slip_for_semester(stud_num, sem):
                InfoDialog("Constraint Violation",
                           f"Student {stud_num} already has a Pink Slip for {sem} semester.\n\n"
                           "Policy: Only ONE Pink Slip per student per semester.\n"
                           "Please check the student's record in the Tracker tab.",
                           success=False, parent=self).exec_()
                return
        except Exception as e:
            print(f"[WARNING] Could not check for duplicate pink slip: {str(e)}")

        dlg = ConfirmDialog("Confirm Save",
                            "Save this Pink Slip record?",
                            parent=self)
        if dlg.exec_():
            try:
                stud_num     = self.pink_no.text().strip()
                stud_name    = self.pink_name.text().strip()
                stud_course  = self.pink_course.text().strip()
                stud_year    = self.pink_year.currentText()
                date_issued  = self.pink_date.date().toPyDate()
                violation    = self.pink_violation.currentText()
                action_taken = self.pink_action.currentText()
                sem          = self.pink_sem.currentText()
                remarks      = self.pink_remarks.toPlainText().strip()
                # officer already read above
                print(f"[DEBUG] Saving pink slip for student {stud_num} ({stud_name})")
                record_id = add_pink_slip(stud_num, date_issued, violation, action_taken, officer,
                              sem=sem, remarks=remarks, stud_name=stud_name,
                              stud_course=stud_course, stud_year=stud_year)
                print(f"[DEBUG] Pink slip saved with ID: {record_id}")
                # Log the action
                log_slip_created(officer, "Pink", stud_name, record_id=record_id)
                InfoDialog("Record Saved",
                           "Pink Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                print(f"[DEBUG] Emitting slips_changed signal")
                data_events.slips_changed.emit()
                print(f"[DEBUG] Signal emitted")
                self._clear_pink_form()
            except Exception as e:
                print(f"[ERROR] Failed to save pink slip: {str(e)}")
                import traceback
                traceback.print_exc()
                InfoDialog("Error", f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    # =========================================================================
    # Tracker tab
    # =========================================================================
    def _load_pink_tracker_data(self):
        from backend.db_pink_slip import get_pink_slips
        sample = []
        try:
            pink_records = get_pink_slips(None) or []
            print(f"[DEBUG] Loaded {len(pink_records)} pink slip records from database")
            for record in pink_records:
                try:
                    stud_name    = record[0] if len(record) > 0 else "N/A"
                    stud_course  = record[1] if len(record) > 1 else "N/A"
                    stud_year    = record[2] if len(record) > 2 else "N/A"
                    stud_num     = record[4] if len(record) > 4 else "N/A"
                    date_issued  = str(record[5]) if len(record) > 5 else "N/A"
                    violation    = record[6] if len(record) > 6 else "N/A"
                    action_taken = record[7] if len(record) > 7 else "N/A"
                    officer      = record[8] if len(record) > 8 else "N/A"
                    semester     = record[9] if len(record) > 9 else "N/A"
                    sample.append((
                        stud_num, stud_name, stud_year, stud_course,
                        semester,
                        date_issued[:10] if date_issued != "N/A" else "N/A",
                        violation, action_taken, officer
                    ))
                except Exception as e:
                    print(f"[ERROR] Failed to parse pink slip record: {str(e)}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[ERROR] Failed to load pink slips: {str(e)}")
            import traceback
            traceback.print_exc()
        self._all_pink_records = sample
        print(f"[DEBUG] Pink tracker showing {len(sample)} records")
        return sample if sample else [
            ("No records", "Add records to see them here",
             "-", "-", "-", "-", "-", "-", "-")
        ]

    def _apply_pink_filters(self):
        search_text = self._pink_search.text().strip().lower()
        sem_val     = self._pink_sem_filter.currentText()
        use_date    = self._pink_date_toggle.currentText() == "Filter by Date Range"
        date_from   = self._pink_date_from.date()
        date_to     = self._pink_date_to.date()

        filtered = []
        for row in self._all_pink_records:
            stud_num, stud_name, year, course, semester, date_str, violation, action, officer = row

            if search_text and (
                    search_text not in stud_num.lower()
                    and search_text not in stud_name.lower()
            ):
                continue

            if sem_val != "All Semesters" and str(semester) != sem_val:
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
                         "-", "-", "-", "-", "-", "-", "-")]
        self._rebuild_pink_table(filtered)

    def _rebuild_pink_table(self, data):
        if self.pink_tracker_layout is None:
            print("[WARNING] Pink tracker layout not initialized yet")
            return
        headers = ["Student No.", "Student Name", "Year", "Course",
                   "Semester", "Date Issued", "Violation", "Action Taken", "Officer"]
        # Remove old table if it exists
        if self.pink_tracker_table is not None:
            for i in range(self.pink_tracker_layout.count()):
                item = self.pink_tracker_layout.itemAt(i)
                if item and item.widget() is self.pink_tracker_table:
                    self.pink_tracker_layout.removeWidget(self.pink_tracker_table)
                    self.pink_tracker_table.deleteLater()
                    break
        # Create and add new table
        self.pink_tracker_table = build_record_table(headers, data)
        _apply_table_selection_style(self.pink_tracker_table, PINK_SLIP)
        self.pink_tracker_table.setMinimumHeight(260)
        self.pink_tracker_layout.insertWidget(self._pink_table_index,
                                              self.pink_tracker_table)

    def _refresh_pink_tracker(self):
        self._load_pink_tracker_data()
        self._apply_pink_filters()

    def _build_tracker_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Pink Slip Record Tracker"))
        lay.addWidget(SubTitle("Track all issued pink slips — one per student per semester"))

        filter_panel = QFrame()
        filter_panel.setStyleSheet(_filter_panel_style(PINK_SLIP))
        panel_lay = QVBoxLayout(filter_panel)
        panel_lay.setContentsMargins(16, 14, 16, 14)
        panel_lay.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self._pink_search = QLineEdit()
        self._pink_search.setPlaceholderText("Search by student name or number...")
        self._pink_search.setFixedHeight(38)
        self._pink_search.setStyleSheet(_search_style(PINK_SLIP))
        self._pink_search.textChanged.connect(self._apply_pink_filters)

        self._pink_sem_filter = QComboBox()
        self._pink_sem_filter.addItems(["All Semesters", "1st", "2nd", "Summer"])
        self._pink_sem_filter.setFixedHeight(38)
        self._pink_sem_filter.setFixedWidth(155)
        self._pink_sem_filter.setStyleSheet(_combo_style(PINK_SLIP))
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self._pink_sem_filter.setCurrentIndex(1)
        elif "2nd" in current_sem:
            self._pink_sem_filter.setCurrentIndex(2)
        self._pink_sem_filter.currentIndexChanged.connect(self._apply_pink_filters)

        refresh_btn = QPushButton("   Refresh ")
        refresh_btn.setStyleSheet(btn_pink())
        refresh_btn.setFixedHeight(38)
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self._refresh_pink_tracker)

        row1.addWidget(self._pink_search, 1)
        row1.addWidget(self._pink_sem_filter)
        row1.addWidget(refresh_btn)
        panel_lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        date_lbl = QLabel("Date Range:")
        date_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        date_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._pink_date_toggle = QComboBox()
        self._pink_date_toggle.addItems(["All Dates", "Filter by Date Range"])
        self._pink_date_toggle.setFixedHeight(38)
        self._pink_date_toggle.setFixedWidth(185)
        self._pink_date_toggle.setStyleSheet(_combo_style(PINK_SLIP))

        self._pink_from_lbl = QLabel("From:")
        self._pink_from_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._pink_from_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._pink_date_from = CalendarDateEdit(QDate.currentDate().addMonths(-1))
        self._pink_date_from.setFixedHeight(38)
        self._pink_date_from.setFixedWidth(165)
        self._pink_date_from.setDisplayFormat("MMM d, yyyy")
        self._pink_date_from.apply_icon_style(_date_edit_style(PINK_SLIP))
        self._pink_date_from.setEnabled(False)

        self._pink_to_lbl = QLabel("To:")
        self._pink_to_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._pink_to_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._pink_date_to = CalendarDateEdit(QDate.currentDate())
        self._pink_date_to.setFixedHeight(38)
        self._pink_date_to.setFixedWidth(165)
        self._pink_date_to.setDisplayFormat("MMM d, yyyy")
        self._pink_date_to.apply_icon_style(_date_edit_style(PINK_SLIP))
        self._pink_date_to.setEnabled(False)

        def _toggle_pink_dates(idx):
            on = (idx == 1)
            self._pink_date_from.setEnabled(on)
            self._pink_date_to.setEnabled(on)
            self._pink_from_lbl.setEnabled(on)
            self._pink_to_lbl.setEnabled(on)
            self._apply_pink_filters()

        self._pink_date_toggle.currentIndexChanged.connect(_toggle_pink_dates)
        self._pink_date_from.dateChanged.connect(self._apply_pink_filters)
        self._pink_date_to.dateChanged.connect(self._apply_pink_filters)

        row2.addWidget(date_lbl)
        row2.addWidget(self._pink_date_toggle)
        row2.addWidget(self._pink_from_lbl)
        row2.addWidget(self._pink_date_from)
        row2.addWidget(self._pink_to_lbl)
        row2.addWidget(self._pink_date_to)
        row2.addStretch()
        panel_lay.addLayout(row2)

        lay.addWidget(filter_panel)

        headers = ["Student No.", "Student Name", "Year", "Course",
                   "Semester", "Date Issued", "Violation", "Action Taken", "Officer"]
        sample = self._load_pink_tracker_data()
        self.pink_tracker_table = build_record_table(headers, sample)
        _apply_table_selection_style(self.pink_tracker_table, PINK_SLIP)
        self.pink_tracker_table.setMinimumHeight(260)
        lay.addWidget(self.pink_tracker_table)

        self.pink_tracker_layout = lay
        self._pink_table_index = 3

        action_row = QHBoxLayout()
        action_row.addStretch()

        view_btn = QPushButton("   View ")
        view_btn.setStyleSheet(btn_outline())
        view_btn.setFixedHeight(38)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(self._view_pink_record)

        del_btn = QPushButton("   Delete ")
        del_btn.setStyleSheet(btn_danger())
        del_btn.setFixedHeight(38)
        del_btn.clicked.connect(self._delete_pink_record)

        action_row.addWidget(view_btn)
        action_row.addWidget(del_btn)
        lay.addLayout(action_row)
        lay.addStretch()
        return w

    def _view_pink_record(self):
        if self.pink_tracker_table is None:
            return
        selected = self.pink_tracker_table.selectedItems()
        if not selected:
            InfoDialog(
                "No Record Selected",
                "Please select a student by clicking the Name or ID Number in the table.",
                success=False, parent=self
            ).exec_()
            return
        row = self.pink_tracker_table.currentRow()
        headers = [
            self.pink_tracker_table.horizontalHeaderItem(c).text()
            for c in range(self.pink_tracker_table.columnCount())
        ]
        fields = []
        for col, header in enumerate(headers):
            item = self.pink_tracker_table.item(row, col)
            fields.append((header, item.text() if item else "—"))
        from ui.pages.trackers import RecordDetailDialog
        dlg = RecordDetailDialog(fields, slip_type="pink", parent=self)
        dlg.exec_()

    def _delete_pink_record(self):
        """Delete selected pink slip record from database."""
        if self.pink_tracker_table is None:
            return
        selected = self.pink_tracker_table.selectedItems()
        if not selected:
            InfoDialog(
                "No Record Selected",
                "Please select a record to delete.",
                success=False, parent=self
            ).exec_()
            return
        
        row = self.pink_tracker_table.currentRow()
        stud_num_item = self.pink_tracker_table.item(row, 0)
        if not stud_num_item:
            return
        
        stud_num = stud_num_item.text()
        if stud_num == "No records":
            return
        
        dlg = ConfirmDialog(
            "Confirm Delete",
            f"Delete pink slip record for student {stud_num}?\nThis action cannot be undone.",
            parent=self
        )
        if dlg.exec_():
            try:
                from backend.db_pink_slip import delete_pink_slip
                print(f"[DEBUG] Deleting pink slip for student {stud_num}")
                delete_pink_slip(stud_num)
                print(f"[DEBUG] Pink slip deleted successfully")
                InfoDialog(
                    "Record Deleted",
                    "Pink slip record has been deleted.",
                    success=True, parent=self
                ).exec_()
                data_events.slips_changed.emit()
            except Exception as e:
                print(f"[ERROR] Failed to delete pink slip: {str(e)}")
                import traceback
                traceback.print_exc()
                InfoDialog(
                    "Error",
                    f"Failed to delete record: {str(e)}",
                    success=False, parent=self
                ).exec_()

    # =========================================================================
    # Summary tab
    # =========================================================================
    def _build_summary_placeholder(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)
        lay.addWidget(SectionTitle("Pink Slip Summary"))
        lay.addWidget(SubTitle("Loading summary..."))
        lay.addStretch()
        return w

    def _on_tab_changed(self, idx: int):
        if idx == 2 and not self._summary_built:
            self._summary_built = True
            summary = self._build_summary_tab()
            self._tabs.removeTab(2)
            self._tabs.insertTab(2, summary, "   Summary & Charts ")
            self._tabs.setCurrentIndex(2)

    def _build_summary_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Pink Slip Summary"))

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        self.pink_stat_tiles = {}
        self._init_pink_stat_tiles(tiles_row)
        lay.addLayout(tiles_row)

        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        refresh_btn = QPushButton("   Refresh Chart  ")
        refresh_btn.setStyleSheet(btn_pink())
        refresh_btn.setFixedHeight(36)
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self._refresh_pink_summary)
        refresh_row.addWidget(refresh_btn)
        refresh_row.addStretch()
        lay.addLayout(refresh_row)

        from ui.chart_widgets import PinkSlipChart
        self.pink_chart = PinkSlipChart(w)
        self.pink_chart.setMinimumHeight(380)
        lay.addWidget(self.pink_chart)

        self._refresh_pink_summary()
        lay.addStretch()
        return w

    def _init_pink_stat_tiles(self, tiles_row: QHBoxLayout):
        for label, colour in [
            ("Total Pink Slips (Sem)", PINK_SLIP),
            ("Students Issued",        "#C2185B"),
            ("Most Common Violation",  "#880E4F"),
            ("Pending Action",         "#F57F17"),
        ]:
            val = "—" if label == "Most Common Violation" else "0"
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
            self.pink_stat_tiles[label] = tile

    def _refresh_pink_summary(self):
        from backend.db_pink_slip import get_pink_slips
        pink_records = get_pink_slips(None) or []

        total                = len(pink_records)
        unique_students_pink = len(set(r[0] for r in pink_records if len(r) > 0))

        violation_counts: dict = {}
        for r in pink_records:
            if len(r) > 6:
                v = str(r[6])
                violation_counts[v] = violation_counts.get(v, 0) + 1

        most_common = (
            max(violation_counts.items(), key=lambda x: x[1])[0]
            if violation_counts else "—"
        )

        year_distribution: dict = {}
        for r in pink_records:
            if len(r) > 2:
                year = str(r[2])
                year_distribution[year] = year_distribution.get(year, 0) + 1

        if self.pink_stat_tiles:
            self.pink_stat_tiles["Total Pink Slips (Sem)"].set_value(total)
            self.pink_stat_tiles["Students Issued"].set_value(unique_students_pink)
            self.pink_stat_tiles["Most Common Violation"].set_value(most_common)
            self.pink_stat_tiles["Pending Action"].set_value("0")

        if self.pink_chart is not None:
            self.pink_chart.update_data(violation_counts, year_distribution)

    # =========================================================================
    # Event handlers
    # =========================================================================
    def _on_slips_changed(self):
        print("[DEBUG] Pink slip page: _on_slips_changed() called")
        try:
            self._refresh_pink_tracker()
            print("[DEBUG] Pink slip tracker refreshed successfully")
        except Exception as e:
            print(f"[ERROR] Failed to refresh pink tracker: {str(e)}")
            import traceback
            traceback.print_exc()
        try:
            self._refresh_pink_summary()
            print("[DEBUG] Pink slip summary refreshed successfully")
        except Exception as e:
            print(f"[ERROR] Failed to refresh pink summary: {str(e)}")
            import traceback
            traceback.print_exc()
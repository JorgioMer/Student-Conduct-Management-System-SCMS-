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
    FieldLabel, Card, add_shadow, ConfirmDialog, InfoDialog, StatTile
)
from ui.pages.base_page import BasePage, page_header, build_record_table
from ui.data_events import data_events

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_green_slip import add_green_slip, get_green_slips
from backend.db_students import add_student, get_student
from backend.config import get_current_semester

import base64
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtCore import QRect, Qt

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
                background: #2E7D32;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QDateEdit::drop-down:hover {{
                background: #1B5E20;
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
            width: 32px;
            background: {accent};
            border-left: 1px solid {accent};
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QDateEdit::drop-down:hover {{
            background: #388E3C;
        }}
        QDateEdit::down-arrow {{
            image: none;
            width: 16px;
            height: 16px;
        }}
        QCalendarWidget QWidget {{
            background: #FFFFFF;
            color: #1A1A2E;
            font-family: "Segoe UI";
            font-size: 12px;
        }}
        QCalendarWidget QAbstractItemView {{
            background: #FFFFFF;
            color: #1A1A2E;
            selection-background-color: {accent};
            selection-color: #FFFFFF;
            gridline-color: #E5E7EB;
        }}
        QCalendarWidget QAbstractItemView:disabled {{
            color: #9CA3AF;
        }}
        QCalendarWidget QToolButton {{
            background: {accent};
            color: #FFFFFF;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 13px;
        }}
        QCalendarWidget QToolButton:hover {{
            background: #388E3C;
        }}
        QCalendarWidget QToolButton::menu-indicator {{
            image: none;
        }}
        QCalendarWidget QSpinBox {{
            background: #FFFFFF;
            color: #1A1A2E;
            border: 1px solid #D0D5DD;
            border-radius: 4px;
            padding: 2px 6px;
            selection-background-color: {accent};
            selection-color: #FFFFFF;
        }}
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background: {accent};
            border-radius: 6px;
            padding: 4px;
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
            background: #1B5E20;
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


class GreenSlipPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.green_tracker_table = None
        self.green_tracker_layout = None
        self._all_green_records = []
        self._green_table_index = 3
        self.green_stat_tiles = {}
        self.green_chart = None         # always initialise to None
        self._summary_built = False
        self._tabs = None
        data_events.slips_changed.connect(self._on_slips_changed)
        self._build()

    def _build(self):
        self.main_layout.addWidget(page_header(
            "green",
            "   Green Slip Management ",
            "Record and track Dispensation & Excuse Green Slips"
        ))

        tabs = QTabWidget()
        self._tabs = tabs
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
        tabs.addTab(self._build_summary_placeholder(), "  Summary & Charts ")
        tabs.currentChanged.connect(self._on_tab_changed)

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # =========================================================================
    # Dispensation tab
    # =========================================================================
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
        self.disp_stud_no = QLineEdit()
        self.disp_stud_no.setPlaceholderText("e.g. 2024-0001")
        self.disp_stud_no.setFixedHeight(38)
        form_lay.addWidget(self.disp_stud_no, 0, 1)

        form_lay.addWidget(lbl("Student Name", True), 0, 2)
        self.disp_stud_name = QLineEdit()
        self.disp_stud_name.setPlaceholderText("Last, First Middle")
        self.disp_stud_name.setFixedHeight(38)
        form_lay.addWidget(self.disp_stud_name, 0, 3)

        form_lay.addWidget(lbl("Year & Course"), 1, 0)
        grade_row = QHBoxLayout()
        self.disp_year = QComboBox()
        self.disp_year.addItems(["1st","2nd","3rd","4th","5th"])
        self.disp_year.setFixedHeight(38)
        self.disp_year.setStyleSheet(_combo_style(GREEN_SLIP))
        self.disp_course = QLineEdit()
        self.disp_course.setPlaceholderText("Course")
        self.disp_course.setFixedHeight(38)
        grade_row.addWidget(self.disp_year)
        grade_row.addWidget(self.disp_course)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Date Availed", True), 1, 2)
        self.disp_date = CalendarDateEdit(QDate.currentDate())
        self.disp_date.setFixedHeight(38)
        self.disp_date.setDisplayFormat("MMMM d, yyyy")
        self.disp_date.apply_icon_style(_date_edit_style(GREEN_SLIP))
        form_lay.addWidget(self.disp_date, 1, 3)

        form_lay.addWidget(lbl("Number of Days", True), 2, 0)
        self.disp_days = QSpinBox()
        self.disp_days.setRange(1, 30)
        self.disp_days.setValue(1)
        self.disp_days.setFixedHeight(38)
        self.disp_days.setSuffix(" day(s)")
        form_lay.addWidget(self.disp_days, 2, 1)

        form_lay.addWidget(lbl("Expiry Date"), 2, 2)
        self.disp_expiry = CalendarDateEdit(QDate.currentDate().addDays(1))
        self.disp_expiry.setFixedHeight(38)
        self.disp_expiry.setDisplayFormat("MMMM d, yyyy")
        self.disp_expiry.setReadOnly(True)
        self.disp_expiry.apply_icon_style(_date_edit_style(GREEN_SLIP) + f"""
            QDateEdit {{ background: {LIGHT_GRAY}; color: #9CA3AF; }}
        """)
        form_lay.addWidget(self.disp_expiry, 2, 3)

        def update_expiry(val):
            self.disp_expiry.setDate(self.disp_date.date().addDays(val))
        self.disp_days.valueChanged.connect(update_expiry)
        self.disp_date.dateChanged.connect(lambda d: update_expiry(self.disp_days.value()))

        form_lay.addWidget(lbl("Purpose / Reason", True), 3, 0)
        self.disp_reason = QTextEdit()
        self.disp_reason.setPlaceholderText("Briefly describe the reason for dispensation...")
        self.disp_reason.setFixedHeight(70)
        form_lay.addWidget(self.disp_reason, 3, 1, 1, 3)

        form_lay.addWidget(lbl("Authorized By", True), 4, 0)
        self.disp_auth = QLineEdit()
        self.disp_auth.setPlaceholderText("Name of authorizing officer")
        self.disp_auth.setFixedHeight(38)
        form_lay.addWidget(self.disp_auth, 4, 1)

        form_lay.addWidget(lbl("Status"), 4, 2)
        self.disp_status = QComboBox()
        self.disp_status.addItems(["Active", "Expired", "Cancelled"])
        self.disp_status.setFixedHeight(38)
        self.disp_status.setStyleSheet(_combo_style(GREEN_SLIP))
        form_lay.addWidget(self.disp_status, 4, 3)

        form_lay.addWidget(lbl("Semester", True), 5, 0)
        self.disp_semester = QComboBox()
        self.disp_semester.addItems(["1st", "2nd", "Summer"])
        self.disp_semester.setFixedHeight(38)
        self.disp_semester.setStyleSheet(_combo_style(GREEN_SLIP))
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self.disp_semester.setCurrentIndex(0)
        elif "2nd" in current_sem:
            self.disp_semester.setCurrentIndex(1)
        form_lay.addWidget(self.disp_semester, 5, 1)

        lay.addWidget(form_group)

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
                stud_num    = self.disp_stud_no.text().strip()
                stud_name   = self.disp_stud_name.text().strip()
                stud_course = self.disp_course.text().strip() if hasattr(self, 'disp_course') else ""
                stud_year   = self.disp_year.currentText()
                slip_type   = "Dispensation"
                date_avail  = self.disp_date.date().toPyDate()
                days        = self.disp_days.value()
                status      = self.disp_status.currentText()
                expiry      = self.disp_expiry.date().toPyDate()
                purpose     = self.disp_reason.toPlainText().strip()
                semester    = self.disp_semester.currentText()
                remarks = absence_type = dates_absence = supp_doc = ""
                auth_by     = self.disp_auth.text().strip()
                add_green_slip(stud_num, slip_type, date_avail, days, status,
                               expiry, purpose, remarks, absence_type,
                               dates_absence, supp_doc, auth_by,
                               stud_name=stud_name, stud_course=stud_course,
                               stud_year=stud_year)
                InfoDialog("Record Saved",
                           "Dispensation Green Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._clear_dispensation()
                data_events.slips_changed.emit()
            except Exception as e:
                InfoDialog("Error", f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

    # =========================================================================
    # Excuse tab
    # =========================================================================
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
                stud_num      = self.exc_stud_no.text().strip()
                stud_name     = self.exc_stud_name.text().strip()
                stud_course   = self.exc_course.text().strip()
                stud_year     = self.exc_year.currentText()
                slip_type     = "Excuse"
                date_avail    = self.exc_date.date().toPyDate()
                days          = 0
                status        = "Active"
                expiry        = self.exc_date.date().toPyDate()
                purpose       = ""
                remarks       = self.exc_remarks.toPlainText().strip()
                absence_type  = self.exc_type.currentText()
                dates_absence = self.exc_abs_date.text().strip()
                supp_doc      = self.exc_doc.currentText()
                auth_by       = self.exc_auth.text().strip()
                semester      = self.exc_semester.currentText()
                add_green_slip(stud_num, slip_type, date_avail, days, status,
                               expiry, purpose, remarks, absence_type,
                               dates_absence, supp_doc, auth_by,
                               stud_name=stud_name, stud_course=stud_course,
                               stud_year=stud_year)
                InfoDialog("Record Saved",
                           "Excuse Green Slip record has been saved successfully!",
                           success=True, parent=self).exec_()
                self._clear_excuse()
                data_events.slips_changed.emit()
            except Exception as e:
                InfoDialog("Error", f"Failed to save record: {str(e)}",
                           success=False, parent=self).exec_()

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
        self.exc_year.setStyleSheet(_combo_style(GREEN_SLIP))
        self.exc_course = QLineEdit()
        self.exc_course.setPlaceholderText("Course")
        self.exc_course.setFixedHeight(38)
        grade_row.addWidget(self.exc_year)
        grade_row.addWidget(self.exc_course)
        form_lay.addLayout(grade_row, 1, 1)

        form_lay.addWidget(lbl("Date Availed", True), 1, 2)
        self.exc_date = CalendarDateEdit(QDate.currentDate())
        self.exc_date.setFixedHeight(38)
        self.exc_date.setDisplayFormat("MMMM d, yyyy")
        self.exc_date.apply_icon_style(_date_edit_style(GREEN_SLIP))
        form_lay.addWidget(self.exc_date, 1, 3)

        form_lay.addWidget(lbl("Absence Type", True), 2, 0)
        self.exc_type = QComboBox()
        self.exc_type.addItems([
            "Medical / Illness", "Family Emergency",
            "School Event / Activity", "Official Function",
            "Weather / Calamity", "Other (specify below)",
        ])
        self.exc_type.setFixedHeight(38)
        self.exc_type.setStyleSheet(_combo_style(GREEN_SLIP))
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
        self.exc_doc.addItems(["Medical Certificate", "Parent Letter",
                               "Official Document", "None"])
        self.exc_doc.setFixedHeight(38)
        self.exc_doc.setStyleSheet(_combo_style(GREEN_SLIP))
        form_lay.addWidget(self.exc_doc, 4, 3)

        form_lay.addWidget(lbl("Semester", True), 5, 0)
        self.exc_semester = QComboBox()
        self.exc_semester.addItems(["1st", "2nd", "Summer"])
        self.exc_semester.setFixedHeight(38)
        self.exc_semester.setStyleSheet(_combo_style(GREEN_SLIP))
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

    # =========================================================================
    # Tracker tab
    # =========================================================================
    def _load_green_tracker_data(self):
        from backend.db_green_slip import get_green_slips
        sample = []
        try:
            for record in (get_green_slips(None) or []):
                try:
                    stud_name    = record[0] if len(record) > 0 else "N/A"
                    stud_course  = record[1] if len(record) > 1 else "N/A"
                    stud_year    = record[2] if len(record) > 2 else "N/A"
                    stud_num     = record[4] if len(record) > 4 else "N/A"
                    is_disp      = record[5] if len(record) > 5 else False
                    slip_type    = "Dispensation" if is_disp else "Excuse"
                    date_avail   = str(record[6]) if len(record) > 6 else "N/A"
                    days_absence = str(record[7]) if len(record) > 7 else "N/A"
                    status       = record[8]      if len(record) > 8 else "Active"
                    expiry       = str(record[9]) if len(record) > 9 else "N/A"
                    sample.append((
                        stud_num, stud_name, stud_year, stud_course, slip_type,
                        date_avail[:10] if date_avail != "N/A" else "N/A",
                        days_absence,
                        expiry[:10]    if expiry    != "N/A" else "N/A",
                        status
                    ))
                except Exception:
                    pass
        except Exception:
            pass
        self._all_green_records = sample
        return sample if sample else [
            ("No records", "Add records to see them here",
             "-", "-", "-", "-", "-", "-", "-")
        ]

    def _apply_green_filters(self):
        search_text = self._green_search.text().strip().lower()
        type_val    = self._green_type_filter.currentText()
        sem_val     = self._green_sem_filter.currentText()
        grade_val   = self._green_grade_filter.currentText()
        use_date    = self._green_date_toggle.currentText() == "Filter by Date Range"
        date_from   = self._green_date_from.date()
        date_to     = self._green_date_to.date()

        filtered = []
        for row in self._all_green_records:
            stud_num, stud_name, year, course, slip_type, date_str, _, _, _ = row

            if search_text and (
                    search_text not in stud_num.lower()
                    and search_text not in stud_name.lower()
            ):
                continue

            if type_val != "All Types" and slip_type != type_val:
                continue

            if grade_val != "All Grades" and year != grade_val:
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
        self._rebuild_green_table(filtered)

    def _rebuild_green_table(self, data):
        if self.green_tracker_table is None or self.green_tracker_layout is None:
            return
        headers = ["Student No.", "Student Name", "Year", "Course",
                   "Slip Type", "Date Availed", "Days / Absence Type",
                   "Expiry / Date", "Status"]
        for i in range(self.green_tracker_layout.count()):
            item = self.green_tracker_layout.itemAt(i)
            if item and item.widget() is self.green_tracker_table:
                self.green_tracker_layout.removeWidget(self.green_tracker_table)
                self.green_tracker_table.deleteLater()
                break
        self.green_tracker_table = build_record_table(headers, data)
        self.green_tracker_table.setMinimumHeight(280)
        self.green_tracker_layout.insertWidget(self._green_table_index,
                                               self.green_tracker_table)

    def _refresh_green_tracker(self):
        self._load_green_tracker_data()
        self._apply_green_filters()

    def _build_tracker_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Green Slip Record Tracker"))
        lay.addWidget(SubTitle("All dispensation and excuse slips are listed below"))

        filter_panel = QFrame()
        filter_panel.setStyleSheet(_filter_panel_style(GREEN_SLIP))
        panel_lay = QVBoxLayout(filter_panel)
        panel_lay.setContentsMargins(16, 14, 16, 14)
        panel_lay.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self._green_search = QLineEdit()
        self._green_search.setPlaceholderText("Search by student name or number...")
        self._green_search.setFixedHeight(38)
        self._green_search.setStyleSheet(_search_style(GREEN_SLIP))
        self._green_search.textChanged.connect(self._apply_green_filters)

        self._green_type_filter = QComboBox()
        self._green_type_filter.addItems(["All Types", "Dispensation", "Excuse"])
        self._green_type_filter.setFixedHeight(38)
        self._green_type_filter.setFixedWidth(155)
        self._green_type_filter.setStyleSheet(_combo_style(GREEN_SLIP))
        self._green_type_filter.currentIndexChanged.connect(self._apply_green_filters)

        self._green_sem_filter = QComboBox()
        self._green_sem_filter.addItems(["All Semesters", "1st", "2nd", "Summer"])
        self._green_sem_filter.setFixedHeight(38)
        self._green_sem_filter.setFixedWidth(145)
        self._green_sem_filter.setStyleSheet(_combo_style(GREEN_SLIP))
        current_sem = get_current_semester()
        if "1st" in current_sem:
            self._green_sem_filter.setCurrentIndex(1)
        elif "2nd" in current_sem:
            self._green_sem_filter.setCurrentIndex(2)
        self._green_sem_filter.currentIndexChanged.connect(self._apply_green_filters)

        self._green_grade_filter = QComboBox()
        self._green_grade_filter.addItems(["All Grades","1st","2nd","3rd","4th","5th"])
        self._green_grade_filter.setFixedHeight(38)
        self._green_grade_filter.setFixedWidth(130)
        self._green_grade_filter.setStyleSheet(_combo_style(GREEN_SLIP))
        self._green_grade_filter.currentIndexChanged.connect(self._apply_green_filters)

        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setStyleSheet(btn_green())
        refresh_btn.setFixedHeight(38)
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self._refresh_green_tracker)

        row1.addWidget(self._green_search, 1)
        row1.addWidget(self._green_type_filter)
        row1.addWidget(self._green_sem_filter)
        row1.addWidget(self._green_grade_filter)
        row1.addWidget(refresh_btn)
        panel_lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        date_lbl = QLabel("Date Range:")
        date_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        date_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._green_date_toggle = QComboBox()
        self._green_date_toggle.addItems(["All Dates", "Filter by Date Range"])
        self._green_date_toggle.setFixedHeight(38)
        self._green_date_toggle.setFixedWidth(185)
        self._green_date_toggle.setStyleSheet(_combo_style(GREEN_SLIP))

        self._green_from_lbl = QLabel("From:")
        self._green_from_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._green_from_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._green_date_from = CalendarDateEdit(QDate.currentDate().addMonths(-1))
        self._green_date_from.setFixedHeight(38)
        self._green_date_from.setFixedWidth(165)
        self._green_date_from.setDisplayFormat("MMM d, yyyy")
        self._green_date_from.apply_icon_style(_date_edit_style(GREEN_SLIP))
        self._green_date_from.setEnabled(False)

        self._green_to_lbl = QLabel("To:")
        self._green_to_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        self._green_to_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        self._green_date_to = CalendarDateEdit(QDate.currentDate())
        self._green_date_to.setFixedHeight(38)
        self._green_date_to.setFixedWidth(165)
        self._green_date_to.setDisplayFormat("MMM d, yyyy")
        self._green_date_to.apply_icon_style(_date_edit_style(GREEN_SLIP))
        self._green_date_to.setEnabled(False)

        def _toggle_green_dates(idx):
            on = (idx == 1)
            self._green_date_from.setEnabled(on)
            self._green_date_to.setEnabled(on)
            self._green_from_lbl.setEnabled(on)
            self._green_to_lbl.setEnabled(on)
            self._apply_green_filters()

        self._green_date_toggle.currentIndexChanged.connect(_toggle_green_dates)
        self._green_date_from.dateChanged.connect(self._apply_green_filters)
        self._green_date_to.dateChanged.connect(self._apply_green_filters)

        row2.addWidget(date_lbl)
        row2.addWidget(self._green_date_toggle)
        row2.addWidget(self._green_from_lbl)
        row2.addWidget(self._green_date_from)
        row2.addWidget(self._green_to_lbl)
        row2.addWidget(self._green_date_to)
        row2.addStretch()
        panel_lay.addLayout(row2)

        lay.addWidget(filter_panel)

        headers = ["Student No.", "Student Name", "Year", "Course",
                   "Slip Type", "Date Availed", "Days / Absence Type",
                   "Expiry / Date", "Status"]
        sample = self._load_green_tracker_data()
        self.green_tracker_table = build_record_table(headers, sample)
        self.green_tracker_table.setMinimumHeight(280)
        lay.addWidget(self.green_tracker_table)

        self.green_tracker_layout = lay
        self._green_table_index = 3

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

    # =========================================================================
    # Summary tab
    # =========================================================================
    def _build_summary_placeholder(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)
        lay.addWidget(SectionTitle("Green Slip Summary"))
        lay.addWidget(SubTitle("Loading summary..."))
        lay.addStretch()
        return w

    def _on_tab_changed(self, idx: int):
        # Summary tab is index 3
        if idx == 3 and not self._summary_built:
            self._summary_built = True
            summary = self._build_summary_tab()
            self._tabs.removeTab(3)
            self._tabs.insertTab(3, summary, "  Summary & Charts ")
            self._tabs.setCurrentIndex(3)

    def _build_summary_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Green Slip Summary"))
        lay.addWidget(SubTitle("Statistical overview of green slip records"))

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        self.green_stat_tiles = {}
        self._init_green_stat_tiles(tiles_row)
        lay.addLayout(tiles_row)

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

        from ui.chart_widgets import GreenSlipChart
        self.green_chart = GreenSlipChart(w)
        self.green_chart.setMinimumHeight(380)
        lay.addWidget(self.green_chart)

        # Populate with real data immediately
        self._refresh_green_summary()
        lay.addStretch()
        return w

    def _init_green_stat_tiles(self, tiles_row: QHBoxLayout):
        """Create stat tiles with zero values — _refresh_green_summary fills them."""
        for label, colour in [
            ("Total Green Slips",      GREEN_SLIP),
            ("Dispensation Slips",     "#388E3C"),
            ("Excuse Slips",           "#66BB6A"),
            ("Currently Active",       "#2E7D32"),
            ("Students with >2 Slips", "#F57F17"),
        ]:
            tile = StatTile(label, "0", colour)
            tiles_row.addWidget(tile)
            self.green_stat_tiles[label] = tile

    def _refresh_green_summary(self):
        """
        Recompute all stats from DB and push them to tiles + chart.
        Safe to call even before summary tab is built (guards handle it).
        """
        from backend.db_green_slip import get_green_slips
        green_records = get_green_slips(None) or []

        # ── Compute all metrics ───────────────────────────────────────────────
        total              = len(green_records)
        dispensation_count = sum(1 for r in green_records
                                 if len(r) > 5 and r[5] == True)
        excuse_count       = sum(1 for r in green_records
                                 if len(r) > 5 and r[5] == False)
        active_count       = sum(1 for r in green_records
                                 if len(r) > 8 and "Active"  in str(r[8]))
        expired_count      = sum(1 for r in green_records
                                 if len(r) > 8 and "Expired" in str(r[8]))

        stud_counts: dict = {}
        for r in green_records:
            if len(r) > 0:
                stud_counts[r[0]] = stud_counts.get(r[0], 0) + 1
        multi = sum(1 for c in stud_counts.values() if c > 2)

        # ── Update stat tiles (only if summary tab has been built) ────────────
        if self.green_stat_tiles:
            self.green_stat_tiles["Total Green Slips"].set_value(total)
            self.green_stat_tiles["Dispensation Slips"].set_value(dispensation_count)
            self.green_stat_tiles["Excuse Slips"].set_value(excuse_count)
            self.green_stat_tiles["Currently Active"].set_value(active_count)
            self.green_stat_tiles["Students with >2 Slips"].set_value(multi)

        # ── Update chart (only if summary tab has been built) ─────────────────
        if self.green_chart is not None:
            self.green_chart.update_data(
                dispensation_count, excuse_count,
                active_count, expired_count,
            )

    # =========================================================================
    # Event handlers
    # =========================================================================
    def _on_slips_changed(self):
        """Fired whenever any slip is saved — refresh tracker + summary."""
        try:
            self._refresh_green_tracker()
        except Exception:
            pass
        try:
            self._refresh_green_summary()
        except Exception:
            pass
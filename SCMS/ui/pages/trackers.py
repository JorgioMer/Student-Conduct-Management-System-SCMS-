# =============================================================================
#  SCMS — Record Trackers Page  (Combined Monthly Overview)
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QWidget, QFrame, QGridLayout
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


class TrackersPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        # FIX: border: none stops QFrame border from being inherited by the label
        t_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none; padding: 0;")

        s_lbl = QLabel("View and filter all slip records — Green, Pink, and Blue — in one place")
        s_lbl.setFont(QFont("Segoe UI", 11))
        # FIX: TEXT_DARK for readability on light yellow + border: none
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
        for label, val, colour in [
            ("Green Slips",      str(green_count),      GREEN_SLIP),
            ("Pink Slips",       str(pink_count),       PINK_SLIP),
            ("Blue Slips",       str(blue_count),       BLUE_SLIP),
            ("Total Records",    str(total_records),    NAVY),
            ("Students Tracked", str(students_tracked), GOLD),
        ]:
            tiles_row.addWidget(StatTile(label, val, colour))
        lay.addLayout(tiles_row)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("   Search by student name or number... ")
        search.setFixedHeight(38)

        slip_filter = QComboBox()
        slip_filter.addItems(["All Slip Types", "Green Slip", "Pink Slip", "Blue Slip"])
        slip_filter.setFixedHeight(38)
        slip_filter.setFixedWidth(160)

        month_filter = QComboBox()
        month_filter.addItems(["This Month (Nov 2024)", "October 2024", "September 2024",
                               "All Months", "Custom Range"])
        month_filter.setFixedHeight(38)
        month_filter.setFixedWidth(210)

        year_filter = QComboBox()
        year_filter.addItems(["All Years", "1st", "2nd", "3rd",
                               "4th", "5th"])
        year_filter.setFixedHeight(38)
        year_filter.setFixedWidth(130)

        filter_btn = QPushButton("   Apply Filter ")
        filter_btn.setStyleSheet(btn_gold())
        filter_btn.setFixedHeight(38)

        filter_row.addWidget(search, 1)
        filter_row.addWidget(slip_filter)
        filter_row.addWidget(month_filter)
        filter_row.addWidget(year_filter)
        filter_row.addWidget(filter_btn)
        lay.addLayout(filter_row)

        headers = ["#", "Student No.", "Student Name", "Year", "Course",
                   "Slip Type", "Date Filed", "Details", "Status"]
        sample      = []
        all_records = []
        try:
            for record in (get_blue_slips(None)  or []): all_records.append(("blue",  record))
            for record in (get_green_slips(None) or []): all_records.append(("green", record))
            for record in (get_pink_slips(None)  or []): all_records.append(("pink",  record))
        except:
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
            except:
                pass

        if not sample:
            sample = [("1", "No records", "Add records to see them here",
                       "-", "-", "-", "-", "-", "-")]

        table = build_record_table(headers, sample)
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

        table.setMinimumHeight(320)
        lay.addWidget(table)

        action_row = QHBoxLayout()
        action_row.addStretch()
        for label, style in [("   View", btn_outline()), ("   Export", btn_gold())]:
            b = QPushButton(label)
            b.setStyleSheet(style)
            b.setFixedHeight(38)
            action_row.addWidget(b)
        lay.addLayout(action_row)
        lay.addStretch()
        return w

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

        lbl = QLabel("Student Number / Name:")
        lbl.setStyleSheet("border: none; background: transparent;")
        s_lay.addWidget(lbl)

        self.stud_search_edit  = QLineEdit()
        self.stud_search_edit.setPlaceholderText("Type student number or name to search...")
        self.stud_search_edit.setFixedHeight(40)
        search_btn = QPushButton("   Search ")
        search_btn.setStyleSheet(btn_gold())
        search_btn.setFixedHeight(40)
        clear_btn  = QPushButton("Clear")
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

    def _search_student(self):
        """Search for a student and display their profile and slip history."""
        from backend.db_students import get_student
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        search_term = self.stud_search_edit.text().strip()
        if not search_term:
            InfoDialog("Input Required", "Please enter a student number or name to search.", 
                      success=False, parent=self).exec_()
            return

        # Get student info
        student_info = get_student(search_term)
        
        if not student_info:
            InfoDialog("Not Found", f"No student found with number/name: {search_term}", 
                      success=False, parent=self).exec_()
            return

        # Clear previous profile display
        while self.profile_layout.count() > 2:  # Keep header and divider
            self.profile_layout.takeAt(2).widget().deleteLater()

        # Display student profile
        stud_num = student_info[0] if len(student_info) > 0 else "N/A"
        stud_name = student_info[1] if len(student_info) > 1 else "N/A"
        stud_course = student_info[2] if len(student_info) > 2 else "N/A"
        stud_year = student_info[3] if len(student_info) > 3 else "N/A"

        profile_grid = QGridLayout()
        profile_grid.setSpacing(12)
        
        profile_fields = [
            ("Student Number:", stud_num),
            ("Student Name:", stud_name),
            ("Year Level:", stud_year),
            ("Course:", stud_course),
        ]
        
        for i, (label, value) in enumerate(profile_fields):
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
            
            val = QLabel(value)
            val.setFont(QFont("Segoe UI", 11))
            val.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
            
            profile_grid.addWidget(lbl, i, 0, alignment=Qt.AlignRight)
            profile_grid.addWidget(val, i, 1, alignment=Qt.AlignLeft)
        
        self.profile_layout.addLayout(profile_grid)

        # Get and display slip history
        history_records = []
        try:
            # Get all slip types for this student
            # Blue: studName[0], course[1], year[2], ID[3], studNumber[4], violationType[5], 
            #       dateOfViolation[6], ?[7], severity[8], action[9], status[10]
            for record in get_blue_slips(stud_num) or []:
                try:
                    violation = record[5] if len(record) > 5 else "N/A"
                    date = str(record[6])[:10] if len(record) > 6 else "N/A"
                    status = record[10] if len(record) > 10 else "Open"
                    history_records.append(("Blue Slip", violation, date, status))
                except:
                    pass

            # Green: studName[0], course[1], year[2], ID[3], studNumber[4], is_disp[5],
            #        dateAvail[6], daysAbsence[7], status[8], expiry[9]
            for record in get_green_slips(stud_num) or []:
                try:
                    slip_type = "Dispensation" if (record[5] == True if len(record) > 5 else False) else "Excuse"
                    date = str(record[6])[:10] if len(record) > 6 else "N/A"
                    status = record[8] if len(record) > 8 else "Active"
                    history_records.append(("Green ("+slip_type+")", date, status, "-"))
                except:
                    pass

            # Pink: studName[0], course[1], year[2], ID[3], studNumber[4], dateIssued[5],
            #       violation[6], actionTaken[7], officer[8], semester[9]
            for record in get_pink_slips(stud_num) or []:
                try:
                    violation = record[6] if len(record) > 6 else "N/A"
                    date = str(record[5])[:10] if len(record) > 5 else "N/A"
                    history_records.append(("Pink Slip", violation, date, "Completed"))
                except:
                    pass
        except:
            pass

        # Clear previous history display
        while self.history_table_container.count() > 0:
            widget = self.history_table_container.takeAt(0).widget()
            if widget:
                widget.deleteLater()

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
    """Clear the student search and reset display."""
    self.stud_search_edit.clear()

    # ── Clear profile (keep index 0=title, 1=divider) ──────────────────
    while self.profile_layout.count() > 2:
        item = self.profile_layout.takeAt(2)
        widget = item.widget()
        if widget and widget is not self.profile_empty:
            widget.deleteLater()
        layout = item.layout()
        if layout:
            # Clear any nested layouts (e.g. the QGridLayout from profile_grid)
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    # Re-add placeholder only if it's not already in the layout
    found = any(
        self.profile_layout.itemAt(i).widget() is self.profile_empty
        for i in range(self.profile_layout.count())
    )
    if not found:
        self.profile_layout.addWidget(self.profile_empty)

    # ── Clear history ───────────────────────────────────────────────────
    while self.history_table_container.count() > 0:
        item = self.history_table_container.takeAt(0)
        widget = item.widget()
        if widget and widget is not self.slip_history_empty:
            widget.deleteLater()

    found = any(
        self.history_table_container.itemAt(i).widget() is self.slip_history_empty
        for i in range(self.history_table_container.count())
    )
    if not found:
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
        period.addItems(["November 2024", "October 2024", "September 2024", "August 2024"])
        period.setFixedHeight(36)
        period.setFixedWidth(200)
        period_row.addWidget(period)
        period_row.addStretch()

        export_btn = QPushButton("   Export Monthly Report ")
        export_btn.setStyleSheet(btn_gold())
        export_btn.setFixedHeight(36)
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
            ("Total", str(len(green_slips) + len(pink_slips) + len(blue_slips)), NAVY),
        ]:
            tiles_row.addWidget(StatTile(label, val, colour))
        lay.addLayout(tiles_row)

        # Create combined chart widget
        from ui.chart_widgets import CombinedAllSlipsChart
        
        combined_chart = CombinedAllSlipsChart(w)
        combined_chart.setMinimumHeight(380)
        lay.addWidget(combined_chart)
        
        # Refresh chart with current data
        self._refresh_monthly_chart(combined_chart)

        lay.addStretch()
        return w

    def _refresh_monthly_chart(self, chart_widget):
        """Refresh the monthly summary chart with current database data."""
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        
        blue_slips = get_blue_slips(None) or []
        green_slips = get_green_slips(None) or []
        pink_slips = get_pink_slips(None) or []
        
        green_count = len(green_slips)
        pink_count = len(pink_slips)
        blue_count = len(blue_slips)
        
        # Update chart data
        chart_widget.update_data(green_count, pink_count, blue_count)


# Helper import
from ui.components import Divider
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
        # Page header
        header = QFrame()
        header.setFixedHeight(82)
        header.setStyleSheet(f"""
            QFrame {{
                background: #FFF8E1;
                border-radius: 12px;
                border-left: 6px solid {GOLD};
                border: 1px solid {GOLD}40;
                border-left: 6px solid {GOLD};
            }}
        """)
        add_shadow(header, blur=12, y=3, color=(0, 0, 0, 18))

        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)

        h_left = QVBoxLayout()
        t_lbl = QLabel("   Record Trackers — Monthly Overview ")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")
        s_lbl = QLabel("View and filter all slip records — Green, Pink, and Blue — in one place")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
        h_left.addWidget(t_lbl)
        h_left.addWidget(s_lbl)
        h_lay.addLayout(h_left)
        h_lay.addStretch()

        self.main_layout.addWidget(header)

        # Tabs
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

        # Stat summary - calculate from real data
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        
        green_slips = get_green_slips(None) or []
        pink_slips = get_pink_slips(None) or []
        blue_slips = get_blue_slips(None) or []
        
        green_count = len(green_slips)
        pink_count = len(pink_slips)
        blue_count = len(blue_slips)
        total_records = green_count + pink_count + blue_count
        
        # Count unique students
        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            if len(r) > 1:
                all_students.add(r[1])
        students_tracked = len(all_students)
        
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        for label, val, colour in [
            ("Green Slips",  str(green_count), GREEN_SLIP),
            ("Pink Slips",   str(pink_count), PINK_SLIP),
            ("Blue Slips",   str(blue_count),  BLUE_SLIP),
            ("Total Records",str(total_records), NAVY),
            ("Students Tracked",str(students_tracked), GOLD),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
        lay.addLayout(tiles_row)

        # Filters
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("   Search by student name or number... ")
        search.setFixedHeight(38)

        slip_filter = QComboBox()
        slip_filter.addItems(["All Slip Types","Green Slip","Pink Slip","Blue Slip"])
        slip_filter.setFixedHeight(38)
        slip_filter.setFixedWidth(160)

        month_filter = QComboBox()
        month_filter.addItems(["This Month (Nov 2024)","October 2024","September 2024",
                               "All Months","Custom Range"])
        month_filter.setFixedHeight(38)
        month_filter.setFixedWidth(210)

        grade_filter = QComboBox()
        grade_filter.addItems(["All Grades","Grade 7","Grade 8","Grade 9",
                               "Grade 10","Grade 11","Grade 12"])
        grade_filter.setFixedHeight(38)
        grade_filter.setFixedWidth(130)

        filter_btn = QPushButton("   Apply Filter ")
        filter_btn.setStyleSheet(btn_gold())
        filter_btn.setFixedHeight(38)

        filter_row.addWidget(search, 1)
        filter_row.addWidget(slip_filter)
        filter_row.addWidget(month_filter)
        filter_row.addWidget(grade_filter)
        filter_row.addWidget(filter_btn)
        lay.addLayout(filter_row)

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        from backend.db_students import get_student
        
        headers = ["#", "Student No.", "Student Name", "Grade", "Section",
                   "Slip Type", "Date Filed", "Details", "Status"]
        sample = []
        
        # Fetch real records
        all_records = []
        try:
            for i, record in enumerate(get_blue_slips(None) or []):
                all_records.append(("blue", record))
            for i, record in enumerate(get_green_slips(None) or []):
                all_records.append(("green", record))
            for i, record in enumerate(get_pink_slips(None) or []):
                all_records.append(("pink", record))
        except:
            pass
        
        for i, (slip_type, record) in enumerate(all_records[:8], 1):
            try:
                stud_num = record[1] if len(record) > 1 else "N/A"
                stud_info = get_student(stud_num)
                stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                grade = stud_info[3] if stud_info and len(stud_info) > 3 else "N/A"
                section = stud_info[2] if stud_info and len(stud_info) > 2 else "N/A"
                
                if slip_type == "blue":
                    slip_label = "🔵 Blue Slip"
                    details = record[4] if len(record) > 4 else "N/A"
                    date = str(record[3]) if len(record) > 3 else "N/A"
                    status = record[7] if len(record) > 7 else "Open / Pending"
                elif slip_type == "green":
                    is_disp = record[2] if len(record) > 2 else False
                    slip_label = "🟢 Green (Disp.)" if is_disp else "🟢 Green (Excuse)"
                    details = str(record[4]) if len(record) > 4 else "N/A"
                    date = str(record[3]) if len(record) > 3 else "N/A"
                    status = record[5] if len(record) > 5 else "Active"
                else:  # pink
                    slip_label = "🔴 Pink Slip"
                    details = record[3] if len(record) > 3 else "N/A"
                    date = str(record[2]) if len(record) > 2 else "N/A"
                    status = "Completed"
                
                sample.append((str(i), stud_num, stud_name, grade, section, slip_label, date[:10], details, status))
            except:
                pass
        
        if not sample:
            sample = [("1", "No records", "Add records to see them here", "-", "-", "-", "-", "-", "-")]
        
        table = build_record_table(headers, sample)
        # Color the slip type column
        SLIP_COLORS = {
            "🟢 Green (Disp.)":  (GREEN_SLIP, "#E8F5E9"),
            "🟢 Green (Excuse)": (GREEN_SLIP, "#E8F5E9"),
            "🔴 Pink Slip":       (PINK_SLIP,  "#FCE4EC"),
            "🔵 Blue Slip":       (BLUE_SLIP,  "#E3F2FD"),
        }
        for r in range(table.rowCount()):
            slip_val = table.item(r, 5).text() if table.item(r, 5) else ""
            if slip_val in SLIP_COLORS:
                fg, bg = SLIP_COLORS[slip_val]
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

        s_lay.addWidget(QLabel("Student Number / Name:"))
        stud_edit = QLineEdit()
        stud_edit.setPlaceholderText("Type student number or name to search...")
        stud_edit.setFixedHeight(40)
        search_btn = QPushButton("   Search ")
        search_btn.setStyleSheet(btn_gold())
        search_btn.setFixedHeight(40)
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_outline())
        clear_btn.setFixedHeight(40)

        s_lay.addWidget(stud_edit, 1)
        s_lay.addWidget(search_btn)
        s_lay.addWidget(clear_btn)
        lay.addWidget(search_frame)

        # Profile card (empty until search)
        profile = QFrame()
        profile.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        p_lay = QGridLayout(profile)
        p_lay.setContentsMargins(20, 14, 20, 14)
        p_lay.setSpacing(8)

        profile_lbl = QLabel("Student Profile")
        profile_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        profile_lbl.setStyleSheet(f"color: {NAVY}; background: transparent;")
        p_lay.addWidget(profile_lbl, 0, 0, 1, 4)
        p_lay.addWidget(Divider(), 1, 0, 1, 4)

        # Show empty state initially
        empty_label = QLabel("Search for a student number to view their profile")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet(f"color: {MID_GRAY}; background: transparent; padding: 30px;")
        p_lay.addWidget(empty_label, 2, 0, 1, 4)

        lay.addWidget(profile)

        # Slip history table
        lay.addWidget(SectionTitle("Slip History"))
        headers = ["Slip Type", "Date", "Details", "Status", "Officer"]
        sample = []
        empty_label = QLabel("Perform a search to view slip history")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet(f"color: {MID_GRAY}; padding: 30px;")
        lay.addWidget(empty_label)
        lay.addStretch()
        return w

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
        period_row.addWidget(QLabel("Select Month:"))
        period = QComboBox()
        period.addItems(["November 2024","October 2024","September 2024","August 2024"])
        period.setFixedHeight(36)
        period.setFixedWidth(200)
        period_row.addWidget(period)
        period_row.addStretch()

        export_btn = QPushButton("   Export Monthly Report ")
        export_btn.setStyleSheet(btn_gold())
        export_btn.setFixedHeight(36)
        period_row.addWidget(export_btn)
        lay.addLayout(period_row)

        # Stat tiles
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(14)
        
        # Calculate real statistics
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        
        green_slips = get_green_slips(None) or []
        pink_slips = get_pink_slips(None) or []
        blue_slips = get_blue_slips(None) or []
        
        green_count = len(green_slips)
        pink_count = len(pink_slips)
        blue_count = len(blue_slips)
        total_count = green_count + pink_count + blue_count
        
        for label, val, colour in [
            ("Green Slips", str(green_count), GREEN_SLIP),
            ("Pink Slips",  str(pink_count), PINK_SLIP),
            ("Blue Slips",  str(blue_count),  BLUE_SLIP),
            ("Total",       str(total_count), NAVY),
        ]:
            tile = StatTile(label, val, colour)
            tiles_row.addWidget(tile)
        lay.addLayout(tiles_row)

        # Chart placeholder
        chart_frame = QFrame()
        chart_frame.setFixedHeight(300)
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background: {OFF_WHITE};
                border: 2px dashed {LIGHT_GRAY};
                border-radius: 12px;
            }}
        """)
        c_lay = QVBoxLayout(chart_frame)
        c_lay.setAlignment(Qt.AlignCenter)
        chart_icon = QLabel("📊")
        chart_icon.setFont(QFont("Segoe UI", 52))
        chart_icon.setAlignment(Qt.AlignCenter)
        chart_icon.setStyleSheet("background: transparent;")
        chart_text = QLabel(
            "Monthly Record Summary — Visual Charts\n\n"
            "Bar Chart: Green / Pink / Blue Slips per Day\n"
            "Pie Chart: Breakdown by Slip Type\n"
            "Line Chart: Trend across months\n\n"
            "(Charts rendered via matplotlib in final system)"
        )
        chart_text.setFont(QFont("Segoe UI", 12))
        chart_text.setAlignment(Qt.AlignCenter)
        chart_text.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
        c_lay.addWidget(chart_icon)
        c_lay.addWidget(chart_text)
        lay.addWidget(chart_frame)

        lay.addStretch()
        return w


# Helper import
from ui.components import Divider

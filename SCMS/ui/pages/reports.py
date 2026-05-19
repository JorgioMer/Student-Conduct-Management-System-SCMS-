# =============================================================================
#  SCMS — Reports Page
# =============================================================================
from PyQt5.QtWidgets import (
    QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QTabWidget, QWidget,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, TEXT_DARK,
    GREEN_SLIP, PINK_SLIP, BLUE_SLIP,
    btn_gold, btn_outline, btn_primary
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    StatTile, add_shadow, InfoDialog
)
from ui.pages.base_page import BasePage, build_record_table
from ui.data_events import data_events
from ui.pdf_preview_dialog import PDFPreviewDialog
from backend.pdf_export import (
    generate_overview_report, generate_slip_report,
    generate_student_conduct_summary
)
from backend.db_activity_log import log_export, log_report_generated
from backend.config import get_course_college, get_college_name, get_all_colleges
import tempfile
import os


class ReportsPage(BasePage):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self.staff_id = self.current_user.get("username", "UNKNOWN")
        self._tabs = None  # Store tab widget reference
        self._built_tabs = set()  # Track which tabs have been built
        self._build()
        # Connect to data changes
        data_events.slips_changed.connect(self._on_slips_changed)

    def _filter_records_by_period(self, records, date_field_index=6):
        """Filter records by the selected report period.
        
        Args:
            records: List of slip records
            date_field_index: Index of the date field in the record tuple (default 6)
        
        Returns:
            Filtered list containing only records from the selected period
        """
        period = self.period_cb.currentText() if hasattr(self, 'period_cb') else ""
        if not records or not period:
            return records
        
        filtered = []
        for record in records:
            try:
                if len(record) <= date_field_index:
                    continue
                
                date_str = str(record[date_field_index]).strip()
                if not date_str or date_str == "N/A":
                    continue
                
                # Parse date (handle DD/MM/YYYY and YYYY-MM-DD formats)
                try:
                    if "/" in date_str:
                        date_obj = datetime.strptime(date_str.split()[0], "%d/%m/%Y")
                    else:
                        date_obj = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
                except ValueError:
                    continue
                
                # Check if date matches period
                if self._date_in_period(date_obj, period):
                    filtered.append(record)
            except Exception:
                continue
        
        return filtered
    
    def _date_in_period(self, date_obj, period_str):
        """Check if a date falls within the selected period."""
        month = date_obj.month
        year = date_obj.year
        
        # Monthly periods (e.g., "May 2026")
        if len(period_str.split()) == 2:
            try:
                period_date = datetime.strptime(period_str, "%B %Y")
                return month == period_date.month and year == period_date.year
            except ValueError:
                return True
        
        # Semester periods
        if "1st Semester" in period_str or "1ST Semester" in period_str:
            return month in [6, 7, 8, 9, 10, 11]  # June to November
        if "2ND Semester" in period_str or "2nd Semester" in period_str:
            return month in [12, 1, 2, 3, 4, 5]  # December to May
        if "Full Year" in period_str:
            return True
        
        return True

    def _build(self):
        # Header
        header = QFrame()
        header.setFixedHeight(82)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {NAVY_DARK}, stop:1 {NAVY}
                );
                border-radius: 12px;
                border-left: 6px solid {GOLD};
            }}
        """)
        add_shadow(header, blur=12, y=3, color=(0, 0, 0, 20))

        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 12, 24, 12)
        h_col = QVBoxLayout()
        h_col.setSpacing(2)

        t_lbl = QLabel("   Reports & Analytics")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        # FIX: border: none prevents QFrame border from rendering around the label text
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; border: none; padding: 0;")

        s_lbl = QLabel("Monthly summaries, visual graphs, and statistical records for all slip types")
        s_lbl.setFont(QFont("Segoe UI", 11))
        # FIX: same fix — white at 85% opacity is visible on the dark navy gradient
        s_lbl.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent; border: none; padding: 0;")

        h_col.addWidget(t_lbl)
        h_col.addWidget(s_lbl)
        h_lay.addLayout(h_col)
        h_lay.addStretch()

        export_all = QPushButton("   Export All Reports ")
        export_all.setStyleSheet(btn_gold())
        export_all.setFixedHeight(38)
        export_all.clicked.connect(self._export_overview_report)
        h_lay.addWidget(export_all)
        self.main_layout.addWidget(header)

        # Period selector - Auto-select current month
        period_row = QHBoxLayout()
        period_lbl = QLabel("Report Period:")
        period_lbl.setStyleSheet("border: none; background: transparent;")
        period_row.addWidget(period_lbl)
        self.period_cb = QComboBox()
        self.period_cb.addItems([
            "January 2026",
            "February 2026",
            "March 2026",
            "April 2026",
            "May 2026",
            "June 2026",
            "July 2026",
            "August 2026",
            "September 2026",
            "October 2026",
            "December 2026",
            "1st Semester S.Y. 2025–2026",
            "2ND Semester S.Y. 2025–2026",
            "S.Y. 2025–2026 (Full Year)",
        ])
        # Auto-select current month
        current_month = datetime.now().strftime("%B %Y")
        index = self.period_cb.findText(current_month)
        if index >= 0:
            self.period_cb.setCurrentIndex(index)
        self.period_cb.setFixedHeight(38)
        self.period_cb.setFixedWidth(280)
        self.period_cb.currentIndexChanged.connect(self._on_period_changed)
        period_row.addWidget(self.period_cb)
        period_row.addStretch()

        self.top_print_btn = QPushButton(" Print Preview ")
        self.top_print_btn.setStyleSheet(btn_outline())
        self.top_print_btn.setFixedHeight(38)
        self.top_print_btn.clicked.connect(self._export_overview_report)
        period_row.addWidget(self.top_print_btn)
        self.main_layout.addLayout(period_row)
        
        # Initialize button state based on current period's data
        self._update_print_button_state()

        # Tabs
        tabs = QTabWidget()
        self._tabs = tabs  # Store reference for refresh
        tabs.addTab(self._build_overview_tab(),  "   Overview ")
        tabs.addTab(self._build_green_report(),  "   Green Slips ")
        tabs.addTab(self._build_pink_report(),   "   Pink Slips ")
        tabs.addTab(self._build_blue_report(),   "   Blue Slips ")
        tabs.addTab(self._build_college_report(), "   By College ")
        tabs.addTab(self._build_toplist_tab(),   "   Student Records ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()


    # ── Overview ──────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        """Clean up signal connections when page is closed"""
        try:
            data_events.slips_changed.disconnect(self._on_slips_changed)
        except Exception:
            pass
        super().closeEvent(event)
    
    def showEvent(self, event):
        """Refresh reports whenever the page is shown (tab clicked)"""
        super().showEvent(event)
        try:
            self._on_slips_changed()
        except Exception as e:
            print(f"[ERROR] Failed to refresh reports on show: {str(e)}")

    def _build_overview_tab(self) -> QWidget:
        from PyQt5.QtWidgets import QScrollArea
        container = QWidget()
        container.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(18)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        w = scroll

        # Get selected period
        selected_period = self.period_cb.currentText() if hasattr(self, 'period_cb') else "November 2026"
        
        lay.addWidget(SectionTitle(f"Monthly Overview — {selected_period}"))

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        # Get all slips and filter by selected period
        green_slips = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
        pink_slips  = self._filter_records_by_period(get_pink_slips(None) or [], date_field_index=5)
        blue_slips  = self._filter_records_by_period(get_blue_slips(None) or [], date_field_index=6)

        green_count   = len(green_slips)
        pink_count    = len(pink_slips)
        blue_count    = len(blue_slips)
        total_records = green_count + pink_count + blue_count

        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            if len(r) > 1:
                all_students.add(r[1])
        students_involved = len(all_students)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)
        for label, val, colour, icon in [
            ("Green Slips Issued",      str(green_count),      GREEN_SLIP, ""),
            ("Pink Slips Issued",       str(pink_count),       PINK_SLIP,  ""),
            ("Blue Slips / Violations", str(blue_count),       BLUE_SLIP,  ""),
            ("Total Records Filed",     str(total_records),    NAVY,       ""),
            ("Students Involved",       str(students_involved),GOLD,       ""),
        ]:
            tiles_row.addWidget(StatTile(f"{icon}  {label}", val, colour))
        lay.addLayout(tiles_row)

        lay.addWidget(Divider())

        charts_label = QLabel("Visual Summary Charts")
        charts_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        charts_label.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(charts_label)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # Slip Distribution Pie Chart
        slip_dist_chart = self._create_slip_distribution_chart(green_count, pink_count, blue_count)
        slip_dist_frame = QFrame()
        slip_dist_frame.setStyleSheet(f"""
            QFrame {{
                background: #E8F5E9;
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        slip_dist_layout = QVBoxLayout(slip_dist_frame)
        slip_dist_layout.setContentsMargins(10, 10, 10, 10)
        slip_dist_frame.setMinimumHeight(300)
        slip_dist_layout.addWidget(slip_dist_chart)
        charts_row.addWidget(slip_dist_frame, 1)

        # Year Level Breakdown Bar Chart
        year_breakdown_chart = self._create_year_breakdown_chart(green_slips + pink_slips + blue_slips)
        year_breakdown_frame = QFrame()
        year_breakdown_frame.setStyleSheet(f"""
            QFrame {{
                background: #FCE4EC;
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        year_breakdown_layout = QVBoxLayout(year_breakdown_frame)
        year_breakdown_layout.setContentsMargins(10, 10, 10, 10)
        year_breakdown_frame.setMinimumHeight(300)
        year_breakdown_layout.addWidget(year_breakdown_chart)
        charts_row.addWidget(year_breakdown_frame, 1)

        # Student Slip Count Distribution
        student_slips_chart = self._create_student_slip_distribution_chart(green_slips + pink_slips + blue_slips)
        student_slips_frame = QFrame()
        student_slips_frame.setStyleSheet(f"""
            QFrame {{
                background: #E3F2FD;
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        student_slips_layout = QVBoxLayout(student_slips_frame)
        student_slips_layout.setContentsMargins(10, 10, 10, 10)
        student_slips_frame.setMinimumHeight(300)
        student_slips_layout.addWidget(student_slips_chart)
        charts_row.addWidget(student_slips_frame, 1)

        lay.addLayout(charts_row)

        # ── College Distribution Chart ───────────────────────────────────────
        lay.addWidget(Divider())
        college_chart_label = QLabel("Distribution by College")
        college_chart_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        college_chart_label.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(college_chart_label)

        # Build college data
        all_slips = green_slips + pink_slips + blue_slips
        college_data = {}
        for college_code in get_all_colleges():
            college_data[college_code] = {
                "name": get_college_name(college_code),
                "students": set(),
                "green": 0,
                "pink": 0,
                "blue": 0,
                "total": 0
            }

        for slip in all_slips:
            try:
                course = slip[1] if len(slip) > 1 else ""
                college_code = get_course_college(course)
                
                if college_code is None:
                    continue

                stud_name = slip[0] if len(slip) > 0 else "Unknown"
                college_data[college_code]["students"].add(stud_name)

                if slip in green_slips:
                    college_data[college_code]["green"] += 1
                elif slip in pink_slips:
                    college_data[college_code]["pink"] += 1
                elif slip in blue_slips:
                    college_data[college_code]["blue"] += 1
                college_data[college_code]["total"] += 1
            except:
                pass

        college_chart = self._create_college_distribution_chart(college_data)
        college_frame = QFrame()
        college_frame.setStyleSheet(f"""
            QFrame {{
                background: #FFF3E0;
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        college_layout = QVBoxLayout(college_frame)
        college_frame.setMinimumHeight(320)
        college_layout.setContentsMargins(10, 10, 10, 10)
        college_layout.addWidget(college_chart)
        lay.addWidget(college_frame)

        return w

    # ── Green Slip Report ─────────────────────────────────────────────────────
    def _build_green_report(self) -> QWidget:
        from backend.db_green_slip import get_green_slips

        green_records = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
        rows = []
        for record in green_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                is_dispensation = record[5] if len(record) > 5 else False
                slip_type = "Dispensation" if is_dispensation else "Excuse"
                date      = str(record[6])[:10] if len(record) > 6 else "N/A"
                days      = str(record[7]) if len(record) > 7 else "N/A"
                status    = record[8] if len(record) > 8 else "Active"
                rows.append((stud_num, stud_name, year, slip_type, date, days, status))
            except:
                pass

        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]

        return self._build_slip_report_tab(
            "green", "Green Slip Monthly Report",
            "Dispensation and Excuse slips issued this month",
            GREEN_SLIP, "#E8F5E9",
            ["Student No.", "Student Name", "Year", "Type", "Date", "Days/Reason", "Status"],
            rows
        )

    def _build_pink_report(self) -> QWidget:
        from backend.db_pink_slip import get_pink_slips

        pink_records = self._filter_records_by_period(get_pink_slips(None) or [], date_field_index=5)
        rows = []
        for record in pink_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                course    = record[1] if len(record) > 1 else "N/A"
                date      = str(record[5])[:10] if len(record) > 5 else "N/A"
                violation = record[6] if len(record) > 6 else "N/A"
                rows.append((stud_num, stud_name, year, course, violation, date))
            except:
                pass

        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-")]

        return self._build_slip_report_tab(
            "pink", "Pink Slip Monthly Report",
            "Penalty slips issued this month (one per student per semester)",
            PINK_SLIP, "#FCE4EC",
            ["Student No.", "Student Name", "Year", "Course", "Violation", "Date Issued"],
            rows
        )

    def _build_blue_report(self) -> QWidget:
        from backend.db_blue_slip import get_blue_slips

        blue_records = self._filter_records_by_period(get_blue_slips(None) or [], date_field_index=6)
        rows = []
        for record in blue_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                violation = record[5] if len(record) > 5 else "N/A"
                severity  = record[8] if len(record) > 8 else "N/A"
                date      = str(record[6])[:10] if len(record) > 6 else "N/A"
                status    = record[10] if len(record) > 10 else "Open"
                rows.append((stud_num, stud_name, year, violation, severity, date, status))
            except:
                pass

        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]

        return self._build_slip_report_tab(
            "blue", "Blue Slip Monthly Report",
            "Violation records and disciplinary actions taken this month",
            BLUE_SLIP, "#E3F2FD",
            ["Student No.", "Student Name", "Year", "Violation", "Severity", "Date", "Status"],
            rows
        )

    def _build_slip_report_tab(self, slip_type, title, subtitle, colour, bg,
                                headers, rows) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        top_row = QHBoxLayout()
        t_lbl = QLabel(title)
        t_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {colour}; background: transparent; border: none;")
        top_row.addWidget(t_lbl)
        top_row.addStretch()

        # Export PDF button
        has_data = not (len(rows) == 1 and rows[0][0] == "No records")
        export_pdf_btn = QPushButton("   Export PDF ")
        export_pdf_btn.setStyleSheet(btn_outline())
        export_pdf_btn.setFixedHeight(36)
        export_pdf_btn.setEnabled(has_data)
        export_pdf_btn.setToolTip("" if has_data else "No data available for this period")
        export_pdf_btn.clicked.connect(
            lambda _, st=slip_type, ttl=title, sbt=subtitle, rw=rows: 
            self._export_slip_report(st, ttl, sbt, rw)
        )
        top_row.addWidget(export_pdf_btn)
        
        # Print button
        print_btn = QPushButton("   Print ")
        print_btn.setStyleSheet(btn_outline())
        print_btn.setFixedHeight(36)
        print_btn.setEnabled(has_data)
        print_btn.setToolTip("" if has_data else "No data available for this period")
        print_btn.clicked.connect(
            lambda _, st=slip_type, ttl=title, sbt=subtitle, rw=rows: 
            self._export_slip_report(st, ttl, sbt, rw)
        )
        top_row.addWidget(print_btn)
        lay.addLayout(top_row)

        sub = QLabel(subtitle)
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")
        lay.addWidget(sub)

        t = build_record_table(headers, rows)
        t.setMinimumHeight(250)
        lay.addWidget(t)

        info_bar = QFrame()
        info_bar.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border-left: 4px solid {colour};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        i_lay = QHBoxLayout(info_bar)
        i_lay.setContentsMargins(12, 8, 12, 8)
        total_lbl = QLabel(f"Total records shown: <b>{len(rows)}</b>")
        total_lbl.setTextFormat(Qt.RichText)
        total_lbl.setFont(QFont("Segoe UI", 11))
        total_lbl.setStyleSheet(f"color: {colour}; background: transparent; border: none;")
        i_lay.addWidget(total_lbl)
        i_lay.addStretch()
        lay.addWidget(info_bar)

        lay.addStretch()
        return w

    # ── College-Based Report tab ──────────────────────────────────────────────
    def _build_college_report(self) -> QWidget:
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        from backend.db_blue_slip import get_blue_slips

        container = QWidget()
        container.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        lay.addWidget(SectionTitle("Distribution by College"))

        # Get and filter all slips by period
        green_slips = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
        pink_slips = self._filter_records_by_period(get_pink_slips(None) or [], date_field_index=5)
        blue_slips = self._filter_records_by_period(get_blue_slips(None) or [], date_field_index=6)
        all_slips = green_slips + pink_slips + blue_slips

        # Organize by college
        college_data = {}
        for college_code in get_all_colleges():
            college_data[college_code] = {
                "name": get_college_name(college_code),
                "students": set(),
                "green": 0,
                "pink": 0,
                "blue": 0,
                "total": 0
            }

        # Count slips by college based on course
        for slip in all_slips:
            try:
                course = slip[1] if len(slip) > 1 else ""
                college_code = get_course_college(course)
                
                if college_code is None:
                    continue

                stud_name = slip[0] if len(slip) > 0 else "Unknown"
                college_data[college_code]["students"].add(stud_name)

                # Determine slip type and count
                if slip in green_slips:
                    college_data[college_code]["green"] += 1
                elif slip in pink_slips:
                    college_data[college_code]["pink"] += 1
                elif slip in blue_slips:
                    college_data[college_code]["blue"] += 1
                college_data[college_code]["total"] += 1
            except:
                pass

        # Create tiles for each college
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(12)
        for college_code, data in college_data.items():
            if data["total"] > 0:
                tile = QFrame()
                tile.setStyleSheet(f"""
                    QFrame {{
                        background: #F8F9FA;
                        border: 1.5px solid {LIGHT_GRAY};
                        border-radius: 10px;
                    }}
                """)
                tile_lay = QVBoxLayout(tile)
                tile_lay.setContentsMargins(14, 12, 14, 12)
                tile_lay.setSpacing(8)

                # College name
                name_lbl = QLabel(college_code)
                name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
                name_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
                tile_lay.addWidget(name_lbl)

                # Statistics
                stats_text = f"Students: {len(data['students'])}\nTotal Records: {data['total']}"
                stats_lbl = QLabel(stats_text)
                stats_lbl.setFont(QFont("Segoe UI", 10))
                stats_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent; border: none;")
                tile_lay.addWidget(stats_lbl)

                # Slip breakdown
                breakdown = QLabel(f"🟢 {data['green']}  🔴 {data['pink']}  🔵 {data['blue']}")
                breakdown.setFont(QFont("Segoe UI", 10))
                breakdown.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; border: none;")
                tile_lay.addWidget(breakdown)

                tiles_row.addWidget(tile)

        tiles_row.addStretch()
        lay.addLayout(tiles_row)
        lay.addWidget(Divider())

        # College breakdown chart
        college_chart = self._create_college_distribution_chart(college_data)
        chart_frame = QFrame()
        chart_frame.setStyleSheet(f"""
            QFrame {{
                background: #F8F9FA;
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        chart_frame.setMinimumHeight(320)
        chart_lay = QVBoxLayout(chart_frame)
        chart_lay.setContentsMargins(10, 10, 10, 10)
        chart_lay.addWidget(college_chart)
        lay.addWidget(chart_frame)

        # Detailed table
        lay.addWidget(QLabel(""))  # Spacer
        detail_lbl = QLabel("College Details")
        detail_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        detail_lbl.setStyleSheet(f"color: {NAVY}; background: transparent; border: none;")
        lay.addWidget(detail_lbl)

        rows = []
        for college_code, data in college_data.items():
            rows.append((
                college_code,
                data["name"],
                str(len(data["students"])),
                str(data["green"]),
                str(data["pink"]),
                str(data["blue"]),
                str(data["total"])
            ))

        detail_table = build_record_table(
            ["Code", "College Name", "Students", "Green", "Pink", "Blue", "Total"],
            rows
        )
        detail_table.setMinimumHeight(len(rows) * 40 + 60)
        detail_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lay.addWidget(detail_table)
        lay.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        return scroll

    # ── Student Top Records tab ───────────────────────────────────────────────
    def _build_toplist_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        lay.addWidget(SectionTitle("Student Conduct Summary"))
        lay.addWidget(SubTitle("Students with the most recorded slips this semester"))

        headers = ["Rank", "Student No.", "Student Name", "Year",
                   "Green Slips", "Pink Slips", "Blue Slips", "Total"]

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        from backend.db_students import get_student

        student_counts = {}
        try:
            for record in get_green_slips(None) or []:
                stud_num = record[4] if len(record) > 4 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["green"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)

            for record in get_pink_slips(None) or []:
                stud_num = record[4] if len(record) > 4 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["pink"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)

            for record in get_blue_slips(None) or []:
                stud_num = record[4] if len(record) > 4 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["blue"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)
        except:
            pass

        sorted_students = sorted(
            student_counts.items(),
            key=lambda x: x[1]["green"] + x[1]["pink"] + x[1]["blue"],
            reverse=True
        )

        sample = []
        for rank, (stud_num, counts) in enumerate(sorted_students[:8], 1):
            try:
                info      = counts["info"]
                stud_name = info[1] if info and len(info) > 1 else "Unknown"
                year      = info[3] if info and len(info) > 3 else "N/A"
                total     = counts["green"] + counts["pink"] + counts["blue"]
                sample.append((str(rank), stud_num, stud_name, year,
                               str(counts["green"]), str(counts["pink"]),
                               str(counts["blue"]), str(total)))
            except:
                pass

        if not sample:
            sample = [("1", "No records", "Add records to see them here",
                       "-", "0", "0", "0", "0")]

        t = build_record_table(headers, sample)
        t.setMinimumHeight(300)
        lay.addWidget(t)

        note = QLabel(
            "   This list helps the Office of the Prefect identify students who may need additional  "
            "counseling, guidance, or follow-up actions. Data shown is for the current semester."
        )
        note.setWordWrap(True)
        note.setFont(QFont("Segoe UI", 11))
        note.setStyleSheet(f"""
            background: #FFF8E1;
            border-left: 4px solid {GOLD};
            border-radius: 6px;
            padding: 10px 14px;
            color: #8D6E0A;
        """)
        lay.addWidget(note)
        lay.addStretch()
        return w

    # ── Chart Methods ─────────────────────────────────────────────────────────
    def _create_slip_distribution_chart(self, green, pink, blue) -> FigureCanvas:
        """Create a pie chart showing the distribution of slip types."""
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='white', edgecolor='none')
        ax = fig.add_subplot(111)
        
        sizes = [green, pink, blue]
        labels = ['Green Slips', 'Pink Slips', 'Blue Slips']
        colors = ['#4CAF50', '#E91E63', '#2196F3']
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                               startangle=90, textprops={'fontsize': 9})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        
        ax.set_title('Slip Distribution', fontsize=11, fontweight='bold', pad=10)
        fig.tight_layout(pad=0.5)
        canvas = FigureCanvas(fig)
        return canvas

    def _create_year_breakdown_chart(self, all_records) -> FigureCanvas:
        """Create a bar chart showing records by year level."""
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='white', edgecolor='none')
        ax = fig.add_subplot(111)
        
        # Count records by year (index 2 in the record tuple)
        year_counts = Counter()
        for record in all_records:
            if len(record) > 2:
                year = record[2]
                if year and year != "N/A":
                    year_counts[str(year)] += 1
        
        if year_counts:
            years = sorted(year_counts.keys())
            counts = [year_counts[y] for y in years]
            colors = ['#4CAF50', '#8BC34A', '#CDDC39', '#FFC107', '#FF9800', '#F44336']
            bar_colors = colors[:len(years)]
            
            bars = ax.bar(years, counts, color=bar_colors, edgecolor='black', linewidth=0.5)
            ax.set_ylabel('Count', fontsize=9)
            ax.set_xlabel('Year Level', fontsize=9)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        
        ax.set_title('Records by Year Level', fontsize=11, fontweight='bold', pad=10)
        ax.tick_params(axis='both', labelsize=8)
        fig.tight_layout(pad=0.5)
        canvas = FigureCanvas(fig)
        return canvas

    def _create_student_slip_distribution_chart(self, all_records) -> FigureCanvas:
        """Create a bar chart showing top students with most slips."""
        fig = Figure(figsize=(5, 4), dpi=90, facecolor='white', edgecolor='none')
        ax = fig.add_subplot(111)
        
        # Count slips per student (index 0 is student name)
        student_counts = Counter()
        for record in all_records:
            if len(record) > 0:
                stud_name = record[0]
                if stud_name and stud_name != "Unknown":
                    student_counts[stud_name] += 1
        
        if student_counts:
            # Get top 6 students
            top_students = sorted(student_counts.items(), key=lambda x: x[1], reverse=True)[:6]
            names = [name[:15] for name, _ in top_students]  # Truncate long names
            counts = [count for _, count in top_students]
            
            bars = ax.barh(names, counts, color='#FF9800', edgecolor='black', linewidth=0.5)
            ax.set_xlabel('Slip Count', fontsize=9)
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{int(width)}', ha='left', va='center', fontsize=8, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        
        ax.set_title('Top Students by Slips', fontsize=11, fontweight='bold', pad=10)
        ax.tick_params(axis='both', labelsize=8)
        fig.tight_layout(pad=0.5)
        canvas = FigureCanvas(fig)
        return canvas

    def _create_college_distribution_chart(self, college_data) -> FigureCanvas:
        """Create a bar chart showing records by college."""
        fig = Figure(figsize=(8, 4), dpi=90, facecolor='white', edgecolor='none')
        ax = fig.add_subplot(111)

        colleges = []
        totals = []
        colors = []
        college_colors = {
            "CEDAS": "#FF6B6B",
            "CABE": "#4ECDC4",
            "CCIS": "#95E1D3",
            "COE": "#F9CA24",
            "CHS": "#6C5CE7",
            "CSP": "#A29BFE"
        }

        for college_code, data in college_data.items():
            if data["total"] > 0:
                colleges.append(college_code)
                totals.append(data["total"])
                colors.append(college_colors.get(college_code, "#999999"))

        if colleges:
            x_pos = range(len(colleges))
            bars = ax.bar(x_pos, totals, color=colors, edgecolor='black', linewidth=0.5)
            ax.set_ylabel('Total Records', fontsize=9)
            ax.set_xlabel('College', fontsize=9)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(colleges, fontsize=8)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

            # Add grid
            ax.yaxis.grid(True, alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        ax.set_title('Records by College', fontsize=11, fontweight='bold', pad=10)
        fig.tight_layout(pad=0.5)
        canvas = FigureCanvas(fig)
        return canvas

    # ── PDF Export Methods ────────────────────────────────────────────────────
    def _export_overview_report(self):
        """Export monthly overview report as PDF."""
        try:
            from backend.db_blue_slip import get_blue_slips
            from backend.db_green_slip import get_green_slips
            from backend.db_pink_slip import get_pink_slips
            
            # Get all records and filter by selected period
            all_green = get_green_slips(None) or []
            all_pink = get_pink_slips(None) or []
            all_blue = get_blue_slips(None) or []
            
            # Filter records by the selected period
            green_filtered = self._filter_records_by_period(all_green, date_field_index=6)
            pink_filtered = self._filter_records_by_period(all_pink, date_field_index=5)
            blue_filtered = self._filter_records_by_period(all_blue, date_field_index=6)
            
            # Collect filtered data
            records_data = {
                'green': green_filtered,
                'pink': pink_filtered,
                'blue': blue_filtered,
            }
            
            total_records = len(records_data['green']) + len(records_data['pink']) + len(records_data['blue'])
            
            # Check if there's data to export
            if total_records == 0:
                InfoDialog(
                    "No Data",
                    "No slip records available for this period.\nPlease select a different time period or date range.",
                    success=False,
                    parent=self
                ).exec_()
                return
            
            # Get selected period from combobox
            selected_period = self.period_cb.currentText() if hasattr(self, 'period_cb') else datetime.now().strftime("%B %Y")
            
            # Generate PDF in temp location
            temp_pdf = os.path.join(tempfile.gettempdir(), 'SCMS_Overview_Report.pdf')
            generate_overview_report(temp_pdf, records_data, period=selected_period)
            
            # Log the export action
            log_report_generated(self.staff_id, "Monthly Overview")
            
            # Show preview dialog
            PDFPreviewDialog(temp_pdf, "Monthly Overview Report", parent=self).exec_()
        except Exception as e:
            InfoDialog(
                "Export Error",
                f"Failed to generate overview report:\n{str(e)}",
                success=False,
                parent=self
            ).exec_()

    def _export_slip_report(self, slip_type, title, subtitle, rows):
        """Export individual slip type report as PDF."""
        # Check if there's data to export
        if not rows or len(rows) == 0:
            InfoDialog(
                "No Data",
                f"No {slip_type} slip records available for this period.\nPlease select a different time period or date range.",
                success=False,
                parent=self
            ).exec_()
            return
        
        try:
            # Convert rows to database record format
            records = [tuple(row) for row in rows] if rows else []
            
            # Get selected period from combobox
            selected_period = self.period_cb.currentText() if hasattr(self, 'period_cb') else datetime.now().strftime("%B %Y")
            
            # Generate PDF in temp location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_pdf = os.path.join(tempfile.gettempdir(), f'SCMS_{slip_type.upper()}_Report_{timestamp}.pdf')
            generate_slip_report(temp_pdf, slip_type, records, subtitle, period=selected_period)
            
            # Log the export action
            log_report_generated(self.staff_id, f"{slip_type.title()} Slip Report")
            
            # Show preview dialog
            PDFPreviewDialog(temp_pdf, title, parent=self).exec_()
        except Exception as e:
            InfoDialog(
                "Export Error",
                f"Failed to generate {slip_type} slip report:\n{str(e)}",
                success=False,
                parent=self
            ).exec_()

    def _update_print_button_state(self):
        """Update the print preview button state based on current period's data."""
        try:
            from backend.db_blue_slip import get_blue_slips
            from backend.db_green_slip import get_green_slips
            from backend.db_pink_slip import get_pink_slips
            
            # Filter records by the selected period
            green_slips_filtered = self._filter_records_by_period(get_green_slips(None) or [], date_field_index=6)
            pink_slips_filtered = self._filter_records_by_period(get_pink_slips(None) or [], date_field_index=5)
            blue_slips_filtered = self._filter_records_by_period(get_blue_slips(None) or [], date_field_index=6)
            
            total_records = len(green_slips_filtered) + len(pink_slips_filtered) + len(blue_slips_filtered)
            
            # Update print preview button state
            if hasattr(self, 'top_print_btn'):
                self.top_print_btn.setEnabled(total_records > 0)
                self.top_print_btn.setToolTip("" if total_records > 0 else "No data available for this period")
        except Exception as e:
            print(f"[ERROR] Failed to update print button state: {str(e)}")

    def _on_slips_changed(self):
        """Refresh reports when slips data changes - called whenever a slip is added."""
        print("[DEBUG] Reports page: _on_slips_changed() called")
        try:
            if self._tabs is None:
                print("[WARNING] Reports tabs not initialized yet")
                return
            
            # Update the print preview button state based on current period data
            self._update_print_button_state()
            
            # Store current tab index
            current_idx = self._tabs.currentIndex()
            print(f"[DEBUG] Currently on tab {current_idx}")
            
            # Rebuild all slip report tabs with fresh data
            tab_configs = [
                (0, self._build_overview_tab(), "   Overview "),
                (1, self._build_green_report(), "   Green Slips "),
                (2, self._build_pink_report(), "   Pink Slips "),
                (3, self._build_blue_report(), "   Blue Slips "),
                (4, self._build_college_report(), "   By College "),
                (5, self._build_toplist_tab(), "   Student Records "),
            ]
            
            # Remove tabs in reverse order to avoid index shifting issues
            for idx in range(self._tabs.count() - 1, -1, -1):
                self._tabs.removeTab(idx)
            
            # Add all tabs back with fresh data
            for idx, widget, label in tab_configs:
                try:
                    self._tabs.addTab(widget, label)
                    print(f"[DEBUG] Refreshed tab {idx}: {label}")
                except Exception as e:
                    print(f"[ERROR] Failed to refresh tab at index {idx}: {str(e)}")
            
            # Reset to previously viewed tab if it still exists
            if current_idx < self._tabs.count():
                self._tabs.setCurrentIndex(current_idx)
                print(f"[DEBUG] Restored tab index to {current_idx}")
        except Exception as e:
            print(f"[ERROR] Failed to refresh reports: {str(e)}")
            import traceback
            traceback.print_exc()

    def _on_period_changed(self):
        """Refresh all reports when the period selection changes."""
        try:
            if self._tabs is None:
                return
            
            # Update print preview button state based on filtered data
            self._update_print_button_state()
            
            # Store current tab index
            current_idx = self._tabs.currentIndex()
            
            # Rebuild all tabs with new period
            tab_configs = [
                (0, self._build_overview_tab(), "   Overview "),
                (1, self._build_green_report(), "   Green Slips "),
                (2, self._build_pink_report(), "   Pink Slips "),
                (3, self._build_blue_report(), "   Blue Slips "),
                (4, self._build_college_report(), "   By College "),
                (5, self._build_toplist_tab(), "   Student Records "),
            ]
            
            # Remove tabs in reverse order to avoid index shifting issues
            for idx in range(self._tabs.count() - 1, -1, -1):
                self._tabs.removeTab(idx)
            
            # Add all tabs back with fresh data
            for idx, widget, label in tab_configs:
                try:
                    self._tabs.addTab(widget, label)
                except Exception as e:
                    print(f"[ERROR] Failed to refresh tab {label}: {str(e)}")
            
            # Restore to same tab if it still exists
            if current_idx < self._tabs.count():
                self._tabs.setCurrentIndex(current_idx)
        except Exception as e:
            print(f"[ERROR] Failed to refresh on period change: {str(e)}")
            import traceback
            traceback.print_exc()
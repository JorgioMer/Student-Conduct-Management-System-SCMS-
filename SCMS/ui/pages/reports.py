# =============================================================================
#  SCMS — Reports Page
# =============================================================================
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
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


class ReportsPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

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
        export_all.clicked.connect(lambda: InfoDialog(
            "Export",
            "All reports have been prepared for export.\n(Backend export will be implemented in final system.)",
            parent=self).exec_())
        h_lay.addWidget(export_all)
        self.main_layout.addWidget(header)

        # Period selector
        period_row = QHBoxLayout()
        period_lbl = QLabel("Report Period:")
        period_lbl.setStyleSheet("border: none; background: transparent;")
        period_row.addWidget(period_lbl)
        self.period_cb = QComboBox()
        self.period_cb.addItems([
            "November 2024",
            "October 2024",
            "September 2024",
            "1st Semester S.Y. 2024–2025",
            "S.Y. 2024–2025 (Full Year)",
        ])
        self.period_cb.setFixedHeight(38)
        self.period_cb.setFixedWidth(280)
        period_row.addWidget(self.period_cb)
        period_row.addStretch()

        print_btn = QPushButton("🖨  Print Preview")
        print_btn.setStyleSheet(btn_outline())
        print_btn.setFixedHeight(38)
        period_row.addWidget(print_btn)
        self.main_layout.addLayout(period_row)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_overview_tab(),  "   Overview ")
        tabs.addTab(self._build_green_report(),  "   Green Slips ")
        tabs.addTab(self._build_pink_report(),   "   Pink Slips ")
        tabs.addTab(self._build_blue_report(),   "   Blue Slips ")
        tabs.addTab(self._build_toplist_tab(),   "   Student Records ")

        self.main_layout.addWidget(tabs)
        self.main_layout.addStretch()

    # ── Overview ──────────────────────────────────────────────────────────────
    def _build_overview_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {WHITE};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(18)

        lay.addWidget(SectionTitle("Monthly Overview — November 2024"))

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
        slip_dist_layout.addWidget(slip_dist_chart)
        charts_row.addWidget(slip_dist_frame)

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
        year_breakdown_layout.addWidget(year_breakdown_chart)
        charts_row.addWidget(year_breakdown_frame)

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
        student_slips_layout.addWidget(student_slips_chart)
        charts_row.addWidget(student_slips_frame)

        lay.addLayout(charts_row)
        lay.addStretch()
        return w

    # ── Green Slip Report ─────────────────────────────────────────────────────
    def _build_green_report(self) -> QWidget:
        from backend.db_green_slip import get_green_slips

        green_records = get_green_slips(None) or []
        rows = []
        for record in green_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                slip_type = "Dispensation" if (record[5] == False if len(record) > 5 else False) else "Excuse"
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

        pink_records = get_pink_slips(None) or []
        rows = []
        for record in pink_records[:5]:
            try:
                stud_name = record[0] if len(record) > 0 else "Unknown"
                stud_num  = record[4] if len(record) > 4 else "N/A"
                year      = record[2] if len(record) > 2 else "N/A"
                violation = record[6] if len(record) > 6 else "N/A"
                date      = str(record[5])[:10] if len(record) > 5 else "N/A"
                action    = record[7] if len(record) > 7 else "N/A"
                rows.append((stud_num, stud_name, year, violation, date, action, "Done"))
            except:
                pass

        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]

        return self._build_slip_report_tab(
            "pink", "Pink Slip Monthly Report",
            "Penalty slips issued this month (one per student per semester)",
            PINK_SLIP, "#FCE4EC",
            ["Student No.", "Student Name", "Year", "Violation", "Date Issued", "Action Taken", "Status"],
            rows
        )

    def _build_blue_report(self) -> QWidget:
        from backend.db_blue_slip import get_blue_slips

        blue_records = get_blue_slips(None) or []
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

        for label, style in [("   Export CSV", btn_outline()), ("   Print", btn_outline())]:
            b = QPushButton(label)
            b.setStyleSheet(style)
            b.setFixedHeight(36)
            b.clicked.connect(lambda _, lbl=label: InfoDialog(
                lbl.strip(), f"{lbl.strip()} action will be implemented in the final system.",
                parent=self).exec_())
            top_row.addWidget(b)
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
                stud_num = record[1] if len(record) > 1 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["green"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)

            for record in get_pink_slips(None) or []:
                stud_num = record[1] if len(record) > 1 else None
                if stud_num:
                    if stud_num not in student_counts:
                        student_counts[stud_num] = {"green": 0, "pink": 0, "blue": 0, "info": None}
                    student_counts[stud_num]["pink"] += 1
                    if not student_counts[stud_num]["info"]:
                        student_counts[stud_num]["info"] = get_student(stud_num)

            for record in get_blue_slips(None) or []:
                stud_num = record[1] if len(record) > 1 else None
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
        fig = Figure(figsize=(4, 3), dpi=90, facecolor='white', edgecolor='none')
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
        fig = Figure(figsize=(4, 3), dpi=90, facecolor='white', edgecolor='none')
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
        fig = Figure(figsize=(4, 3), dpi=90, facecolor='white', edgecolor='none')
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
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
        t_lbl = QLabel("   Reports & Analytics ")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")
        s_lbl = QLabel("Monthly summaries, visual graphs, and statistical records for all slip types")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet(f"color: rgba(255,255,255,0.65); background: transparent;")
        h_col.addWidget(t_lbl)
        h_col.addWidget(s_lbl)
        h_lay.addLayout(h_col)
        h_lay.addStretch()

        export_all = QPushButton("   Export All Reports ")
        export_all.setStyleSheet(btn_gold())
        export_all.setFixedHeight(38)
        export_all.clicked.connect(lambda: InfoDialog(
            "Export", "All reports have been prepared for export.\n(Backend export will be implemented in final system.)",
            parent=self).exec_())
        h_lay.addWidget(export_all)
        self.main_layout.addWidget(header)

        # Period selector
        period_row = QHBoxLayout()
        period_row.addWidget(QLabel("Report Period:"))
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
        tabs.addTab(self._build_overview_tab(),   "   Overview ")
        tabs.addTab(self._build_green_report(),   "   Green Slips ")
        tabs.addTab(self._build_pink_report(),    "   Pink Slips ")
        tabs.addTab(self._build_blue_report(),    "   Blue Slips ")
        tabs.addTab(self._build_toplist_tab(),    "   Student Records ")

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

        # Big stat tiles - calculate from real data
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
        students_involved = len(all_students)
        
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)
        for label, val, colour, icon in [
            ("Green Slips Issued",     str(green_count), GREEN_SLIP, ""),
            ("Pink Slips Issued",      str(pink_count), PINK_SLIP,  ""),
            ("Blue Slips / Violations",str(blue_count),  BLUE_SLIP,  ""),
            ("Total Records Filed",    str(total_records), NAVY,       ""),
            ("Students Involved",      str(students_involved), GOLD,       ""),
        ]:
            tile = StatTile(f"{icon}  {label}", val, colour)
            tiles_row.addWidget(tile)
        lay.addLayout(tiles_row)

        lay.addWidget(Divider())

        # Chart placeholder grid
        charts_label = QLabel("Visual Summary Charts")
        charts_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        charts_label.setStyleSheet(f"color: {NAVY}; background: transparent;")
        lay.addWidget(charts_label)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        for title, color, description in [
            ("Slip Distribution",    "#E8F5E9", "Pie chart showing the\nproportion of each slip type"),
            ("Daily Filing Trend",   "#E3F2FD", "Line chart showing records\nfiled per day this month"),
            ("Grade Level Breakdown","#FCE4EC", "Bar chart showing records\nby grade level"),
        ]:
            chart_card = QFrame()
            chart_card.setStyleSheet(f"""
                QFrame {{
                    background: {color};
                    border: 1.5px dashed {LIGHT_GRAY};
                    border-radius: 10px;
                }}
            """)
            c_lay = QVBoxLayout(chart_card)
            c_lay.setAlignment(Qt.AlignCenter)
            c_lay.setContentsMargins(14, 14, 14, 14)

            icon_lbl = QLabel("📊")
            icon_lbl.setFont(QFont("Segoe UI", 32))
            icon_lbl.setAlignment(Qt.AlignCenter)
            icon_lbl.setStyleSheet("background: transparent;")

            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
            t_lbl.setAlignment(Qt.AlignCenter)
            t_lbl.setStyleSheet(f"color: {NAVY}; background: transparent;")

            d_lbl = QLabel(description)
            d_lbl.setFont(QFont("Segoe UI", 10))
            d_lbl.setAlignment(Qt.AlignCenter)
            d_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")

            c_lay.addWidget(icon_lbl)
            c_lay.addWidget(t_lbl)
            c_lay.addWidget(d_lbl)
            charts_row.addWidget(chart_card)

        lay.addLayout(charts_row)
        lay.addStretch()
        return w

    # ── Green Slip Report ─────────────────────────────────────────────────────
    def _build_green_report(self) -> QWidget:
        from backend.db_green_slip import get_green_slips
        from backend.db_students import get_student
        
        # Fetch real green slip records
        green_records = get_green_slips(None) or []
        rows = []
        for record in green_records[:5]:  # Limit to 5
            try:
                stud_num = record[1] if len(record) > 1 else "N/A"
                stud_info = get_student(stud_num)
                stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                grade = stud_info[3] if stud_info and len(stud_info) > 3 else "N/A"
                is_disp = record[2] if len(record) > 2 else False
                slip_type = "Dispensation" if is_disp else "Excuse"
                date = str(record[3])[:10] if len(record) > 3 else "N/A"
                days_reason = str(record[4]) if len(record) > 4 else "N/A"
                status = record[5] if len(record) > 5 else "Active"
                rows.append((stud_num, stud_name, grade, slip_type, date, days_reason, status))
            except:
                pass
        
        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]
        
        return self._build_slip_report_tab(
            "green", "Green Slip Monthly Report",
            "Dispensation and Excuse slips issued this month",
            GREEN_SLIP, "#E8F5E9",
            ["Student No.", "Student Name", "Grade", "Type", "Date", "Days/Reason", "Status"],
            rows
        )

    def _build_pink_report(self) -> QWidget:
        from backend.db_pink_slip import get_pink_slips
        from backend.db_students import get_student
        
        # Fetch real pink slip records
        pink_records = get_pink_slips(None) or []
        rows = []
        for record in pink_records[:5]:  # Limit to 5
            try:
                stud_num = record[1] if len(record) > 1 else "N/A"
                stud_info = get_student(stud_num)
                stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                grade = stud_info[3] if stud_info and len(stud_info) > 3 else "N/A"
                violation = record[3] if len(record) > 3 else "N/A"
                date = str(record[2])[:10] if len(record) > 2 else "N/A"
                action = record[4] if len(record) > 4 else "N/A"
                status = "Done"  # Pink slips are typically completed
                rows.append((stud_num, stud_name, grade, violation, date, action, status))
            except:
                pass
        
        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]
        
        return self._build_slip_report_tab(
            "pink", "Pink Slip Monthly Report",
            "Penalty slips issued this month (one per student per semester)",
            PINK_SLIP, "#FCE4EC",
            ["Student No.", "Student Name", "Grade", "Violation", "Date Issued", "Action Taken", "Status"],
            rows
        )

    def _build_blue_report(self) -> QWidget:
        from backend.db_blue_slip import get_blue_slips
        from backend.db_students import get_student
        
        # Fetch real blue slip records
        blue_records = get_blue_slips(None) or []
        rows = []
        for record in blue_records[:5]:  # Limit to 5
            try:
                stud_num = record[1] if len(record) > 1 else "N/A"
                stud_info = get_student(stud_num)
                stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                grade = stud_info[3] if stud_info and len(stud_info) > 3 else "N/A"
                violation = record[2] if len(record) > 2 else "N/A"
                severity = record[5] if len(record) > 5 else "N/A"
                date = str(record[3])[:10] if len(record) > 3 else "N/A"
                status = record[7] if len(record) > 7 else "Open"
                rows.append((stud_num, stud_name, grade, violation, severity, date, status))
            except:
                pass
        
        if not rows:
            rows = [("No records", "Add records to see them here", "-", "-", "-", "-", "-")]
        
        return self._build_slip_report_tab(
            "blue", "Blue Slip Monthly Report",
            "Violation records and disciplinary actions taken this month",
            BLUE_SLIP, "#E3F2FD",
            ["Student No.", "Student Name", "Grade", "Violation", "Severity", "Date", "Status"],
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
        t_lbl.setStyleSheet(f"color: {colour}; background: transparent;")
        top_row.addWidget(t_lbl)
        top_row.addStretch()

        for label, style in [("   Export CSV", btn_outline()), ("   Print", btn_outline())]:
            b = QPushButton(label)
            b.setStyleSheet(style)
            b.setFixedHeight(36)
            b.clicked.connect(lambda _, lbl=label: InfoDialog(
                lbl.replace("  ", " "), f"{lbl} action will be implemented in the final system.",
                parent=self).exec_())
            top_row.addWidget(b)
        lay.addLayout(top_row)

        sub = QLabel(subtitle)
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
        lay.addWidget(sub)

        t = build_record_table(headers, rows)
        t.setMinimumHeight(250)
        lay.addWidget(t)

        # Summary info bar
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
        total_lbl.setStyleSheet(f"color: {colour}; background: transparent;")
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

        headers = ["Rank", "Student No.", "Student Name", "Grade",
                   "Green Slips", "Pink Slips", "Blue Slips", "Total"]
        
        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        from backend.db_students import get_student
        
        # Count records by student
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
        
        # Sort by total slips
        sorted_students = sorted(student_counts.items(), 
                               key=lambda x: x[1]["green"] + x[1]["pink"] + x[1]["blue"], 
                               reverse=True)
        
        sample = []
        for rank, (stud_num, counts) in enumerate(sorted_students[:8], 1):
            try:
                info = counts["info"]
                stud_name = info[1] if info and len(info) > 1 else "Unknown"
                grade = info[3] if info and len(info) > 3 else "N/A"
                total = counts["green"] + counts["pink"] + counts["blue"]
                sample.append((str(rank), stud_num, stud_name, grade, 
                             str(counts["green"]), str(counts["pink"]), str(counts["blue"]), str(total)))
            except:
                pass
        
        if not sample:
            sample = [("1", "No records", "Add records to see them here", "-", "0", "0", "0", "0")]
        
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

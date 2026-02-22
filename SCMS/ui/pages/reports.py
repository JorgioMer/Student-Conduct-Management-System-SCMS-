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
        t_lbl = QLabel("📊  Reports & Analytics")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")
        s_lbl = QLabel("Monthly summaries, visual graphs, and statistical records for all slip types")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet(f"color: rgba(255,255,255,0.65); background: transparent;")
        h_col.addWidget(t_lbl)
        h_col.addWidget(s_lbl)
        h_lay.addLayout(h_col)
        h_lay.addStretch()

        export_all = QPushButton("📤  Export All Reports")
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
        tabs.addTab(self._build_overview_tab(),   "📈  Overview")
        tabs.addTab(self._build_green_report(),   "📗  Green Slips")
        tabs.addTab(self._build_pink_report(),    "📕  Pink Slips")
        tabs.addTab(self._build_blue_report(),    "📘  Blue Slips")
        tabs.addTab(self._build_toplist_tab(),    "⭐  Student Records")

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

        # Big stat tiles
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)
        for label, val, colour, icon in [
            ("Green Slips Issued",     "24", GREEN_SLIP, "📗"),
            ("Pink Slips Issued",      "11", PINK_SLIP,  "📕"),
            ("Blue Slips / Violations","8",  BLUE_SLIP,  "📘"),
            ("Total Records Filed",    "43", NAVY,       "📋"),
            ("Students Involved",      "38", GOLD,       "🧑‍🎓"),
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
        return self._build_slip_report_tab(
            "green", "Green Slip Monthly Report",
            "Dispensation and Excuse slips issued this month",
            GREEN_SLIP, "#E8F5E9",
            ["Student No.", "Student Name", "Grade", "Type", "Date", "Days/Reason", "Status"],
            [
                ("2024-0001", "Dela Cruz, Juan", "Gr.9", "Dispensation", "Nov 20", "2 days", "Active"),
                ("2024-0078", "Lim, Angela C.",  "Gr.8", "Excuse",       "Nov 17", "Medical","Done"),
                ("2024-0200", "Torres, Liza F.", "Gr.11","Dispensation", "Nov 14", "1 day",  "Active"),
                ("2024-0212", "Flores, Anna M.", "Gr.7", "Excuse",       "Nov 12", "Family", "Done"),
                ("2024-0305", "Ocampo, Jose R.", "Gr.10","Dispensation", "Nov 8",  "3 days", "Expired"),
            ]
        )

    def _build_pink_report(self) -> QWidget:
        return self._build_slip_report_tab(
            "pink", "Pink Slip Monthly Report",
            "Penalty slips issued this month (one per student per semester)",
            PINK_SLIP, "#FCE4EC",
            ["Student No.", "Student Name", "Grade", "Violation", "Date Issued", "Action Taken", "Status"],
            [
                ("2024-0033", "Garcia, Paolo B.",  "Gr.11", "Uniform",   "Nov 15", "Warning",        "Done"),
                ("2024-0112", "Reyes, Carlo L.",   "Gr.9",  "Tardiness", "Nov 10", "Parent Notif.",   "Done"),
                ("2024-0256", "Aquino, Diana P.",  "Gr.10", "Misconduct","Oct 25", "Community Svc.",  "Done"),
            ]
        )

    def _build_blue_report(self) -> QWidget:
        return self._build_slip_report_tab(
            "blue", "Blue Slip Monthly Report",
            "Violation records and disciplinary actions taken this month",
            BLUE_SLIP, "#E3F2FD",
            ["Student No.", "Student Name", "Grade", "Violation", "Severity", "Date", "Status"],
            [
                ("2024-0045", "Santos, Maria R.",  "Gr.10", "Bullying",         "Level 3", "Nov 19", "Pending"),
                ("2024-0033", "Garcia, Paolo B.",  "Gr.11", "Skipping Class",   "Level 1", "Nov 15", "Resolved"),
                ("2024-0199", "Mendoza, Lara K.",  "Gr.9",  "Disrespect",       "Level 2", "Nov 12", "Done"),
                ("2024-0310", "Villanueva, R. A.", "Gr.12", "Cheating",         "Level 3", "Nov 8",  "Escalated"),
            ]
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

        for label, style in [("📤  Export CSV", btn_outline()), ("🖨  Print", btn_outline())]:
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
        sample = [
            ("1", "2024-0045", "Santos, Maria R.",    "Grade 10", "1", "0", "1", "2"),
            ("2", "2024-0033", "Garcia, Paolo B.",    "Grade 11", "0", "1", "1", "2"),
            ("3", "2024-0001", "Dela Cruz, Juan M.",  "Grade 9",  "2", "0", "0", "2"),
            ("4", "2024-0310", "Villanueva, R. A.",   "Grade 12", "0", "0", "1", "1"),
            ("5", "2024-0112", "Reyes, Carlo L.",     "Grade 9",  "0", "1", "0", "1"),
            ("6", "2024-0199", "Mendoza, Lara K.",    "Grade 9",  "0", "0", "1", "1"),
            ("7", "2024-0078", "Lim, Angela C.",      "Grade 8",  "1", "0", "0", "1"),
            ("8", "2024-0200", "Torres, Liza F.",     "Grade 11", "1", "0", "0", "1"),
        ]

        t = build_record_table(headers, sample)
        t.setMinimumHeight(300)
        lay.addWidget(t)

        note = QLabel(
            "ℹ  This list helps the Office of the Prefect identify students who may need additional "
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

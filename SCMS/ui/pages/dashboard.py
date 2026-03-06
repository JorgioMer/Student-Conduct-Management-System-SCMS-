# =============================================================================
#  SCMS — Dashboard Page
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import qtawesome as qta  # pip install qtawesome

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, TEXT_DARK,
    GREEN_SLIP, PINK_SLIP, BLUE_SLIP,
    btn_primary, btn_outline
)
from ui.components import (
    SectionTitle, SubTitle, Divider, StatTile,
    SlipCard, Card, add_shadow
)


# ---------------------------------------------------------------------------
# Helper — creates a QLabel that renders a qtawesome icon as a pixmap
# ---------------------------------------------------------------------------
def _icon_label(fa_name: str, size: int = 22, color: str = WHITE) -> QLabel:
    """Return a QLabel showing the requested Font Awesome icon."""
    lbl = QLabel()
    lbl.setPixmap(qta.icon(fa_name, color=color).pixmap(size, size))
    lbl.setStyleSheet("background: transparent;")
    lbl.setAlignment(Qt.AlignCenter)
    return lbl


class DashboardPage(QWidget):
    navigate_to = pyqtSignal(int)   # emits page index

    def __init__(self, role: str = "Admin", parent=None):
        super().__init__(parent)
        self.role = role
        self.setStyleSheet(f"background: {OFF_WHITE};")
        self._build()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {OFF_WHITE};")
        scroll.setWidget(content)

        main = QVBoxLayout(content)
        main.setContentsMargins(36, 30, 36, 30)
        main.setSpacing(28)

        # ── Hero banner ───────────────────────────────────────────────────────
        banner = QFrame()
        banner.setObjectName("Banner")
        banner.setFixedHeight(110)
        banner.setStyleSheet(f"""
            QFrame#Banner {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {NAVY_DARK}, stop:0.6 {NAVY}, stop:1 #2E4070
                );
                border-radius: 14px;
                border-left: 6px solid {GOLD};
            }}
        """)
        add_shadow(banner, blur=20, y=5, color=(0, 0, 0, 35))

        banner_lay = QHBoxLayout(banner)
        banner_lay.setContentsMargins(28, 16, 28, 16)

        # --- Left text block --------------------------------------------------
        banner_text = QVBoxLayout()
        banner_text.setSpacing(4)
        today = QDate.currentDate().toString("dddd, MMMM d, yyyy")

        # Greeting row with icon
        greeting_row = QHBoxLayout()
        greeting_row.setSpacing(8)
        greeting_row.setContentsMargins(0, 0, 0, 0)
        home_icon = _icon_label("fa5s.home", size=18, color=GOLD)
        greeting = QLabel("Good day — Welcome to the Office of the Prefect")
        greeting.setFont(QFont("Segoe UI", 16, QFont.Bold))
        greeting.setStyleSheet(f"color: {WHITE}; background: transparent;")
        greeting_row.addWidget(home_icon)
        greeting_row.addWidget(greeting)
        greeting_row.addStretch()

        # Date row: calendar icon + date string
        date_row = QHBoxLayout()
        date_row.setSpacing(6)
        date_row.setContentsMargins(0, 0, 0, 0)
        cal_icon = _icon_label("fa5s.calendar-alt", size=16, color=GOLD)
        date_lbl = QLabel(today)
        date_lbl.setFont(QFont("Segoe UI", 11))
        date_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")
        date_row.addWidget(cal_icon)
        date_row.addWidget(date_lbl)
        date_row.addStretch()

        banner_text.addLayout(greeting_row)
        banner_text.addLayout(date_row)

    
        banner_lay.addLayout(banner_text, 1)
        main.addWidget(banner)

        # ── Stat tiles row ────────────────────────────────────────────────────
        # Section title with chart-bar icon
        main.addWidget(_make_section_title("fa5s.chart-bar", "This Month's Summary"))

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
        pending_blue = sum(1 for r in blue_slips if len(r) > 7 and "Pending" in str(r[7]))
        
        # Count unique students across all slips
        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            if len(r) > 1:
                all_students.add(r[1])
        active_students = len(all_students)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)

        tiles_data = [
            ("Green Slips Issued",     str(green_count), GREEN_SLIP),
            ("Pink Slips Issued",      str(pink_count), PINK_SLIP),
            ("Blue Slips Issued",      str(blue_count),  BLUE_SLIP),
            ("Pending Blue Slips",     str(pending_blue),  BLUE_SLIP),
            ("Active Students Tracked",str(active_students), NAVY),
        ]
        for lbl, val, col in tiles_data:
            tile = StatTile(lbl, val, col)
            tiles_row.addWidget(tile)

        main.addLayout(tiles_row)
        main.addWidget(Divider())

        # ── Quick access cards ────────────────────────────────────────────────
        main.addWidget(_make_section_title("fa5s.folder-open", "Quick Access"))
        main.addWidget(_make_subtitle("fa5s.arrow-circle-right", "Select a slip type or function to get started"))

        cards_grid = QGridLayout()
        cards_grid.setSpacing(18)

        # Icon names map to Font Awesome 5 Solid
        cards_info = [
            ("green", "Green Slip",      "Dispensation\n& Excuse Records",    "fa5s.file-alt",      1),
            ("pink",  "Pink Slip",       "Penalty Slip\nRecord (Once/Sem.)",  "fa5s.file-invoice",      2),
            ("blue",  "Blue Slip",       "Violation &\nDisciplinary Record",  "fa5s.file-alt",          3),
            ("gold",  "Record Trackers", "Monitor all\nslip records",         "fa5s.list-alt",          4),
            ("gold",  "Reports",         "Monthly Summary\n& Visual Charts",  "fa5s.chart-pie",         5),
            ("gold",  "Settings",        "Manage Users\n& System Config",     "fa5s.cogs",              6),
        ]

        for i, (color, title, desc, fa_icon, page_idx) in enumerate(cards_info):
            card = SlipCard(color, title, desc, fa_icon)   # pass fa_icon name
            card.clicked.connect(lambda idx=page_idx: self.navigate_to.emit(idx))
            row, col = divmod(i, 3)
            cards_grid.addWidget(card, row, col)

        main.addLayout(cards_grid)
        main.addWidget(Divider())

        # ── Recent activity table ─────────────────────────────────────────────
        main.addWidget(_make_section_title("fa5s.history", "Recent Activity"))
        main.addWidget(_make_subtitle("fa5s.clipboard-list", "Latest slip records entered into the system"))

        table = QTableWidget(6, 5)
        table.setHorizontalHeaderLabels(
            ["Student No.", "Student Name", "Slip Type", "Date Filed", "Status"]
        )
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(f"""
            QTableWidget {{
                alternate-background-color: #F0F4FF;
                background: {WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setFixedHeight(220)

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips
        from backend.db_students import get_student
        
        # Fetch recent records from database
        all_records = []
        
        try:
            # Get blue slips
            blue_records = get_blue_slips(None) if hasattr(get_blue_slips, '__call__') else []
            for record in blue_records[:10]:  # Limit to 10
                all_records.append(('blue', record))
            
            # Get green slips
            green_records = get_green_slips(None) if hasattr(get_green_slips, '__call__') else []
            for record in green_records[:10]:
                all_records.append(('green', record))
            
            # Get pink slips
            pink_records = get_pink_slips(None) if hasattr(get_pink_slips, '__call__') else []
            for record in pink_records[:10]:
                all_records.append(('pink', record))
        except:
            all_records = []
        
        if not all_records:
            # Show empty state message
            empty_msg = QLabel("No records found. Start by adding slips to see them here.")
            empty_msg.setAlignment(Qt.AlignCenter)
            empty_msg.setStyleSheet(f"color: {MID_GRAY}; padding: 40px;")
            main.addWidget(empty_msg)
        else:
            # Build table from actual records
            for r, (slip_type, record) in enumerate(all_records[:6]):
                if r >= 6:
                    break
                try:
                    if slip_type == 'blue':
                        stud_num = record[1] if len(record) > 1 else "N/A"
                        stud_info = get_student(stud_num)
                        stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                        slip_label = "Blue Slip"
                        status = record[6] if len(record) > 6 else "Open / Pending"
                        date = str(record[3]) if len(record) > 3 else "N/A"
                    elif slip_type == 'green':
                        stud_num = record[1] if len(record) > 1 else "N/A"
                        stud_info = get_student(stud_num)
                        stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                        is_disp = record[2] if len(record) > 2 else False
                        slip_label = "Green (Dispensation)" if is_disp else "Green (Excuse)"
                        status = record[5] if len(record) > 5 else "Active"
                        date = str(record[3]) if len(record) > 3 else "N/A"
                    else:  # pink
                        stud_num = record[1] if len(record) > 1 else "N/A"
                        stud_info = get_student(stud_num)
                        stud_name = stud_info[1] if stud_info and len(stud_info) > 1 else "Unknown"
                        slip_label = "Pink Slip"
                        status = "Completed"
                        date = str(record[2]) if len(record) > 2 else "N/A"
                    
                    row_data = (stud_num, stud_name, slip_label, date[:10] if len(date) > 10 else date, status)
                    for c, val in enumerate(row_data):
                        item = QTableWidgetItem(val)
                        item.setTextAlignment(Qt.AlignCenter)
                        if c == 2:
                            if "Green" in val:
                                item.setForeground(QColor(GREEN_SLIP))
                            elif "Pink" in val:
                                item.setForeground(QColor(PINK_SLIP))
                            elif "Blue" in val:
                                item.setForeground(QColor(BLUE_SLIP))
                        if c == 4:
                            STATUS_COLORS = {
                                "Active":    ("#D4EDDA", "#155724"),
                                "Pending":   ("#FFF3CD", "#856404"),
                                "Completed": ("#CCE5FF", "#004085"),
                                "Resolved":  ("#D1ECF1", "#0C5460"),
                                "Open / Pending": ("#F8D7DA", "#721C24"),
                            }
                            bg, fg = STATUS_COLORS.get(val, ("#eee", "#333"))
                            item.setBackground(QColor(bg))
                            item.setForeground(QColor(fg))
                        table.setItem(r, c, item)
                except Exception as e:
                    pass

        main.addWidget(table)
        main.addStretch()


# ---------------------------------------------------------------------------
# Helper — section title row with a leading qtawesome icon
# ---------------------------------------------------------------------------
def _make_section_title(fa_icon_name: str, text: str) -> QWidget:
    """Returns a row widget with an icon + bold section label."""
    row = QWidget()
    row.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    icon_lbl = QLabel()
    icon_lbl.setPixmap(qta.icon(fa_icon_name, color=NAVY).pixmap(20, 20))
    icon_lbl.setStyleSheet("background: transparent;")

    title_lbl = QLabel(text)
    title_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
    title_lbl.setStyleSheet(f"color: {NAVY}; background: transparent;")

    lay.addWidget(icon_lbl)
    lay.addWidget(title_lbl)
    lay.addStretch()
    return row


# ---------------------------------------------------------------------------
# Helper — subtitle row with a leading qtawesome icon
# ---------------------------------------------------------------------------
def _make_subtitle(fa_icon_name: str, text: str) -> QWidget:
    """Returns a row widget with an icon + subtitle label."""
    row = QWidget()
    row.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    icon_lbl = QLabel()
    icon_lbl.setPixmap(qta.icon(fa_icon_name, color=MID_GRAY).pixmap(16, 16))
    icon_lbl.setStyleSheet("background: transparent;")

    subtitle_lbl = QLabel(text)
    subtitle_lbl.setFont(QFont("Segoe UI", 11))
    subtitle_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")

    lay.addWidget(icon_lbl)
    lay.addWidget(subtitle_lbl)
    lay.addStretch()
    return row
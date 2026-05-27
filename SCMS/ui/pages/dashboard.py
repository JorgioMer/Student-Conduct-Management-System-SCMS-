# =============================================================================
#  SCMS — Dashboard Page
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
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
from ui.data_events import data_events

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_green_slip import check_and_update_expired_green_slips


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

        # Month tracking for auto-refresh
        today = QDate.currentDate()
        self.current_month = today.month()
        self.current_year = today.year()
        self.main_layout = None
        self.scroll_widget = None

        # Timer to check for month changes (every minute)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._check_month_change)
        self.refresh_timer.start(60000)

        # Connect to slip data changes for instant refresh
        data_events.slips_changed.connect(self._on_slips_changed)

        self._build()

    def _check_month_change(self):
        """Check if the month has changed and refresh dashboard if needed"""
        today = QDate.currentDate()
        if today.month() != self.current_month or today.year() != self.current_year:
            self.current_month = today.month()
            self.current_year = today.year()
            self._refresh_dashboard()

    def _on_slips_changed(self):
        """Refresh dashboard when slips data changes - called whenever a slip is added."""
        try:
            self._refresh_dashboard()
        except Exception as e:
            print(f"[ERROR] Failed to refresh dashboard on slip change: {str(e)}")

    def closeEvent(self, event):
        """Clean up signal connections when page is closed"""
        try:
            data_events.slips_changed.disconnect(self._on_slips_changed)
        except Exception:
            pass
        if self.refresh_timer:
            self.refresh_timer.stop()
        super().closeEvent(event)

    def showEvent(self, event):
        """Refresh dashboard whenever the page is shown (tab clicked)"""
        super().showEvent(event)
        try:
            self._refresh_dashboard()
        except Exception as e:
            print(f"[ERROR] Failed to refresh dashboard on show: {str(e)}")

    def _refresh_dashboard(self):
        """Refresh dashboard data (called on month change or data change)"""
        parent = self
        parent.setStyleSheet(f"background: {OFF_WHITE};")

        # Clear existing layout
        if self.main_layout is not None:
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        self._build()

    def _build(self):
        # First, check and update any expired green slips
        try:
            check_and_update_expired_green_slips()
        except Exception as e:
            print(f"[WARNING] Failed to check for expired green slips: {str(e)}")

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
        main.addWidget(_make_section_title("fa5s.chart-bar", "This Month's Summary"))

        from backend.db_blue_slip import get_blue_slips
        from backend.db_green_slip import get_green_slips
        from backend.db_pink_slip import get_pink_slips

        green_slips = get_green_slips(None) or []
        pink_slips  = get_pink_slips(None)  or []
        blue_slips  = get_blue_slips(None)  or []

        green_count   = len(green_slips)
        pink_count    = len(pink_slips)
        blue_count    = len(blue_slips)
        # Blue: status is at index 8 (confirmed from debug output)
        pending_blue  = sum(1 for r in blue_slips if r and len(r) > 8 and "Pending" in str(r[8]))

        all_students = set()
        for r in green_slips + pink_slips + blue_slips:
            # studNumber is at index 1 for all slip types (confirmed from debug output)
            if r and len(r) > 1 and r[1]:
                all_students.add(str(r[1]))
        active_students = len(all_students)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)

        tiles_data = [
            ("Green Slips Issued",      str(green_count),    GREEN_SLIP),
            ("Pink Slips Issued",       str(pink_count),     PINK_SLIP),
            ("Blue Slips Issued",       str(blue_count),     BLUE_SLIP),
            ("Pending Blue Slips",      str(pending_blue),   BLUE_SLIP),
            ("Active Students Tracked", str(active_students), NAVY),
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

        cards_info = [
            ("green", "Green Slip",      "Dispensation\n& Excuse Records",   "fa5s.file-alt",     1),
            ("pink",  "Pink Slip",       "Penalty Slip\nRecord (Once/Sem.)", "fa5s.file-invoice", 2),
            ("blue",  "Blue Slip",       "Violation &\nDisciplinary Record", "fa5s.file-alt",     3),
            ("gold",  "Record Trackers", "Monitor all\nslip records",        "fa5s.list-alt",     4),
            ("gold",  "Reports",         "Monthly Summary\n& Visual Charts", "fa5s.chart-pie",    5),
            ("gold",  "Settings",        "Manage Users\n& System Config",    "fa5s.cogs",         6),
        ]

        for i, (color, title, desc, fa_icon, page_idx) in enumerate(cards_info):
            card = SlipCard(color, title, desc, fa_icon)
            card.clicked.connect(lambda idx=page_idx: self.navigate_to.emit(idx))
            row, col = divmod(i, 3)
            cards_grid.addWidget(card, row, col)

        main.addLayout(cards_grid)
        main.addWidget(Divider())

        # ── Recent activity table ─────────────────────────────────────────────
        main.addWidget(_make_section_title("fa5s.history", "Recent Activity"))
        main.addWidget(_make_subtitle("fa5s.clipboard-list", "Latest slip records entered into the system"))

        from datetime import datetime

        all_records = []

        try:
            for record in (get_blue_slips(None) or []):
                all_records.append(('blue', record))
            for record in (get_green_slips(None) or []):
                all_records.append(('green', record))
            for record in (get_pink_slips(None) or []):
                all_records.append(('pink', record))
        except Exception as e:
            print(f"[ERROR] Failed to load records for Recent Activity: {e}")
            all_records = []

        def get_record_date(slip_data):
            slip_type, record = slip_data
            try:
                # date is at index 6 for blue/green, index 5 for pink
                if slip_type in ('blue', 'green'):
                    date_str = str(record[6]) if len(record) > 6 else "1900-01-01"
                else:  # pink
                    date_str = str(record[5]) if len(record) > 5 else "1900-01-01"
                return datetime.strptime(date_str[:10], "%Y-%m-%d")
            except Exception:
                return datetime(1900, 1, 1)

        try:
            all_records.sort(key=get_record_date, reverse=True)
        except Exception:
            pass

        if not all_records:
            empty_msg = QLabel("No records found. Start by adding slips to see them here.")
            empty_msg.setAlignment(Qt.AlignCenter)
            empty_msg.setStyleSheet(f"color: {MID_GRAY}; padding: 40px;")
            main.addWidget(empty_msg)
        else:
            num_rows = min(6, len(all_records))

            table = QTableWidget(num_rows, 6)
            table.setHorizontalHeaderLabels(
                ["Student No.", "Student Name", "Slip Type", "Date Filed", "Filed By", "Status"]
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
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student No.
            header.setSectionResizeMode(1, QHeaderView.Stretch)           # Student Name
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Slip Type
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date Filed
            header.setSectionResizeMode(4, QHeaderView.Stretch)           # Filed By
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
            table.setWordWrap(False)
            table.setFixedHeight(max(200, 36 * (num_rows + 1)))
            table.verticalHeader().setDefaultSectionSize(36)

            STATUS_COLORS = {
                "Active":         ("#D4EDDA", "#155724"),
                "Pending":        ("#FFF3CD", "#856404"),
                "Completed":      ("#CCE5FF", "#004085"),
                "Resolved":       ("#D1ECF1", "#0C5460"),
                "Open / Pending": ("#F8D7DA", "#721C24"),
            }

            for r, (slip_type, record) in enumerate(all_records[:6]):
                try:
                    # Actual DB column order (confirmed from debug output):
                    # Pink:  (ID[0], studNum[1], studName[2], year[3], course[4], date[5],
                    #          violation[6], action[7], officer[8], semester[9])
                    # Blue:  (ID[0], studNum[1], studName[2], year[3], course[4],
                    #          violationType[5], date[6], action[7], status[8])
                    # Green: (ID[0], studNum[1], studName[2], year[3], course[4],
                    #          is_disp[5], date[6], days[7], expiry[8], status[9], authorizedBy[10])

                    stud_num  = str(record[1]) if len(record) > 1 else "N/A"
                    stud_name = str(record[2]) if len(record) > 2 else "Unknown"

                    if slip_type == 'blue':
                        slip_label = "Blue Slip"
                        date       = str(record[6])[:10] if len(record) > 6 else "N/A"
                        status     = str(record[8])      if len(record) > 8 else "Open / Pending"
                        filed_by   = "—"  # no officer column in blue slip DB result

                    elif slip_type == 'green':
                        is_disp    = record[5] is True   if len(record) > 5 else False
                        slip_label = "Green (Dispensation)" if is_disp else "Green (Excuse)"
                        date       = str(record[6])[:10] if len(record) > 6 else "N/A"
                        status     = str(record[9])      if len(record) > 9 else "Active"
                        filed_by   = str(record[10])     if len(record) > 10 and record[10] else "—"

                    else:  # pink
                        slip_label = "Pink Slip"
                        date       = str(record[5])[:10] if len(record) > 5 else "N/A"
                        status     = "Completed"
                        filed_by   = str(record[8])      if len(record) > 8 and record[8] else "—"

                    # Normalise filed_by
                    if not filed_by or filed_by.strip() in ("", "None"):
                        filed_by = "—"
                    else:
                        filed_by = filed_by.strip()

                    row_data = (stud_num, stud_name, slip_label, date, filed_by, status)
                    for c, val in enumerate(row_data):
                        item = QTableWidgetItem(str(val))
                        item.setTextAlignment(Qt.AlignCenter)

                        if c == 2:  # Slip Type colour
                            if "Green" in val:
                                item.setForeground(QColor(GREEN_SLIP))
                            elif "Pink" in val:
                                item.setForeground(QColor(PINK_SLIP))
                            elif "Blue" in val:
                                item.setForeground(QColor(BLUE_SLIP))

                        if c == 5:  # Status colour
                            bg, fg = STATUS_COLORS.get(val, ("#eee", "#333"))
                            item.setBackground(QColor(bg))
                            item.setForeground(QColor(fg))

                        table.setItem(r, c, item)

                except Exception as e:
                    print(f"[ERROR] Recent Activity row {r} ({slip_type}) failed: {e}")

            main.addWidget(table)

        main.addStretch()

    def closeEvent(self, event):
        """Clean up timer when dashboard is closed"""
        self.refresh_timer.stop()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Helper — section title row with a leading qtawesome icon
# ---------------------------------------------------------------------------
def _make_section_title(fa_icon_name: str, text: str) -> QWidget:
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
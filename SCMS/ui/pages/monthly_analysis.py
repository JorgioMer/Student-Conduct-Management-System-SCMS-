# =============================================================================
#  SCMS — Monthly Analysis Page (Auto-filtered by Current Month)
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QGridLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import qtawesome as qta
from datetime import datetime, timedelta

from ui.styles import (
    NAVY, GOLD, WHITE, OFF_WHITE, LIGHT_GRAY, MID_GRAY, TEXT_DARK,
    GREEN_SLIP, PINK_SLIP, BLUE_SLIP, btn_primary, btn_outline
)
from ui.components import (
    SectionTitle, SubTitle, Divider, StatTile, Card, add_shadow
)
from ui.pages.base_page import page_header, build_record_table

from backend.db_blue_slip import get_blue_slips
from backend.db_green_slip import get_green_slips
from backend.db_pink_slip import get_pink_slips


def _icon_label(fa_name: str, size: int = 22, color: str = WHITE) -> QLabel:
    """Return a QLabel showing the requested Font Awesome icon."""
    lbl = QLabel()
    lbl.setPixmap(qta.icon(fa_name, color=color).pixmap(size, size))
    lbl.setStyleSheet("background: transparent;")
    lbl.setAlignment(Qt.AlignCenter)
    return lbl


class MonthlyAnalysisPage(QWidget):
    """Monthly analysis page that auto-filters by current month."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {OFF_WHITE};")
        self.current_month = None
        self.current_year = None
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._check_month_change)
        self.refresh_timer.start(60000)  # Check every minute for month change
        self._build()
        self._load_data()
    
    def _build(self):
        """Build the UI"""
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        # Header
        main.addWidget(page_header(
            "gold",
            "  Monthly Analysis ",
            "Automatic monthly filtering and statistical analysis"
        ))
        
        # Scroll area for content
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {OFF_WHITE}; border: none;")
        
        content = QWidget()
        content.setStyleSheet(f"background: {OFF_WHITE};")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(28, 20, 28, 20)
        content_lay.setSpacing(24)
        
        # ── Month/Year Display & Controls ────────────────────────────────────
        month_bar = QFrame()
        month_bar.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        month_lay = QHBoxLayout(month_bar)
        month_lay.setContentsMargins(16, 16, 16, 16)
        month_lay.setSpacing(20)
        
        # Current month display
        self.month_label = QLabel()
        self.month_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.month_label.setStyleSheet(f"color: {NAVY};")
        month_lay.addWidget(self.month_label)
        
        month_lay.addStretch()
        
        # Month navigation buttons
        prev_btn = QPushButton("← Previous Month")
        prev_btn.setStyleSheet(btn_outline())
        prev_btn.setMaximumWidth(150)
        prev_btn.clicked.connect(self._show_previous_month)
        
        next_btn = QPushButton("Next Month →")
        next_btn.setStyleSheet(btn_outline())
        next_btn.setMaximumWidth(150)
        next_btn.clicked.connect(self._show_next_month)
        
        refresh_btn = QPushButton("↻ Refresh Current")
        refresh_btn.setStyleSheet(btn_primary())
        refresh_btn.setMaximumWidth(150)
        refresh_btn.clicked.connect(self._show_current_month)
        
        month_lay.addWidget(prev_btn)
        month_lay.addWidget(next_btn)
        month_lay.addWidget(refresh_btn)
        
        content_lay.addWidget(month_bar)
        
        # ── Monthly Stats Tiles ──────────────────────────────────────────────
        content_lay.addWidget(self._make_section_title("fa5s.chart-bar", "Monthly Summary"))
        
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(16)
        
        self.stat_tiles = {
            'green': StatTile("Green Slips", "0", GREEN_SLIP),
            'pink': StatTile("Pink Slips", "0", PINK_SLIP),
            'blue': StatTile("Blue Slips", "0", BLUE_SLIP),
            'pending': StatTile("Pending", "0", BLUE_SLIP),
            'students': StatTile("Active Students", "0", NAVY),
        }
        
        for tile in self.stat_tiles.values():
            tiles_layout.addWidget(tile)
        
        content_lay.addLayout(tiles_layout)
        content_lay.addWidget(Divider())
        
        # ── Monthly Records Table ────────────────────────────────────────────
        content_lay.addWidget(self._make_section_title("fa5s.table", "Monthly Records"))
        content_lay.addWidget(self._make_subtitle("fa5s.arrow-circle-right", "All slips filed this month"))
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(
            ["Student No.", "Name", "Slip Type", "Date", "Status", "Notes"]
        )
        self.records_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.records_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setStyleSheet(f"""
            QTableWidget {{
                alternate-background-color: #F0F4FF;
                background: {WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Student No.
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Slip Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Notes
        
        self.records_table.setMinimumHeight(400)
        self.records_table.setWordWrap(False)
        self.records_table.verticalHeader().setDefaultSectionSize(36)
        
        content_lay.addWidget(self.records_table)
        content_lay.addStretch()
        
        scroll.setWidget(content)
        main.addWidget(scroll)
    
    def _check_month_change(self):
        """Check if month has changed and refresh if needed"""
        today = QDate.currentDate()
        if self.current_month != today.month() or self.current_year != today.year():
            self._load_data()
    
    def _get_month_range(self, year, month):
        """Get first and last day of month as datetime objects"""
        from datetime import datetime, timedelta
        first_day = datetime(year, month, 1)
        # Last day of month
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        return first_day, last_day
    
    def _filter_records_by_date(self, records, start_date, end_date):
        """Filter records by date range"""
        filtered = []
        for record in records:
            try:
                # Try different date column positions
                date_str = None
                for col_idx in [5, 6, 7]:  # Try common date column indices
                    if len(record) > col_idx and record[col_idx]:
                        date_str = str(record[col_idx])[:10]
                        break
                
                if date_str:
                    try:
                        record_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if start_date <= record_date <= end_date:
                            filtered.append(record)
                    except:
                        pass
            except:
                pass
        
        return filtered
    
    def _show_current_month(self):
        """Show data for current month"""
        today = QDate.currentDate()
        self.current_month = today.month()
        self.current_year = today.year()
        self._load_data()
    
    def _show_previous_month(self):
        """Show data for previous month"""
        if self.current_month is None:
            today = QDate.currentDate()
            month = today.month() - 1
            year = today.year()
        else:
            month = self.current_month - 1
            year = self.current_year
        
        if month < 1:
            month = 12
            year -= 1
        
        self.current_month = month
        self.current_year = year
        self._load_data()
    
    def _show_next_month(self):
        """Show data for next month"""
        if self.current_month is None:
            today = QDate.currentDate()
            month = today.month() + 1
            year = today.year()
        else:
            month = self.current_month + 1
            year = self.current_year
        
        if month > 12:
            month = 1
            year += 1
        
        self.current_month = month
        self.current_year = year
        self._load_data()
    
    def _load_data(self):
        """Load and display data for the selected month"""
        if self.current_month is None or self.current_year is None:
            today = QDate.currentDate()
            self.current_month = today.month()
            self.current_year = today.year()
        
        # Update month label
        month_names = ["", "January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        self.month_label.setText(f"{month_names[self.current_month]} {self.current_year}")
        
        # Get date range
        start_date, end_date = self._get_month_range(self.current_year, self.current_month)
        
        # Get all slips
        green_slips = get_green_slips(None) or []
        pink_slips = get_pink_slips(None) or []
        blue_slips = get_blue_slips(None) or []
        
        # Filter by month
        green_month = self._filter_records_by_date(green_slips, start_date, end_date)
        pink_month = self._filter_records_by_date(pink_slips, start_date, end_date)
        blue_month = self._filter_records_by_date(blue_slips, start_date, end_date)
        
        # Calculate stats
        green_count = len(green_month)
        pink_count = len(pink_month)
        blue_count = len(blue_month)
        pending_blue = sum(1 for r in blue_month if r and len(r) > 7 and "Pending" in str(r[7]))
        
        all_students = set()
        for r in green_month + pink_month + blue_month:
            if r and len(r) > 1 and r[1]:
                all_students.add(str(r[1]))
        
        # Update tiles
        self.stat_tiles['green'].set_value(str(green_count))
        self.stat_tiles['pink'].set_value(str(pink_count))
        self.stat_tiles['blue'].set_value(str(blue_count))
        self.stat_tiles['pending'].set_value(str(pending_blue))
        self.stat_tiles['students'].set_value(str(len(all_students)))
        
        # Update table
        self._populate_records_table(green_month, pink_month, blue_month)
    
    def _populate_records_table(self, green_records, pink_records, blue_records):
        """Populate the records table"""
        all_records = []
        
        # Combine and tag records
        for r in green_records:
            all_records.append(('green', r))
        for r in pink_records:
            all_records.append(('pink', r))
        for r in blue_records:
            all_records.append(('blue', r))
        
        # Sort by date (descending)
        def get_date(item):
            slip_type, record = item
            try:
                if slip_type == 'blue':
                    date_str = str(record[6])[:10] if len(record) > 6 else "1900-01-01"
                elif slip_type == 'green':
                    date_str = str(record[6])[:10] if len(record) > 6 else "1900-01-01"
                else:  # pink
                    date_str = str(record[5])[:10] if len(record) > 5 else "1900-01-01"
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return datetime(1900, 1, 1)
        
        try:
            all_records.sort(key=get_date, reverse=True)
        except:
            pass
        
        # Clear and populate table
        self.records_table.setRowCount(len(all_records))
        
        for row_idx, (slip_type, record) in enumerate(all_records):
            try:
                # Extract data based on slip type
                if slip_type == 'blue':
                    stud_name = record[0] if len(record) > 0 else "Unknown"
                    stud_num = record[4] if len(record) > 4 else "N/A"
                    slip_label = "Blue Slip"
                    status = record[10] if len(record) > 10 else "Open / Pending"
                    date = str(record[6])[:10] if len(record) > 6 else "N/A"
                    notes = record[11] if len(record) > 11 else "—"
                
                elif slip_type == 'green':
                    stud_name = record[0] if len(record) > 0 else "Unknown"
                    stud_num = record[4] if len(record) > 4 else "N/A"
                    is_disp = record[5] == True if len(record) > 5 else False
                    slip_label = "Green (Disp.)" if is_disp else "Green (Excuse)"
                    status = record[8] if len(record) > 8 else "Active"
                    date = str(record[6])[:10] if len(record) > 6 else "N/A"
                    notes = record[10] if len(record) > 10 else "—"
                
                else:  # pink
                    stud_name = record[0] if len(record) > 0 else "Unknown"
                    stud_num = record[4] if len(record) > 4 else "N/A"
                    slip_label = "Pink Slip"
                    status = "Completed"
                    date = str(record[5])[:10] if len(record) > 5 else "N/A"
                    notes = record[8] if len(record) > 8 else "—"
                
                row_data = [stud_num, stud_name, slip_label, date, status, notes]
                
                for col_idx, val in enumerate(row_data):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    if col_idx == 2:  # Slip Type
                        if "Green" in val:
                            item.setForeground(QColor(GREEN_SLIP))
                        elif "Pink" in val:
                            item.setForeground(QColor(PINK_SLIP))
                        elif "Blue" in val:
                            item.setForeground(QColor(BLUE_SLIP))
                    
                    if col_idx == 4:  # Status
                        STATUS_COLORS = {
                            "Active": ("#D4EDDA", "#155724"),
                            "Pending": ("#FFF3CD", "#856404"),
                            "Completed": ("#CCE5FF", "#004085"),
                            "Open / Pending": ("#F8D7DA", "#721C24"),
                        }
                        bg, fg = STATUS_COLORS.get(val, ("#eee", "#333"))
                        item.setBackground(QColor(bg))
                        item.setForeground(QColor(fg))
                    
                    self.records_table.setItem(row_idx, col_idx, item)
            
            except Exception:
                pass
    
    def _make_section_title(self, fa_icon_name: str, text: str) -> QWidget:
        """Create a section title with icon"""
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
    
    def _make_subtitle(self, fa_icon_name: str, text: str) -> QWidget:
        """Create a subtitle with icon"""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(fa_icon_name, color=MID_GRAY).pixmap(16, 16))
        icon_lbl.setStyleSheet("background: transparent;")
        
        text_lbl = QLabel(text)
        text_lbl.setFont(QFont("Segoe UI", 10))
        text_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")
        
        lay.addWidget(icon_lbl)
        lay.addWidget(text_lbl)
        lay.addStretch()
        
        return row
    
    def closeEvent(self, event):
        """Clean up timer when page is closed"""
        self.refresh_timer.stop()
        super().closeEvent(event)

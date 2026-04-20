# =============================================================================
#  SCMS — Activity Logs Page
# =============================================================================
"""
Dedicated page for viewing and filtering activity logs.
Tracks all user actions: slip creation, edits, exports, etc.
"""

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QWidget, QFrame, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, TEXT_DARK,
    btn_gold, btn_outline, btn_primary
)
from ui.components import (
    SectionTitle, SubTitle, Divider,
    StatTile, add_shadow, InfoDialog
)
from ui.pages.base_page import BasePage, build_record_table
from backend.db_activity_log import LogManager, ActionType
from datetime import datetime, timedelta


# ── Color mapping for action types ───────────────────────────────────────────
ACTION_COLORS = {
    ActionType.SLIP_CREATED: "#4CAF50",      # Green
    ActionType.SLIP_MODIFIED: "#FF9800",     # Orange
    ActionType.SLIP_DELETED: "#F44336",      # Red
    ActionType.SLIP_VIEWED: "#2196F3",       # Blue
    ActionType.FILE_EXPORTED: "#9C27B0",     # Purple
    ActionType.REPORT_GENERATED: "#3F51B5",  # Indigo
    ActionType.PRINT_ACTION: "#00BCD4",      # Cyan
    ActionType.USER_AUTHENTICATED: "#4CAF50", # Green
    ActionType.SETTINGS_CHANGED: "#FF5722",  # Deep Orange
    ActionType.BATCH_OPERATION: "#673AB7",   # Deep Purple
    ActionType.RECORD_IMPORTED: "#009688",   # Teal
    ActionType.RECORD_SEARCHED: "#B39DDB",   # Light Purple
}


class ActivityLogsPage(BasePage):
    """Dedicated page for viewing system activity logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.logs_per_page = 50
        self._build()

    def _build(self):
        """Build the logs page UI."""
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

        t_lbl = QLabel("   Activity Logs")
        t_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        t_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; border: none; padding: 0;")

        s_lbl = QLabel("Complete audit trail of all user actions: slip operations, exports, and system changes")
        s_lbl.setFont(QFont("Segoe UI", 11))
        s_lbl.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent; border: none; padding: 0;")

        h_col.addWidget(t_lbl)
        h_col.addWidget(s_lbl)
        h_lay.addLayout(h_col)
        h_lay.addStretch()

        export_logs_btn = QPushButton("   📥 Export Logs ")
        export_logs_btn.setStyleSheet(btn_gold())
        export_logs_btn.setFixedHeight(38)
        export_logs_btn.clicked.connect(self._export_logs)
        h_lay.addWidget(export_logs_btn)
        
        self.main_layout.addWidget(header)

        # Statistics Row
        stats_lay = QHBoxLayout()
        stats_lay.setSpacing(12)
        
        total_logs = LogManager.get_total_logs()
        self.total_logs_tile = StatTile("📊 Total Logs", str(total_logs), NAVY)
        stats_lay.addWidget(self.total_logs_tile)
        
        self.today_logs_tile = StatTile("📅 Today", "0", GOLD)
        stats_lay.addWidget(self.today_logs_tile)
        
        self.month_logs_tile = StatTile("📆 This Month", "0", "#2196F3")
        stats_lay.addWidget(self.month_logs_tile)
        
        self.main_layout.addLayout(stats_lay)
        self.main_layout.addSpacing(12)

        # Filters Row
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 10px;
            }}
        """)
        add_shadow(filter_frame, blur=8, y=2, color=(0, 0, 0, 14))
        
        filter_lay = QHBoxLayout(filter_frame)
        filter_lay.setContentsMargins(12, 10, 12, 10)
        filter_lay.setSpacing(10)

        # Search box
        search_lbl = QLabel("Search:")
        search_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        filter_lay.addWidget(search_lbl)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by staff ID, description, or record ID...")
        self.search_input.setFixedHeight(34)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border-color: {NAVY};
                background: {OFF_WHITE};
            }}
        """)
        filter_lay.addWidget(self.search_input, 2)

        # Action type filter
        action_lbl = QLabel("Action Type:")
        action_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        filter_lay.addWidget(action_lbl)
        
        self.action_filter = QComboBox()
        self.action_filter.addItems([
            "All Actions",
            "Slip Created",
            "Slip Modified",
            "Slip Deleted",
            "Export",
            "Report Generated",
            "Print",
            "Search"
        ])
        self.action_filter.setFixedHeight(34)
        self.action_filter.setFixedWidth(140)
        filter_lay.addWidget(self.action_filter)

        # Status filter
        status_lbl = QLabel("Status:")
        status_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        filter_lay.addWidget(status_lbl)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "SUCCESS", "FAILED"])
        self.status_filter.setFixedHeight(34)
        self.status_filter.setFixedWidth(100)
        filter_lay.addWidget(self.status_filter)

        # Date range
        date_lbl = QLabel("Date Range:")
        date_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        filter_lay.addWidget(date_lbl)
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setFixedHeight(34)
        self.date_from.setFixedWidth(110)
        self.date_from.setStyleSheet(f"""
            QDateEdit {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 6px;
                padding: 0 6px;
                font-size: 10px;
            }}
        """)
        filter_lay.addWidget(self.date_from)
        
        to_lbl = QLabel("to")
        to_lbl.setStyleSheet(f"color: {TEXT_DARK}; border: none; background: transparent;")
        filter_lay.addWidget(to_lbl)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setFixedHeight(34)
        self.date_to.setFixedWidth(110)
        self.date_to.setStyleSheet(f"""
            QDateEdit {{
                border: 1.5px solid {LIGHT_GRAY};
                border-radius: 6px;
                padding: 0 6px;
                font-size: 10px;
            }}
        """)
        filter_lay.addWidget(self.date_to)

        filter_lay.addStretch()

        # Apply filter button
        apply_btn = QPushButton("🔍 Apply Filter")
        apply_btn.setFixedHeight(34)
        apply_btn.setFixedWidth(120)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {NAVY};
                color: {GOLD};
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {GOLD};
                color: {NAVY};
            }}
        """)
        apply_btn.clicked.connect(self._apply_filters)
        filter_lay.addWidget(apply_btn)

        # Reset filter button
        reset_btn = QPushButton("↺ Reset")
        reset_btn.setFixedHeight(34)
        reset_btn.setFixedWidth(80)
        reset_btn.setStyleSheet(btn_outline())
        reset_btn.clicked.connect(self._reset_filters)
        filter_lay.addWidget(reset_btn)

        self.main_layout.addWidget(filter_frame)

        # Logs Table
        headers = ["Timestamp", "Action Type", "Staff ID", "Description", "Record ID", "Status"]
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(len(headers))
        self.logs_table.setHorizontalHeaderLabels(headers)
        self.logs_table.horizontalHeader().setStretchLastSection(True)
        self.logs_table.setColumnWidth(0, 160)
        self.logs_table.setColumnWidth(1, 130)
        self.logs_table.setColumnWidth(2, 100)
        self.logs_table.setColumnWidth(3, 280)
        self.logs_table.setColumnWidth(4, 100)
        self.logs_table.setColumnWidth(5, 80)
        
        self.logs_table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {LIGHT_GRAY};
                background: {WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background: {NAVY};
                color: {GOLD};
                padding: 6px;
                border: none;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {LIGHT_GRAY};
            }}
            QTableWidget::item:selected {{
                background: {NAVY}40;
                color: {TEXT_DARK};
            }}
        """)
        self.logs_table.setMinimumHeight(400)
        self.main_layout.addWidget(self.logs_table)

        # Pagination Row
        pag_lay = QHBoxLayout()
        pag_lay.addStretch()
        
        prev_btn = QPushButton("← Previous")
        prev_btn.setFixedWidth(100)
        prev_btn.setStyleSheet(btn_outline())
        prev_btn.clicked.connect(self._prev_page)
        pag_lay.addWidget(prev_btn)
        
        self.page_lbl = QLabel("Page 1")
        self.page_lbl.setStyleSheet(f"color: {NAVY}; font-weight: bold; border: none; background: transparent;")
        self.page_lbl.setFixedWidth(80)
        self.page_lbl.setAlignment(Qt.AlignCenter)
        pag_lay.addWidget(self.page_lbl)
        
        next_btn = QPushButton("Next →")
        next_btn.setFixedWidth(100)
        next_btn.setStyleSheet(btn_outline())
        next_btn.clicked.connect(self._next_page)
        pag_lay.addWidget(next_btn)
        
        pag_lay.addStretch()
        
        self.main_layout.addLayout(pag_lay)
        self.main_layout.addStretch()

        # Load initial data
        self._refresh_stats()
        self._load_logs()

    def _load_logs(self):
        """Load logs from database and display them."""
        try:
            offset = self.current_page * self.logs_per_page
            logs = LogManager.get_logs(limit=self.logs_per_page, offset=offset)
            
            self.logs_table.setRowCount(len(logs))
            
            for row, log in enumerate(logs):
                try:
                    timestamp = str(log[1])[:19]  # Format datetime
                    action_type = log[2]
                    staff_id = str(log[3])
                    description = str(log[4])[:100]  # Truncate
                    record_id = str(log[5]) if log[5] else "—"
                    status = str(log[8]) if len(log) > 8 else "SUCCESS"
                    
                    # Timestamp
                    timestamp_item = QTableWidgetItem(timestamp)
                    timestamp_item.setFont(QFont("Segoe UI", 9))
                    self.logs_table.setItem(row, 0, timestamp_item)
                    
                    # Action type with color
                    action_item = QTableWidgetItem(action_type.replace("_", " "))
                    action_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                    color = ACTION_COLORS.get(action_type, NAVY)
                    action_item.setForeground(QColor(color))
                    self.logs_table.setItem(row, 1, action_item)
                    
                    # Staff ID
                    staff_item = QTableWidgetItem(staff_id)
                    staff_item.setFont(QFont("Segoe UI", 9))
                    self.logs_table.setItem(row, 2, staff_item)
                    
                    # Description
                    desc_item = QTableWidgetItem(description)
                    desc_item.setFont(QFont("Segoe UI", 9))
                    self.logs_table.setItem(row, 3, desc_item)
                    
                    # Record ID
                    record_item = QTableWidgetItem(record_id)
                    record_item.setFont(QFont("Segoe UI", 9))
                    self.logs_table.setItem(row, 4, record_item)
                    
                    # Status
                    status_item = QTableWidgetItem(status)
                    status_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                    if status == "SUCCESS":
                        status_item.setForeground(QColor("#4CAF50"))
                    else:
                        status_item.setForeground(QColor("#F44336"))
                    self.logs_table.setItem(row, 5, status_item)
                    
                except Exception as e:
                    print(f"Error processing log row: {str(e)}")
            
            # Update page label
            self.page_lbl.setText(f"Page {self.current_page + 1}")
            
        except Exception as e:
            InfoDialog(
                "Error Loading Logs",
                f"Failed to load logs: {str(e)}",
                success=False,
                parent=self
            ).exec_()

    def _refresh_stats(self):
        """Refresh statistics tiles."""
        try:
            total = LogManager.get_total_logs()
            self.total_logs_tile.set_value(str(total))
            
            # Today's logs
            today_logs = LogManager.get_logs_by_date_range(
                QDate.currentDate(), 
                QDate.currentDate()
            )
            self.today_logs_tile.set_value(str(len(today_logs)))
            
            # This month logs
            month_start = QDate.currentDate().addDays(-QDate.currentDate().day() + 1)
            month_logs = LogManager.get_logs_by_date_range(
                month_start,
                QDate.currentDate()
            )
            self.month_logs_tile.set_value(str(len(month_logs)))
            
        except Exception as e:
            print(f"Error refreshing stats: {str(e)}")

    def _apply_filters(self):
        """Apply selected filters."""
        # TODO: Implement advanced filtering
        self.current_page = 0
        self._load_logs()

    def _reset_filters(self):
        """Reset all filters to default."""
        self.search_input.clear()
        self.action_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.current_page = 0
        self._load_logs()

    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_logs()

    def _next_page(self):
        """Go to next page."""
        self.current_page += 1
        self._load_logs()

    def _export_logs(self):
        """Export current logs as CSV or PDF."""
        try:
            import csv
            from datetime import datetime
            
            logs = LogManager.get_logs(limit=1000)  # Export up to 1000
            
            if not logs:
                InfoDialog(
                    "No Logs",
                    "No logs available to export.",
                    success=False,
                    parent=self
                ).exec_()
                return
            
            # Create CSV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"SCMS_Activity_Logs_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Log ID", "Timestamp", "Action Type", "Staff ID",
                    "Description", "Record ID", "Record Type", "Status"
                ])
                
                for log in logs:
                    writer.writerow([
                        log[0],  # LogID
                        log[1],  # Timestamp
                        log[2],  # ActionType
                        log[3],  # StaffID
                        log[4],  # Description
                        log[5],  # RecordID
                        log[6],  # RecordType
                        log[8],  # Status
                    ])
            
            InfoDialog(
                "Export Successful",
                f"Logs exported to:\n{filename}",
                success=True,
                parent=self
            ).exec_()
            
        except Exception as e:
            InfoDialog(
                "Export Error",
                f"Failed to export logs:\n{str(e)}",
                success=False,
                parent=self
            ).exec_()

# =============================================================================
#  SCMS — Shared Base Page + Form Helpers
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QSpinBox, QSizePolicy,
    QGridLayout, QGroupBox, QTabWidget, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, TEXT_DARK, RED_ERR,
    GREEN_SLIP, PINK_SLIP, BLUE_SLIP,
    btn_primary, btn_outline, btn_danger, btn_gold,
    btn_green, btn_pink, btn_blue
)
from ui.components import (
    SectionTitle, SubTitle, Divider, FieldLabel,
    Card, add_shadow, ConfirmDialog, InfoDialog
)


# ── Generic scrollable page wrapper ──────────────────────────────────────────
class BasePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {OFF_WHITE};")

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        self._content = QWidget()
        self._content.setStyleSheet(f"background: {OFF_WHITE};")
        self._scroll.setWidget(self._content)

        self.main_layout = QVBoxLayout(self._content)
        self.main_layout.setContentsMargins(36, 28, 36, 28)
        self.main_layout.setSpacing(20)


# ── Colour badge for slip type ────────────────────────────────────────────────
def slip_badge(slip_type: str) -> QLabel:
    colours = {
        "green": (GREEN_SLIP, "#E8F5E9"),
        "pink":  (PINK_SLIP,  "#FCE4EC"),
        "blue":  (BLUE_SLIP,  "#E3F2FD"),
    }
    text_map = {
        "green": "🟢 Green Slip",
        "pink":  "🔴 Pink Slip",
        "blue":  "🔵 Blue Slip",
    }
    colour, bg = colours.get(slip_type, (NAVY, LIGHT_GRAY))
    lbl = QLabel(text_map.get(slip_type, "Slip"))
    lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
    lbl.setStyleSheet(f"""
        background: {bg};
        color: {colour};
        border: 2px solid {colour};
        border-radius: 6px;
        padding: 4px 14px;
    """)
    lbl.setFixedHeight(34)
    return lbl


# ── Page header bar ───────────────────────────────────────────────────────────
def page_header(slip_type: str, main_title: str, subtitle: str) -> QFrame:
    colours = {
        "green": (GREEN_SLIP, "#E8F5E9"),
        "pink":  (PINK_SLIP,  "#FCE4EC"),
        "blue":  (BLUE_SLIP,  "#E3F2FD"),
        "gold":  (GOLD,       "#FFF8E1"),
    }
    colour, bg = colours.get(slip_type, (NAVY, LIGHT_GRAY))

    header = QFrame()
    header.setFixedHeight(82)
    header.setStyleSheet(f"""
        QFrame {{
            background: {bg};
            border-radius: 12px;
            border-left: 6px solid {colour};
            border: 1px solid {colour}40;
            border-left: 6px solid {colour};
        }}
    """)
    add_shadow(header, blur=12, y=3, color=(0, 0, 0, 18))

    lay = QHBoxLayout(header)
    lay.setContentsMargins(24, 12, 24, 12)
    lay.setSpacing(16)

    left_col = QVBoxLayout()
    left_col.setSpacing(2)

    title_lbl = QLabel(main_title)
    title_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
    title_lbl.setStyleSheet(f"color: {colour}; background: transparent;")

    sub_lbl = QLabel(subtitle)
    sub_lbl.setFont(QFont("Segoe UI", 11))
    sub_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")

    left_col.addWidget(title_lbl)
    left_col.addWidget(sub_lbl)
    lay.addLayout(left_col)
    lay.addStretch()
    lay.addWidget(slip_badge(slip_type))

    return header


# ── Reusable search bar ───────────────────────────────────────────────────────
def search_bar(placeholder: str = "Search...") -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(10)

    search_icon = QLabel("🔍")
    search_icon.setFont(QFont("Segoe UI", 14))
    search_icon.setStyleSheet("background: transparent;")

    edit = QLineEdit()
    edit.setPlaceholderText(placeholder)
    edit.setFixedHeight(38)
    edit.setStyleSheet(f"""
        QLineEdit {{
            background: {WHITE};
            border: 1.5px solid {LIGHT_GRAY};
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 1.5px solid {NAVY};
        }}
    """)

    row.addWidget(search_icon)
    row.addWidget(edit, 1)
    return row, edit


# ── Generic record table builder ──────────────────────────────────────────────
def build_record_table(headers: list, row_data: list) -> QTableWidget:
    table = QTableWidget(len(row_data), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    table.horizontalHeader().setStretchLastSection(True)
    table.setStyleSheet(f"""
        QTableWidget {{
            alternate-background-color: #F5F8FF;
            background: {WHITE};
            border: 1px solid {LIGHT_GRAY};
            border-radius: 10px;
            outline: none;
        }}
        QTableWidget::item {{ padding: 8px 10px; }}
        QTableWidget::item:selected {{
            background: #EEF2FF;
            color: {NAVY};
        }}
    """)
    for r, row in enumerate(row_data):
        for c, val in enumerate(row):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(r, c, item)
    return table

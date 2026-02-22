# =============================================================================
#  SCMS — Student Conduct Management System
#  Global Stylesheet  (Red + White palette)
# =============================================================================

# ── Brand colours ────────────────────────────────────────────────────────────
NAVY       = "#B71C1C"   # primary deep red
NAVY_DARK  = "#7F0000"   # sidebar / header dark shade
NAVY_MID   = "#C62828"   # hover state for sidebar items
GOLD       = "#EF9A9A"   # accent light red / rose
GOLD_LIGHT = "#FFCDD2"   # lighter rose for hover
WHITE      = "#FFFFFF"
OFF_WHITE  = "#FFF5F5"   # page background (warm white)
LIGHT_GRAY = "#FFCDD2"   # card borders / dividers
MID_GRAY   = "#EF9A9A"   # placeholder / secondary text
TEXT_DARK  = "#7F0000"   # main body text
TEXT_MED   = "#C62828"   # sub-labels
RED_ERR    = "#D32F2F"   # error messages
GREEN_OK   = "#2E7D32"   # success
BLUE_INFO  = "#1565C0"   # info badges

# ── Slip accent colours ───────────────────────────────────────────────────────
GREEN_SLIP = "#2E7D32"
PINK_SLIP  = "#C2185B"
BLUE_SLIP  = "#1565C0"

# =============================================================================
GLOBAL_STYLE = f"""
/* ── Base ────────────────────────────────────────────────────────────────── */
QWidget {{
    font-family: "Segoe UI", "Calibri", sans-serif;
    font-size: 13px;
    color: {TEXT_DARK};
    background-color: {OFF_WHITE};
}}

QMainWindow {{
    background-color: {OFF_WHITE};
}}

/* ── Scrollbars ──────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    width: 8px;
    background: {LIGHT_GRAY};
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {MID_GRAY};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {NAVY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Tooltips ────────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {NAVY_DARK};
    color: {WHITE};
    border: 1px solid {GOLD};
    padding: 5px 8px;
    border-radius: 4px;
    font-size: 12px;
}}

/* ── Labels ──────────────────────────────────────────────────────────────── */
QLabel {{
    background: transparent;
    color: {TEXT_DARK};
}}

/* ── Line Edits ──────────────────────────────────────────────────────────── */
QLineEdit {{
    background-color: {WHITE};
    border: 1.5px solid {LIGHT_GRAY};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT_DARK};
    selection-background-color: {GOLD};
}}
QLineEdit:focus {{
    border: 1.5px solid {NAVY};
    background-color: {WHITE};
}}
QLineEdit:hover {{
    border: 1.5px solid {NAVY_MID};
}}
QLineEdit[readOnly="true"] {{
    background-color: {LIGHT_GRAY};
    color: {MID_GRAY};
}}

/* ── ComboBoxes ──────────────────────────────────────────────────────────── */
QComboBox {{
    background-color: {WHITE};
    border: 1.5px solid {LIGHT_GRAY};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    color: {TEXT_DARK};
}}
QComboBox:focus {{
    border: 1.5px solid {NAVY};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}
QComboBox QAbstractItemView {{
    background: {WHITE};
    border: 1px solid {LIGHT_GRAY};
    selection-background-color: {NAVY};
    selection-color: {WHITE};
    outline: none;
}}

/* ── Date Edit ───────────────────────────────────────────────────────────── */
QDateEdit {{
    background-color: {WHITE};
    border: 1.5px solid {LIGHT_GRAY};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
    color: {TEXT_DARK};
}}
QDateEdit:focus {{
    border: 1.5px solid {NAVY};
}}
QDateEdit::drop-down {{
    border: none;
    width: 28px;
}}

/* ── SpinBox ─────────────────────────────────────────────────────────────── */
QSpinBox {{
    background-color: {WHITE};
    border: 1.5px solid {LIGHT_GRAY};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
}}
QSpinBox:focus {{
    border: 1.5px solid {NAVY};
}}

/* ── Text Edit ───────────────────────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {{
    background-color: {WHITE};
    border: 1.5px solid {LIGHT_GRAY};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT_DARK};
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1.5px solid {NAVY};
}}

/* ── Table Widget ────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {WHITE};
    border: 1px solid {LIGHT_GRAY};
    border-radius: 8px;
    gridline-color: {LIGHT_GRAY};
    outline: none;
    font-size: 13px;
}}
QTableWidget::item {{
    padding: 8px 10px;
    border-bottom: 1px solid {LIGHT_GRAY};
}}
QTableWidget::item:selected {{
    background-color: #FFEBEE;
    color: {NAVY};
}}
QTableWidget::item:hover {{
    background-color: #FFF5F5;
}}
QHeaderView::section {{
    background-color: {NAVY};
    color: {WHITE};
    padding: 10px 12px;
    border: none;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 0.5px;
}}
QHeaderView::section:first {{
    border-top-left-radius: 8px;
}}
QHeaderView::section:last {{
    border-top-right-radius: 8px;
}}

/* ── Tab Widget ──────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {LIGHT_GRAY};
    border-radius: 8px;
    background: {WHITE};
    top: -1px;
}}
QTabBar::tab {{
    background: {LIGHT_GRAY};
    color: {TEXT_MED};
    padding: 10px 22px;
    margin-right: 3px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 13px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {NAVY};
    color: {WHITE};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background: {NAVY_MID};
    color: {WHITE};
}}

/* ── Message Box ─────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {WHITE};
}}
QMessageBox QLabel {{
    color: {TEXT_DARK};
    font-size: 13px;
}}

/* ── Group Box ───────────────────────────────────────────────────────────── */
QGroupBox {{
    border: 1.5px solid {LIGHT_GRAY};
    border-radius: 8px;
    margin-top: 18px;
    padding: 12px 10px 10px 10px;
    background: {WHITE};
    font-weight: bold;
    color: {NAVY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: -2px;
    padding: 0 6px;
    background: {WHITE};
    color: {NAVY};
    font-size: 13px;
}}

/* ── Checkboxes / Radio ──────────────────────────────────────────────────── */
QCheckBox, QRadioButton {{
    spacing: 8px;
    font-size: 13px;
    color: {TEXT_DARK};
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
}}
QCheckBox::indicator:checked {{
    background-color: {NAVY};
    border: 2px solid {NAVY};
    border-radius: 3px;
}}
QRadioButton::indicator:checked {{
    background-color: {NAVY};
    border: 2px solid {NAVY};
    border-radius: 8px;
}}

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle {{
    background: {LIGHT_GRAY};
    width: 2px;
}}

/* ── Status Bar ──────────────────────────────────────────────────────────── */
QStatusBar {{
    background: {NAVY_DARK};
    color: {WHITE};
    font-size: 11px;
    padding: 2px 8px;
}}
"""

# ── Reusable button style factories ──────────────────────────────────────────

def btn_primary():
    return f"""
    QPushButton {{
        background-color: {NAVY};
        color: {WHITE};
        border: none;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 0.3px;
    }}
    QPushButton:hover {{
        background-color: {NAVY_MID};
    }}
    QPushButton:pressed {{
        background-color: {NAVY_DARK};
    }}
    QPushButton:disabled {{
        background-color: {LIGHT_GRAY};
        color: {MID_GRAY};
    }}
    """

def btn_gold():
    return f"""
    QPushButton {{
        background-color: {GOLD};
        color: {NAVY_DARK};
        border: none;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {GOLD_LIGHT};
    }}
    QPushButton:pressed {{
        background-color: #EF9A9A;
    }}
    """

def btn_danger():
    return f"""
    QPushButton {{
        background-color: {RED_ERR};
        color: {WHITE};
        border: none;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #C0392B;
    }}
    QPushButton:pressed {{
        background-color: #962D22;
    }}
    """

def btn_outline():
    return f"""
    QPushButton {{
        background-color: transparent;
        color: {NAVY};
        border: 1.5px solid {NAVY};
        border-radius: 7px;
        padding: 9px 22px;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {NAVY};
        color: {WHITE};
    }}
    QPushButton:pressed {{
        background-color: {NAVY_DARK};
        color: {WHITE};
    }}
    """

def btn_green():
    return f"""
    QPushButton {{
        background-color: {GREEN_SLIP};
        color: {WHITE};
        border: none;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #1B5E20;
    }}
    QPushButton:pressed {{
        background-color: #144D18;
    }}
    """

def btn_pink():
    return f"""
    QPushButton {{
        background-color: {PINK_SLIP};
        color: {WHITE};
        border: none;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #880E4F;
    }}
    QPushButton:pressed {{
        background-color: #6A0C3E;
    }}
    """

def btn_blue():
    return f"""
    QPushButton {{
        background-color: {BLUE_SLIP};
        color: {WHITE};
        border: none;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #0D47A1;
    }}
    QPushButton:pressed {{
        background-color: #0A3880;
    }}
    """

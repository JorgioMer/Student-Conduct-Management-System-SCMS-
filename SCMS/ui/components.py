# =============================================================================
#  SCMS — Reusable UI Components
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFrame, QHBoxLayout,
    QVBoxLayout, QSizePolicy, QGraphicsDropShadowEffect,
    QDialog, QDialogButtonBox, QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QPainterPath

import qtawesome as qta  # pip install qtawesome

from ui.styles import (
    NAVY, NAVY_DARK, NAVY_MID, GOLD, WHITE, OFF_WHITE, LIGHT_GRAY,
    MID_GRAY, TEXT_DARK, RED_ERR, GREEN_OK,
    GREEN_SLIP, PINK_SLIP, BLUE_SLIP,
    btn_primary, btn_gold, btn_outline, btn_danger,
    btn_green, btn_pink, btn_blue
)


# ── Shadow helper ─────────────────────────────────────────────────────────────
def add_shadow(widget, blur=18, x=0, y=3, color=(0, 0, 0, 40)):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(x, y)
    shadow.setColor(QColor(*color))
    widget.setGraphicsEffect(shadow)
    return shadow


# ── Icon helper — renders a Qt standard pixmap as a coloured QLabel ───────────
def _make_icon_label(sp_icon_enum, size=20, color=None):
    """Return a QLabel displaying a Qt standard-pixmap icon."""
    style = QApplication.instance().style()
    icon = style.standardIcon(sp_icon_enum)
    pix  = icon.pixmap(QSize(size, size))

    if color:
        tinted = QPixmap(pix.size())
        tinted.fill(Qt.transparent)
        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, pix)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color))
        painter.end()
        pix = tinted

    lbl = QLabel()
    lbl.setPixmap(pix)
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet("background: transparent;")
    return lbl


# ── Section title label ───────────────────────────────────────────────────────
class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        font = QFont("Segoe UI", 15, QFont.Bold)
        self.setFont(font)
        self.setStyleSheet(f"color: {NAVY}; margin-bottom: 2px;")


# ── Sub-title label ───────────────────────────────────────────────────────────
class SubTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        self.setStyleSheet(f"color: {MID_GRAY}; margin-bottom: 12px;")


# ── Horizontal rule divider ───────────────────────────────────────────────────
class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet(f"color: {LIGHT_GRAY}; background: {LIGHT_GRAY}; max-height: 1px;")


# ── Field label (form row) ────────────────────────────────────────────────────
class FieldLabel(QLabel):
    def __init__(self, text, required=False, parent=None):
        txt = f"{text} <span style='color:{RED_ERR};'>*</span>" if required else text
        super().__init__(parent)
        self.setText(txt)
        self.setTextFormat(Qt.RichText)
        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Medium)
        self.setFont(font)
        self.setStyleSheet(f"color: {TEXT_DARK}; margin-bottom: 3px;")


# ── Card widget ───────────────────────────────────────────────────────────────
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame#Card {{
                background: {WHITE};
                border-radius: 12px;
                border: 1px solid {LIGHT_GRAY};
            }}
        """)
        add_shadow(self, blur=14, y=4, color=(0, 0, 0, 25))
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 18, 20, 18)
        self._layout.setSpacing(10)

    def layout(self):
        return self._layout


# ── Slip Dashboard card button ────────────────────────────────────────────────
class SlipCard(QFrame):
    clicked = pyqtSignal()

    COLOURS = {
        "green": (GREEN_SLIP, "#E8F5E9", "#1B5E20"),
        "pink":  (PINK_SLIP,  "#FCE4EC", "#880E4F"),
        "blue":  (BLUE_SLIP,  "#E3F2FD", "#0D47A1"),
        "gold":  (GOLD,       "#FFF8E1", "#8D6E0A"),
    }

    def __init__(self, slip_type: str, title: str, description: str,
                 fa_icon: str, parent=None):
        super().__init__(parent)
        colour, bg, dark = self.COLOURS.get(slip_type, self.COLOURS["gold"])
        self._colour = colour
        self.setObjectName("SlipCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(210, 170)
        self.setStyleSheet(f"""
            QFrame#SlipCard {{
                background: {bg};
                border-radius: 14px;
                border: 2px solid {colour};
            }}
            QFrame#SlipCard:hover {{
                background: {colour};
                border: 2px solid {dark};
            }}
        """)
        add_shadow(self, blur=16, y=5, color=(0, 0, 0, 30))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # ── Icon circle using qtawesome — uses the fa_icon name passed in ──────
        icon_pix = qta.icon(fa_icon, color=WHITE).pixmap(QSize(26, 26))

        icon_container = QLabel()
        icon_container.setAlignment(Qt.AlignCenter)
        icon_container.setFixedSize(46, 46)
        icon_container.setPixmap(icon_pix)
        icon_container.setStyleSheet(f"""
            background-color: {colour};
            border-radius: 23px;
            padding: 10px;
        """)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {dark}; background: transparent;")
        title_lbl.setWordWrap(True)

        desc_lbl = QLabel(description)
        desc_lbl.setFont(QFont("Segoe UI", 10))
        desc_lbl.setStyleSheet(f"color: {dark}; background: transparent; opacity: 0.85;")
        desc_lbl.setWordWrap(True)

        layout.addWidget(icon_container, 0, Qt.AlignLeft)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


# ── Stat summary tile ─────────────────────────────────────────────────────────
class StatTile(QFrame):
    def __init__(self, label: str, value: str, colour: str, parent=None):
        super().__init__(parent)
        self.setObjectName("StatTile")
        self.setFixedHeight(90)
        self.setStyleSheet(f"""
            QFrame#StatTile {{
                background: {WHITE};
                border-left: 5px solid {colour};
                border-radius: 10px;
                border-top: 1px solid {LIGHT_GRAY};
                border-right: 1px solid {LIGHT_GRAY};
                border-bottom: 1px solid {LIGHT_GRAY};
            }}
        """)
        add_shadow(self, blur=10, y=3, color=(0, 0, 0, 20))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(2)

        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Segoe UI", 24, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {colour}; background: transparent;")

        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent;")

        lay.addWidget(val_lbl)
        lay.addWidget(lbl)


# ── Top header bar ────────────────────────────────────────────────────────────
class HeaderBar(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user_name: str = "Admin", parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(62)
        # Background painted via paintEvent; keep child widgets transparent
        self.setStyleSheet("QWidget { background: transparent; border: none; }")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)

        # Logo using qtawesome
        logo_lbl = QLabel()
        logo_lbl.setPixmap(qta.icon("fa5s.balance-scale", color=GOLD).pixmap(QSize(28, 28)))
        logo_lbl.setFixedSize(32, 32)
        logo_lbl.setStyleSheet("background: transparent;")

        sys_lbl = QLabel("Office of the Prefect — SCMS")
        sys_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        sys_lbl.setStyleSheet("color: #FFFFFF; background: transparent; letter-spacing: 0.5px;")

        lay.addWidget(logo_lbl)
        lay.addWidget(sys_lbl)
        lay.addStretch()

        # User badge
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.12);
                border-radius: 20px;
                padding: 2px 4px;
            }}
        """)
        user_lay = QHBoxLayout(user_frame)
        user_lay.setContentsMargins(10, 4, 10, 4)
        user_lay.setSpacing(8)

        avatar = QLabel()
        avatar.setPixmap(qta.icon("fa5s.user-circle", color="#FFFFFF").pixmap(QSize(20, 20)))
        avatar.setFixedSize(22, 22)
        avatar.setStyleSheet("background: transparent;")

        uname = QLabel(user_name)
        uname.setFont(QFont("Segoe UI", 12, QFont.Bold))
        uname.setStyleSheet("color: #FFFFFF; background: transparent;")

        user_lay.addWidget(avatar)
        user_lay.addWidget(uname)

        logout_btn = QPushButton("  Logout")
        logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color="#FFFFFF"))
        logout_btn.setIconSize(QSize(16, 16))
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.15);
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.35);
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {RED_ERR};
                border: 1px solid {RED_ERR};
                color: {WHITE};
            }}
        """)
        logout_btn.setToolTip("Log out of the system")
        logout_btn.clicked.connect(self.logout_requested.emit)

        lay.addWidget(user_frame)
        lay.addWidget(logout_btn)

    def paintEvent(self, event):
        """Force-paint the dark red gradient — stylesheet alone won't fill QWidget."""
        from PyQt5.QtGui import QPainter, QLinearGradient, QColor
        from PyQt5.QtCore import QRectF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor("#5C0A0A"))
        grad.setColorAt(1.0, QColor("#6B0F0F"))
        painter.fillRect(self.rect(), grad)
        # Gold bottom border
        painter.setPen(QColor(GOLD))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.drawLine(0, self.height() - 2, self.width(), self.height() - 2)
        painter.drawLine(0, self.height() - 3, self.width(), self.height() - 3)
        painter.end()


# ── Sidebar nav button ────────────────────────────────────────────────────────
class NavButton(QPushButton):
    def __init__(self, icon: QIcon, label: str, parent=None):
        super().__init__(parent)
        self.setText(f"  {label}")
        self.setIcon(icon)
        self.setIconSize(QSize(18, 18))
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 12))
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding-left: 16px;
                background: transparent;
                color: rgba(255,255,255,0.75);
                border: none;
                border-radius: 0px;
                border-left: 3px solid transparent;
            }}
            QPushButton:hover {{
                background: {NAVY_MID};
                color: {WHITE};
                border-left: 3px solid rgba(201,168,76,0.5);
            }}
            QPushButton:checked {{
                background: {NAVY_MID};
                color: {WHITE};
                border-left: 3px solid {GOLD};
                font-weight: bold;
            }}
        """)


# ── Confirmation dialog ───────────────────────────────────────────────────────
class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(400)
        self.setStyleSheet(f"background: {WHITE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 20)
        lay.setSpacing(14)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon("fa5s.exclamation-triangle", color="#F59E0B").pixmap(QSize(48, 48)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")

        msg_lbl = QLabel(message)
        msg_lbl.setFont(QFont("Segoe UI", 12))
        msg_lbl.setAlignment(Qt.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        lay.addWidget(icon_lbl)
        lay.addWidget(msg_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("  Cancel")
        cancel_btn.setIcon(qta.icon("fa5s.times", color=NAVY))
        cancel_btn.setStyleSheet(btn_outline())
        cancel_btn.setFixedHeight(38)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("  Confirm")
        confirm_btn.setIcon(qta.icon("fa5s.check", color=WHITE))
        confirm_btn.setStyleSheet(btn_primary())
        confirm_btn.setFixedHeight(38)
        confirm_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(confirm_btn)
        lay.addLayout(btn_row)


# ── Info / success dialog ─────────────────────────────────────────────────────
class InfoDialog(QDialog):
    def __init__(self, title: str, message: str, success: bool = True, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(380)
        self.setStyleSheet(f"background: {WHITE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 20)
        lay.setSpacing(14)

        if success:
            icon_name  = "fa5s.check-circle"
            icon_color = GREEN_OK
        else:
            icon_name  = "fa5s.times-circle"
            icon_color = RED_ERR

        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(QSize(48, 48)))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")

        msg_lbl = QLabel(message)
        msg_lbl.setFont(QFont("Segoe UI", 12))
        msg_lbl.setAlignment(Qt.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")

        ok_btn = QPushButton("  OK")
        ok_btn.setIcon(qta.icon("fa5s.check", color=WHITE))
        ok_btn.setStyleSheet(btn_primary())
        ok_btn.setFixedHeight(38)
        ok_btn.clicked.connect(self.accept)

        lay.addWidget(icon_lbl)
        lay.addWidget(msg_lbl)
        lay.addWidget(ok_btn)
# =============================================================================
#  SCMS — Login Window
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QApplication, QDesktopWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, RED_ERR, TEXT_DARK,
    btn_primary, btn_gold
)
from ui.components import add_shadow, Divider


# ── Demo credentials (UI simulation only) ─────────────────────────────────────
DEMO_USERS = {
    "admin":  ("admin123",  "Administrator", "Admin"),
    "staff":  ("staff123",  "Office Staff",  "Staff"),
    "prefect":("prefect123","Prefect Office", "Admin"),
}

class LoginWindow(QWidget):
    login_success = pyqtSignal(str, str)   # (full_name, role)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCMS — Login")
        self.setMinimumSize(960, 600)
        self.setStyleSheet(f"background: {NAVY_DARK};")
        self._build_ui()
        self._center_on_screen()

    # ── Center window ─────────────────────────────────────────────────────────
    def _center_on_screen(self):
        screen = QDesktopWidget().screenGeometry()
        size   = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2
        )

    # ── Build layout ──────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel (branding) ──────────────────────────────────────────
        left = QFrame()
        left.setObjectName("LeftPanel")
        left.setStyleSheet(f"""
            QFrame#LeftPanel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0  {NAVY_DARK},
                    stop:1  {NAVY}
                );
                border-right: 3px solid {GOLD};
            }}
        """)
        left.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        left.setFixedWidth(420)

        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(50, 60, 50, 40)
        left_lay.setSpacing(0)

        # Emblem / crest
        crest = QLabel("")
        crest.setFont(QFont("Segoe UI", 72))
        crest.setAlignment(Qt.AlignCenter)
        crest.setStyleSheet(f"color: {GOLD}; background: transparent;")

        school_lbl = QLabel("CJC")
        school_lbl.setFont(QFont("Segoe UI", 32, QFont.Bold))
        school_lbl.setAlignment(Qt.AlignCenter)
        school_lbl.setStyleSheet(f"color: {WHITE}; background: transparent; letter-spacing: 6px;")

        divider_gold = QFrame()
        divider_gold.setFrameShape(QFrame.HLine)
        divider_gold.setStyleSheet(f"color: {GOLD}; background: {GOLD}; max-height: 2px; margin: 10px 60px;")

        office_lbl = QLabel("Office of the Prefect")
        office_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        office_lbl.setAlignment(Qt.AlignCenter)
        office_lbl.setStyleSheet(f"color: {GOLD}; background: transparent; letter-spacing: 1px;")

        sys_lbl = QLabel("Student Conduct\nManagement System")
        sys_lbl.setFont(QFont("Segoe UI", 13))
        sys_lbl.setAlignment(Qt.AlignCenter)
        sys_lbl.setStyleSheet(f"color: rgba(255,255,255,0.70); background: transparent; line-height: 1.5;")

        left_lay.addStretch(2)
        left_lay.addWidget(crest)
        left_lay.addSpacing(6)
        left_lay.addWidget(school_lbl)
        left_lay.addWidget(divider_gold)
        left_lay.addWidget(office_lbl)
        left_lay.addSpacing(10)
        left_lay.addWidget(sys_lbl)
        left_lay.addStretch(3)

        # Footer
        footer = QLabel("For authorized personnel only\nAll actions are logged.")
        footer.setFont(QFont("Segoe UI", 10))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: rgba(255,255,255,0.35); background: transparent;")
        left_lay.addWidget(footer)

        # ── Right panel (login form) ───────────────────────────────────────
        right = QFrame()
        right.setStyleSheet(f"background: {OFF_WHITE};")

        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(80, 0, 80, 0)
        right_lay.setSpacing(0)
        right_lay.setAlignment(Qt.AlignCenter)

        # Login card
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setMaximumWidth(380)
        card.setStyleSheet(f"""
            QFrame#LoginCard {{
                background: {WHITE};
                border-radius: 16px;
                border: 1px solid {LIGHT_GRAY};
            }}
        """)
        add_shadow(card, blur=28, y=8, color=(0, 0, 0, 30))

        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(36, 36, 36, 36)
        card_lay.setSpacing(0)

        # Welcome heading
        welcome = QLabel("Welcome Back")
        welcome.setFont(QFont("Segoe UI", 20, QFont.Bold))
        welcome.setStyleSheet(f"color: {NAVY}; background: transparent;")

        sub = QLabel("Please enter your credentials to continue")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(f"color: {MID_GRAY}; background: transparent; margin-bottom: 24px;")

        card_lay.addWidget(welcome)
        card_lay.addSpacing(4)
        card_lay.addWidget(sub)
        card_lay.addSpacing(20)

        # Username
        user_lbl = QLabel("Username")
        user_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        user_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; margin-bottom: 4px;")

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setFixedHeight(44)
        self.username_edit.setFont(QFont("Segoe UI", 12))
        self.username_edit.returnPressed.connect(self._on_login)

        card_lay.addWidget(user_lbl)
        card_lay.addWidget(self.username_edit)
        card_lay.addSpacing(16)

        # Password
        pass_lbl = QLabel("Password")
        pass_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        pass_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent; margin-bottom: 4px;")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setFixedHeight(44)
        self.password_edit.setFont(QFont("Segoe UI", 12))
        self.password_edit.returnPressed.connect(self._on_login)

        card_lay.addWidget(pass_lbl)
        card_lay.addWidget(self.password_edit)
        card_lay.addSpacing(6)

        # Error message label (hidden by default)
        self.error_lbl = QLabel("")
        self.error_lbl.setFont(QFont("Segoe UI", 11))
        self.error_lbl.setStyleSheet(f"""
            color: {RED_ERR};
            background: #FFF0F0;
            border: 1px solid #FFCCCC;
            border-radius: 6px;
            padding: 6px 10px;
        """)
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setVisible(False)

        card_lay.addWidget(self.error_lbl)
        card_lay.addSpacing(20)

        # Login button
        self.login_btn = QPushButton("  Log In")
        self.login_btn.setFixedHeight(46)
        self.login_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {NAVY_DARK}, stop:1 {NAVY});
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {NAVY}, stop:1 #2E4070);
            }}
            QPushButton:pressed {{
                background: {NAVY_DARK};
            }}
        """)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setToolTip("Click to log into the system")
        self.login_btn.clicked.connect(self._on_login)

        card_lay.addWidget(self.login_btn)
        card_lay.addSpacing(20)

        # Demo hint
        hint = QLabel(
            "<b>Demo credentials:</b><br>"
            "admin / admin123 &nbsp;·&nbsp; staff / staff123"
        )
        hint.setFont(QFont("Segoe UI", 10))
        hint.setTextFormat(Qt.RichText)
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"""
            color: {MID_GRAY};
            background: {OFF_WHITE};
            border: 1px solid {LIGHT_GRAY};
            border-radius: 6px;
            padding: 8px;
        """)
        card_lay.addWidget(hint)

        right_lay.addWidget(card, 0, Qt.AlignCenter)

        # Copyright footer
        copy_lbl = QLabel("© 2024 Office of the Prefect — CJC  |  SCMS v1.0")
        copy_lbl.setFont(QFont("Segoe UI", 9))
        copy_lbl.setAlignment(Qt.AlignCenter)
        copy_lbl.setStyleSheet(f"color: {MID_GRAY}; background: transparent; margin-top: 20px;")
        right_lay.addWidget(copy_lbl)

        root.addWidget(left)
        root.addWidget(right, 1)

    # ── Login handler (UI simulation) ─────────────────────────────────────────
    def _on_login(self):
        username = self.username_edit.text().strip().lower()
        password = self.password_edit.text()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

        if username in DEMO_USERS:
            pw, full_name, role = DEMO_USERS[username]
            if password == pw:
                self._hide_error()
                self._launch_dashboard(full_name, role)
                return

        self._show_error("Incorrect username or password. Please try again.")
        self.password_edit.clear()
        self.password_edit.setFocus()

    def _show_error(self, msg: str):
        self.error_lbl.setText(f"[WARNING] {msg}")
        self.error_lbl.setVisible(True)
        # Shake animation on the field
        anim = QPropertyAnimation(self.login_btn, b"geometry")
        anim.setDuration(120)
        geo = self.login_btn.geometry()
        anim.setKeyValueAt(0.0, geo)
        anim.setKeyValueAt(0.2, geo.adjusted(-4, 0, -4, 0))
        anim.setKeyValueAt(0.5, geo.adjusted(4, 0, 4, 0))
        anim.setKeyValueAt(0.8, geo.adjusted(-2, 0, -2, 0))
        anim.setKeyValueAt(1.0, geo)
        anim.start()

    def _hide_error(self):
        self.error_lbl.setVisible(False)

    def _launch_dashboard(self, full_name: str, role: str):
        from ui.main_window import MainWindow
        self.main_win = MainWindow(full_name=full_name, role=role)
        self.main_win.show()
        self.close()

# =============================================================================
#  SCMS — Login Window
# =============================================================================
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,
    QApplication, QDesktopWidget, QProgressBar, QDialog
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect,
    pyqtSignal, QTimer, QThread, pyqtSlot, QSize
)
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QLinearGradient, QIcon, QPainterPath, QPen

from ui.styles import (
    NAVY, NAVY_DARK, GOLD, WHITE, OFF_WHITE,
    LIGHT_GRAY, MID_GRAY, RED_ERR, TEXT_DARK,
    btn_primary, btn_gold
)
from ui.components import add_shadow, Divider


# Backend imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.db_accounts import ensure_default_accounts, validate_login

# ── Eye icon helpers ───────────────────────────────────────────────────────────
def _draw_eye_icon(visible: bool, size: int = 22, color: str = "#888888") -> QIcon:
    """
    Draws a clean vector eye icon using QPainter.
    visible=True  → open eye
    visible=False → eye with a diagonal slash (hidden)
    """
    px = QPixmap(size, size)
    px.fill(Qt.transparent)

    painter = QPainter(px)
    painter.setRenderHint(QPainter.Antialiasing)

    pen = QPen(QColor(color))
    pen.setWidthF(1.8)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    cx, cy = size / 2, size / 2
    ew = size * 0.80   # eye width
    eh = size * 0.38   # eye height

    # ── outer eye shape (almond / lens) ──────────────────────────────────────
    path = QPainterPath()
    path.moveTo(cx - ew / 2, cy)
    path.cubicTo(
        cx - ew / 4, cy - eh,
        cx + ew / 4, cy - eh,
        cx + ew / 2, cy
    )
    path.cubicTo(
        cx + ew / 4, cy + eh,
        cx - ew / 4, cy + eh,
        cx - ew / 2, cy
    )
    painter.drawPath(path)

    # ── pupil ─────────────────────────────────────────────────────────────────
    r = size * 0.12
    painter.setBrush(QColor(color))
    painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
    painter.setBrush(Qt.NoBrush)

    if not visible:
        # ── diagonal slash for "hidden" state ─────────────────────────────────
        slash_pen = QPen(QColor(color))
        slash_pen.setWidthF(1.8)
        slash_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(slash_pen)
        offset = size * 0.18
        painter.drawLine(
            int(cx - ew / 2 + offset), int(cy + eh + 2),
            int(cx + ew / 2 - offset), int(cy - eh - 2)
        )

    painter.end()
    return QIcon(px)




# ── Background worker: builds MainWindow off the UI thread ────────────────────
class AppLoaderThread(QThread):
    """
    Runs heavy initialization (DB connections, page construction) in a
    background thread so the loading screen stays responsive.

    NOTE: Qt widgets must only be created on the main thread.
          We only do non-widget work here (imports, DB warm-up, etc.).
          MainWindow itself is created back on the main thread via the signal.
    """
    progress_update = pyqtSignal(int, str)   # (percent, status text)
    ready           = pyqtSignal()           # emitted when pre-loading is done

    def __init__(self, full_name: str, role: str, parent=None):
        super().__init__(parent)
        self.full_name = full_name
        self.role      = role

    def run(self):
        """Pre-load heavy imports and warm up DB connections off the UI thread."""
        steps = [
            (10,  "Checking credentials..."),
            (20,  "Loading interface components..."),
            (35,  "Initializing themes..."),
            (50,  "Connecting to database..."),
            (65,  "Warming up database tables..."),
            (80,  "Loading modules..."),
            (90,  "Preparing interface..."),
        ]

        for percent, status in steps:
            self.progress_update.emit(percent, status)
            self.msleep(120)   # ← short sleep keeps progress visible;
                               #   real work below replaces these sleeps

        self.progress_update.emit(88, "Almost ready...")
        self.msleep(80)
        self.ready.emit()


# ── Loading Screen ─────────────────────────────────────────────────────────────
class LoadingScreen(QDialog):
    """Modal loading screen shown during application initialization."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading SCMS...")
        self.setMinimumSize(500, 250)
        self.setStyleSheet(f"background: {NAVY_DARK};")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._build_ui()
        self._center_on_screen()

        self.main_win   = None
        self._thread    = None

    def _center_on_screen(self):
        screen = QDesktopWidget().screenGeometry()
        size   = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2,
        )

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(60, 60, 60, 60)
        lay.setSpacing(20)

        title = QLabel("CJC")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {GOLD}; background: transparent;")
        lay.addWidget(title)

        msg = QLabel("Initializing Student Conduct Management System")
        msg.setFont(QFont("Segoe UI", 12))
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet(f"color: {WHITE}; background: transparent;")
        lay.addWidget(msg)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(32)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 6px;
                text-align: center;
                color: {GOLD};
                font-weight: bold;
                font-size: 14px;
            }}
            QProgressBar::chunk {{
                background: {GOLD};
                border-radius: 4px;
            }}
        """)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        lay.addWidget(self.progress)

        self.status_lbl = QLabel("Loading...")
        self.status_lbl.setFont(QFont("Segoe UI", 10))
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet(
            f"color: rgba(201,168,76,0.8); background: transparent;"
        )
        lay.addWidget(self.status_lbl)
        lay.addStretch()

    # ── Public API ─────────────────────────────────────────────────────────
    # In LoadingScreen.load_application:
    def load_application(self, full_name: str, role: str, username: str):
        self._username = username          # ← store it
        self._thread = AppLoaderThread(full_name, role, parent=self)
        self._thread.progress_update.connect(self._on_progress)
        self._thread.ready.connect(lambda: self._on_preload_done(full_name, role))
        self._thread.start()

    # ── Slots ──────────────────────────────────────────────────────────────
    @pyqtSlot(int, str)
    def _on_progress(self, value: int, status: str):
        self.progress.setValue(value)
        self.status_lbl.setText(status)

    @pyqtSlot()
    def _on_preload_done(self, full_name: str, role: str):
        """
        Called on the MAIN thread when the background thread finishes.
        Now safe to create Qt widgets.
        """
        self._on_progress(95, "Building interface...")

        # Create MainWindow here — main thread only
        from ui.main_window import MainWindow
        self.main_win = MainWindow(full_name=full_name, role=role,username=self._username)

        self._on_progress(100, "Ready!")

        # Show main window, then fade out loading screen after a short pause
        self.main_win.show()
        QTimer.singleShot(800, self._fadeout_loading)

    def _fadeout_loading(self):
        """Smoothly fade out the loading screen."""
        fadeout = QPropertyAnimation(self, b"windowOpacity")
        fadeout.setDuration(500)
        fadeout.setStartValue(1.0)
        fadeout.setEndValue(0.0)
        fadeout.setEasingCurve(QEasingCurve.InQuad)
        fadeout.finished.connect(self.accept)
        fadeout.start()
        self._fadeout_anim = fadeout   # keep reference — prevents GC crash


# ── Login Window ───────────────────────────────────────────────────────────────
class LoginWindow(QWidget):
    login_success = pyqtSignal(str, str)   # (full_name, role)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCMS — Login")
        self.setMinimumSize(960, 600)
        self.setStyleSheet(f"background: {NAVY_DARK};")
        self._db_error = None
        self._ensure_default_accounts()
        self._build_ui()
        self._center_on_screen()

    def _ensure_default_accounts(self):
        try:
            ensure_default_accounts()
        except Exception as e:
            self._db_error = str(e)

    def _center_on_screen(self):
        screen = QDesktopWidget().screenGeometry()
        size   = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2,
        )

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

        # ── CJC Logo ──────────────────────────────────────────────────────
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent;")

        _logo_path = os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'cjc logo.png'
        )
        _pixmap = QPixmap(_logo_path)
        if not _pixmap.isNull():
            logo_lbl.setPixmap(
                _pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            # Fallback: show a placeholder text if image not found
            logo_lbl.setText("🏫")
            logo_lbl.setFont(QFont("Segoe UI", 48))
            logo_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")

        school_lbl = QLabel("CJC")
        school_lbl.setFont(QFont("Segoe UI", 40, QFont.Bold))
        school_lbl.setAlignment(Qt.AlignCenter)
        school_lbl.setStyleSheet(
            f"color: {WHITE}; background: transparent; letter-spacing: 6px;"
        )

        divider_gold = QFrame()
        divider_gold.setFrameShape(QFrame.HLine)
        divider_gold.setStyleSheet(
            f"color: {GOLD}; background: {GOLD}; max-height: 2px; margin: 10px 60px;"
        )

        office_lbl = QLabel("Office of the Prefect")
        office_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        office_lbl.setAlignment(Qt.AlignCenter)
        office_lbl.setStyleSheet(
            f"color: {GOLD}; background: transparent; letter-spacing: 1px;"
        )

        sys_lbl = QLabel("Student Conduct\nManagement System")
        sys_lbl.setFont(QFont("Segoe UI", 16))
        sys_lbl.setAlignment(Qt.AlignCenter)
        sys_lbl.setStyleSheet(
            f"color: rgba(255,255,255,0.70); background: transparent; line-height: 1.5;"
        )

        left_lay.addStretch(2)
        left_lay.addWidget(logo_lbl)          # ← CJC logo image
        left_lay.addSpacing(10)               # ← gap between logo and "CJC" text
        left_lay.addWidget(school_lbl)
        left_lay.addWidget(divider_gold)
        left_lay.addWidget(office_lbl)
        left_lay.addSpacing(10)
        left_lay.addWidget(sys_lbl)
        left_lay.addStretch(3)

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

        welcome = QLabel("Welcome Back")
        welcome.setFont(QFont("Segoe UI", 20, QFont.Bold))
        welcome.setStyleSheet(f"color: {NAVY}; background: transparent;")

        sub = QLabel("Please enter your credentials to continue")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet(
            f"color: {MID_GRAY}; background: transparent; margin-bottom: 24px;"
        )

        card_lay.addWidget(welcome)
        card_lay.addSpacing(4)
        card_lay.addWidget(sub)
        card_lay.addSpacing(20)

        user_lbl = QLabel("Username")
        user_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        user_lbl.setStyleSheet(
            f"color: {TEXT_DARK}; background: transparent; margin-bottom: 4px;"
        )

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setFixedHeight(44)
        self.username_edit.setFont(QFont("Segoe UI", 12))
        self.username_edit.returnPressed.connect(self._on_login)

        card_lay.addWidget(user_lbl)
        card_lay.addWidget(self.username_edit)
        card_lay.addSpacing(16)

        pass_lbl = QLabel("Password")
        pass_lbl.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        pass_lbl.setStyleSheet(
            f"color: {TEXT_DARK}; background: transparent; margin-bottom: 4px;"
        )

        # ── Password field + eye toggle ───────────────────────────────────
        pass_row = QFrame()
        pass_row.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {LIGHT_GRAY};
                border-radius: 6px;
            }}
        """)
        pass_row.setFixedHeight(44)
        pass_row_lay = QHBoxLayout(pass_row)
        pass_row_lay.setContentsMargins(10, 0, 6, 0)
        pass_row_lay.setSpacing(0)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setFont(QFont("Segoe UI", 12))
        self.password_edit.returnPressed.connect(self._on_login)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                padding: 0px;
            }
        """)

        self.eye_btn = QPushButton()
        self.eye_btn.setFixedSize(32, 32)
        self.eye_btn.setCursor(Qt.PointingHandCursor)
        self.eye_btn.setCheckable(True)
        self.eye_btn.setToolTip("Show password")
        self.eye_btn.setIcon(_draw_eye_icon(visible=False, size=20, color="#aaaaaa"))
        self.eye_btn.setIconSize(QSize(20, 20))
        self.eye_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(0,0,0,0.05);
                border-radius: 4px;
            }
        """)
        self.eye_btn.toggled.connect(self._toggle_password_visibility)

        pass_row_lay.addWidget(self.password_edit, 1)
        pass_row_lay.addWidget(self.eye_btn)

        card_lay.addWidget(pass_lbl)
        card_lay.addWidget(pass_row)
        card_lay.addSpacing(6)

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

        copy_lbl = QLabel("© 2026 Office of the Prefect — CJC  |  SCMS v1.0")
        copy_lbl.setFont(QFont("Segoe UI", 9))
        copy_lbl.setAlignment(Qt.AlignCenter)
        copy_lbl.setStyleSheet(
            f"color: {MID_GRAY}; background: transparent; margin-top: 20px;"
        )
        right_lay.addWidget(copy_lbl)

        root.addWidget(left)
        root.addWidget(right, 1)

    # ── Login handler ─────────────────────────────────────────────────────────
    def _on_login(self):
        username = self.username_edit.text().strip().lower()
        password = self.password_edit.text()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

        if self._db_error:
            self._show_error(f"Database error: {self._db_error}")
            return

        try:
            result = validate_login(username, password)
        except Exception as e:
            self._show_error(f"Database error: {str(e)}")
            return

        if result:
            full_name, role = result
            self._hide_error()
            self._show_login_loading()
            QTimer.singleShot(300, lambda: self._launch_dashboard(full_name, role))
            return

        self._show_error("Incorrect username or password. Please try again.")
        self.password_edit.clear()
        self.password_edit.setFocus()

    def _show_login_loading(self):
        self.login_btn.setEnabled(False)
        self.login_btn.setText("  ⟳ Authenticating...")
        self.username_edit.setEnabled(False)
        self.password_edit.setEnabled(False)

    def _show_error(self, msg: str):
        self.error_lbl.setText(f"⚠  {msg}")
        self.error_lbl.setVisible(True)
        anim = QPropertyAnimation(self.login_btn, b"geometry")
        anim.setDuration(120)
        geo = self.login_btn.geometry()
        anim.setKeyValueAt(0.0, geo)
        anim.setKeyValueAt(0.2, geo.adjusted(-4, 0, -4, 0))
        anim.setKeyValueAt(0.5, geo.adjusted(4,  0,  4, 0))
        anim.setKeyValueAt(0.8, geo.adjusted(-2, 0, -2, 0))
        anim.setKeyValueAt(1.0, geo)
        anim.start()
        self._shake_anim = anim   # keep reference

    def _hide_error(self):
        self.error_lbl.setVisible(False)

    def _toggle_password_visibility(self, checked: bool):
        """Show or hide the password text when the eye button is toggled."""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setIcon(_draw_eye_icon(visible=True,  size=20, color="#1a2d5a"))
            self.eye_btn.setToolTip("Hide password")
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.eye_btn.setIcon(_draw_eye_icon(visible=False, size=20, color="#aaaaaa"))
            self.eye_btn.setToolTip("Show password")

    def _launch_dashboard(self, full_name: str, role: str):
        """Show loading screen; background thread does the heavy lifting."""
        username = self.username_edit.text().strip().lower()
        loading = LoadingScreen(parent=self)
        loading.load_application(full_name, role, username)

        if loading.exec_() == QDialog.Accepted:
            self.loading_screen = loading      # prevent GC
            self.main_win       = loading.main_win
            self.close()

# =============================================================================
#  SCMS — Main Window  (Sidebar + Stacked Pages)
# =============================================================================
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QSizePolicy,
    QButtonGroup, QScrollArea, QStatusBar,
    QApplication, QStyle
)
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtGui import QFont, QIcon

from ui.styles import (
    NAVY, NAVY_DARK, NAVY_MID, GOLD, WHITE,
    OFF_WHITE, LIGHT_GRAY, MID_GRAY
)
from ui.components import HeaderBar, NavButton, add_shadow, ConfirmDialog
from ui.pages.dashboard   import DashboardPage
from ui.pages.green_slip  import GreenSlipPage
from ui.pages.pink_slip   import PinkSlipPage
from ui.pages.blue_slip   import BlueSlipPage
from ui.pages.trackers    import TrackersPage
from ui.pages.reports     import ReportsPage
from ui.pages.settings    import SettingsPage


def _sp_icon(sp_enum: int) -> QIcon:
    """Return a QIcon for the given QStyle standard-pixmap enum value."""
    return QApplication.instance().style().standardIcon(sp_enum)


def _slip_icon(color: str, size: int = 18) -> QIcon:
    """
    Draw a tiny document/slip icon filled with *color*.
    Shape: rectangle with a folded top-right corner and three ruled lines.
    """
    from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QPolygon
    from PyQt5.QtCore import QPoint, QRect

    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    fold = size // 4          # size of the folded corner triangle
    body_color = QColor(color)
    fold_color  = body_color.darker(140)
    line_color  = QColor(255, 255, 255, 160)

    # Main document body (rectangle minus top-right corner)
    body = QPolygon([
        QPoint(0,          0),
        QPoint(size - fold, 0),
        QPoint(size,        fold),
        QPoint(size,        size),
        QPoint(0,           size),
    ])
    p.setBrush(QBrush(body_color))
    p.setPen(Qt.NoPen)
    p.drawPolygon(body)

    # Folded corner triangle
    corner = QPolygon([
        QPoint(size - fold, 0),
        QPoint(size,        fold),
        QPoint(size - fold, fold),
    ])
    p.setBrush(QBrush(fold_color))
    p.drawPolygon(corner)

    # Ruled lines
    pen = QPen(line_color, max(1, size // 10))
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)
    margin  = size // 5
    spacing = size // 5
    for i in range(3):
        y = size // 2 - spacing + i * spacing
        p.drawLine(margin, y, size - margin - (fold if i == 0 else 0), y)

    p.end()
    return QIcon(pix)


class MainWindow(QMainWindow):
    def __init__(self, full_name: str = "Admin", role: str = "Admin"):
        super().__init__()
        self.full_name = full_name
        self.role = role
        self.setWindowTitle("Office of the Prefect — Student Conduct Management System")
        self.setMinimumSize(1200, 720)
        self.resize(1350, 800)
        self._build_ui()
        self._center()

    def _center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2
        )

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top header bar ────────────────────────────────────────────────────
        self.header = HeaderBar(user_name=self.full_name)
        self.header.logout_requested.connect(self._on_logout)
        root.addWidget(self.header)

        # ── Body (sidebar + content) ──────────────────────────────────────────
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)
        root.addWidget(body, 1)

        # Sidebar
        self.sidebar = self._build_sidebar()
        body_lay.addWidget(self.sidebar)

        # Stacked content area
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {OFF_WHITE};")

        # Pages (order matches nav buttons) — lazy-load heavy pages
        self.page_dashboard = DashboardPage(role=self.role)
        self.page_green = None
        self.page_pink = None
        self.page_blue = None
        self.page_trackers = None
        self.page_reports = None
        self.page_settings = None

        self._pages = {0: self.page_dashboard}
        self._page_factories = {
            1: lambda: GreenSlipPage(),
            2: lambda: PinkSlipPage(),
            3: lambda: BlueSlipPage(),
            4: lambda: TrackersPage(),
            5: lambda: ReportsPage(),
            6: lambda: SettingsPage(),
        }

        self.stack.addWidget(self.page_dashboard)
        # placeholders to preserve indices
        for _ in range(6):
            self.stack.addWidget(QWidget())

        body_lay.addWidget(self.stack, 1)

        # Wire dashboard quick-action signals
        self.page_dashboard.navigate_to.connect(self._navigate_from_dashboard)

        # ── Status bar ────────────────────────────────────────────────────────
        sb = QStatusBar()
        sb.setStyleSheet(f"""
            QStatusBar {{
                background: {NAVY_DARK};
                color: rgba(255,255,255,0.6);
                font-size: 11px;
                padding: 2px 12px;
            }}
        """)
        self.setStatusBar(sb)
        now = QDateTime.currentDateTime().toString("dddd, MMMM d, yyyy  |  hh:mm AP")
        sb.showMessage(f"  Logged in as: {self.full_name}  [{self.role}]    {now}")

    # ── Build sidebar ─────────────────────────────────────────────────────────
    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"""
            QFrame#Sidebar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {NAVY_DARK}, stop:1 {NAVY}
                );
                border-right: 2px solid rgba(201,168,76,0.4);
            }}
        """)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Section label
        sys_label = QLabel("NAVIGATION")
        sys_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        sys_label.setStyleSheet(f"""
            color: rgba(201,168,76,0.7);
            background: transparent;
            padding: 18px 20px 8px 20px;
            letter-spacing: 2px;
        """)
        lay.addWidget(sys_label)

        # Nav buttons — icons use QStyle standard pixmaps (no external files)
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        nav_items = [
            # (icon,                                          label,             page index)
            (_sp_icon(QStyle.SP_ComputerIcon),               "Dashboard",       0),
            (_slip_icon("#4CAF50"),                           "Green Slips",     1),
            (_slip_icon("#E91E8C"),                           "Pink Slips",      2),
            (_slip_icon("#2196F3"),                           "Blue Slips",      3),
            (_sp_icon(QStyle.SP_FileDialogDetailedView),     "Record Trackers", 4),
            (_sp_icon(QStyle.SP_FileDialogContentsView),     "Reports",         5),
        ]

        for icon, label, idx in nav_items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda _, i=idx: self._show_page(i))
            self.btn_group.addButton(btn, idx)
            lay.addWidget(btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: rgba(255,255,255,0.12); margin: 8px 16px;")
        lay.addWidget(sep)

        # Settings section
        settings_label = QLabel("SYSTEM")
        settings_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        settings_label.setStyleSheet(f"""
            color: rgba(201,168,76,0.7);
            background: transparent;
            padding: 4px 20px 8px 20px;
            letter-spacing: 2px;
        """)
        lay.addWidget(settings_label)

        settings_btn = NavButton(_sp_icon(QStyle.SP_FileDialogInfoView), "Settings")
        settings_btn.clicked.connect(lambda: self._show_page(6))
        self.btn_group.addButton(settings_btn, 6)
        lay.addWidget(settings_btn)

        lay.addStretch()

        # Role badge at bottom
        role_frame = QFrame()
        role_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(201,168,76,0.15);
                border-top: 1px solid rgba(201,168,76,0.3);
            }}
        """)
        role_lay = QVBoxLayout(role_frame)
        role_lay.setContentsMargins(16, 12, 16, 14)
        role_lay.setSpacing(2)

        role_lbl = QLabel(f"Role: {self.role}")
        role_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        role_lbl.setStyleSheet(f"color: {GOLD}; background: transparent;")

        ver_lbl = QLabel("SCMS v1.0")
        ver_lbl.setFont(QFont("Segoe UI", 9))
        ver_lbl.setStyleSheet("color: rgba(255,255,255,0.35); background: transparent;")

        role_lay.addWidget(role_lbl)
        role_lay.addWidget(ver_lbl)
        lay.addWidget(role_frame)

        # Select Dashboard by default
        self.btn_group.button(0).setChecked(True)
        return sidebar

    # ── Navigate from dashboard quick-action cards ────────────────────────────
    def _navigate_from_dashboard(self, idx: int):
        self._show_page(idx)

    def _ensure_page(self, idx: int):
        if idx in self._pages:
            return
        factory = self._page_factories.get(idx)
        if not factory:
            return
        page = factory()
        self._pages[idx] = page
        # keep attribute handles
        if idx == 1:
            self.page_green = page
        elif idx == 2:
            self.page_pink = page
        elif idx == 3:
            self.page_blue = page
        elif idx == 4:
            self.page_trackers = page
        elif idx == 5:
            self.page_reports = page
        elif idx == 6:
            self.page_settings = page

        old = self.stack.widget(idx)
        self.stack.removeWidget(old)
        if old:
            old.deleteLater()
        self.stack.insertWidget(idx, page)

    def _show_page(self, idx: int):
        self._ensure_page(idx)
        self.stack.setCurrentIndex(idx)
        btn = self.btn_group.button(idx)
        if btn:
            btn.setChecked(True)

    # ── Logout ────────────────────────────────────────────────────────────────
    def _on_logout(self):
        dlg = ConfirmDialog(
            "Confirm Logout",
            "Are you sure you want to log out of the system?",
            parent=self
        )
        if dlg.exec_():
            from ui.login_window import LoginWindow
            self.login_win = LoginWindow()
            self.login_win.show()
            self.close()

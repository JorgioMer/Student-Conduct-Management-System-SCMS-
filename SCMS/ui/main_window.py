# =============================================================================
#  SCMS — Main Window  (Sidebar + Stacked Pages)
# =============================================================================
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QSizePolicy,
    QButtonGroup, QScrollArea, QStatusBar,
    QApplication, QStyle
)
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtGui import QFont, QIcon

logger = logging.getLogger(__name__)

from ui.styles import (
    NAVY, NAVY_DARK, NAVY_MID, GOLD, WHITE,
    OFF_WHITE, LIGHT_GRAY, MID_GRAY
)
from ui.components import HeaderBar, NavButton, add_shadow, ConfirmDialog

# ── Import only DashboardPage immediately (shown on startup) ─────────────────
logger.debug("  Importing DashboardPage...")
try:
    from ui.pages.dashboard import DashboardPage
    logger.debug("  DashboardPage imported successfully")
except Exception as e:
    logger.error(f"Failed to import DashboardPage: {str(e)}", exc_info=True)
    raise

# ── Lazy-load other pages (imported only when user navigates to them) ─────────
# This prevents startup from blocking on heavy page dependencies like ReportsPage
logger.debug("Page imports deferred to lazy-loading (will import on first access)")



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
    def __init__(self, full_name: str = "Admin", role: str = "Admin", username: str = "admin"):
        logger.debug("MainWindow.__init__ called...")
        super().__init__()
        
        logger.debug("Setting MainWindow properties...")
        self.full_name = full_name
        self.role = role
        self.username = username
        self.setWindowTitle("Office of the Prefect — Student Conduct Management System")
        self.setMinimumSize(1200, 720)
        self.resize(1350, 800)
        
        logger.debug("Building UI...")
        self._build_ui()
        
        logger.debug("Centering window...")
        self._center()
        
        logger.info(f"MainWindow initialized successfully for {full_name}")

    def _center(self):
        from PyQt5.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2
        )

    def _build_ui(self):
        logger.debug("_build_ui starting...")
        try:
            central = QWidget()
            self.setCentralWidget(central)
            root = QVBoxLayout(central)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(0)

            # ── Top header bar ────────────────────────────────────────────────────
            logger.debug("Creating HeaderBar...")
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
            logger.debug("Building sidebar...")
            self.sidebar = self._build_sidebar()
            body_lay.addWidget(self.sidebar)

            # Stacked content area
            logger.debug("Creating stacked widget...")
            self.stack = QStackedWidget()
            self.stack.setStyleSheet(f"background: {OFF_WHITE};")

            # Pages (order matches nav buttons) — lazy-load heavy pages
            logger.debug("Creating DashboardPage...")
            self.page_dashboard = DashboardPage(role=self.role)
            logger.debug("DashboardPage created successfully")
            
            self.page_green = None
            self.page_pink = None
            self.page_blue = None
            self.page_trackers = None
            self.page_reports = None
            self.page_logs = None
            self.page_settings = None

            self._pages = {0: self.page_dashboard}
            
            # Page factory functions for lazy-loading (import only when user navigates)
            def _make_green_slip():
                logger.debug("    Lazy-loading GreenSlipPage...")
                from ui.pages.green_slip import GreenSlipPage
                return GreenSlipPage()
            
            def _make_pink_slip():
                logger.debug("    Lazy-loading PinkSlipPage...")
                from ui.pages.pink_slip import PinkSlipPage
                return PinkSlipPage()
            
            def _make_blue_slip():
                logger.debug("    Lazy-loading BlueSlipPage...")
                from ui.pages.blue_slip import BlueSlipPage
                return BlueSlipPage()
            
            def _make_trackers():
                logger.debug("    Lazy-loading TrackersPage...")
                from ui.pages.trackers import TrackersPage
                return TrackersPage(current_user={
                    "username":  self.username,
                    "full_name": self.full_name,
                    "role":      self.role,
                })
            
            def _make_reports():
                logger.debug("    Lazy-loading ReportsPage...")
                from ui.pages.reports import ReportsPage
                return ReportsPage(current_user={
                    "username":  self.username,
                    "full_name": self.full_name,
                    "role":      self.role,
                })
            
            def _make_activity_logs():
                logger.debug("    Lazy-loading ActivityLogsPage...")
                from ui.pages.activity_logs import ActivityLogsPage
                return ActivityLogsPage()
            
            def _make_settings():
                logger.debug("    Lazy-loading SettingsPage...")
                from ui.pages.settings import SettingsPage
                return SettingsPage(current_user={
                    "username":  self.username,
                    "full_name": self.full_name,
                    "role":      self.role,
                })
            
            self._page_factories = {
                1: _make_green_slip,
                2: _make_pink_slip,
                3: _make_blue_slip,
                4: _make_trackers,
                5: _make_reports,
                6: _make_activity_logs,
                7: _make_settings,
            }

            logger.debug("Adding pages to stacked widget...")
            self.stack.addWidget(self.page_dashboard)
            # placeholders to preserve indices
            for _ in range(7):
                self.stack.addWidget(QWidget())

            body_lay.addWidget(self.stack, 1)

            # Wire dashboard quick-action signals
            logger.debug("Connecting dashboard navigation signal...")
            self.page_dashboard.navigate_to.connect(self._navigate_from_dashboard)

            # ── Status bar ────────────────────────────────────────────────────────
            logger.debug("Creating status bar...")
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
            
            logger.debug("_build_ui completed successfully")
            
        except Exception as e:
            logger.error(f"Error in _build_ui: {str(e)}", exc_info=True)
            raise

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
            (_sp_icon(QStyle.SP_FileDialogListView),         "Activity Logs",   6),
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
        settings_btn.clicked.connect(lambda: self._show_page(7))
        self.btn_group.addButton(settings_btn, 7)
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
        logger.debug(f"_ensure_page({idx}) called...")
        if idx in self._pages:
            logger.debug(f"  Page {idx} already loaded")
            return
        
        factory = self._page_factories.get(idx)
        if not factory:
            logger.warning(f"  No factory for page {idx}")
            return
        
        try:
            logger.debug(f"  Creating page {idx}...")
            page = factory()
            logger.debug(f"  Page {idx} created successfully")
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
                self.page_logs = page
            elif idx == 7:
                self.page_settings = page

            old = self.stack.widget(idx)
            self.stack.removeWidget(old)
            if old:
                old.deleteLater()
            self.stack.insertWidget(idx, page)
            logger.debug(f"  Page {idx} inserted into stack")
            
        except Exception as e:
            logger.error(f"Error loading page {idx}: {str(e)}", exc_info=True)
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error Loading Page", 
                f"Failed to load page {idx}:\n\n{str(e)}")

    def _show_page(self, idx: int):
        logger.debug(f"_show_page({idx}) called...")
        self._ensure_page(idx)
        self.stack.setCurrentIndex(idx)
        btn = self.btn_group.button(idx)
        if btn:
            btn.setChecked(True)
        logger.debug(f"  Page {idx} now displayed")

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

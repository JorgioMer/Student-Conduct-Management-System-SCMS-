"""
================================================================================
  Student Conduct Management System (SCMS)
  Office of the Prefect — CJC

  Entry Point: main.py
  Run with:  python main.py

  Requirements:
    pip install PyQt5
    pip install pyodbc

  Phase: UI Prototype with Database Integration
================================================================================
"""
import sys
import os
import ctypes
import logging
import traceback
from datetime import datetime
from PyQt5.QtGui import QIcon

# ── Setup comprehensive logging ────────────────────────────────────────────
def _setup_logging():
    """Configure logging to capture all errors and output."""
    log_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "SCMS", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"scms_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"=== SCMS Debug Log Started ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Log file: {log_file}")
    
    return logger, log_file

logger, debug_log = _setup_logging()

# ── Capture uncaught exceptions ────────────────────────────────────────────
def _exception_hook(exc_type, exc_value, exc_traceback):
    """Capture uncaught exceptions to log file."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"UNCAUGHT EXCEPTION:\n{error_msg}")
    print(f"\n[FATAL ERROR] See debug log for details: {debug_log}\n{error_msg}", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = _exception_hook

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Pre-initialize matplotlib before any UI (prevents hanging on Reports page) ──
logger.debug("Pre-initializing matplotlib...")
try:
    import matplotlib
    # Only pre-import pyplot and configure rcParams - don't set backend globally
    # Chart widgets will set their own backends (Qt5Agg for interactive, Agg for static)
    
    from matplotlib import rcParams
    # Configure matplotlib for report generation
    rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
    rcParams['figure.figsize'] = (10, 6)
    # Suppress matplotlib debug output
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
    logger.debug("  matplotlib pre-initialized successfully (backend will be set by chart modules)")
except Exception as e:
    logger.warning(f"matplotlib initialization warning (non-critical): {str(e)}")
    import traceback
    logger.debug(traceback.format_exc())

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from ui.styles import GLOBAL_STYLE
from ui.login_window import LoginWindow

# Backend modules available for import
from backend import db_connection, db_students, db_green_slip, db_blue_slip, db_pink_slip
from backend.db_init_activity_log import create_activity_log_table


def main():
    logger.info("Starting SCMS application...")
    
    try:
        # High-DPI support
        logger.debug("Configuring High-DPI support...")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # ── Force Windows taskbar to show custom icon ─────────────────────────────────
        if sys.platform == "win32":
            logger.debug("Setting Windows taskbar icon...")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "CJC.SCMS.OfficePrefect.1.0"
            )
        
        logger.debug("Creating QApplication...")
        app = QApplication(sys.argv)

        # ── App-wide icon (window + taskbar) ─────────────────────────────────────────
        logger.debug("Setting application icon and metadata...")
        _base_dir = os.path.dirname(os.path.abspath(__file__))
        _icon_path = os.path.join(_base_dir, "assets", "final-cjc-logo.png")
        if os.path.exists(_icon_path):
            app.setWindowIcon(QIcon(_icon_path))
            app.setApplicationName("SCMS — Office of the Prefect")
            app.setOrganizationName("CJC")
            logger.info(f"Icon loaded from: {_icon_path}")
        else:
            logger.warning(f"Icon not found at: {_icon_path}")

        # Global font
        logger.debug("Setting global application font...")
        app.setFont(QFont("Segoe UI", 10))

        # Apply global stylesheet
        logger.debug("Applying global stylesheet...")
        app.setStyleSheet(GLOBAL_STYLE)

        # Initialize activity log table
        logger.debug("Initializing activity log table...")
        try:
            success = create_activity_log_table()
            if not success:
                logger.warning("Activity log table initialization failed. Logging may not work.")
            else:
                logger.info("Activity log table initialized successfully.")
        except Exception as e:
            logger.error(f"Error during activity log initialization: {str(e)}", exc_info=True)

        # Show login window
        logger.debug("Creating and showing login window...")
        login = LoginWindow()
        login.show()
        logger.info("Login window displayed. Application ready.")

        logger.debug("Starting application event loop...")
        exit_code = app.exec_()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"FATAL ERROR in main(): {str(e)}", exc_info=True)
        print(f"\n[FATAL ERROR] Application crashed. Debug log: {debug_log}\n{traceback.format_exc()}", file=sys.stderr)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Application terminated with error: {str(e)}", exc_info=True)
        sys.exit(1)

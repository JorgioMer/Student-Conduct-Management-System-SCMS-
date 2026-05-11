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
from PyQt5.QtGui import QIcon

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from ui.styles import GLOBAL_STYLE
from ui.login_window import LoginWindow

# Backend modules available for import
from backend import db_connection, db_students, db_green_slip, db_blue_slip, db_pink_slip
from backend.db_init_activity_log import create_activity_log_table


def main():
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # ── Force Windows taskbar to show custom icon ─────────────────────────────────
    if sys.platform == "win32":
      ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "CJC.SCMS.OfficePrefect.1.0"
    )
    
    app = QApplication(sys.argv)

    # ── App-wide icon (window + taskbar) ─────────────────────────────────────────
    _base_dir = os.path.dirname(os.path.abspath(__file__))
    _icon_path = os.path.join(_base_dir, "assets", "final-cjc-logo.png")
    _app_icon = None
    if os.path.exists(_icon_path):
      _app_icon = QIcon(_icon_path)
      app.setWindowIcon(_app_icon)
      # Store icon as app property to prevent garbage collection
      app._app_icon = _app_icon
      app.setApplicationName("SCMS — Office of the Prefect")
      app.setOrganizationName("CJC")

    # Global font
    app.setFont(QFont("Segoe UI", 10))

    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLE)

    # Initialize activity log table
    try:
        success = create_activity_log_table()
        if not success:
            print("⚠ Warning: Activity log table initialization failed. Logging may not work.")
    except Exception as e:
        print(f"⚠ Error during activity log initialization: {str(e)}")

    # Show login window
    login = LoginWindow()
    # Set icon on login window
    if _app_icon:
        login.setWindowIcon(_app_icon)
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

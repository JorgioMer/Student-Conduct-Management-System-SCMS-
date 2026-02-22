"""
================================================================================
  Student Conduct Management System (SCMS)
  Office of the Prefect — CJC

  Entry Point: main.py
  Run with:  python main.py

  Requirements:
    pip install PyQt5

  Phase: UI Prototype (No database/backend)
================================================================================
"""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.styles import GLOBAL_STYLE
from ui.login_window import LoginWindow


def main():
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("SCMS — Office of the Prefect")
    app.setOrganizationName("CJC")

    # Global font
    app.setFont(QFont("Segoe UI", 10))

    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLE)

    # Show login window
    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

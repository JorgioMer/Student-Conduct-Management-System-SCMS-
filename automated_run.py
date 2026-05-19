import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# Add current directory to path
sys.path.append(os.getcwd())

from SCMS.views.login_view import LoginView
from SCMS.controllers.login_controller import LoginController

def run_test():
    app = QApplication(sys.argv)
    
    login_view = LoginView()
    # Mocking the controller to handle navigation
    # In the real app, LoginController handles this.
    # We'll just trigger the login button and hope the logic follows.
    
    login_view.show()
    
    def perform_actions():
        print("Typing credentials...")
        login_view.ui.id_input.setText("1")
        login_view.ui.password_input.setText("password")
        
        print("Clicking login...")
        QTest.mouseClick(login_view.ui.login_button, Qt.MouseButton.LeftButton)
        
        # Wait for main window to appear
        QTimer.singleShot(5000, check_main_window)

    def check_main_window():
        print("Checking for main window...")
        main_window = None
        for widget in QApplication.topLevelWidgets():
            # Check if it's the main window (usually MainWindow class)
            if "MainWindow" in str(type(widget)):
                main_window = widget
                break
        
        if main_window:
            print("Main window found!")
            # 3. Click Reports
            print("Clicking Reports...")
            # Note: UI attribute names might vary, checking common names
            reports_btn = getattr(main_window.ui, 'nav_reports', None) or getattr(main_window.ui, 'reports_btn', None)
            if reports_btn:
                QTest.mouseClick(reports_btn, Qt.MouseButton.LeftButton)
            
            # 4. Click Trackers
            QTimer.singleShot(3000, lambda: click_trackers(main_window))
        else:
            print("Main window not found. Login might have failed or is slow.")
            app.quit()

    def click_trackers(main_window):
        print("Clicking Trackers...")
        trackers_btn = getattr(main_window.ui, 'nav_trackers', None) or getattr(main_window.ui, 'trackers_btn', None)
        if trackers_btn:
            QTest.mouseClick(trackers_btn, Qt.MouseButton.LeftButton)
        
        QTimer.singleShot(5000, lambda: app.quit())

    QTimer.singleShot(2000, perform_actions)
    
    # Safety timeout
    QTimer.singleShot(25000, app.quit)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    run_test()

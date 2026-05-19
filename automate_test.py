import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest
from SCMS.main import SCMSApp
from SCMS.views.login_view import LoginView

def automation():
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        login_view = LoginView()
        login_view.show()
        
        # 1. Login
        print("Logging in...")
        login_view.ui.id_input.setText("1")
        login_view.ui.password_input.setText("password")
        QTest.mouseClick(login_view.ui.login_button, Qt.MouseButton.LeftButton)
        
        # Small wait for main window
        time.sleep(2)
        
        # Access the main window (it should be stored somewhere or we find it)
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.objectName() == "MainWindow" or "SCMS" in widget.windowTitle():
                main_window = widget
                break
        
        if main_window:
            print("Main window found.")
            # 3. Click Reports button
            print("Clicking Reports button...")
            if hasattr(main_window.ui, 'reports_btn'):
                QTest.mouseClick(main_window.ui.reports_btn, Qt.MouseButton.LeftButton)
                time.sleep(2)
            
            # 4. Click Trackers button
            print("Clicking Trackers button...")
            if hasattr(main_window.ui, 'trackers_btn'):
                QTest.mouseClick(main_window.ui.trackers_btn, Qt.MouseButton.LeftButton)
                time.sleep(2)
        else:
            print("Main window NOT found.")
            
        print("Automation finished.")
        app.quit()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # This is a bit tricky to run within the existing app structure without modifying SCMS/main.py
    # Let's try to run a modified version of main.py logic
    pass

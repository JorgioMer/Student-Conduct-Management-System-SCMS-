@echo off
"C:\Program Files\Python313\python.exe" -m pip install --only-binary=all reportlab PyQt5 matplotlib Pillow
echo Core deps installed. pyodbc requires C++ Build Tools (download from https://visualstudio.microsoft.com/visual-cpp-build-tools/)
echo Rerun SCMS/main.py to test - reportlab error should be gone.
pause


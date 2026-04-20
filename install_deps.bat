@echo off
"C:\Program Files\Python313\python.exe" -m pip install --only-binary=all -r requirements.txt || "C:\Program Files\Python313\python.exe" -m pip install reportlab PyQt5 matplotlib Pillow
echo Installation complete (pyodbc needs C++ tools). Rerun SCMS/main.py
pause



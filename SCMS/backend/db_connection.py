import os
import sys
import shutil
import pyodbc

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "SCMS")
LOCAL_DB_PATH = os.path.join(DATA_DIR, "SMCSDatabase.accdb")


def _template_db_candidates():
    candidates = []

    # Source layout (dev)
    candidates.append(os.path.join(BACKEND_DIR, "database", "SMCSDatabase.accdb"))

    # PyInstaller one-file/one-folder extraction
    if hasattr(sys, "_MEIPASS"):
        candidates.append(os.path.join(sys._MEIPASS, "backend", "database", "SMCSDatabase.accdb"))

    return candidates


def ensure_local_database():
    """Create a local writable DB copy if it doesn't exist."""
    if os.path.exists(LOCAL_DB_PATH):
        return LOCAL_DB_PATH

    os.makedirs(DATA_DIR, exist_ok=True)

    for candidate in _template_db_candidates():
        if os.path.exists(candidate):
            shutil.copy2(candidate, LOCAL_DB_PATH)
            return LOCAL_DB_PATH

    raise FileNotFoundError("Database template not found for initialization.")


DB_PATH = ensure_local_database()

def get_connection():
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str)

import os
import sys
import shutil
import pyodbc


def _get_base_path() -> str:
    """
    Returns the directory containing SCMS.exe when frozen,
    or the directory of this .py file during development.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller one-folder: sys.executable = .../SCMS/SCMS.exe
        return os.path.dirname(sys.executable)
    # Dev: this file lives at SCMS/backend/database_connection.py
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = _get_base_path()

# ── AppData: where the user's live database lives ─────────────────────────
DATA_DIR      = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "SCMS")
LOCAL_DB_PATH = os.path.join(DATA_DIR, "SCMSDatabase.accdb")   # FIX: was SMCSDatabase


def _template_db_candidates() -> list[str]:
    """
    Ordered list of locations to look for the blank/template database.
    The first one that exists will be used to seed the user's AppData copy.
    """
    return [
        # PyInstaller one-folder build  →  SCMS\backend\database\SCMSDatabase.accdb
        os.path.join(BASE_PATH, "backend", "database", "SCMSDatabase.accdb"),

        # Dev layout  →  <repo>\SCMS\backend\database\SCMSDatabase.accdb
        os.path.join(BASE_PATH, "database", "SCMSDatabase.accdb"),

        # PyInstaller one-FILE bundle (_MEIPASS temp dir) — keep as last resort
        *(
            [os.path.join(sys._MEIPASS, "backend", "database", "SCMSDatabase.accdb")]
            if hasattr(sys, "_MEIPASS")
            else []
        ),
    ]


def ensure_local_database() -> str:
    """
    Copies the blank template database into AppData\SCMS\ on first run.
    Subsequent runs skip the copy and return the existing path.
    Returns the path to the user's writable database.
    Raises FileNotFoundError if no template can be located.
    """
    if os.path.exists(LOCAL_DB_PATH):
        return LOCAL_DB_PATH

    os.makedirs(DATA_DIR, exist_ok=True)

    for candidate in _template_db_candidates():
        if os.path.exists(candidate):
            shutil.copy2(candidate, LOCAL_DB_PATH)
            print(f"[SCMS] Database initialised from: {candidate}")
            return LOCAL_DB_PATH

    # Nothing found — give the developer a useful error with all paths checked
    checked = "\n  ".join(_template_db_candidates())
    raise FileNotFoundError(
        f"Database template not found. Locations checked:\n  {checked}\n"
        f"BASE_PATH resolved to: {BASE_PATH}"
    )


DB_PATH = ensure_local_database()


def get_connection() -> pyodbc.Connection:
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str)
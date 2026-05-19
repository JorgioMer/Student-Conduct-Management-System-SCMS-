import os
import sys
import shutil
import pyodbc
import platform


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


def _check_access_driver_available() -> bool:
    """
    Check if the Microsoft Access Driver is installed on this system.
    Returns True if available, False otherwise.
    """
    try:
        sources = pyodbc.dataSources()
        # Check for any of the valid Access driver names
        valid_drivers = [
            "Microsoft Access Driver (*.mdb, *.accdb)",
            "Microsoft Access Driver (*.mdb)",
            "Microsoft Access dBASE Driver (*.dbf, *.ndx, *.mdx)",
        ]
        return any(driver in sources for driver in valid_drivers)
    except Exception:
        pass
    
    # Alternative check using pyodbc drivers list
    try:
        drivers = pyodbc.drivers()
        valid_drivers = [
            "Microsoft Access Driver (*.mdb, *.accdb)",
            "Microsoft Access Driver (*.mdb)",
        ]
        for valid_driver in valid_drivers:
            if valid_driver in drivers:
                return True
        return False
    except Exception:
        return False


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
    r"""
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
            try:
                shutil.copy2(candidate, LOCAL_DB_PATH)
                print(f"[OK] Database initialised from: {candidate}")
                return LOCAL_DB_PATH
            except Exception as e:
                print(f"[ERROR] Failed to copy database template: {str(e)}")
                raise

    # Nothing found — give the developer a useful error with all paths checked
    checked = "\n  ".join(_template_db_candidates())
    error_msg = (
        f"[ERROR] Database template not found. Locations checked:\n  {checked}\n"
        f"BASE_PATH resolved to: {BASE_PATH}\n"
        f"LOCAL_DB_PATH would be: {LOCAL_DB_PATH}"
    )
    print(error_msg)
    raise FileNotFoundError(error_msg)


DB_PATH = ensure_local_database()


def get_connection() -> pyodbc.Connection:
    """
    Create and return a pyodbc connection to the SCMS database.
    
    Raises:
        RuntimeError: If Microsoft Access Driver is not installed
        pyodbc.Error: If connection fails for other reasons
    """
    # Check if driver is available before attempting connection
    if not _check_access_driver_available():
        error_msg = (
            "Microsoft Access Driver is not installed on this system.\n\n"
            "SOLUTION:\n"
            "1. Download 'Microsoft Access Database Engine 2016' (32-bit or 64-bit, matching your Office or Windows)\n"
            "   From: https://www.microsoft.com/download/details.aspx?id=54920\n\n"
            "2. Or install Microsoft Office (which includes Access drivers)\n\n"
            "3. Restart the application after installation\n"
        )
        raise RuntimeError(error_msg)
    
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        if "not found" in str(e) or "cannot find" in str(e).lower():
            raise RuntimeError(f"Database file not found at: {DB_PATH}") from e
        elif "driver" in str(e).lower():
            raise RuntimeError(
                "Microsoft Access Driver not properly installed.\n"
                "Please install Microsoft Access Database Engine 2016 or Microsoft Office."
            ) from e
        else:
            raise
import pyodbc
import os

# Path to your Access database file
# Get the directory where this file is located
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "database", "SMCSDatabase.accdb")

def get_connection():
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str)

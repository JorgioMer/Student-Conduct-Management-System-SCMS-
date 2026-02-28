import pyodbc

# Path to your Access database file
DB_PATH = r"SCMS\backend\database\SMCSDatabase.accdb"

def get_connection():
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str)

from datetime import datetime

from .db_connection import get_connection


DEFAULT_ACCOUNTS = [
    ("admin", "Administrator", "admin123", "Admin", "Active"),
    ("staff", "Office Staff", "staff123", "Staff", "Active"),
]


def get_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT accUserName, accFullName, accRole, accStatus, loginTime
        FROM Accounts
        ORDER BY accUserName
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_account_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT accUserName, accFullName, accPass, accRole, accStatus, loginTime
        FROM Accounts
        WHERE accUserName = ?
        """,
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def add_account(username, full_name, password, role, status="Active"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Accounts (accUserName, accFullName, accPass, accRole, accStatus)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, full_name, password, role, status),
    )
    conn.commit()
    conn.close()


def update_login_time(username, when=None):
    login_time = when or datetime.now()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Accounts
        SET loginTime = ?
        WHERE accUserName = ?
        """,
        (login_time, username),
    )
    conn.commit()
    conn.close()


def validate_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT accUserName, accFullName, accRole, accStatus
        FROM Accounts
        WHERE accUserName = ? AND accPass = ?
        """,
        (username, password),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    acc_user, full_name, role, status = row
    if status and str(status).lower() != "active":
        return None

    update_login_time(acc_user)
    return full_name, role


def ensure_default_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Accounts")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            """
            INSERT INTO Accounts (accUserName, accFullName, accPass, accRole, accStatus)
            VALUES (?, ?, ?, ?, ?)
            """,
            DEFAULT_ACCOUNTS,
        )
        conn.commit()
    conn.close()

def update_account_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Accounts
        SET accPass = ?
        WHERE accUserName = ?
        """,
        (new_password, username),
    )
    conn.commit()
    conn.close()

def update_account(username, full_name, role, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Accounts
        SET accFullName = ?, accRole = ?, accStatus = ?
        WHERE accUserName = ?
        """,
        (full_name, role, status, username),
    )
    conn.commit()
    conn.close()


def delete_account(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Accounts WHERE accUserName = ?",
        (username,),
    )
    conn.commit()
    conn.close()
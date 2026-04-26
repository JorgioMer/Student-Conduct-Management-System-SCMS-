from datetime import datetime

from .db_connection import get_connection


DEFAULT_ACCOUNTS = [
    ("admin", "Administrator", "admin123", "Admin", "Active"),
    ("staff", "Office Staff", "staff123", "Staff", "Active"),
]


def get_accounts():
    conn = None
    try:
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
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve accounts: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_account_by_username(username):
    conn = None
    try:
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
        return row
    except Exception as e:
        raise Exception(f"Failed to retrieve account {username}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def add_account(username, full_name, password, role, status="Active"):
    conn = None
    try:
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
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to add account {username}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def update_login_time(username, when=None):
    login_time = when or datetime.now()
    conn = None
    try:
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
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update login time for {username}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def validate_login(username, password):
    conn = None
    try:
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

        if not row:
            return None

        acc_user, full_name, role, status = row
        if not status or str(status).lower() != "active":
            return None

        update_login_time(acc_user)
        return full_name, role
    except Exception as e:
        raise Exception(f"Login validation failed: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def ensure_default_accounts():
    conn = None
    try:
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
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to ensure default accounts: {str(e)}") from e
    finally:
        if conn:
            conn.close()

def update_account_password(username, new_password):
    conn = None
    try:
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
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update password for {username}: {str(e)}") from e
    finally:
        if conn:
            conn.close()

def update_account(username, full_name, role, status):
    conn = None
    try:
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
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update account {username}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def delete_account(username):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Accounts WHERE accUserName = ?",
            (username,),
        )
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete account {username}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_officer_names() -> list:
    """
    Return a list of full names (accFullName) from the Accounts table
    where the account is Active.  Used to populate officer dropdowns
    on all slip forms.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT accFullName FROM Accounts "
            "WHERE accStatus = 'Active' "
            "ORDER BY accFullName"
        )
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows if r[0]]
    except Exception as e:
        print(f"[db_accounts] get_officer_names error: {e}")
        return []
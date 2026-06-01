from .db_connection import get_connection
from .db_students import add_student_if_not_exists
import datetime as _dt
from datetime import datetime


# ---------------------------------------------------------------------------
# Module-level date parser — handles every shape pyodbc + Access can produce:
#   - Native datetime.datetime  ("2026-05-27 00:00:00")
#   - Native datetime.date      ("2026-05-27")
#   - "YYYY-MM-DD"  ISO string  (pink / blue slips)
#   - "DD/MM/YYYY"  string      (Access regional default — green slips on new PCs)
#   - "MM/DD/YYYY"  string      (rare US-locale variant)
#   - Datetime string with trailing time  ("2026-05-27 00:00:00")
#   - None / empty string       (returns None safely)
#
# Keeping this at module level means db_green_slip, reports_page, and any
# future caller all share exactly the same logic with no duplication.
# ---------------------------------------------------------------------------
def _parse_date(raw):
    """
    Parse any date value returned by pyodbc into a datetime.date object.
    Returns None if the value is empty or unparseable.
    """
    if raw is None:
        return None
    # Native date/datetime objects — no string parsing needed
    if isinstance(raw, datetime):           # datetime.datetime
        return raw.date()
    if isinstance(raw, _dt.date):           # datetime.date (not datetime subclass)
        return raw
    # String path
    s = str(raw).strip()
    if s in ("", "None", "N/A"):
        return None
    # Drop any trailing time component ("2026-05-27 00:00:00" -> "2026-05-27")
    s = s.split()[0]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def check_and_update_expired_green_slips():
    """
    Automatically update expired Green Slip statuses.
    Updates status from "Active" to "Expired" if the expiry date has passed.

    Returns:
        int: Number of slips that were updated
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()

        cursor.execute("""
            SELECT [ID], [exprDate_greenDisp], [status_green]
            FROM [Green Slip Record]
            WHERE [status_green] = 'Active' AND [exprDate_greenDisp] IS NOT NULL
        """)

        active_slips  = cursor.fetchall()
        expired_count = 0

        for slip in active_slips:
            slip_id     = slip[0]
            expiry_date = _parse_date(slip[1])   # use the shared parser

            if expiry_date is None:
                continue

            try:
                if expiry_date < today:
                    cursor.execute("""
                        UPDATE [Green Slip Record]
                        SET [status_green] = 'Expired'
                        WHERE [ID] = ?
                    """, (slip_id,))
                    expired_count += 1
            except Exception as slip_error:
                print(f"[WARNING] Error processing slip {slip_id}: {str(slip_error)}")
                continue

        if expired_count > 0:
            conn.commit()

        return expired_count

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to check and update expired green slips: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def add_green_slip(stud_num, slip_type, date_avail,
                   days, status, expiry, purpose,
                   remarks, absence_type, dates_absence,
                   supp_doc, auth_by, stud_name="", stud_course="", stud_year=""):
    """
    Add a Green Slip record to the database.

    slip_type: "Dispensation" or "Excuse"
    - Dispensation => slipType_green = True  (Yes)
    - Excuse        => slipType_green = False (No)

    Automatically adds the student if they don't exist.
    """
    add_student_if_not_exists(stud_num, name=stud_name, course=stud_course, year=stud_year)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # FIX: Cast bool to int explicitly.
        # Python bool (True/False) causes a "Data type mismatch" error on
        # some versions of the Microsoft Access ODBC driver when inserting
        # into a Yes/No field. Passing 1/0 (integer) works on every version.
        is_dispensation = 1 if slip_type.lower() == "dispensation" else 0

        cursor.execute("""
            INSERT INTO [Green Slip Record]
            (studNumber, slipType_green, dateAvail_green,
             daysOfAbs_greenDisp, status_green, exprDate_greenDisp,
             purpose_greenDisp, remarks_greenExc,
             absceneType_greenExc, datesOfAbs_greenExc,
             suppDoc_greenExc, authBy_green)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stud_num, is_dispensation, date_avail, days, status,
              expiry, purpose, remarks, absence_type,
              dates_absence, supp_doc, auth_by))
        conn.commit()

        cursor.execute("SELECT @@IDENTITY AS id")
        result    = cursor.fetchone()
        record_id = str(result[0]) if result else None
        return record_id

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to add green slip for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_green_slips(student_number):
    """
    Return green slip rows joined with student info.

    Column order (0-indexed):
      [0]  ID
      [1]  studNumber
      [2]  studName
      [3]  studYrLvl
      [4]  studCourse
      [5]  slipType_green        (True = Dispensation, False = Excuse)
      [6]  dateAvail_green       <- primary date field (Date/Time or text "DD/MM/YYYY")
      [7]  daysOfAbs_greenDisp
      [8]  exprDate_greenDisp
      [9]  status_green
      [10] datesOfAbs_greenExc   <- "YYYY-MM-DD to YYYY-MM-DD" for Excuse slips

    Always use resolve_green_slip_date(record) for date filtering —
    never index into [6] directly — because the raw value shape varies
    by PC locale and ODBC driver version.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        base_select = """
            SELECT g.[ID], g.[studNumber], s.[studName], s.[studYrLvl], s.[studCourse],
                   g.[slipType_green], g.[dateAvail_green], g.[daysOfAbs_greenDisp],
                   g.[exprDate_greenDisp], g.[status_green], g.[datesOfAbs_greenExc]
            FROM Students s
            INNER JOIN [Green Slip Record] g
                   ON s.[studNumber] = g.[studNumber]
        """

        if student_number is None:
            cursor.execute(base_select)
        else:
            cursor.execute(base_select + " WHERE g.[studNumber] = ?", (student_number,))

        rows = cursor.fetchall()
        return rows

    except Exception as e:
        raise Exception(f"Failed to retrieve green slips: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def resolve_green_slip_date(record):
    """
    Return a datetime.date for a green slip record (as returned by get_green_slips).

    Resolution order:
      1. dateAvail_green  (index 6) — works for Dispensation and Excuse alike.
         Raw value may be a native datetime/date object OR a locale-formatted
         string ("27/05/2026" on Access-default regional settings, "2026-05-27"
         on ISO systems).  _parse_date() handles all variants.
      2. Start date parsed from datesOfAbs_greenExc  (index 10) — Excuse fallback.
         Stored as "YYYY-MM-DD to YYYY-MM-DD".
      3. None if neither field yields a parseable date.
    """
    # Primary: dateAvail_green
    result = _parse_date(record[6] if len(record) > 6 else None)
    if result:
        return result

    # Fallback: start of datesOfAbs_greenExc range
    dates_of_abs = record[10] if len(record) > 10 else None
    if dates_of_abs and " to " in str(dates_of_abs):
        result = _parse_date(str(dates_of_abs).split(" to ")[0].strip())
        if result:
            return result

    return None


def delete_green_slip(slip_id):
    """Delete a specific green slip record by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM [Green Slip Record]
            WHERE ID = ?
        """, (slip_id,))
        conn.commit()
        rows_deleted = cursor.rowcount
        if rows_deleted == 0:
            raise Exception(f"No green slip found with ID {slip_id}")
        return rows_deleted
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete green slip with ID {slip_id}: {str(e)}") from e
    finally:
        if conn:
            conn.close()
from .db_connection import get_connection
from .db_students import add_student_if_not_exists
from datetime import datetime


def check_and_update_expired_green_slips():
    """
    Automatically update expired Green Slip statuses.
    Checks all green slips and updates status from "Active" to "Expired"
    if the expiry date has passed.

    Returns:
        int: Number of slips that were expired and updated
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

        active_slips = cursor.fetchall()
        expired_count = 0

        for slip in active_slips:
            slip_id     = slip[0]
            expiry_date = slip[1]

            try:
                if isinstance(expiry_date, str):
                    date_str = expiry_date.split()[0]
                    try:
                        expiry_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    except ValueError:
                        try:
                            expiry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            expiry_date = datetime.strptime(date_str, '%m/%d/%Y').date()
                elif hasattr(expiry_date, 'date'):
                    expiry_date = expiry_date.date()

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

        is_dispensation = slip_type.lower() == "dispensation"

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
      [6]  dateAvail_green       <- filing date; primary date field for filtering
      [7]  daysOfAbs_greenDisp
      [8]  exprDate_greenDisp
      [9]  status_green
      [10] datesOfAbs_greenExc   <- "YYYY-MM-DD to YYYY-MM-DD" for Excuse slips

    For period filtering use resolve_green_slip_date() which handles both
    the Dispensation (index 6) and Excuse (index 10 fallback) cases cleanly.
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


# ---------------------------------------------------------------------------
# Shared helper — resolve the single representative date for a green slip row.
# Import this in reports_page instead of inline date-parsing logic.
# ---------------------------------------------------------------------------
def resolve_green_slip_date(record):
    """
    Return a datetime.date for a green slip record (as returned by get_green_slips).

    Resolution order:
      1. dateAvail_green  (index 6)  -- works for both slip types
      2. START portion of datesOfAbs_greenExc (index 10) -- Excuse-slip fallback
      3. None if neither can be parsed

    This centralises all green-slip date logic so reports_page, the tracker,
    and anywhere else never have to duplicate or guess at indexes.
    """
    def _parse(raw):
        if not raw or str(raw).strip() in ("", "None", "N/A"):
            return None
        s = str(raw).strip().split()[0]   # drop any trailing time component
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    # Primary: dateAvail_green
    result = _parse(record[6] if len(record) > 6 else None)
    if result:
        return result

    # Fallback: start date of datesOfAbs_greenExc range
    dates_of_abs = record[10] if len(record) > 10 else None
    if dates_of_abs and " to " in str(dates_of_abs):
        result = _parse(str(dates_of_abs).split(" to ")[0].strip())
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
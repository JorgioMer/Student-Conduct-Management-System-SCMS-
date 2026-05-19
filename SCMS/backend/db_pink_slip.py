from .db_connection import get_connection
from .db_students import add_student_if_not_exists


def add_pink_slip(stud_num, date_issued, violation, action_taken, officer, sem="", 
                  remarks="", stud_name="", stud_course="", stud_year=""):
    """
    Add a Pink Slip record to the database.
    Automatically adds the student if they don't exist.
    """
    # First, add student if they don't exist
    add_student_if_not_exists(stud_num, name=stud_name, course=stud_course, year=stud_year)
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO [Pink Slip Record]
            (studNumber, dateIssued_pink, violation_pink, 
             actionTaken_pink, offcInCharge_pink, sem_pink, remarks_pink)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (stud_num, date_issued, violation, action_taken, officer, sem, remarks))
        conn.commit()
        
        # Get the ID of the newly inserted record
        cursor.execute("SELECT @@IDENTITY AS id")
        result = cursor.fetchone()
        record_id = str(result[0]) if result else None
        return record_id
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to add pink slip for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_pink_slips(student_number):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if student_number is None:
            # Return ALL pink slips
            cursor.execute("""
                SELECT s.studName, s.studCourse,
                       s.studYrLvl, p.*
                FROM Students s
                INNER JOIN [Pink Slip Record] p 
                       ON s.studNumber = p.studNumber
            """)
        else:
            # Return slips for specific student
            cursor.execute("""
                SELECT s.studName, s.studCourse,
                       s.studYrLvl, p.*
                FROM Students s
                INNER JOIN [Pink Slip Record] p 
                       ON s.studNumber = p.studNumber
                WHERE p.studNumber = ?
            """, (student_number,))
        
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve pink slips: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def has_pink_slip_for_semester(stud_num, semester):
    """
    Check if a student already has a Pink Slip for a given semester.
    
    Args:
        stud_num: Student number
        semester: Semester string (e.g., "1st", "2nd", "Summer")
    
    Returns:
        True if student already has a pink slip for this semester, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as cnt
            FROM [Pink Slip Record]
            WHERE studNumber = ? AND sem_pink = ?
        """, (stud_num, semester))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        return count > 0
    except Exception as e:
        raise Exception(f"Failed to check pink slip for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_pink_slips_for_semester(stud_num, semester):
    """
    Get all Pink Slip records for a student in a given semester.
    
    Args:
        stud_num: Student number
        semester: Semester string (e.g., "1st", "2nd", "Summer")
    
    Returns:
        List of pink slip records for the student in that semester
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.studName, s.studCourse,
                   s.studYrLvl, p.*
            FROM Students s
            INNER JOIN [Pink Slip Record] p 
                   ON s.studNumber = p.studNumber
            WHERE p.studNumber = ? AND p.sem_pink = ?
        """, (stud_num, semester))
        
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve pink slips for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def delete_pink_slip(stud_num):
    """Delete a pink slip record for a specific student."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM [Pink Slip Record]
            WHERE studNumber = ?
        """, (stud_num,))
        conn.commit()
        rows_deleted = cursor.rowcount
        if rows_deleted == 0:
            raise Exception(f"No pink slip found for student {stud_num}")
        return rows_deleted
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete pink slip for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()

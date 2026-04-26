from .db_connection import get_connection
from .db_students import add_student_if_not_exists


def add_blue_slip(stud_num, violation_type, date_of_violation, severity, 
                  action_taken, status="Open / Pending", violation_desc="", 
                  witnesses="", stud_name="", stud_course="", stud_year=""):
    """
    Add a Blue Slip violation record to the database.
    Automatically adds the student if they don't exist.
    """
    # First, add student if they don't exist
    add_student_if_not_exists(stud_num, name=stud_name, course=stud_course, year=stud_year)
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO [Blue Slip Record]
            (studNumber, violationType_blue, dateOfViolation_blue, 
             severityLvl_blue, actionTaken_blue, status_blue, 
             violationDesc_blue, witnesses_blue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (stud_num, violation_type, date_of_violation, severity, 
              action_taken, status, violation_desc, witnesses))
        conn.commit()
        
        # Get the ID of the newly inserted record
        cursor.execute("SELECT @@IDENTITY AS id")
        result = cursor.fetchone()
        record_id = str(result[0]) if result else None
        return record_id
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to add blue slip for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_blue_slips(student_number):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if student_number is None:
            # Return ALL blue slips
            cursor.execute("""
                SELECT s.studName, s.studCourse,
                       s.studYrLvl, b.*
                FROM Students s
                INNER JOIN [Blue Slip Record] b
                       ON s.studNumber = b.studNumber
            """)
        else:
            # Return slips for specific student
            cursor.execute("""
                SELECT s.studName, s.studCourse,
                       s.studYrLvl, b.*
                FROM Students s
                INNER JOIN [Blue Slip Record] b
                       ON s.studNumber = b.studNumber
                WHERE b.studNumber = ?
            """, (student_number,))
        
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve blue slips: {str(e)}") from e
    finally:
        if conn:
            conn.close()

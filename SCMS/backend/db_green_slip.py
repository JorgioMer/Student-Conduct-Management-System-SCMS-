from .db_connection import get_connection
from .db_students import add_student_if_not_exists


def add_green_slip(stud_num, slip_type, date_avail, 
                   days, status, expiry, purpose, 
                   remarks, absence_type, dates_absence, 
                   supp_doc, auth_by, stud_name="", stud_course="", stud_year=""):
    """
    Add a Green Slip record to the database.
    
    slip_type: "Dispensation" or "Excuse"
    - Dispensation → slipType_green = True (Yes)
    - Excuse → slipType_green = False (No)
    
    Automatically adds the student if they don't exist.
    """
    # First, add student if they don't exist
    add_student_if_not_exists(stud_num, name=stud_name, course=stud_course, year=stud_year)
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Convert slip_type to Yes/No boolean for Access database
        # Dispensation = True (Yes), Excuse = False (No)
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
        
        # Get the ID of the newly inserted record
        cursor.execute("SELECT @@IDENTITY AS id")
        result = cursor.fetchone()
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
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if student_number is None:
            # Return ALL green slips
            cursor.execute("""
                SELECT s.studName, s.studCourse, 
                       s.studYrLvl, g.*
                FROM Students s
                INNER JOIN [Green Slip Record] g 
                       ON s.studNumber = g.studNumber
            """)
        else:
            # Return slips for specific student
            cursor.execute("""
                SELECT s.studName, s.studCourse, 
                       s.studYrLvl, g.*
                FROM Students s
                INNER JOIN [Green Slip Record] g 
                       ON s.studNumber = g.studNumber
                WHERE g.studNumber = ?
            """, (student_number,))
        
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve green slips: {str(e)}") from e
    finally:
        if conn:
            conn.close()

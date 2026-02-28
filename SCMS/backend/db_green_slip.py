from .db_connection import get_connection
from .db_students import add_student_if_not_exists


def add_green_slip(stud_num, slip_type, date_avail, 
                   days, status, expiry, purpose, 
                   remarks, absence_type, dates_absence, 
                   supp_doc, auth_by, stud_name="", stud_course="", stud_year="", semester=""):
    """
    Add a Green Slip record to the database.
    
    slip_type: "Dispensation" or "Excuse"
    - Dispensation → slipType_green = True (Yes)
    - Excuse → slipType_green = False (No)
    
    Automatically adds the student if they don't exist.
    """
    # First, add student if they don't exist
    add_student_if_not_exists(stud_num, name=stud_name, course=stud_course, year=stud_year, semester=semester)
    
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
    conn.close()


def get_green_slips(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.studName, s.studCourse, 
               s.studYrLvl, g.*
        FROM Students s
        INNER JOIN [Green Slip Record] g 
               ON s.studNumber = g.studNumber
        WHERE g.studNumber = ?
    """, (student_number,))
    rows = cursor.fetchall()
    conn.close()
    return rows

from .db_connection import get_connection
from .db_students import add_student_if_not_exists


def add_pink_slip(stud_num, date_issued, violation, action_taken, officer, sem="", 
                  remarks="", stud_name="", stud_course="", stud_year=""):
    """
    Add a Pink Slip record to the database.
    Automatically adds the student if they don't exist.
    """
    try:
        # First, add student if they don't exist
        add_student_if_not_exists(stud_num, name=stud_name, course=stud_course, year=stud_year)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO [Pink Slip Record]
            (studNumber, dateIssued_pink, violation_pink, 
             actionTaken_pink, offcInCharge_pink, sem_pink, remarks_pink)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (stud_num, date_issued, violation, action_taken, officer, sem, remarks))
        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception(f"Failed to add pink slip for student {stud_num}: {str(e)}")


def get_pink_slips(student_number):
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
    conn.close()
    return rows

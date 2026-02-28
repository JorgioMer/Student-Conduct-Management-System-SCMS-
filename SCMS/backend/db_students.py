from .db_connection import get_connection


def add_student(stud_num, name, course, year, semester, school_yr, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Students 
        (studNumber, studName, studCourse, 
         studYrLvl, semester, schoolYr, studStatus)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (stud_num, name, course, year, semester, school_yr, status))
    conn.commit()
    conn.close()


def get_student(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT studNumber, studName, 
               studCourse, studYrLvl,
               semester, schoolYr, studStatus
        FROM Students
        WHERE studNumber = ?
    """, (student_number,))
    row = cursor.fetchone()
    conn.close()
    return row


def add_student_if_not_exists(stud_num, name="", course="", year="", semester="", school_yr="", status="Active"):
    """
    Add a student to the database if they don't already exist.
    Only requires studNumber; other fields can be partial or empty.
    Called automatically when creating slips.
    """
    if not stud_num:
        raise ValueError("Student number is required")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if student already exists
        cursor.execute("SELECT studNumber FROM Students WHERE studNumber = ?", (stud_num,))
        existing = cursor.fetchone()
        
        if not existing:
            # Add student with available partial info
            # Use empty string or reasonable defaults for missing fields
            cursor.execute("""
                INSERT INTO Students 
                (studNumber, studName, studCourse, 
                 studYrLvl, semester, schoolYr, studStatus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stud_num, name or "", course or "", year or "", 
                  semester or "", school_yr or "", status or "Active"))
            conn.commit()
            return True  # Student was added
        
        return False  # Student already existed
    except Exception as e:
        raise Exception(f"Failed to add student {stud_num}: {str(e)}")
    finally:
        conn.close()

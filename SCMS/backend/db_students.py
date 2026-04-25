from .db_connection import get_connection
from .config import get_school_year


def add_student(stud_num, name, course, year, school_yr, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Students 
        (studNumber, studName, studCourse, 
         studYrLvl, schoolYr, studStatus)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (stud_num, name, course, year, school_yr, status))
    conn.commit()
    conn.close()


def get_student(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT studNumber, studName, 
               studCourse, studYrLvl,
               schoolYr, studStatus
        FROM Students
        WHERE studNumber = ?
    """, (student_number,))
    row = cursor.fetchone()
    conn.close()
    return row


def add_student_if_not_exists(stud_num, name="", course="", year="", school_yr="", status="Active"):
    """
    Add a student to the database if they don't already exist.
    Only requires studNumber; other fields can be partial or empty.
    Called automatically when creating slips.
    
    If student exists with blank fields, updates them with new data provided.
    This allows gradual enrichment of student records as new slips are created.
    If school_yr is not provided, uses the current school year from settings.
    """
    if not stud_num:
        raise ValueError("Student number is required")
    
    # Use current school year from config if not provided
    if not school_yr:
        school_yr = get_school_year()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if student already exists
        cursor.execute("""
            SELECT studNumber, studName, studCourse, studYrLvl 
            FROM Students WHERE studNumber = ?
        """, (stud_num,))
        existing = cursor.fetchone()
        
        if not existing:
            # Add new student with available partial info
            cursor.execute("""
                INSERT INTO Students 
                (studNumber, studName, studCourse, 
                 studYrLvl, schoolYr, studStatus)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (stud_num, name or "", course or "", year or "", 
                  school_yr, status or "Active"))
            conn.commit()
            return True  # Student was added
        else:
            # Student exists - update any blank fields with new data
            existing_name = existing[1] if existing[1] else ""
            existing_course = existing[2] if existing[2] else ""
            existing_year = existing[3] if existing[3] else ""
            
            # Prepare updated values - use existing if not blank, otherwise use new
            updated_name = existing_name or name or ""
            updated_course = existing_course or course or ""
            updated_year = existing_year or year or ""
            
            # Check if any improvement is being made (filling in blank fields)
            should_update = False
            if (name and not existing_name) or \
               (course and not existing_course) or \
               (year and not existing_year):
                should_update = True
            
            if should_update:
                cursor.execute("""
                    UPDATE Students 
                    SET studName = ?, studCourse = ?, studYrLvl = ?
                    WHERE studNumber = ?
                """, (updated_name, updated_course, updated_year, stud_num))
                conn.commit()
        
        return False  # Student already existed
    except Exception as e:
        raise Exception(f"Failed to add student {stud_num}: {str(e)}")
    finally:
        conn.close()


def update_all_students_school_year(new_school_year):
    """
    Update students' school year ONLY if they don't already have one.
    Preserves existing school year entries.
    Called when changing the school year in settings.
    
    Args:
        new_school_year: The new school year to set for students without one
        
    Returns:
        Tuple: (success: bool, updated_count: int, error_msg: str or None)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update only students with NULL or empty school year
        cursor.execute("""
            UPDATE Students
            SET schoolYr = ?
            WHERE schoolYr IS NULL OR schoolYr = ''
        """, (new_school_year,))
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return True, updated_count, None
    except Exception as e:
        return False, 0, str(e)

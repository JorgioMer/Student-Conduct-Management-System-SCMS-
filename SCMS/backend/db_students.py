from .db_connection import get_connection
from .config import get_school_year


def delete_student(student_number):
    """
    PREVENTED: Student records cannot be deleted.
    This function is intentionally blocked to ensure data integrity.
    
    Args:
        student_number: Student number (not used - always raises error)
    
    Raises:
        PermissionError: Always raised - students cannot be deleted
    """
    raise PermissionError(
        "Student records cannot be deleted. This is a protected operation.\n"
        "If you need to remove a student record, contact your administrator to:\n"
        "1. Archive the record to a historical table, or\n"
        "2. Modify the student's status field instead"
    )


def add_student(stud_num, name, course, year, school_yr, status):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Students 
            (studNumber, studName, studCourse, 
             studYrLvl, schoolYr, studStatus)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (stud_num, name, course, year, school_yr, status))
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        error_msg = str(e).lower()
        # Check for UNIQUE constraint violation
        if "unique" in error_msg or "duplicate" in error_msg:
            raise Exception(f"Student number {stud_num} already exists in the system. Each student must have a unique number.") from e
        raise Exception(f"Failed to add student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_student(student_number):
    conn = None
    try:
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
        return row
    except Exception as e:
        raise Exception(f"Failed to retrieve student {student_number}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def add_student_if_not_exists(stud_num, name="", course="", year="", school_yr="", status="Active"):
    """
    Add a student to the database if they don't already exist.
    Only requires studNumber; other fields can be partial or empty.
    Called automatically when creating slips.
    
    If student exists with blank fields, updates them with new data provided.
    This allows gradual enrichment of student records as new slips are created.
    If school_yr is not provided, uses the current school year from settings.
    """
    # Validate and sanitize student number
    stud_num = str(stud_num).strip() if stud_num else ""
    if not stud_num:
        raise ValueError("Student number is required and cannot be empty")
    
    if len(stud_num) > 50:
        raise ValueError("Student number is too long (max 50 characters)")
    
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
            try:
                cursor.execute("""
                    INSERT INTO Students 
                    (studNumber, studName, studCourse, 
                     studYrLvl, schoolYr, studStatus)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (stud_num, name or "", course or "", year or "", 
                      school_yr, status or "Active"))
                conn.commit()
                return True  # Student was added
            except Exception as insert_error:
                # Check if it's a UNIQUE constraint violation
                error_msg = str(insert_error).lower()
                if "unique" in error_msg or "duplicate" in error_msg:
                    # The student exists but we couldn't find it in the SELECT above
                    # This is likely a race condition - treat as already existing
                    print(f"[WARNING] Student {stud_num} appears to be a duplicate. Skipping insert.")
                    conn.rollback()
                    return False
                raise
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
        conn.rollback()
        error_msg = str(e).lower()
        if "unique" in error_msg or "duplicate" in error_msg:
            print(f"[INFO] Student {stud_num} already exists in database (duplicate check)")
            return False
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

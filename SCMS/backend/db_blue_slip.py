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
            # Return ALL blue slips with ID first for deletion
            cursor.execute("""
                SELECT b.[ID], b.[studNumber], s.[studName], s.[studYrLvl],
                       b.[violationType_blue], b.[severityLvl_blue], b.[dateOfViolation_blue],
                       b.[actionTaken_blue], b.[status_blue]
                FROM Students s
                INNER JOIN [Blue Slip Record] b
                       ON s.[studNumber] = b.[studNumber]
            """)
        else:
            # Return slips for specific student
            cursor.execute("""
                SELECT b.[ID], b.[studNumber], s.[studName], s.[studYrLvl],
                       b.[violationType_blue], b.[severityLvl_blue], b.[dateOfViolation_blue],
                       b.[actionTaken_blue], b.[status_blue]
                FROM Students s
                INNER JOIN [Blue Slip Record] b
                       ON s.[studNumber] = b.[studNumber]
                WHERE b.[studNumber] = ?
            """, (student_number,))
        
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve blue slips: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def update_blue_slip_status(stud_num, new_status):
    """Update the status of a blue slip record for a specific student."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE [Blue Slip Record]
            SET [status_blue] = ?
            WHERE [studNumber] = ?
        """, (new_status, stud_num))
        conn.commit()
        rows_updated = cursor.rowcount
        if rows_updated == 0:
            raise Exception(f"No blue slip found for student {stud_num}")
        return rows_updated
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update blue slip status for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def delete_blue_slip(slip_id):
    """Delete a specific blue slip record by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM [Blue Slip Record]
            WHERE ID = ?
        """, (slip_id,))
        conn.commit()
        rows_deleted = cursor.rowcount
        if rows_deleted == 0:
            raise Exception(f"No blue slip found with ID {slip_id}")
        return rows_deleted
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete blue slip with ID {slip_id}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def count_violations_by_type(stud_num, violation_type=None):
    """
    Count the number of violations for a student, optionally filtered by type.
    
    Args:
        stud_num: Student number
        violation_type: Optional violation type to filter by
    
    Returns:
        Count of violations matching the criteria
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if violation_type:
            cursor.execute("""
                SELECT COUNT(*) as cnt
                FROM [Blue Slip Record]
                WHERE studNumber = ? AND violationType_blue = ?
            """, (stud_num, violation_type))
        else:
            cursor.execute("""
                SELECT COUNT(*) as cnt
                FROM [Blue Slip Record]
                WHERE studNumber = ?
            """, (stud_num,))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        return count
    except Exception as e:
        raise Exception(f"Failed to count violations for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def get_violation_history(stud_num, violation_type=None):
    """
    Get all violation records for a student, optionally filtered by type.
    
    Args:
        stud_num: Student number
        violation_type: Optional violation type to filter by
    
    Returns:
        List of violation records sorted by date (earliest first)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if violation_type:
            cursor.execute("""
                SELECT s.[studName], s.[studCourse],
                       s.[studYrLvl], b.*
                FROM Students s
                INNER JOIN [Blue Slip Record] b
                       ON s.[studNumber] = b.[studNumber]
                WHERE b.[studNumber] = ? AND b.[violationType_blue] = ?
                ORDER BY b.[dateOfViolation_blue] ASC
            """, (stud_num, violation_type))
        else:
            cursor.execute("""
                SELECT s.[studName], s.[studCourse],
                       s.[studYrLvl], b.*
                FROM Students s
                INNER JOIN [Blue Slip Record] b
                       ON s.[studNumber] = b.[studNumber]
                WHERE b.[studNumber] = ?
                ORDER BY b.[dateOfViolation_blue] ASC
            """, (stud_num,))
        
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise Exception(f"Failed to retrieve violation history for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()


def should_escalate_violation(stud_num, violation_type, is_manual_escalation=False):
    """
    Determine if a violation should be marked as escalated.
    
    Rules:
    - If manually flagged by officer: escalate
    - If student has 2+ prior violations of the SAME type: escalate
    - Otherwise: do not escalate
    
    Args:
        stud_num: Student number
        violation_type: Type of violation
        is_manual_escalation: Whether officer manually flagged it
    
    Returns:
        True if violation should be escalated, False otherwise
    """
    if is_manual_escalation:
        return True
    
    # Check for 2+ prior violations of same type
    prior_count = count_violations_by_type(stud_num, violation_type)
    return prior_count >= 2


def update_blue_slip_escalation(record_id, is_escalated):
    """
    Update the escalation status of a blue slip record.
    
    Args:
        record_id: ID of the blue slip record
        is_escalated: Boolean - True to mark as escalated, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update status_blue to include "Escalated" indicator
        new_status = "Escalated" if is_escalated else "Open / Pending"
        
        cursor.execute("""
            UPDATE [Blue Slip Record]
            SET [status_blue] = ?
            WHERE [ID] = ?
        """, (new_status, record_id))
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update escalation status for record {record_id}: {str(e)}") from e
    finally:
        if conn:
            conn.close()

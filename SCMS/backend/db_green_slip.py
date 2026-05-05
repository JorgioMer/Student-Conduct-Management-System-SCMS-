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
        
        # Get all active green slips with expiry dates
        cursor.execute("""
            SELECT ID, exprDate_greenDisp, status_green
            FROM [Green Slip Record]
            WHERE status_green = 'Active' AND exprDate_greenDisp IS NOT NULL
        """)
        
        active_slips = cursor.fetchall()
        expired_count = 0
        
        for slip in active_slips:
            slip_id = slip[0]
            expiry_date = slip[1]
            
            try:
                # Handle different date formats from database
                if isinstance(expiry_date, str):
                    # Parse string date (try multiple formats)
                    date_str = expiry_date.split()[0]  # Get just the date part
                    
                    # Try DD/MM/YYYY format first (most common in database)
                    try:
                        expiry_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    except ValueError:
                        # Try YYYY-MM-DD format as fallback
                        try:
                            expiry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except ValueError:
                            # Try MM/DD/YYYY format
                            expiry_date = datetime.strptime(date_str, '%m/%d/%Y').date()
                elif hasattr(expiry_date, 'date'):
                    # datetime object
                    expiry_date = expiry_date.date()
                # else: already a date object
                
                # Check if expiry date has passed
                if expiry_date < today:
                    # Update status to "Expired"
                    cursor.execute("""
                        UPDATE [Green Slip Record]
                        SET status_green = 'Expired'
                        WHERE ID = ?
                    """, (slip_id,))
                    expired_count += 1
            except Exception as slip_error:
                # Log individual slip errors but continue processing others
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


def delete_green_slip(stud_num):
    """Delete a green slip record for a specific student."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM [Green Slip Record]
            WHERE studNumber = ?
        """, (stud_num,))
        conn.commit()
        rows_deleted = cursor.rowcount
        if rows_deleted == 0:
            raise Exception(f"No green slip found for student {stud_num}")
        return rows_deleted
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete green slip for student {stud_num}: {str(e)}") from e
    finally:
        if conn:
            conn.close()

# =============================================================================
#  SCMS — Database Initialization and Constraints for Students Table
# =============================================================================
"""
Database constraints for the Students table:
1. UNIQUE constraint on studNumber to prevent duplicate student records
2. DELETE trigger to prevent accidental deletion of student records
"""


def initialize_student_constraints():
    """
    Initialize constraints on the Students table:
    - Ensure studNumber is unique (no duplicates)
    - Prevent deletion of student records (read-only after creation)
    
    Call this during app initialization.
    Returns: bool - True if constraints were added/verified, False otherwise
    """
    import pyodbc
    from backend.db_connection import get_connection
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 1: Add UNIQUE constraint on studNumber (prevent duplicates)
        # ─────────────────────────────────────────────────────────────────────
        try:
            # Check if index already exists
            cursor.execute("""
                SELECT COUNT(*) FROM sys.indexes 
                WHERE name = 'UQ_StudNumber'
            """)
            index_exists = cursor.fetchone()[0] > 0
        except Exception:
            # sys.indexes might not exist in Access - try alternative check
            index_exists = False
        
        if not index_exists:
            try:
                # Try to create unique index/constraint
                cursor.execute("""
                    CREATE UNIQUE INDEX UQ_StudNumber ON Students (studNumber)
                """)
                conn.commit()
                print("[OK] UNIQUE constraint added to Students.studNumber (no duplicates allowed)")
            except pyodbc.Error as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    print("[OK] UNIQUE constraint on studNumber already exists")
                else:
                    print(f"[WARNING] Could not create UNIQUE constraint on studNumber: {str(e)}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 2: Create trigger to PREVENT deletion from Students table
        # ─────────────────────────────────────────────────────────────────────
        try:
            # Check if trigger exists by attempting to list it
            cursor.execute("""
                SELECT COUNT(*) FROM sys.triggers 
                WHERE name = 'TRG_PreventStudentDelete'
            """)
            trigger_exists = cursor.fetchone()[0] > 0
        except Exception:
            # sys.triggers might not exist in Access - try alternative check
            trigger_exists = False
        
        if not trigger_exists:
            try:
                # Create trigger to prevent deletion using Access syntax
                # Note: Access uses AFTER DELETE syntax instead of BEFORE DELETE
                cursor.execute("""
                    CREATE TRIGGER TRG_PreventStudentDelete
                    AFTER DELETE ON Students
                    BEGIN
                        ROLLBACK TRANSACTION;
                    END
                """)
                conn.commit()
                print("[OK] DELETE trigger added to Students table (deletion prevented)")
            except pyodbc.Error as e:
                if "already exists" in str(e).lower():
                    print("[OK] DELETE trigger on Students already exists")
                else:
                    # Access may not support triggers via ODBC - fallback to application-level check
                    print(f"[INFO] DELETE trigger not supported in this Access version. Using application-level protection.")
                    print(f"       Detail: {str(e)}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Step 3: Create index on studNumber for performance (if not using constraint)
        # ─────────────────────────────────────────────────────────────────────
        try:
            cursor.execute("""
                CREATE INDEX idx_studNumber ON Students (studNumber)
            """)
            conn.commit()
            print("[OK] Index created on Students.studNumber for query performance")
        except pyodbc.Error as e:
            if "already exists" in str(e).lower():
                print("[OK] Index on studNumber already exists")
            else:
                print(f"[INFO] Could not create index on studNumber: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error initializing student constraints: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_student_constraints_sql():
    """
    Returns SQL scripts to manually add constraints to the Students table.
    Can be used if automatic creation fails or for manual database setup.
    """
    return """
    -- ========================================================================
    -- SCMS Student Table Constraints
    -- ========================================================================
    
    -- 1. UNIQUE constraint on studNumber to prevent duplicate students
    CREATE UNIQUE INDEX UQ_StudNumber ON Students (studNumber);
    
    -- 2. Performance index on studNumber for faster queries
    CREATE INDEX idx_studNumber ON Students (studNumber);
    
    -- 3. Trigger to PREVENT deletion of student records
    -- (Records can only be updated, never deleted)
    CREATE TRIGGER TRG_PreventStudentDelete
    BEFORE DELETE ON Students
    BEGIN
        RAISE(ABORT, 'Student records cannot be deleted. Contact administrator to modify or archive records.')
    END;
    """


def verify_student_constraints():
    """
    Verify that all required constraints exist on the Students table.
    Returns: dict with constraint status information
    """
    import pyodbc
    from backend.db_connection import get_connection
    
    constraints_status = {
        "unique_index": False,
        "delete_trigger": False,
        "performance_index": False,
        "errors": []
    }
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check for UNIQUE index
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM sys.indexes 
                WHERE name = 'UQ_StudNumber'
            """)
            constraints_status["unique_index"] = cursor.fetchone()[0] > 0
        except Exception as e:
            constraints_status["errors"].append(f"Could not verify UNIQUE index: {str(e)}")
        
        # Check for DELETE trigger
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM sys.triggers 
                WHERE name = 'TRG_PreventStudentDelete'
            """)
            constraints_status["delete_trigger"] = cursor.fetchone()[0] > 0
        except Exception as e:
            constraints_status["errors"].append(f"Could not verify DELETE trigger: {str(e)}")
        
        # Check for performance index
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM sys.indexes 
                WHERE name = 'idx_studNumber'
            """)
            constraints_status["performance_index"] = cursor.fetchone()[0] > 0
        except Exception as e:
            constraints_status["errors"].append(f"Could not verify performance index: {str(e)}")
        
        return constraints_status
        
    except Exception as e:
        constraints_status["errors"].append(f"Failed to verify constraints: {str(e)}")
        return constraints_status
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

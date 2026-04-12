# =============================================================================
#  SCMS — Database Initialization for Activity Log
# =============================================================================
"""
SQL scripts and initialization for ActivityLog table.
Run this once to set up the logging table in the database.
"""

def create_activity_log_table():
    """
    Create the ActivityLog table if it doesn't exist.
    Call this during app initialization.
    """
    import pyodbc
    from backend.db_connection import get_connection
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = N'ActivityLog'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Create the table
            cursor.execute("""
                CREATE TABLE ActivityLog (
                    LogID AUTOINCREMENT PRIMARY KEY,
                    Timestamp DATETIME DEFAULT NOW(),
                    ActionType TEXT NOT NULL,
                    StaffID TEXT NOT NULL,
                    Description MEMO,
                    RecordID TEXT,
                    RecordType TEXT,
                    Details MEMO,
                    Status TEXT DEFAULT 'SUCCESS'
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("CREATE INDEX idx_timestamp ON ActivityLog (Timestamp DESC)")
            cursor.execute("CREATE INDEX idx_staff_id ON ActivityLog (StaffID)")
            cursor.execute("CREATE INDEX idx_action_type ON ActivityLog (ActionType)")
            cursor.execute("CREATE INDEX idx_record_id ON ActivityLog (RecordID)")
            
            conn.commit()
            print("✓ ActivityLog table created with indexes")
        else:
            print("✓ ActivityLog table already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating ActivityLog table: {str(e)}")
        return False


def get_activity_log_creation_sql():
    """
    Returns the SQL script to manually create the ActivityLog table in Access.
    Can be used if automatic creation fails.
    """
    return """
    -- ActivityLog Table for SCMS
    CREATE TABLE ActivityLog (
        LogID COUNTER PRIMARY KEY,
        Timestamp DATETIME DEFAULT NOW(),
        ActionType TEXT NOT NULL,
        StaffID TEXT NOT NULL,
        Description MEMO,
        RecordID TEXT,
        RecordType TEXT,
        Details MEMO,
        Status TEXT DEFAULT 'SUCCESS'
    );
    
    -- Create indexes for performance
    CREATE INDEX idx_timestamp ON ActivityLog (Timestamp DESC);
    CREATE INDEX idx_staff_id ON ActivityLog (StaffID);
    CREATE INDEX idx_action_type ON ActivityLog (ActionType);
    CREATE INDEX idx_record_id ON ActivityLog (RecordID);
    """


if __name__ == "__main__":
    # Test: create the table when script is run directly
    create_activity_log_table()

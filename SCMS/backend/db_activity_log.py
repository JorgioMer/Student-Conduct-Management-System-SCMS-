# =============================================================================
#  SCMS — Activity Log Database Module
# =============================================================================
"""
Handles all logging of user actions in the system.
Tracks: file operations, edits, exports, and administrative actions.
"""

import pyodbc
from datetime import datetime
from backend.db_connection import get_connection
from typing import Optional, List, Tuple


# ── Action Types ──────────────────────────────────────────────────────────────
class ActionType:
    """Activity log action type constants."""
    SLIP_CREATED = "SLIP_CREATED"
    SLIP_MODIFIED = "SLIP_MODIFIED"
    SLIP_DELETED = "SLIP_DELETED"
    SLIP_VIEWED = "SLIP_VIEWED"
    FILE_EXPORTED = "FILE_EXPORTED"
    REPORT_GENERATED = "REPORT_GENERATED"
    PRINT_ACTION = "PRINT_ACTION"
    USER_AUTHENTICATED = "USER_AUTHENTICATED"
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    BATCH_OPERATION = "BATCH_OPERATION"
    RECORD_IMPORTED = "RECORD_IMPORTED"
    RECORD_SEARCHED = "RECORD_SEARCHED"


class LogManager:
    """Manages activity logging for all SCMS operations."""

    @staticmethod
    def log_action(
        action_type: str,
        staff_id: str,
        description: str,
        record_id: Optional[str] = None,
        record_type: Optional[str] = None,
        details: Optional[str] = None,
        status: str = "SUCCESS"
    ) -> bool:
        """
        Log an action to the database.
        
        Args:
            action_type: Type of action (see ActionType constants)
            staff_id: ID of the staff/admin performing the action
            description: Human-readable description of the action
            record_id: ID of the record affected (if applicable)
            record_type: Type of record affected (Green/Pink/Blue slip)
            details: Additional details (before/after values, etc.)
            status: SUCCESS or FAILED
        
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now()
            
            # Insert into ActivityLog table
            query = """
                INSERT INTO ActivityLog 
                ([Timestamp], ActionType, StaffID, [Description], RecordID, RecordType, Details, [Status])
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                timestamp,
                action_type,
                staff_id,
                description,
                record_id,
                record_type,
                details,
                status
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging action: {str(e)}")
            return False

    @staticmethod
    def get_logs(limit: int = 100, offset: int = 0) -> List[Tuple]:
        """
        Retrieve recent activity logs.
        
        Args:
            limit: Maximum number of records to retrieve
            offset: Offset for pagination
        
        Returns:
            List of log tuples (ID, Timestamp, ActionType, StaffID, Description, 
                               RecordID, RecordType, Details, Status)
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT TOP (?)
                    LogID, [Timestamp], ActionType, StaffID, [Description],
                    RecordID, RecordType, Details, [Status]
                FROM ActivityLog
                ORDER BY [Timestamp] DESC
                OFFSET ? ROWS
            """
            
            cursor.execute(query, (limit, offset))
            logs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Error retrieving logs: {str(e)}")
            return []

    @staticmethod
    def get_logs_by_staff(staff_id: str, limit: int = 100, offset: int = 0) -> List[Tuple]:
        """
        Retrieve activity logs for a specific staff member.
        
        Args:
            staff_id: ID of the staff member
            limit: Maximum number of records
            offset: Offset for pagination
        
        Returns:
            List of log tuples
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT TOP (?)
                    LogID, [Timestamp], ActionType, StaffID, [Description],
                    RecordID, RecordType, Details, [Status]
                FROM ActivityLog
                WHERE StaffID = ?
                ORDER BY [Timestamp] DESC
                OFFSET ? ROWS
            """
            
            cursor.execute(query, (limit, staff_id, offset))
            logs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Error retrieving staff logs: {str(e)}")
            return []

    @staticmethod
    def get_logs_by_type(action_type: str, limit: int = 100, offset: int = 0) -> List[Tuple]:
        """
        Retrieve activity logs by action type.
        
        Args:
            action_type: Type of action to filter by
            limit: Maximum number of records
            offset: Offset for pagination
        
        Returns:
            List of log tuples
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT TOP (?)
                    LogID, [Timestamp], ActionType, StaffID, [Description],
                    RecordID, RecordType, Details, [Status]
                FROM ActivityLog
                WHERE ActionType = ?
                ORDER BY [Timestamp] DESC
                OFFSET ? ROWS
            """
            
            cursor.execute(query, (limit, action_type, offset))
            logs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Error retrieving logs by type: {str(e)}")
            return []

    @staticmethod
    def get_logs_by_date_range(start_date, end_date, limit: int = 100, offset: int = 0) -> List[Tuple]:
        """
        Retrieve activity logs within a date range.
        
        Args:
            start_date: Start date (datetime or string 'YYYY-MM-DD')
            end_date: End date (datetime or string 'YYYY-MM-DD')
            limit: Maximum number of records
            offset: Offset for pagination
        
        Returns:
            List of log tuples
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT TOP (?)
                    LogID, [Timestamp], ActionType, StaffID, [Description],
                    RecordID, RecordType, Details, [Status]
                FROM ActivityLog
                WHERE CAST([Timestamp] AS DATE) BETWEEN ? AND ?
                ORDER BY [Timestamp] DESC
                OFFSET ? ROWS
            """
            
            cursor.execute(query, (limit, start_date, end_date, offset))
            logs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Error retrieving logs by date: {str(e)}")
            return []

    @staticmethod
    def get_logs_by_record(record_id: str) -> List[Tuple]:
        """
        Retrieve all logs related to a specific record.
        
        Args:
            record_id: ID of the record
        
        Returns:
            List of log tuples
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT LogID, [Timestamp], ActionType, StaffID, [Description],
                       RecordID, RecordType, Details, [Status]
                FROM ActivityLog
                WHERE RecordID = ?
                ORDER BY [Timestamp] DESC
            """
            
            cursor.execute(query, (record_id,))
            logs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return logs
            
        except Exception as e:
            print(f"Error retrieving record logs: {str(e)}")
            return []

    @staticmethod
    def get_total_logs() -> int:
        """Get total count of log entries."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM ActivityLog")
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting log count: {str(e)}")
            return 0

    @staticmethod
    def clear_old_logs(days: int = 365) -> bool:
        """
        Delete logs older than specified days (for maintenance).
        
        Args:
            days: Number of days to retain (default: 365 years of logs)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                DELETE FROM ActivityLog
                WHERE [Timestamp] < DATEADD(day, ?, GETDATE())
            """
            
            cursor.execute(query, (-days,))
            conn.commit()
            
            deleted = cursor.rowcount
            cursor.close()
            conn.close()
            
            print(f"Deleted {deleted} old log entries")
            return True
            
        except Exception as e:
            print(f"Error clearing old logs: {str(e)}")
            return False


# ── Convenience logging functions ─────────────────────────────────────────────
def log_slip_created(staff_id: str, slip_type: str, student_name: str, record_id: Optional[str] = None):
    """Log slip creation."""
    LogManager.log_action(
        ActionType.SLIP_CREATED,
        staff_id,
        f"Created {slip_type} slip for {student_name}",
        record_id=record_id,
        record_type=slip_type
    )


def log_slip_modified(staff_id: str, slip_type: str, student_name: str, record_id: Optional[str] = None, details: Optional[str] = None):
    """Log slip modification."""
    LogManager.log_action(
        ActionType.SLIP_MODIFIED,
        staff_id,
        f"Modified {slip_type} slip for {student_name}",
        record_id=record_id,
        record_type=slip_type,
        details=details
    )


def log_slip_deleted(staff_id: str, slip_type: str, student_name: str, record_id: Optional[str] = None):
    """Log slip deletion."""
    LogManager.log_action(
        ActionType.SLIP_DELETED,
        staff_id,
        f"Deleted {slip_type} slip for {student_name}",
        record_id=record_id,
        record_type=slip_type
    )


def log_export(staff_id: str, export_type: str, record_count: int):
    """Log export action."""
    LogManager.log_action(
        ActionType.FILE_EXPORTED,
        staff_id,
        f"Exported {export_type} report ({record_count} records)"
    )


def log_print(staff_id: str, document_type: str):
    """Log print action."""
    LogManager.log_action(
        ActionType.PRINT_ACTION,
        staff_id,
        f"Printed {document_type}"
    )


def log_report_generated(staff_id: str, report_type: str):
    """Log report generation."""
    LogManager.log_action(
        ActionType.REPORT_GENERATED,
        staff_id,
        f"Generated {report_type} report"
    )


def log_search(staff_id: str, search_criteria: str, results_count: int):
    """Log search action."""
    LogManager.log_action(
        ActionType.RECORD_SEARCHED,
        staff_id,
        f"Searched records with criteria: {search_criteria} ({results_count} results found)"
    )


def log_batch_operation(staff_id: str, operation_type: str, record_count: int):
    """Log batch operations."""
    LogManager.log_action(
        ActionType.BATCH_OPERATION,
        staff_id,
        f"Executed batch {operation_type} on {record_count} records"
    )

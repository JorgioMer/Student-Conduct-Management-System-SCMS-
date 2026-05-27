import os
import sys
import shutil
import pyodbc
import time
import gc
from queue import Queue, Empty
import threading


def _get_base_path() -> str:
    """
    Returns the directory containing SCMS.exe when frozen,
    or the directory of this .py file during development.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller one-folder: sys.executable = .../SCMS/SCMS.exe
        return os.path.dirname(sys.executable)
    # Dev: this file lives at SCMS/backend/database_connection.py
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = _get_base_path()

# ── AppData: where the user's live database lives ─────────────────────────
DATA_DIR      = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "SCMS")
LOCAL_DB_PATH = os.path.join(DATA_DIR, "SCMSDatabase.accdb")   # FIX: was SMCSDatabase


def _template_db_candidates() -> list[str]:
    """
    Ordered list of locations to look for the blank/template database.
    The first one that exists will be used to seed the user's AppData copy.
    """
    return [
        # PyInstaller one-folder build  →  SCMS\backend\database\SCMSDatabase.accdb
        os.path.join(BASE_PATH, "backend", "database", "SCMSDatabase.accdb"),

        # Dev layout  →  <repo>\SCMS\backend\database\SCMSDatabase.accdb
        os.path.join(BASE_PATH, "database", "SCMSDatabase.accdb"),

        # PyInstaller one-FILE bundle (_MEIPASS temp dir) — keep as last resort
        *(
            [os.path.join(sys._MEIPASS, "backend", "database", "SCMSDatabase.accdb")]
            if hasattr(sys, "_MEIPASS")
            else []
        ),
    ]


def ensure_local_database() -> str:
    r"""
    Copies the blank template database into AppData\SCMS\ on first run.
    Subsequent runs skip the copy and return the existing path.
    Returns the path to the user's writable database.
    Raises FileNotFoundError if no template can be located.
    """
    if os.path.exists(LOCAL_DB_PATH):
        return LOCAL_DB_PATH

    os.makedirs(DATA_DIR, exist_ok=True)

    for candidate in _template_db_candidates():
        if os.path.exists(candidate):
            try:
                shutil.copy2(candidate, LOCAL_DB_PATH)
                print(f"[OK] Database initialised from: {candidate}")
                return LOCAL_DB_PATH
            except Exception as e:
                print(f"[ERROR] Failed to copy database template: {str(e)}")
                raise

    # Nothing found — give the developer a useful error with all paths checked
    checked = "\n  ".join(_template_db_candidates())
    error_msg = (
        f"[ERROR] Database template not found. Locations checked:\n  {checked}\n"
        f"BASE_PATH resolved to: {BASE_PATH}\n"
        f"LOCAL_DB_PATH would be: {LOCAL_DB_PATH}"
    )
    print(error_msg)
    raise FileNotFoundError(error_msg)


DB_PATH = ensure_local_database()


class PooledConnection:
    """
    Wrapper around a pyodbc connection that intercepts close() calls.
    When close() is called, returns the connection to the pool instead of closing it.
    This allows the same pooled connection to be reused many times.
    
    Automatically rolls back any pending transactions before returning to pool
    to ensure clean state for next use.
    """
    
    def __init__(self, raw_conn, pool):
        self._raw_conn = raw_conn
        self._pool = pool
    
    def close(self):
        """Return connection to pool after cleaning up any pending transactions."""
        if self._raw_conn is None:
            return
        
        try:
            # Always rollback any pending transaction before returning to pool
            # This ensures the connection is in a clean state
            try:
                self._raw_conn.rollback()
            except:
                pass
        finally:
            # Return to pool for reuse
            self._pool.return_connection(self._raw_conn)
    
    def cursor(self, *args, **kwargs):
        """Delegate cursor creation to raw connection."""
        return self._raw_conn.cursor(*args, **kwargs)
    
    def commit(self):
        """Delegate commit to raw connection."""
        return self._raw_conn.commit()
    
    def rollback(self):
        """Delegate rollback to raw connection."""
        return self._raw_conn.rollback()
    
    def __getattr__(self, name):
        """Delegate any other attributes to raw connection."""
        return getattr(self._raw_conn, name)


class ConnectionPool:
    """
    Simple connection pool to reuse database connections and avoid exceeding
    Access driver's concurrent connection limit (typically 10-20).
    
    Maintains a pool of pre-opened connections that are borrowed and returned
    by client code. When code calls conn.close(), it goes back into the pool
    instead of being closed.
    """
    
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialized = False
        self._all_conns = []  # Track all connections for cleanup
        self._init_pool()
    
    def _init_pool(self):
        """Initialize the pool with fresh connections."""
        with self.lock:
            if self._initialized:
                return
            
            for _ in range(self.pool_size):
                try:
                    conn = self._create_connection()
                    self._all_conns.append(conn)
                    self.pool.put(conn, block=False)
                except Exception as e:
                    print(f"[WARNING] Failed to pre-create connection: {str(e)}")
            
            self._initialized = True
            print(f"[INFO] Connection pool initialized with {self.pool.qsize()} connections")
    
    def _create_connection(self) -> pyodbc.Connection:
        """Create a new database connection with basic error handling."""
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            rf"DBQ={DB_PATH};"
        )
        return pyodbc.connect(conn_str)
    
    def get_connection(self, timeout=2.0) -> PooledConnection:
        """
        Get a connection from the pool wrapped in PooledConnection.
        
        Args:
            timeout: How long to wait for an available connection (seconds)
        
        Returns:
            A PooledConnection wrapper ready to use
        """
        try:
            # Try to get a connection from the pool (non-blocking with short timeout)
            raw_conn = self.pool.get(block=True, timeout=timeout)
            
            # Test if connection is still alive
            try:
                cursor = raw_conn.cursor()
                cursor.close()
            except Exception as e:
                # Connection died, remove from tracking and create a new one
                try:
                    raw_conn.close()
                    self._all_conns.remove(raw_conn)
                except:
                    pass
                try:
                    raw_conn = self._create_connection()
                    self._all_conns.append(raw_conn)
                except Exception as e2:
                    print(f"[ERROR] Failed to create replacement connection: {str(e2)}")
                    raise
            
            # Wrap and return
            return PooledConnection(raw_conn, self)
                
        except Empty:
            # Pool exhausted - try to create a temporary connection
            print(f"[WARNING] Connection pool exhausted. Creating temporary connection.")
            try:
                raw_conn = self._create_connection()
                # Don't track temporary connections, they'll be closed normally
                return PooledConnection(raw_conn, self)
            except Exception as e:
                raise Exception(f"Failed to get database connection: {str(e)}") from e
    
    def return_connection(self, conn):
        """
        Return a connection to the pool for reuse.
        Called when PooledConnection.close() is invoked.
        
        Args:
            conn: The raw pyodbc connection to return
        """
        if conn is None:
            return
        
        try:
            # Try to return to pool if there's space
            self.pool.put(conn, block=False)
        except Exception:
            # Pool is full, close the connection
            try:
                conn.close()
            except:
                pass
    
    def close_all(self):
        """Close all connections in the pool. Call at application shutdown."""
        print(f"[INFO] Closing connection pool ({len(self._all_conns)} connections)...")
        for conn in self._all_conns:
            try:
                conn.close()
            except:
                pass
        self._all_conns.clear()
        self._initialized = False


# Global connection pool (created once at module load)
_connection_pool = ConnectionPool(pool_size=5)


def get_connection() -> PooledConnection:
    """
    Get a database connection from the pool.
    
    The pool keeps 5 persistent connections open and reuses them, avoiding
    the "Too many client tasks" error from opening/closing too many connections.
    
    When you call close() on the returned connection, it goes back to the pool
    instead of being closed, ready for the next operation.
    
    Usage:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # ... use cursor ...
        finally:
            # This returns connection to pool, not closes it
            conn.close()
    """
    return _connection_pool.get_connection()


def close_connection_pool():
    """Close all connections in the pool. Call at application shutdown."""
    _connection_pool.close_all()
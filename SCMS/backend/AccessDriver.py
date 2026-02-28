# Database connection and queries - now organized into separate modules
from .db_connection import get_connection
from .db_students import add_student, get_student, add_student_if_not_exists
from .db_green_slip import add_green_slip, get_green_slips
from .db_blue_slip import add_blue_slip, get_blue_slips
from .db_pink_slip import add_pink_slip, get_pink_slips

# Re-export for backwards compatibility
__all__ = [
    'get_connection',
    'add_student',
    'get_student',
    'add_student_if_not_exists',
    'add_green_slip',
    'get_green_slips',
    'add_pink_slip',
    'get_pink_slips',
    'add_blue_slip',
    'get_blue_slips',
]



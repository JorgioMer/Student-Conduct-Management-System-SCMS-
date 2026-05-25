"""
Configuration Management for SCMS
Handles saving and loading system settings
"""
import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "school_year": "2024–2025",
    "school_years_list": ["2024–2025", "2023–2024", "2022–2023"],
    "current_semester": "1st Semester",
    "green_slip_threshold": "2",
    "escalation_trigger": "3",
    "notifications": {
        "green_slip_alert": True,
        "pink_slip_warn": True,
        "auto_escalate": True,
        "monthly_summary": True,
    },
    "custom_courses": {}  # Format: {"COURSE_CODE": "COLLEGE_CODE", ...}
}


def load_config():
    """Load configuration from file, or return default if file doesn't exist"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


def get_current_semester():
    """Get the currently selected semester"""
    config = load_config()
    return config.get("current_semester", "1st Semester")


def set_current_semester(semester):
    """Set the current semester"""
    config = load_config()
    config["current_semester"] = semester
    return save_config(config)


def get_school_year():
    """Get the currently selected school year"""
    config = load_config()
    return config.get("school_year", "2024–2025")


def set_school_year(year):
    """Set the school year"""
    config = load_config()
    config["school_year"] = year
    return save_config(config)


def get_school_years_list():
    """Get list of all available school years"""
    config = load_config()
    return config.get("school_years_list", DEFAULT_CONFIG["school_years_list"])


def add_school_year(year):
    """Add a new school year to the list"""
    config = load_config()
    school_years = config.get("school_years_list", DEFAULT_CONFIG["school_years_list"].copy())
    if year not in school_years:
        school_years.insert(0, year)  # Add to front
        config["school_years_list"] = school_years
        return save_config(config)
    return True


def remove_school_year(year):
    """Remove a school year from the list (cannot remove current year)"""
    config = load_config()
    if config.get("school_year") == year:
        return False  # Cannot remove current year
    school_years = config.get("school_years_list", DEFAULT_CONFIG["school_years_list"].copy())
    if year in school_years:
        school_years.remove(year)
        config["school_years_list"] = school_years
        return save_config(config)
    return True


# ── College and Course Mapping ────────────────────────────────────────────────
COLLEGES = {
    "CEDAS": {
        "name": "College of Education and Sciences",
        "courses": ["BSP", "BS CRIM", "BS MATH", "AB ELS", "BECED", "BEED", "BPED", 
                   "BSED ENG", "BSED FIL", "BSED MATH", "BSED SCI", "BTV-TED"]
    },
    "CABE": {
        "name": "College of Business and Entrepreneurship",
        "courses": ["BSA", "BSMA", "BSAIS", "BPA", "BSTM", "BSHM", "BSBA-FM", 
                   "BSBA-MM", "BSBA-HRDM", "DHTT"]
    },
    "CCIS": {
        "name": "College Of Computing and Information Sciences",
        "courses": ["BSCS", "BSIT", "BLIS"]
    },
    "COE": {
        "name": "College of Engineering",
        "courses": ["BSCE", "BSECE", "BSCPE"]
    },
    "CHS": {
        "name": "College of Health Sciences",
        "courses": ["BSN", "BSRT", "BSMLS"]
    },
    "CSP": {
        "name": "College of Special Programs",
        "courses": ["CSP"]
    }
}


def get_course_college(course_code):
    """Get the college code for a given course code"""
    course_upper = course_code.upper().strip()
    for college_code, college_info in COLLEGES.items():
        if course_upper in college_info["courses"]:
            return college_code
    return None


def get_college_name(college_code):
    """Get the full name of a college by its code"""
    if college_code in COLLEGES:
        return COLLEGES[college_code]["name"]
    return college_code


def get_all_colleges():
    """Get list of all colleges with their codes"""
    return list(COLLEGES.keys())


def get_all_courses():
    """Get a flat list of all available courses"""
    courses = []
    for college_info in COLLEGES.values():
        courses.extend(college_info["courses"])
    
    # Add custom courses
    config = load_config()
    custom_courses = config.get("custom_courses", {})
    courses.extend(custom_courses.keys())
    
    return sorted(courses)


def get_current_year():
    """Extract the starting year from school year string (e.g., '2024–2025' → 2024)"""
    school_year = get_school_year()
    try:
        # Extract first year from format like "2024–2025"
        year_part = school_year.split("–")[0].strip() if "–" in school_year else school_year.split("-")[0].strip()
        return int(year_part)
    except (ValueError, IndexError):
        # Fallback to current year
        from datetime import datetime
        return datetime.now().year


def get_custom_courses():
    """Get dictionary of all custom courses: {course_code: college_code}"""
    config = load_config()
    return config.get("custom_courses", {})


def add_custom_course(course_code, college_code):
    """Add a new custom course under a college
    
    Args:
        course_code: The course code/name (e.g., "BSMA-CUSTOM")
        college_code: The college code where this course belongs
    
    Returns:
        True if added successfully, False if course already exists
    """
    course_code = course_code.strip().upper()
    if not course_code:
        return False
    
    config = load_config()
    custom_courses = config.get("custom_courses", {})
    
    # Check if course already exists (custom or built-in)
    if course_code in custom_courses or course_code in get_all_courses():
        return False
    
    custom_courses[course_code] = college_code
    config["custom_courses"] = custom_courses
    return save_config(config)


def remove_custom_course(course_code):
    """Remove a custom course
    
    Args:
        course_code: The course code to remove
    
    Returns:
        True if removed successfully, False if not found or is built-in
    """
    course_code = course_code.strip().upper()
    config = load_config()
    custom_courses = config.get("custom_courses", {})
    
    if course_code in custom_courses:
        del custom_courses[course_code]
        config["custom_courses"] = custom_courses
        return save_config(config)
    
    return False


def get_period_options():
    """Generate period options for report filtering based on current year
    
    Returns:
        List of period strings in format:
        - "January 2024", "February 2024", ..., "December 2024"
        - "1st Semester S.Y. 2024–2025"
        - "2ND Semester S.Y. 2024–2025"
        - "S.Y. 2024–2025 (Full Year)"
    """
    year = get_current_year()
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    options = [f"{month} {year}" for month in months]
    options.extend([
        f"1st Semester S.Y. {year}–{year+1}",
        f"2ND Semester S.Y. {year}–{year+1}",
        f"S.Y. {year}–{year+1} (Full Year)",
    ])
    return options


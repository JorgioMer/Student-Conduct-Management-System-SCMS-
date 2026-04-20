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
    }
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
    return sorted(courses)

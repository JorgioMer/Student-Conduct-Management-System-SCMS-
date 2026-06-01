#!/usr/bin/env python3
"""
Test script to verify green slip save bug is fixed.
Simulates the exact scenario: add a green slip, commit, and verify it's in the database.
"""

import sys
import os
import shutil
from datetime import datetime, date
import tempfile

# Add SCMS to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SCMS"))

def test_green_slip_save():
    """Test green slip save with fixed connection pooling."""
    
    print("=" * 70)
    print("GREEN SLIP SAVE FIX VERIFICATION TEST")
    print("=" * 70)
    
    # Create a temporary test database (copy of template)
    from SCMS.backend import db_connection
    
    print("\n[STEP 1] Setting up test database...")
    test_dir = tempfile.mkdtemp(prefix="scms_test_")
    test_db_path = os.path.join(test_dir, "SCMSDatabase.accdb")
    
    # Find and copy template database
    template_candidates = [
        os.path.join(os.path.dirname(__file__), "SCMS", "backend", "database", "SCMSDatabase.accdb"),
        os.path.join(os.path.dirname(__file__), "build", "scms", "backend", "database", "SCMSDatabase.accdb"),
    ]
    
    template_path = None
    for candidate in template_candidates:
        if os.path.exists(candidate):
            template_path = candidate
            break
    
    if not template_path:
        print(f"[ERROR] Template database not found. Checked:")
        for c in template_candidates:
            print(f"  - {c}")
        return False
    
    try:
        shutil.copy2(template_path, test_db_path)
        print(f"✓ Test database created at: {test_db_path}")
    except Exception as e:
        print(f"✗ Failed to copy database: {e}")
        return False
    
    # Override the connection to use our test database
    original_db_path = db_connection.LOCAL_DB_PATH
    db_connection.LOCAL_DB_PATH = test_db_path
    db_connection.DB_PATH = test_db_path
    
    try:
        # Import after path is set
        from SCMS.backend.db_green_slip import add_green_slip, get_green_slips
        from SCMS.backend.db_students import add_student_if_not_exists
        
        print("\n[STEP 2] Adding test student...")
        test_stud_no = "2026-TEST-001"
        test_stud_name = "Test Student"
        test_course = "CS101"
        test_year = "2nd"
        
        add_student_if_not_exists(
            test_stud_no,
            name=test_stud_name,
            course=test_course,
            year=test_year
        )
        print(f"✓ Student added: {test_stud_no}")
        
        print("\n[STEP 3] Testing DISPENSATION green slip save...")
        
        try:
            slip_id = add_green_slip(
                stud_num=test_stud_no,
                slip_type="Dispensation",
                date_avail=date.today(),
                days="5",
                status="Active",
                expiry=None,
                purpose="Testing",
                remarks="Test dispensation slip",
                absence_type=None,
                dates_absence=None,
                supp_doc="None",
                auth_by="Test Admin",
                stud_name=test_stud_name,
                stud_course=test_course,
                stud_year=test_year
            )
            print(f"✓ Dispensation slip added with ID: {slip_id}")
        except Exception as e:
            print(f"✗ Failed to add dispensation slip: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n[STEP 4] Testing EXCUSE green slip save...")
        
        try:
            slip_id_2 = add_green_slip(
                stud_num=test_stud_no,
                slip_type="Excuse",
                date_avail=date.today(),
                days=None,
                status="Active",
                expiry=None,
                purpose=None,
                remarks="Test excuse slip",
                absence_type="Medical / Illness",
                dates_absence="2026-06-01 to 2026-06-02",
                supp_doc="Medical Certificate",
                auth_by="Test Admin",
                stud_name=test_stud_name,
                stud_course=test_course,
                stud_year=test_year
            )
            print(f"✓ Excuse slip added with ID: {slip_id_2}")
        except Exception as e:
            print(f"✗ Failed to add excuse slip: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n[STEP 5] Verifying slips are saved in database...")
        
        try:
            slips = get_green_slips(test_stud_no)
            if not slips:
                print(f"✗ FAILED: No slips found for student {test_stud_no}")
                print("  This indicates the rollback bug is still present!")
                return False
            
            print(f"✓ Found {len(slips)} green slip(s) in database")
            
            for i, slip in enumerate(slips, 1):
                slip_id, stud_num, stud_name, year, course, slip_type, date_avail, days, expiry, status, dates_abs = slip
                slip_type_name = "Dispensation" if slip_type else "Excuse"
                print(f"\n  Slip {i}:")
                print(f"    ID: {slip_id}")
                print(f"    Type: {slip_type_name}")
                print(f"    Date Availed: {date_avail}")
                print(f"    Status: {status}")
            
            print("\n" + "=" * 70)
            print("✓ SUCCESS: Green slip save bug is FIXED!")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"✗ Failed to retrieve slips: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    finally:
        # Cleanup
        db_connection.LOCAL_DB_PATH = original_db_path
        db_connection.DB_PATH = original_db_path
        try:
            shutil.rmtree(test_dir)
            print(f"\n✓ Test database cleaned up")
        except:
            pass


if __name__ == "__main__":
    success = test_green_slip_save()
    sys.exit(0 if success else 1)

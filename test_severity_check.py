"""Check what severity data looks like in the database"""
import sys
sys.path.insert(0, 'SCMS')

from backend.db_blue_slip import get_blue_slips

blue_slips = get_blue_slips(None) or []

if blue_slips:
    print("Blue Slip Severity Levels:")
    print("=" * 60)
    for record in blue_slips:
        if len(record) > 8:
            severity = record[8]
            print(f"  Raw: {repr(severity)}")
            print(f"  Display: {severity}")
            print(f"  Ord values: {[ord(c) for c in str(severity)]}")
            print()
else:
    print("No records found")

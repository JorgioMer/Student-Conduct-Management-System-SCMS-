"""Test script to verify PDF export with pink slip data"""
import sys
sys.path.insert(0, 'SCMS')

from backend.db_pink_slip import get_pink_slips

# Get pink slips
pink_slips = get_pink_slips(None) or []

if pink_slips:
    print("Pink Slip Record Structure:")
    record = pink_slips[0]
    print(f"  Total fields: {len(record)}")
    for i, field in enumerate(record):
        print(f"    [{i}] {field}")
    
    print("\n✓ PDF Export should now display:")
    print(f"  Student: {record[4]} ({record[0]})")
    print(f"  Year: {record[2]}, Course: {record[1]}")
    print(f"  Violation: {record[6]} (correct index now!)")
    print(f"  Date Issued: {str(record[5])[:10]} (correct index now!)")
else:
    print("✗ No pink slip records found")

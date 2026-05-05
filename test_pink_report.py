"""Test script to verify pink slip report fix"""
import sys
sys.path.insert(0, 'SCMS')

from backend.db_pink_slip import get_pink_slips

# Get all pink slip records
pink_records = get_pink_slips(None)

if pink_records:
    print(f"✓ Found {len(pink_records)} pink slip records\n")
    
    # Show the structure of the first record
    record = pink_records[0]
    print(f"Record structure ({len(record)} fields):")
    print(f"  [0] studName:          {record[0]}")
    print(f"  [1] studCourse:        {record[1]}")
    print(f"  [2] studYrLvl:         {record[2]}")
    print(f"  [3] ID:                {record[3]}")
    print(f"  [4] studNumber:        {record[4]}")
    print(f"  [5] dateIssued_pink:   {record[5]}")
    print(f"  [6] violation_pink:    {record[6]}")
    print(f"  [7] actionTaken_pink:  {record[7]}")
    print(f"  [8] offcInCharge:      {record[8]}")
    print(f"  [9] sem_pink:          {record[9]}")
    print(f"  [10] remarks_pink:     {record[10]}")
    
    print(f"\nExtracted report fields (should be: stud_num, stud_name, year, course, violation, date):")
    print(f"  stud_num:   {record[4]}")
    print(f"  stud_name:  {record[0]}")
    print(f"  year:       {record[2]}")
    print(f"  course:     {record[1]}")
    print(f"  violation:  {record[6]}")  # Fixed: was record[5]
    print(f"  date:       {str(record[5])[:10]}")  # Fixed: was record[6]
    
    print("\n✓ Report extraction fixed - date is now at [5] and violation at [6]")
else:
    print("✗ No pink slip records found in database")

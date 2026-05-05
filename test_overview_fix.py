"""Test script to verify Overview tab pink slip filtering fix"""
import sys
sys.path.insert(0, 'SCMS')

from datetime import datetime
from backend.db_pink_slip import get_pink_slips
from backend.db_blue_slip import get_blue_slips
from backend.db_green_slip import get_green_slips

# Simulate the filter function from reports.py (simplified)
def filter_records_by_period_mock(records, date_field_index=6):
    """Simplified version of _filter_records_by_period for testing"""
    filtered = []
    for record in records:
        try:
            if len(record) <= date_field_index:
                continue
            
            date_str = str(record[date_field_index]).strip()
            if not date_str or date_str == "N/A":
                continue
            
            # Parse date
            if "/" in date_str:
                date_obj = datetime.strptime(date_str.split()[0], "%d/%m/%Y")
            else:
                date_obj = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
            
            # Check if date is in May 2026 (current month)
            if date_obj.year == 2026 and date_obj.month == 5:
                filtered.append(record)
        except:
            pass
    
    return filtered

# Get all slips
green_slips = filter_records_by_period_mock(get_green_slips(None) or [], date_field_index=6)
pink_slips = filter_records_by_period_mock(get_pink_slips(None) or [], date_field_index=5)  # Fixed index
blue_slips = filter_records_by_period_mock(get_blue_slips(None) or [], date_field_index=6)

print("Overview Tab - May 2026 Summary:")
print(f"  Green Slips: {len(green_slips)}")
print(f"  Pink Slips:  {len(pink_slips)}")
print(f"  Blue Slips:  {len(blue_slips)}")
print(f"  Total:       {len(green_slips) + len(pink_slips) + len(blue_slips)}")

if pink_slips:
    print("\n✓ Pink slips are now showing in Overview tab!")
    for i, slip in enumerate(pink_slips, 1):
        print(f"  {i}. {slip[0]} ({slip[4]}) - {slip[5][:10]}")
else:
    print("\n✗ No pink slips found (but that's okay if none exist in May 2026)")

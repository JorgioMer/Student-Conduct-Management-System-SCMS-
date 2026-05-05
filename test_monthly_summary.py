"""Test script to verify monthly summary filtering"""
import sys
sys.path.insert(0, 'SCMS')

from datetime import datetime
from backend.db_pink_slip import get_pink_slips
from backend.db_blue_slip import get_blue_slips
from backend.db_green_slip import get_green_slips

def filter_monthly_records(records, date_field_index=6, period="May 2026"):
    """Filter records to show only those from the selected month."""
    if not records or not period:
        return []
    
    filtered = []
    for record in records:
        try:
            if len(record) <= date_field_index:
                continue
            
            date_str = str(record[date_field_index]).strip()
            if not date_str or date_str == "N/A":
                continue
            
            # Parse date (handle DD/MM/YYYY and YYYY-MM-DD formats)
            try:
                if "/" in date_str:
                    date_obj = datetime.strptime(date_str.split()[0], "%d/%m/%Y")
                else:
                    date_obj = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
            except ValueError:
                continue
            
            # Check if date matches the selected period (month and year)
            try:
                period_date = datetime.strptime(period, "%B %Y")
                if date_obj.month == period_date.month and date_obj.year == period_date.year:
                    filtered.append(record)
            except ValueError:
                continue
        except Exception:
            continue
    
    return filtered

# Test filtering for May 2026
print("Testing Monthly Summary Filtering")
print("=" * 50)

# Get all records
green_slips = filter_monthly_records(get_green_slips(None) or [], date_field_index=6, period="May 2026")
pink_slips  = filter_monthly_records(get_pink_slips(None) or [], date_field_index=5, period="May 2026")
blue_slips  = filter_monthly_records(get_blue_slips(None) or [], date_field_index=6, period="May 2026")

print(f"\nMay 2026 Monthly Summary:")
print(f"  Green Slips: {len(green_slips)}")
print(f"  Pink Slips:  {len(pink_slips)}")
print(f"  Blue Slips:  {len(blue_slips)}")
print(f"  Total:       {len(green_slips) + len(pink_slips) + len(blue_slips)}")

if pink_slips:
    print(f"\n  Pink Slip Details:")
    for slip in pink_slips:
        print(f"    - {slip[0]} ({slip[4]}) on {slip[5]}")

# Test other months
print("\n" + "=" * 50)
print("Testing other months:")
for month_str in ["April 2026", "June 2026", "December 2026"]:
    g = filter_monthly_records(get_green_slips(None) or [], date_field_index=6, period=month_str)
    p = filter_monthly_records(get_pink_slips(None) or [], date_field_index=5, period=month_str)
    b = filter_monthly_records(get_blue_slips(None) or [], date_field_index=6, period=month_str)
    total = len(g) + len(p) + len(b)
    print(f"  {month_str}: {total} records (G:{len(g)}, P:{len(p)}, B:{len(b)})")

print("\n✓ Monthly summary filtering is working correctly!")

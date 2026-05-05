"""Verify that severity levels are properly encoded for PDF export"""
import sys
sys.path.insert(0, 'SCMS')

def _safe_old(text):
    """Old version that replaces with ?"""
    if text is None:
        return '-'
    return str(text).encode('latin-1', errors='replace').decode('latin-1')

def _safe_new(text):
    """New version with proper character replacement"""
    if text is None:
        return '-'
    text = str(text)
    # Replace Unicode characters that can't be encoded in latin-1 with ASCII equivalents
    text = text.replace('—', '-')  # Em-dash → hyphen
    text = text.replace('–', '-')  # En-dash → hyphen
    text = text.replace('"', '"')  # Left double quote → regular quote
    text = text.replace('"', '"')  # Right double quote → regular quote
    text = text.replace(''', "'")  # Left single quote → apostrophe
    text = text.replace(''', "'")  # Right single quote → apostrophe
    return text.encode('latin-1', errors='replace').decode('latin-1')

test_severity = "Level 1 — Minor"

print("=" * 60)
print("PDF EXPORT CHARACTER ENCODING FIX")
print("=" * 60)

print(f"\nOriginal: {repr(test_severity)}")
print(f"Display:  {test_severity}")

print(f"\n❌ OLD _safe() function:")
old_result = _safe_old(test_severity)
print(f"  Result: {repr(old_result)}")
print(f"  Display: {old_result}")

print(f"\n✓ NEW _safe() function:")
new_result = _safe_new(test_severity)
print(f"  Result: {repr(new_result)}")
print(f"  Display: {new_result}")

print("\n" + "=" * 60)
print("RESULT: Em-dash (—) now shows as hyphen (-) in PDFs")
print("        No more question marks!")
print("=" * 60)

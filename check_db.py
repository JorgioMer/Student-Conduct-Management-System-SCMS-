import sys
sys.path.insert(0, 'SCMS')
from backend.db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Get column names
cursor.execute('SELECT * FROM Students')
columns = [desc[0] for desc in cursor.description]
print('Students columns:', columns)
print()

# Get all students
cursor.execute('SELECT * FROM Students')
print('Students:')
for row in cursor.fetchall():
    print(row)
print()

# Check Pink Slip table
cursor.execute('SELECT * FROM [Pink Slip Record]')
columns = [desc[0] for desc in cursor.description]
print('Pink Slip Record columns:', columns)
print()

print('Pink Slips:')
for row in cursor.fetchall():
    print(row)
print()

# Check Blue Slip table
try:
    cursor.execute('SELECT * FROM [Blue Slip Record]')
    columns = [desc[0] for desc in cursor.description]
    print('Blue Slip Record columns:', columns)
    print()
    
    print('Blue Slips:')
    for row in cursor.fetchall():
        print(row)
    print()
except Exception as e:
    print(f'Blue Slip Record error: {e}')
    print()

# Check Green Slip table
try:
    cursor.execute('SELECT * FROM [Green Slip Record]')
    columns = [desc[0] for desc in cursor.description]
    print('Green Slip Record columns:', columns)
    print()
    
    print('Green Slips:')
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print(f'Green Slip Record error: {e}')

conn.close()

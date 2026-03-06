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

conn.close()

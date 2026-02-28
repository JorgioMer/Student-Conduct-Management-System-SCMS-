from db_connection import get_connection


def get_blue_slips(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.studentName, s.studentCourse,
               s.studentYearLvl, b.*
        FROM Students s
        INNER JOIN [Blue Slip Records] b 
               ON s.studentNumber = b.studentNumber
        WHERE b.studentNumber = ?
    """, (student_number,))
    rows = cursor.fetchall()
    conn.close()
    return rows

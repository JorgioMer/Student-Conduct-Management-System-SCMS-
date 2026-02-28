from db_connection import get_connection


def get_pink_slips(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.studentName, s.studentCourse,
               s.studentYearLvl, p.*
        FROM Students s
        INNER JOIN [Pink Slip Records] p 
               ON s.studentNumber = p.studentNumber
        WHERE p.studentNumber = ?
    """, (student_number,))
    rows = cursor.fetchall()
    conn.close()
    return rows

from db_connection import get_connection


def add_student(stud_num, name, course, year, semester, school_yr, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Students 
        (studentNumber, studentName, studentCourse, 
         studentYearLvl, semester, schoolYr, studentStatus)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (stud_num, name, course, year, semester, school_yr, status))
    conn.commit()
    conn.close()


def get_student(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT studentNumber, studentName, 
               studentCourse, studentYearLvl,
               semester, schoolYr, studentStatus
        FROM Students
        WHERE studentNumber = ?
    """, (student_number,))
    row = cursor.fetchone()
    conn.close()
    return row

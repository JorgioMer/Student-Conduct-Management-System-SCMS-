import pyodbc

# Path to your Access database file
DB_PATH = r"SCMS\backend\SCMS_Database.accdb"

def get_connection():
    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    print("connected")
    return pyodbc.connect(conn_str)





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


def get_green_slips(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.studentName, s.studentCourse, 
               s.studentYearLvl, g.*
        FROM Students s
        INNER JOIN [Green Slip Records] g 
               ON s.studentNumber = g.studentNumber
        WHERE g.studentNumber = ?
    """, (student_number,))
    rows = cursor.fetchall()
    conn.close()
    return rows


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


def add_green_slip(stud_num, slip_type, date_avail, 
                   days, status, expiry, purpose, 
                   remarks, absence_type, dates_absence, 
                   supp_doc, auth_by):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO [Green Slip Records]
        (studentNumber, slipType_green, dateAvail_green,
         DaysOfAbs_greenDispen, status_green, expiryDate_greenDispen,
         purposeReason_greenDispen, remarks_greenExc,
         abscenceType_greenExc, datesOfAbscence_greenExc,
         suppDoc_greenExc, authBy_green)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (stud_num, slip_type, date_avail, days, status,
          expiry, purpose, remarks, absence_type, 
          dates_absence, supp_doc, auth_by))
    conn.commit()
    conn.close()
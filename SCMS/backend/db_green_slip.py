from db_connection import get_connection


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

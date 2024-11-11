from config import api, db
from flask import jsonify, request

@api.route("/addNotice", methods = ['POST']) #/addNotice is endpoint for when the request will be made by client
def addnotice():
    data = request.json #Expects the json data
    notice_to_be_added = data["notice_name"] #data contains the the json data which is in key value pair format
    notice_desc=data["notice_description"] # Here notice description is a key in data object
    author = data["author"]
    cur = db.cursor()
    cur.execute("INSERT INTO notice(notice_name, notice_description, author) VALUES (%s, %s, %s)", (notice_to_be_added, notice_desc, author))
    db.commit()
    return jsonify({"message": "Notice added successfully."}), 201


@api.route("/results", methods = ['GET']) # Working as expected
def Results():
    cur = db.cursor()
    cur.execute("SELECT * FROM test")
    results_retrieved = cur.fetchall()
    result_list = []
    if results_retrieved:
        for result in results_retrieved:
            result_data = {
                "test_id": result[0],
                "student_id": result[2],
                "subject_id": result[1],
                "score": result[3]
            }
            result_list.append(result_data)
    
        return jsonify(result_list)
    else:
        return jsonify({"error": "Error retrieving results"})   
  

@api.route("/result/student", methods = ['GET']) # Working as expected
def RandomStudentScore():
    data = request.json
    
    student_id=data["id"]
    if not student_id:
        return "Enter valid student id!", 400
    cur = db.cursor()
    cur.execute("SELECT * FROM test WHERE student_id = %s", (student_id,))
    student = cur.fetchall()
    all_data=[]
    if student:
        for row in student:
            student_data = {
                "test_id": row[0],
                "subject_id": row[1], 
                "score": row[3]
            }
            all_data.append(student_data)
        return jsonify(all_data)
    else:
        return jsonify({"message": "Enter valid student id!"})
    
    
@api.route("/result/forSubject", methods = ['GET'])
def ParticularSubject():
    data = request.json
    subject_id = data["subject_id"]
    cur = db.cursor()
    cur.execute("SELECT * FROM test WHERE subject_id = %s", (subject_id))
    student = cur.fetchall()
    all_data = []
    if student:
        for row in student:
            student_data = {
                "test_id": row[0],
                "score": row[4],
                "student_id":row[3]
            }
            all_data.append(student_data)
            
        return jsonify(all_data)
    else:
        return "Enter valid subject id!" 



@api.route("/result/insertScores", methods = ['POST']) # Working as expected!
def insertScores():
    cur = db.cursor()
    data = request.json
    student_id = data["id"]
    subject_id = data["subject_id"]
    test_score = data["test_score"]
    test_id = data["test_id"]
    cur.execute("INSERT INTO test(test_id, subject_id, student_id, score) VALUES (%s, %s, %s, %s)", (test_id, subject_id, student_id, test_score))
    db.commit()
    return jsonify({"message": "Score added successfully."}), 201 


@api.route("/viewNotice", methods = ['GET'])
def viewNotice():
    cur = db.cursor()
    cur.execute("SELECT * FROM notice WHERE DATE(cur_date) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()")
    notices = cur.fetchall()
    notices_list = []
    if notices:
        for notice in notices:
            #if notices_count[0] > 10 and notice[0] <= (notices_count - 10):
                #continue
            notice_data = {
                "notice_id": notice[0],
                "notice_name": notice[1], 
                "notice_description": notice[2],
                "notice_date": notice[3].strftime('%Y-%m-%d'),
                "author": notice[4]
            }
            notices_list.append(notice_data)
        return jsonify(notices_list)
    else:
        return jsonify({"message": "No availabe Notice!"})
  

@api.route("/fillAttendance", methods = ['POST'])
def fillAttendance():
    cur = db.cursor()
    data = request.json
    presentees = data["presentStudents"]  # Array of student IDs    
    #classId = data["classId"]
    subject_name = data["subject_name"]
    print(data)
    # Update the lectures_completed for the subject
    cur.execute("UPDATE subject SET lectures_completed = lectures_completed + 1 WHERE subject_name = %s", (subject_name,))
    db.commit()  # Commit after updating the subject table
    
    # Fetch the updated lectures_completed for the subject
    cur.execute("SELECT lectures_completed FROM subject WHERE subject_name = %s", (subject_name,))
    lec_completed = cur.fetchone()
    
    if lec_completed:
        lec_completed = lec_completed[0]  # Get the first value (lectures_completed)
    else:
        # Handle case where the subject was not found
        print("Subject not found!")
        return
    
    cur.execute("SELECT subject_id FROM subject WHERE subject_name = %s", subject_name)
    subject_id = cur.fetchone()
    subject_id = subject_id[0]
    # Loop through each student in the presentees list
    for student_id in presentees:
        # Update lectures_attended for each student
        cur.execute("UPDATE student SET lectures_attended = lectures_attended + 1 WHERE student_id = %s AND subject_id = %s", (student_id, subject_id))
        db.commit()  # Commit after updating the student table
        
        # Fetch the updated lectures_attended for the student
        cur.execute("SELECT lectures_attended FROM student WHERE student_id = %s AND subject_id = %s", (student_id, subject_id))
        lec_attended = cur.fetchone()
        
        if lec_attended:
            lec_attended = lec_attended[0]  # Get the first value (lectures_attended)
        else:
            # Handle case where the student was not found
            print(f"Student {student_id} not found!")
            continue
        
        # Calculate attendance percentage
        if lec_completed > 0:  # To prevent division by zero
            attendance_percent = (lec_attended / lec_completed) * 100
        else:
            attendance_percent = 0  # If no lectures have been completed yet, set to 0
        
        # Update the attendance table for the specific student and class on the given date
        cur.execute("""
            UPDATE attendance
            SET total = %s
            WHERE student_id = %s AND subject_id = %s
        """, (attendance_percent, student_id, subject_id))
    
    db.commit()  # Commit after all updates
    return jsonify({"message": "Attendance Added"})


@api.route("/attendance/specificStudent", methods = ['POST'])
def studentAttendance():
    cur = db.cursor()
    data = request.json
    student_id = data["student_id"]
    cur.execute("SELECT * FROM attendance WHERE student_id = %s", (student_id))
    
    attendanceInfo = cur.fetchall()
    print(type(attendanceInfo))
    if attendanceInfo is None:
        return jsonify({"message": "No information on this student"})
    studentAttendance = []
    """ for oneSubject in attendanceInfo:
        subjectAttendance = {
            "subject_id": oneSubject[2],
            "SubjectTotal": oneSubject[3]
        }
        studentAttendance.append(subjectAttendance) """
    attendance = {
        "Physics": attendanceInfo[0][2],
        "Mathematics": attendanceInfo[1][2],
        "Biology": attendanceInfo[2][2],
        "Chemistry": attendanceInfo[3][2]
    }
    return jsonify(attendance)
        
   
        
@api.route("/attendance/specificSubject", methods = ['GET'])
def specificSubject():
    cur = db.cursor()
    data = request.json
    subject_id = data["subject_id"]
    cur.execute("SELECT * FROM attendance WHERE subject_id = %s", (subject_id))
    attendanceInfo = cur.fetchall()
    if attendanceInfo is None:
        return jsonify({"message": "No information on this subject id"})
    subjectAttendance = []
    for oneSubject in attendanceInfo:
        sAttendance = {
            "id": oneSubject[0],
            "StudentTotal": oneSubject[3]
        }
        subjectAttendance.append(sAttendance)
    return jsonify(subjectAttendance)


   
@api.route("/attendance/allAttendance", methods = ['GET'])
def allAttendance():
    cur = db.cursor()
    cur.execute("SELECT * FROM student_login")
    
    allAttendance = cur.fetchall()
    attendanceList = []
    for row in allAttendance:
        name = row[2]
        student_id = row[0]
        cur.execute("SELECT total FROM attendance WHERE subject_id = 1 AND student_id = %s", (row[0]))
        physicstotal = cur.fetchone()
        physicstotal = physicstotal[0]
        cur.execute("SELECT total FROM attendance WHERE subject_id = 2 AND student_id = %s", (row[0]))
        mathstotal = cur.fetchone()
        mathstotal = mathstotal[0]
        cur.execute("SELECT total FROM attendance WHERE subject_id = 3 AND student_id = %s", (row[0]))
        biototal = cur.fetchone()
        biototal = biototal[0]
        cur.execute("SELECT total FROM attendance WHERE subject_id = 4 AND student_id = %s", (row[0]))
        chemtotal = cur.fetchone()
        chemtotal = chemtotal[0]
        oneRow = {
            "id": row[0],
            "name": name,
            "Mathematics": mathstotal,
            "Physics": physicstotal,
            "Biology": biototal,
            "Chemistry": chemtotal
        }
        attendanceList.append(oneRow)
        
    return jsonify(attendanceList)


@api.route("/allStudents", methods = ['GET'])
def allStudents():
    cur = db.cursor()
    cur.execute("SELECT student_id FROM student_login")
    student_data = cur.fetchall()
    #student_id = student_data[0]
    allstudents = []
    if student_data:
        for row in student_data:
            student_id = row[0]
            cur.execute("SELECT DISTINCT student_name FROM student WHERE student_id = %s", (student_id))
            name = cur.fetchone()
            cur.execute("SELECT email FROM student_login WhERE student_id = %s", (student_id))
            email = cur.fetchone()
            email = email[0]
            name = name[0]
            studentlist = {
                "id": student_id,
                "name": name,
                "email": email
            }
            allstudents.append(studentlist)
        return jsonify(allstudents)
    return jsonify([])
            


@api.route("/login/admin", methods = ['POST'])
def adminLogin():
    data = request.json
    role = data["role"]
    admin_email = data["email"]
    admin_pass = data["password"]
    cur = db.cursor()
    cur.execute("SELECT * FROM admin WHERE admin_email = %s AND admin_password = %s", (admin_email, admin_pass))
    dbdata = cur.fetchone()
    if dbdata is None:
        return jsonify({"message": "User does not exist"})
    admin_id = dbdata[0]
    admin_mail = dbdata[2]
    admin_pass = dbdata[3]
    if role == "admin":
        if admin_mail and admin_pass:
            return jsonify({
                "role" : role,
                "token": admin_id
        })
    return jsonify({"error": "Incorrect Role"})



@api.route("/login/student", methods = ['POST'])
def studentLogin():
    #role = request.args.get('role')
    data = request.json
    role = data["role"]
    student_email = data["email"]
    student_pass = data["password"]
    cur = db.cursor()
    cur.execute("SELECT * FROM student_login WHERE email = %s AND password = %s", (student_email, student_pass))
    dbdata = cur.fetchone()
    if dbdata is None:
        return jsonify({"message": "User does not exist"})
    student_id = dbdata[0]
    student_mail = dbdata[1]
    student_pass = dbdata[3]
    if role == "student":
        if student_mail and student_pass:
            return jsonify({
                "role" : role,
                "token": student_id
        })
    return jsonify({"error": "Incorrect Role"})        


@api.route("/login/faculty", methods = ['POST'])
def facultyLogin():
    data = request.json
    role = data["role"]
    faculty_email = data["email"]
    faculty_pass = data["password"]
    cur = db.cursor()
    cur.execute("SELECT * FROM faculty WHERE email = %s AND password = %s", (faculty_email, faculty_pass))
    dbdata = cur.fetchone()
    if dbdata is None:
        return jsonify({"message": "User does not exist"})
    faculty_id = dbdata[0]
    faculty_mail = dbdata[1]
    faculty_pass = dbdata[2]
    if role == "faculty":
        if faculty_mail and faculty_pass:
            return jsonify({
                "role" : role,
                "token": faculty_id
        })
    return jsonify({"error": "Incorrect Role"})        



@api.route("/login/cashier", methods = ['POST'])
def cashierLogin():
    data = request.json
    role = data["role"]
    cashier_email = data["email"]
    cashier_pass = data["password"]
    cur = db.cursor()
    cur.execute("SELECT * FROM cashier WHERE cashier_email = %s AND cashier_password = %s", (cashier_email, cashier_pass))
    dbdata = cur.fetchone()
    if dbdata is None:
        return jsonify({"message": "User does not exist"})
    cashier_id = dbdata[0]
    cashier_mail = dbdata[1]
    cashier_pass = dbdata[2]
    
    if role == "cashier":
        if cashier_mail and cashier_pass:
            return jsonify({"token": cashier_id})
        return jsonify({"error": "Invalid Credentials"})
    return jsonify({"error": "Incorrect Role"})


@api.route("/addStudent", methods = ['POST'])
def addStudent():
    cur = db.cursor()
    data = request.json
    student_name = data["name"]
    #class_div = data["class_div"]
    student_email = data["email"]
    student_password = data["password"]
    '''class_id = 0
    if class_div == "A":
        class_id = 1
    else: 
        class_id = 2
    '''
    #cur.execute("SET foreign_key_checks = 0") #temporarily disable
    #db.commit()
    cur.execute("INSERT INTO student_login(email, name, password) VALUES(%s, %s, %s)", (student_email, student_name, student_password))
    db.commit()
    
    cur.execute("SELECT * FROM student_login WHERE email = %s", (student_email))
    studentInfo = cur.fetchone()
    if studentInfo is None:
        return jsonify({"error": "Student not found after insertion"}), 500
    student_id = studentInfo[0]
    
    # Insert values into student table for each subject
    cur.execute("INSERT INTO student(student_name, student_id, lectures_attended, subject_id) VALUES(%s, %s, %s, %s)", (student_name, student_id, 0, 1))
    db.commit()
    cur.execute("INSERT INTO student(student_name, student_id, lectures_attended, subject_id) VALUES(%s, %s, %s, %s)", (student_name, student_id, 0, 2))
    db.commit()
    cur.execute("INSERT INTO student(student_name, student_id, lectures_attended, subject_id) VALUES(%s, %s, %s, %s)", (student_name, student_id, 0, 3))
    db.commit()
    cur.execute("INSERT INTO student(student_name, student_id, lectures_attended, subject_id) VALUES(%s, %s, %s, %s)", (student_name, student_id, 0, 4))
    db.commit()
    # Insert into fees for the student
    cur.execute("INSERT INTO fees(id, fees_paid, fees_remaining) VALUES (%s, %s, %s)", (student_id, 0, 25000))
    db.commit()
    # Insert into attendance table for each subject
    cur.execute("INSERT INTO attendance(student_id, subject_id, total) VALUES (%s, %s, %s)", ( student_id, 1, 0.0))
    db.commit()
    cur.execute("INSERT INTO attendance(student_id, subject_id, total) VALUES (%s, %s, %s)", ( student_id, 2, 0.0))
    db.commit()
    cur.execute("INSERT INTO attendance(student_id, subject_id, total) VALUES (%s, %s, %s)", ( student_id, 3, 0.0))
    db.commit()
    cur.execute("INSERT INTO attendance(student_id, subject_id, total) VALUES (%s, %s, %s)", ( student_id, 4, 0.0))
    db.commit()
    #cur.execute("SET foreign_key_checks = 1")
    #db.commit()
    return jsonify({"message": "Student Added"})


@api.route("/fees/payFees", methods = ['POST'])
def payFees():
    cur = db.cursor()
    data = request.json
    student_id = data["student_id"]
    thisMuch = data["feesAmount"]
    cur.execute("SELECT * FROM fees WHERE id = %s", (student_id))
    studentFeesInfo = cur.fetchone()
    if studentFeesInfo is None:
        return jsonify({"message": "No such student exists"})
    feesPaid = studentFeesInfo[1]
    feesRemaining = studentFeesInfo[2]
    cur.execute("UPDATE fees SET fees_paid = fees_paid+%s WHERE id = %s", (thisMuch, student_id))
    cur.execute("UPDATE fees SET fees_remaining = fees_remaining-%s WHERE id = %s",(thisMuch, student_id))
    db.commit()
    cur.execute("SELECT fees_remaining FROM fees WHERE id = %s", (student_id))
    feesRemaining = cur.fetchone()
    return jsonify({"message": "Fees updated"})
    

@api.route("/fees/checkFees", methods = ['POST'])
def checkFees():
        cur = db.cursor()
        data = request.json
        student_id = data["student_id"]
        cur.execute("SELECT * FROM fees WHERE id = %s", (student_id))
        feeDetails = cur.fetchone()
        if feeDetails is None:
            return jsonify({"message": "No Information on this student id"})
        paidFees = feeDetails[1]
        feesRemaining = feeDetails[2]
        feesInfoList = {}
        totalFees = paidFees+feesRemaining
        feesInfoList = {
            "paidFees": paidFees,
            "totalFees": totalFees
        }
        
        return jsonify(feesInfoList)
        

@api.route("/fees/allFees", methods = ['GET'])
def allFees():
        cur = db.cursor()
        cur.execute("SELECT * FROM fees")
        feeDetails = cur.fetchall()
        if feeDetails is None:
            return jsonify({"message": "No Information on this student id"})
        """ student_id = feeDetails[0]
        feesPaid = feeDetails[1]
        feesRemaining = feeDetails[2] """
        feesInfoList = []
        for individual in feeDetails:
            cur.execute("SELECT name FROM student_login WHERE student_id = %s", (individual[0]))
            stud_name = cur.fetchone()
            stud_name = stud_name[0]
            onerow = {
                "id": individual[0],
                "name": stud_name,
                "paidFees": individual[1],
                "totalFees": individual[1]+individual[2]
            }
            feesInfoList.append(onerow)
        return jsonify(feesInfoList)
 

@api.route("/addCashier", methods = ['POST'])
def addCashier():
    cur = db.cursor()
    data = request.json
    #cashier_id = data["cashier_id"]
    name = data["name"]
    cashier_email = data["email"]
    cashier_password = data["password"]
    cur.execute("INSERT INTO cashier(cashier_email, cashier_password, name) VALUES (%s, %s, %s)", (cashier_email, cashier_password, name))
    db.commit()
    return ({"message": "New cashier added"})


@api.route("/addFaculty", methods = ['POST'])
def addFaculty():
    cur = db.cursor()
    data = request.json
    name = data["name"]
    #faculty_id = data["id"]
    faculty_email = data["email"]
    faculty_password = data["password"]
    cur.execute("INSERT INTO faculty(name, email, password) VALUES (%s, %s, %s)", (name, faculty_email, faculty_password))
    db.commit()
    return ({"message": "New faculty added"})


@api.route("/viewFaculty", methods = ['GET'])
def viewFaculty():
    cur = db.cursor()
    cur.execute("SELECT * FROM faculty")
    data = cur.fetchall()
    facultylist = []
    if data:    
        for row in data:
                info = {
                    "name": row[3],
                    "email": row[1]
                }
                facultylist.append(info)
        return jsonify(facultylist)
    return jsonify([])


@api.route("/viewCashier", methods = ['GET'])
def viewCashier():
    cur = db.cursor()
    cur.execute("SELECT * FROM cashier")
    data = cur.fetchall()
    facultyList = []
    if data:    
        for row in data:
                info = {
                    "name": row[3],
                    "email": row[1]
                }
                facultyList.append(info)
        return jsonify(facultyList)
    return jsonify([])



if __name__=='__main__':
    api.run(host = '0.0.0.0', debug = 'True')
    # host = '192.168.115.246'

import mysql.connector
import sys

try:
    connection = mysql.connector.connect(
        user="root",
        password="Password@1234",
        host="localhost",
        port=3308,
        database="scheduler",
        charset="utf8mb4",
        auth_plugin='mysql_native_password'

    )
#except mysql.Error as e:
except ValueError:
    print("Error connecting to Mysql Platform:{e}")
    sys.exit(1)

def get_crn_course(crn):
    cursor11=connection.cursor()
    sql= f"SELECT Department,Number,Name,Credits,Professor, Start_Time, End_Time, Days,Location, CRN  FROM scheduler.spring2024 s WHERE s.CRN ='{crn}';"
    cursor11.execute(sql)
    rows=cursor11.fetchall()
    return rows
def create_new_student(data):
    cursor2=connection.cursor()
    sql = "INSERT INTO scheduler.students (Name,PantherID, Degree, Major, Email, Phone) VALUES (%s, %s, %s, %s,%s, %s)"
    cursor2.execute(sql, data)
    connection.commit()


def check_id(pantherid):
    cursor=connection.cursor()
    sql="SELECT DISTINCT PantherID FROM scheduler.students"
    cursor.execute(sql)
    result=cursor.fetchall()
    ids=[]
    for x in result:
        ids.append(int(x[0]))
    if int(pantherid) in ids:
        return True
    else:
        return False
def getcourses111(dept):
    cursor=connection.cursor()

    
    command1=f"SELECT Name, Number FROM classes WHERE Department= '{dept}' "
    numbers=[]
    names=[]
    url=[]
    cursor.execute(command1)
    rows = cursor.fetchall()
    for row in rows:
        num=dept+str(row[1])
        numbers.append(num)
        names.append(row[0])
    return names,numbers


def get_url(dept,number):
        cursor10=connection.cursor(buffered=True)
        main2=f"SELECT Prerequisites  FROM scheduler.classes WHERE Department ='{dept}' and Number= '{number}'"
        cursor10.execute(main2)
        urls = cursor10.fetchone()
        return urls
def getcourses(dept):
    cursor=connection.cursor()
    main= f"SELECT Name, `Number`, CRN, Professor, Credits, Start_Time, End_Time, Location, Days FROM ( SELECT Name, `Number`, CRN, Professor, Credits, Start_Time, End_Time, Location, Days, ROW_NUMBER() OVER (PARTITION BY s.`Number` ORDER BY CRN) AS rn FROM scheduler.spring2024 s where Department='{dept}' ) AS numbered WHERE rn = 1;"
    #command1=f"SELECT DISTINCT s.Name, s.`Number`, s.CRN, s.Professor, s.Credits, s.Start_Time, s.End_Time, s.Location,  s.Days, c.Prerequisites  FROM scheduler.spring2024 s  JOIN scheduler.classes c ON s.Department = c.Department AND s.`Number` = c.`Number`  WHERE s.Department = '{dept}'"
    numbers=[]
    names=[]
    #url=[]
    crn=[]
    professor=[]
    credits=[]
    time=[]
    location=[]
    days=[]
    only_nums=[]
    cursor.execute(main)
    rows = cursor.fetchall()
    for row in rows:
        only_nums.append(str(row[1]))
        num=dept+str(row[1])
        numbers.append(num)
        names.append(row[0])
        crn.append(row[2])
        professor.append(row[3])
        credits.append(row[4])
        tim= row[5] + " - " + row[6]
        time.append(tim)
        days.append(row[-1])
        location.append(row[-2])
        #url.append(row[-1])
    #print(numbers)
    def urls(only_nums: tuple, dept):
        cursor10=connection.cursor()
        main2=f"select distinct Prerequisites  from scheduler.classes where Department ='{dept}' and Number in {only_nums}"
        cursor10.execute(main2)
        urls = cursor.fetchall()
        return urls
    url=urls(tuple(only_nums), dept)
    print(url)
    #print(numbers,names,crn,professor,credits, url, time,days, location)
    return numbers,names,crn,professor,credits, url, time,days, location

def directory():
    cursor5=connection.cursor()
    command5=f"SELECT Name, Department, Email, Phone,PantherID from scheduler.professors p"
    names=[]
    department=[]
    email=[]
    phone=[]
    id=[]
    cursor5.execute(command5)
    rows=cursor5.fetchall()
    for row in rows:
        names.append(row[0])
        department.append(row[1])
        email.append(row[2])
        phone.append(row[3])
        id.append(row[-1])
    return names,department, email,phone,id

def uniqdepartments():
    cursor6=connection.cursor()
    command6="SELECT DISTINCT Department FROM scheduler.professors p"
    cursor6.execute(command6)
    rows=cursor6.fetchall()
    dep=[]
    for x in rows:
        dep.append(x[0])
    return dep

def profid(name):
    cursor7=connection.cursor()
    sql=f"select PantherID  from scheduler.professors p where Name = '{name}'"
    cursor7.execute(sql)
    rows=cursor7.fetchone()
    return rows[0]

def add_classes(data):
    cursor2=connection.cursor()
    sql = "INSERT INTO scheduler.spring2024 (Department,ProfessorID, Number, Name,Credits,Professor,Start_time,End_time,Days,Location,CRN) VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s)"
    cursor2.execute(sql, data)
    connection.commit()

def delete(data):
    cursor3=connection.cursor()
    sql = "DELETE FROM scheduler.spring2024 WHERE Department = %s AND Number = %s AND CRN = %s"
    cursor3.execute(sql, (data[0], int(data[1]), str(data[2])))
    connection.commit() 
    print("DELETED")  

def updates(data):
    cursor2 = connection.cursor()
    sql = "UPDATE scheduler.spring2024 SET Department = %s, ProfessorID = %s, Number = %s, Name = %s, Credits = %s, Professor = %s, Start_time = %s, End_time = %s, Days = %s, Location = %s WHERE CRN = %s"
    cursor2.execute(sql, data)
    connection.commit()

def add_prof(data):
    cursor8=connection.cursor()
    sql="INSERT INTO scheduler.professors (Name, PantherID, Department, Email, Phone) VALUES (%s, %s, %s, %s, %s)"
    cursor8.execute(sql,data)
    connection.commit()

def update_prof(data):
    cursor8 = connection.cursor()
    sql = "UPDATE scheduler.professors SET Name=%s, Department=%s, Email=%s, Phone=%s WHERE PantherID=%s"
    cursor8.execute(sql, (data[0], data[2], data[-2], data[-1], data[1]))
    connection.commit()

def remove_prof(data):
    print(data)
    cursor9=connection.cursor()
    sql=f"DELETE FROM  scheduler.professors  WHERE PantherID={int(data)}"
    cursor9.execute(sql)
    connection.commit()

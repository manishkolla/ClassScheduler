from flask import Flask, render_template, request, url_for, redirect ,session
from flask import jsonify
from email.mime.text import MIMEText 
import smtplib 
from email.message import EmailMessage 
from auth import create_user, sign_in_with_email_and_password, reset_password
from databaseconnection import getcourses,add_classes,delete, updates,directory,uniqdepartments,getcourses111,profid,add_prof,update_prof,remove_prof, get_url,check_id,create_new_student,get_crn_course
import firebase_admin
from firebase_admin import credentials,db
from firebase_admin import storage



app = Flask(__name__)
cred = credentials.Certificate('creds.json')
DB_URL="https://schedulemaker-36fe8-default-rtdb.firebaseio.com"
firebase_admin.initialize_app(cred, {"databaseURL": DB_URL})

@app.route('/Saved')
def register():
    try:
        #student_past = db.reference(f'Students/{pantherid}/past')
        present_ref = db.reference(f'Students/{pantherid}/present')
        
        # Fetch existing registered classes
        existing_classes = present_ref.get()
        print("ESISTING: ", existing_classes)
        # If there are existing classes, merge them with the new classes
        if existing_classes:
            new=registered_classes+existing_classes
            present_ref.set(new)
            print("came")
        else:
            print("ELSE")
            # If there are no existing classes, set the registered classes directly
            present_ref.set(registered_classes)
        
        return render_template('registered_success.html')
    except:
        return render_template('Schedule.html')
    



@app.route('/ViewmyClasses')
def myclasses():
    present_ref = db.reference(f'Students/{pantherid}/present').get()
    #SELECT Department,Number,Name,Credits,Professor, Start_Time, End_Time, Days,Location, CRN  FROM scheduler.spring2024 s WHERE s.CRN ='{crn}'
    classes_rn=[]
    for x in present_ref:
        details=get_crn_course(x)[0]
        print(details)
        numbers=details[0]
        names=details[1]
        names=details[2]
        credits=details[3]
        professor=details[4]
        days=details[7]
        s_time=details[5]
        e_time=details[6]
        time= str(days) + str(s_time) + str(e_time)
        crn=details[-1]
        location=details[-2]
        classes_add= {"name": names,
                    "number": numbers,
                    "CRN": crn,
                    "Professor": professor,
                    "Credits": credits,
                    "daytime": time,
                    "Location": location
                    }
        classes_rn.append(classes_add)
    print(classes_rn)
    return render_template('viewclasses_stud.html', classes=classes_rn)

@app.route('/removesavedclass/success')
def success_course_removed():
    return render_template('remove_class_success')

@app.route("/removesavedclass", methods= ['GET', 'POST'])
def remove_my_class():
    if request.method == 'POST':
        saved_classes = db.reference(f'Students/{pantherid}/present').get()
        present_ref = db.reference(f'Students/{pantherid}/present')
        crn=request.form['crn']
        for x in saved_classes:
            if int(crn) == int(x):
                saved_classes.remove(x)
            else:
                pass
        present_ref.set(saved_classes)
        return render_template('remove_class_success.html')
    else:
        return render_template('removed_saved_class.html')



global classes


role=''
department=''
@app.route("/", methods=['GET', 'POST'])
def index():
    global role
    if request.method == 'POST':
        if 'student' in request.form:
            role='student'
            return render_template('base.html')
        elif 'faculty' in request.form:
            role='faculty'
            return redirect(url_for('faculty_login'))
    return render_template('decision.html')

@app.route("/schedule", methods=['POST']) 
def schedule():
    global registered_classes
    registered_classes=[]
    global selected_classes
    finalclasses=[]
    global numbers
    numbers=[]
    if request.method == 'POST':
        selected_classes = request.form.getlist('classes')
        for x in selected_classes:
            dep=x.split(",")[-1][:-4]
            numbers.append(x.split(",")[-1])
        links=[]
        for x in numbers:
            x=x[-4:]
            print(x,dep)
            l=get_url(dep,x)
            l=l[0]
            print(l)
            links.append(l)
        for course in classes:
            for number in range(len(numbers)):
                if course["number"] == numbers[number]:
                    registered_classes.append(int(course['CRN']))
                    selected_classes[number]+= f", CRN: {course['CRN']}"
                    selected_classes[number]+= f", Professor: {course['Professor']}"
                    selected_classes[number]+= f", Credits: {course['Credits']}"
                    selected_classes[number]+= f", Location: {course['Location']}"
                    selected_classes[number]+= f" , Day & Time: {course['daytime']}"
                    selected_classes[number]+= f" ,{links[number]}"
                    #selected_classes[number]+= f" ,{course['url'][0]}"
        print(registered_classes)
        return redirect(url_for('scheduler'))
    else:
        return render_template('index.html')

@app.route('/schedule')
def scheduler():
    return render_template('Schedule.html', selected_classes=selected_classes)


# Route for faculty login
@app.route("/faculty/login", methods=['GET', 'POST'])
def faculty_login():
    # Add your faculty login logic here
    return render_template('faculty.html')


@app.route('/faculty/postlogin', methods=['POST', 'GET'])
def facultylogin():
    if request.method=='POST':
        username = request.form['username']       
        username=username.lower()
        password = request.form['password']
        global degree
        global department
        department= request.form['department']
        global d
        d=department
        degree= request.form['degree']
        print(department,degree)
        if username == 'admin' and password == 'admin':  # Dummy authentication
            # Redirect the user to a different webpage after successful login
            return redirect(url_for('facultymodify'))  # Redirect to 'dashboard' route
        elif username!='admin' and password!='admin':
            try:
                sign_in_with_email_and_password(username,password)
                #session['user']=username
                return redirect(url_for('facultymodify'))
            except:
                return render_template('faculty.html', error='Invalid username or password')
                #return redirect(url_for('signups'))
        else:
            return render_template('faculty.html')
    else:
            # If login is unsuccessful, redirect back to the login page or show an error message
        return render_template('faculty.html')

@app.route('/faculty/signups')  
def faculty_signup():
    return render_template('facultysignup.html')

@app.route('/faculty/postsignup', methods=['POST', 'GET'])       
def facultysignup():
    print("flask")
    if request.method=='POST':
        username = request.form['email']
        username=username.lower()
        password = request.form['password']
        try:
            create_user(username,password)
            print("created")
            return redirect(url_for('faculty_login'))
            #return render_template('faculty.html')
        except:
            return render_template('facultysignup.html', error='An error occurred, Please try again')
    return render_template('facultysignup.html')

@app.route('/facultymodify', methods=['POST','GET'])
def facultymodify():
    return render_template('facultyfeatures.html')

@app.route('/faculty/forgotpassword', methods=['GET', 'POST'])
def facultyforgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        reset_password(email)
        return render_template('faculty.html')

    return render_template('facultyforgotpassword.html')
##############################################################################
@app.route('/faculty/addprofessor', methods=['GET','POST'])
def addprof():
    if request.method == 'POST':
        depart=request.form['department']
        num=request.form['number']
        name=request.form['name']
        email=request.form['email']
        id=request.form['panther']
    try:
        add_prof((name,int(id),depart,email,int(num)))
        print("Prof Added")
        return render_template('successprof.html')
    except Exception as e:
            return render_template('addprof.html')
    
@app.route('/faculty/addprof/success')
def addprof_success():
    return render_template('successprof.html')
##############################################################################
@app.route('/faculty/updateprofessor', methods=['GET','POST'])
def updateprof():
    if request.method == 'POST':
        depart=request.form['department']
        num=request.form['number']
        name=request.form['name']
        email=request.form['email']
        id=request.form['panther']
    try:
        update_prof((name,int(id),depart,email,int(num)))
        print((name,int(id),depart,email,int(num)))
        print("Prof Updated")
        return render_template('successprof.html')
    except Exception as e:
            print(e)
            return render_template('updateprof.html')
    
@app.route('/faculty/updateprof/success')
def upd_prof_success():
    return render_template('successprof.html')
##############################################################################

@app.route('/faculty/removeprof', methods=['GET', 'POST'])
def deleteprof():
    return render_template('removeprof.html')

@app.route('/faculty/removeprofessor', methods=['GET','POST'])
def removeprof():
    if request.method == 'POST':
        depart=request.form['department']
        num=request.form['number']
        name=request.form['name']
        email=request.form['email']
        id=request.form['panther']
    try:
        remove_prof((id))
        print("Prof Deleted")
        return render_template('successprof.html')
    except Exception as e:
            print(e)
            return render_template('removeprof.html')
@app.route('/faculty/removeprof/success')
def rem_prof_success():
    return render_template('successprof.html')
#############################################################################
@app.route('/faculty/addclasses', methods=['GET','POST'])
def addclasses():
    message = request.args.get('message')
    return render_template('addcourses.html', message=message)

@app.route('/faculty/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        depart=request.form['department']
        num=request.form['number']
        name=request.form['courseName']
        credits=request.form['credits']
        crn=request.form['crn']
        prof=request.form['professor']
        days=request.form['d']
        stime=request.form['st']
        etime=request.form['et']
        location=request.form['location']
        professorid=profid((prof))

    #Department,ProfessorID, Number, Name,Credits,Professor,Start_time,End_time,Days,Location,CRN
    try:
         add_classes((depart,professorid,num,name,credits,prof,stime,etime,days,location,crn))
         return redirect(url_for('success'))
    except Exception as e:
        return redirect(url_for('addclasses'), message=str(e))
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

@app.route('/faculty/updateclasses', methods=['GET','POST'])
def updateclasses(message=""):
    # message = request.args.get('message')
    #message=""
    return render_template('updatecourse.html', message=message)

@app.route('/faculty/update', methods=['GET','POST'])
def update():
    global depart
    if request.method == 'POST':
        depart=request.form['department']
        num=request.form['number']
        name=request.form['courseName']
        credits=request.form['credits']
        crn=request.form['crn']
        prof=request.form['professor']
        days=request.form['d']
        stime=request.form['st']
        etime=request.form['et']
        location=request.form['location']
        professorid=profid((prof))
    # print(depart,num,name,credits,professorid,days,stime,etime,location)
    try:
         updates((depart,str(professorid),int(num),name,credits,prof,stime,etime,days,location,str(crn)))
         print("Updated!")
         return redirect(url_for('successupd'))
    except Exception as e:
        return redirect(url_for('updateclasses', message=str(e)))
    
@app.route('/faculty/update/success', methods=['GET','POST'])
def successupd():
    return render_template('success_upd.html')

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route('/faculty/removeclasses', methods=['GET','POST'])
def removeclasses():
    message = request.args.get('message')
    return render_template('removecourses.html', message=message)

@app.route('/faculty/remove', methods=['GET','POST'])
def remove():
    if request.method == 'POST':
        depart=request.form['department']
        num=request.form['number']
        name=request.form['courseName']
        crn=request.form['crn']
    try:
         delete((depart,num,crn))
         return redirect(url_for('successremoval'))
    except Exception as e:
        return render_template('removecourses.html', message=str(e))
    
@app.route('/faculty/removeclasses/success')
def successremoval():
    return render_template('successremoval.html')

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.route('/faculty/viewclasses', methods=['GET','POST'])
def view():
    return redirect(url_for('viewfunction'))

@app.route('/faculty/view')
def viewfunction():
    #numbers,names,crn,professor,credits, url, time, location
    def retrival(name):
        global classes
        classes=[]
        numbers=getcourses(name)[0]
        names=getcourses(name)[1]
        urls=getcourses(name)[5]
        crn=getcourses(name)[2]
        professor=getcourses(name)[3]
        credits=getcourses(name)[4]
        time=getcourses(name)[6]
        days=getcourses(name)[-2]
        location=getcourses(name)[-1]
        for a,b,c,d,e,f,g,h,i in zip(numbers,names,crn,professor,credits, urls, time,days, location):
            classes_add= {"name": b,
                    "number": a,
                    "CRN": c,
                    "Professor": d,
                    "Credits": e,
                    "daytime": g,
                    "Days": h,
                    "Location": i,
                    "url": f}
            classes.append(classes_add)
        return classes
    if department== 'Computer Science' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('CSC'))
    if department== 'Economics' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('ECON'))
    if department== 'Biology' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('BIOL'))
    if department== 'Chemistry' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('CHEM'))
    if department== 'Criminal Justice' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('CRJU'))
    if department== 'English' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('ENGL'))
    if department== 'Computer Information Sciences' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('CIS'))
    if department== 'Data Science' and degree=='Bachelors':
        return render_template('viewspring.html',classes=retrival('DSCI'))
    else:
        return render_template('faculty.html', error='This website is in development phases, and not fully functional to support all majors and degree types')
################################################
@app.route('/faculty/viewprofessor', methods=['GET','POST'])
def viewdirect():
    direct=directory()
    names=direct[0]
    department=direct[1]
    email=direct[2]
    phone=direct[3]
    panther=direct[-1]
    staff=[]
    for a,b,c,d,e in zip(names,department,email,phone,panther):
        staff_data= {"name": a, "department":b, "email": c, "phone": d, "PantherID": e}
        staff.append(staff_data)
    return render_template('viewdirectory.html',classes=staff, departments=uniqdepartments())
#############################################################
@app.route('/faculty/catalog')
def catalog():
    return redirect(url_for('viewcatalog'))

@app.route('/faculty/viewcatalog')
def viewcatalog():
    print(d)
    department=""
    if d=='Computer Science' or d=='Data Science':
        print("yes, cs")
        department='CSC'
    if d=='Economics':
        print("yes, econ")
        department='ECON'
    if d== 'Criminal Justice':
        print("yes, cj")
        department='CRJU'
    if d== 'Biology':
        print("yes, bio")
        department='BIOL'
    if d=='Chemistry':
        department= 'CHEM'
    if d== 'English':
        department='ENGL'
    else:
        pass
    nam=getcourses111(department)[0]
    num=getcourses111(department)[1]
    all_courses=[]
    for x,y in zip(nam,num):
        all= {"name": x, 
              "number": y}
        all_courses.append(all)
    return render_template('viewclasses.html',classes=all_courses)
   
#######################################################################
@app.route('/faculty/addclasses/success')
def success():
    return render_template('success.html')
######################################################################
@app.route('/Studentfeatures')
def studfeatures():
    return render_template('studentfeatures.html')

global pantherid
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['username']       
        username=username.lower()
        password = request.form['password']
        global major
        global degree
        major = request.form['major']
        degree= request.form['degree']
        global pantherid
        pantherid=request.form['pantherid']
        if username == 'admin' and password == 'admin':  # Dummy authentication
            # Redirect the user to a different webpage after successful login
            return redirect(url_for('studfeatures'))
            #return redirect(url_for('ClassesSelection'))  # Redirect to 'dashboard' route
        elif username!='admin' and password!='admin':
            try:
                if check_id(pantherid)== True:
                    sign_in_with_email_and_password(username,password)
                    return redirect(url_for('studfeatures'))
                else:
                    return render_template('index.html', error='Invalid Panther ID')
                #session['user']=username
            except:
                return render_template('index.html', error='Invalid username or password')
                #return redirect(url_for('signups'))
        else:
            return render_template('index.html')
    else:
            # If login is unsuccessful, redirect back to the login page or show an error message
        return render_template('index.html')
    # Perform login authentication and processing here
    # Redirect or render a new page based on the result
    # return redirect(url_for('ClassesSelection'))



@app.route('/signups')  
def signups():
    return render_template('decision.html')

@app.route('/signup', methods=['POST', 'GET'])       
def signup():
    if request.method=='POST':
        name=request.form['fullname']
        username = request.form['email']
        username=username.lower()
        password = request.form['password']
        pantherid=request.form['pantherid']
        degree=request.form['degree']
        major=request.form['Major']
        phone=request.form['phone']
        try:
            if check_id(pantherid) == True:
                create_user(username,password)
                return render_template('decision.html')
            else:
                try:
                    create_new_student((name,pantherid, degree, major, username,phone))
                    create_user(username,password)
                    return render_template('decision.html')
                except:
                    return render_template('signup.html', error='An error occurred') 
        except:
            return render_template('signup.html', error='An error occurred')
    return render_template('signup.html')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        reset_password(email)
        return render_template('decision.html')

    return render_template('forgotpassword.html')


def logout(session):
    session.pop('user')
    return render_template('index.html')

@app.route('/ClassesSelection')
def ClassesSelection():
    def retrival(name):
        global classes
        classes=[]
        numbers=getcourses(name)[0]
        names=getcourses(name)[1]
        urls=getcourses(name)[5]
        crn=getcourses(name)[2]
        professor=getcourses(name)[3]
        credits=getcourses(name)[4]
        time=getcourses(name)[6]
        location=getcourses(name)[-1]
        days=getcourses(name)[-2]
        for a,b,c,d,e,f,g,h,i in zip(numbers,names,crn,professor,credits, urls, time, location,days):
            z=str(i) + " " + str(g)
            classes_add= {"name": b,
                    "number": a,
                    "CRN": c,
                    "Professor": d,
                    "Credits": e,
                    "daytime": z,
                    "Location": h,
                    "url": f}
            classes.append(classes_add)
        return classes
    if major== 'Computer Science' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('CSC'))
    if major== 'Economics' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('ECON'))
    if major== 'Biology' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('BIOL'))
    if major== 'Chemistry' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('CHEM'))
    if major== 'Criminal Justice' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('CRJU'))
    if major== 'English' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('ENGL'))
    if major== 'Computer Information Sciences' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('CIS'))
    if major== 'Data Science' and degree=='Bachelors':
        return render_template('ClassesSelection.html',classes=retrival('DSCI'))
    else:
        return render_template('index.html', error='This website is in development phases, and not fully functional to support all majors and degree types')




if __name__=='__main__':
    app.run(debug=True)
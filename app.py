from flask import Flask, render_template, request, url_for, redirect ,session
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText 
import smtplib 
from email.message import EmailMessage 
from auth import create_user, sign_in_with_email_and_password, reset_password


# from datetime import datatime
app = Flask(__name__)
# app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
db=SQLAlchemy()
db.init_app(app)

class SelectedClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)

@app.route("/", methods=['POST','GET'])
def index():
    return render_template('base.html')


@app.route("/schedule", methods=['POST']) 
def schedule():
    global finalclasses
    finalclasses=[]
    if request.method == 'POST':
        selected_classes = request.form.getlist('classes')  # Get the list of selected classes
        for class_name in selected_classes:
            print(class_name)
            selected_class = SelectedClass(class_name=class_name)
            finalclasses.append(class_name)
            db.session.add(selected_class)
        db.session.commit()
        return redirect(url_for('scheduler'))
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['username']       
        username=username.lower()
        password = request.form['password']
        major = request.form['major']
        degree= request.form['degree']
        if username == 'admin' and password == 'admin':  # Dummy authentication
            # Redirect the user to a different webpage after successful login
            return redirect(url_for('ClassesSelection'))  # Redirect to 'dashboard' route
        elif username!='admin' and password!='admin':
            try:
                sign_in_with_email_and_password(username,password)
                #session['user']=username
                return redirect(url_for('ClassesSelection'))
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
    return render_template('signup.html')

@app.route('/signup', methods=['POST', 'GET'])       
def signup():
    if request.method=='POST':
        username = request.form['email']
        username=username.lower()
        password = request.form['password']
        try:
            create_user(username,password)
            return redirect(url_for('login'))
        except:
            return render_template('signup.html', error='An error occurred')
    return render_template('signup.html')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        reset_password(email)
        return redirect(url_for('login'))  # Redirect to login after initiating password reset
    return render_template('forgotpassword.html')


def logout(session):
    session.pop('user')
    return render_template('index.html')

@app.route('/ClassesSelection')
def ClassesSelection():
    # Render the dashboard page
    return render_template('ClassesSelection.html')


@app.route('/schedule')
def scheduler():
    # Pass the selected classes data to the schedule template
    #selected_classes = SelectedClass.query.all()
    print(finalclasses)
    return render_template('Schedule.html', selected_classes=finalclasses)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
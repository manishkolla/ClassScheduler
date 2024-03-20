import firebase_admin
from firebase_admin import credentials,db
from firebase_admin import storage
import pyrebase
import  creds

#cred = credentials.Certificate(r"C:\Users\mkolla1\OneDrive - Georgia State University\Desktop\Spring 2024\DBMS\Project\ClassScheduler\creds.json")
firebase=pyrebase.initialize_app(creds.firebaseConfig)
auth=firebase.auth()

# Function to create a new user
def create_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email,password)
        print('Successfully created user:', user)
    except:
        print('Error creating user:')

# Function to sign in with email and password
def sign_in_with_email_and_password(email, password):
        auth.sign_in_with_email_and_password(email,password)

def reset_password(email):
     auth.send_password_reset_email(email)
# # Example usage:
# if __name__ == "__main__":
#     # Example of creating a new user
#     create_user('example@example.com', 'password123')

#     # Example of signing in with email and password
#     sign_in_with_email_and_password('example@example.com', 'password123')
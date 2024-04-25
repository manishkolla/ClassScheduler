from flask import Flask, request, jsonify
from auth import authenticate_user  # Assuming authenticate_user function is implemented in auth.py
import mysql.connector

# Initialize Flask application
app = Flask(__name__)

# Define MySQL connection parameters
mysql_config = {
    'user': 'root',
    'password': 'Data10!',
    'host': 'localhost',
    'port': 3306,
    'database': 'scheduler',
    'charset': 'utf8mb4',
    'auth_plugin': 'mysql_native_password'
}

# Establish MySQL connection
connection = mysql.connector.connect(**mysql_config)
cursor = connection.cursor()

# Function to check if timings overlap
def check_overlap(schedule, new_schedule):
    for time_slot in schedule:
        for new_time_slot in new_schedule:
            if (new_time_slot['start_time'] < time_slot['end_time']) and (new_time_slot['end_time'] > time_slot['start_time']):
                return True
    return False

# Route to generate tentative schedule based on student filters
@app.route('/generate_tentative_schedule', methods=['POST'])
def generate_tentative_schedule():
    # Assuming user authentication is required
    auth_token = request.headers.get('Authorization')
    if not authenticate_user(auth_token):
        return jsonify({'message': 'Unauthorized'}), 401

    # Get user input (department and course number)
    data = request.json
    department = data.get('department')
    course_number = data.get('course_number')

    # Generate SQL query based on department and course number
    sql_query = f"SELECT * FROM Spring2024 WHERE Department='{department}' AND CourseNumber='{course_number}'"

    # Execute SQL query
    cursor.execute(sql_query)
    result = cursor.fetchall()

    # Extract schedule information from the result
    schedule = [{'crn': row[0], 'start_time': row[1], 'end_time': row[2]} for row in result]

    # Check if timings overlap
    if check_overlap(schedule, new_schedule):
        return jsonify({'message': 'Schedule timings overlap. Cannot generate schedule.'}), 400

    # Return generated tentative schedule
    return jsonify({'tentative_schedule': schedule})

# Add more routes and functionality as needed

if __name__ == '__main__':
    app.run(debug=True)

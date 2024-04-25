import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
try:
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()
    logger.info("MySQL connection established successfully")
except mysql.connector.Error as err:
    logger.error(f"Error connecting to MySQL: {err}")
    raise

# Function to check if timings overlap
def check_overlap(schedule, new_schedule):
    """
    Checks to see if there is any overlap between the existing schedule and the new schedule.

    Args:
        schedule (list): Existing schedule.
        new_schedule (list): New schedule to be checked for overlap.

    Returns:
        bool: True if there is an overlap, False otherwise.
    """
    for time_slot in schedule:
        for new_time_slot in new_schedule:
            if (new_time_slot['Start_Time'] < time_slot['End_Time']) and \
               (new_time_slot['End_Time'] > time_slot['Start_Time']) and \
               (new_time_slot['Days'] == time_slot['Days']):
                return True
    return False

# Function to generate tentative schedule based on student filters
def generate_tentative_schedule(department, course_number, new_schedule):
    """
    Generates a tentative schedule based on the student filters.

    Args:
        department (str): Department of the course.
        course_number (str): Course number.
        new_schedule (list): New schedule to be checked for overlap.

    Returns:
        dict: Tentative schedule or error message.
    """
    try:
        # Generate SQL query based on department and course number
        sql_query = f"SELECT * FROM Spring2024 WHERE Department='{department}' AND CourseNumber='{course_number}'"

        # Execute SQL query
        cursor.execute(sql_query)
        result = cursor.fetchall()

        # Extract schedule information from the result
        schedule = [{'CRN': row[0], 'Start_Time': row[1], 'End_Time': row[2], 'Days': row[3]} for row in result]

        # Check if timings overlap
        if check_overlap(schedule, new_schedule):
            return {'message': 'Schedule timings overlap. Cannot generate schedule.'}, 400

        # Return generated tentative schedule
        return {'tentative_schedule': schedule}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {'message': 'Internal Server Error'}, 500

# Function to fetch all courses
def get_all_courses():
    """
    Fetches all the courses from the database.

    Returns:
        dict: List of all courses or error message.
    """
    try:
        # Execute SQL query to fetch all courses
        cursor.execute("SELECT * FROM Spring2024")
        result = cursor.fetchall()

        # Return list of all courses
        courses = [{'CRN': row[0], 'Department': row[1], 'CourseNumber': row[2], 'Name': row[3]} for row in result]
        return {'courses': courses}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {'message': 'Internal Server Error'}, 500

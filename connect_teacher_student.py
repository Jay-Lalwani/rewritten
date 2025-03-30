import os
import sys
from flask import Flask
from sqlalchemy import text
from dotenv import load_dotenv
from database.models import db, Student, Teacher, Assignment, student_assignment_progress

# Load environment variables from .env file
load_dotenv()

# Create a minimal Flask app
app = Flask(__name__)

# Use the DATABASE_URL from .env file
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not found in environment variables")
    print("Please make sure your .env file contains the DATABASE_URL variable")
    sys.exit(1)

print(f"Using database: {database_url}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def connect_all_students_to_all_assignments():
    with app.app_context():
        try:
            # First check if tables exist
            print("Checking database tables...")
            try:
                student_count = Student.query.count()
                assignment_count = Assignment.query.count()
                print(f"Database connection successful. Found {student_count} students and {assignment_count} assignments")
            except Exception as e:
                print(f"Error accessing tables: {str(e)}")
                print("The database may not be initialized or tables may not exist.")
                return
            
            # Get all students, teachers, and assignments
            students = Student.query.all()
            assignments = Assignment.query.all()
            
            print(f"Found {len(students)} students and {len(assignments)} assignments")
            
            # For each student, associate with each assignment
            for student in students:
                print(f"Processing student: {student.name}")
                for assignment in assignments:
                    # Check if the student is already associated with this assignment
                    existing = db.session.query(student_assignment_progress).filter_by(
                        student_id=student.id, 
                        assignment_id=assignment.id
                    ).first()
                    
                    if not existing:
                        print(f"  Connecting to assignment: {assignment.title}")
                        # Create the association
                        stmt = student_assignment_progress.insert().values(
                            student_id=student.id,
                            assignment_id=assignment.id,
                            completed=False,
                            last_scene_id=0
                        )
                        db.session.execute(stmt)
            
            # Commit all changes
            db.session.commit()
            print("All students connected to all assignments successfully!")
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    connect_all_students_to_all_assignments()
    print("Script completed!") 
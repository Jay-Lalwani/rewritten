#!/usr/bin/env python3
"""
Populate Grade Data Script

This script adds grade data and quiz responses for existing students and assignments.
It does not create new users, only adds data to existing relationships.
"""

import os
import sys
import random
import datetime
import uuid
from sqlalchemy import text

# Add the parent directory to the path so we can import from the project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure we're using the correct database path before importing app
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(base_dir, "rewritten", "database", "rewritten.db")
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
print(f"Using database at: {db_path}")

# Make sure database directory exists
db_dir = os.path.join(base_dir, "rewritten", "database")
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)
    print(f"Created database directory: {db_dir}")

from app import app
from database.models import db, Student, Teacher, Assignment, QuestionResponse, student_assignment_progress, Session as GameSession

# Override the database URI in the app config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
print(f"Database URI set to: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Sample quiz questions by scenario
QUIZ_QUESTIONS = {
    "Cuban Missile Crisis": [
        {"question": "Who was the US President during the Cuban Missile Crisis?", "correct_answer": "John F. Kennedy"},
        {"question": "In what year did the Cuban Missile Crisis occur?", "correct_answer": "1962"},
        {"question": "How many days did the Cuban Missile Crisis last?", "correct_answer": "13"},
        {"question": "What Soviet leader ordered missiles to be placed in Cuba?", "correct_answer": "Nikita Khrushchev"},
        {"question": "What was the name of the US naval blockade of Cuba?", "correct_answer": "Quarantine"}
    ],
    "Apollo 11": [
        {"question": "Who was the first person to walk on the moon?", "correct_answer": "Neil Armstrong"},
        {"question": "What was the name of the lunar module that landed on the moon?", "correct_answer": "Eagle"},
        {"question": "In what year did the Apollo 11 mission take place?", "correct_answer": "1969"},
        {"question": "What were the first words spoken from the moon?", "correct_answer": "Houston, Tranquility Base here. The Eagle has landed."},
        {"question": "Who was the command module pilot who orbited the moon?", "correct_answer": "Michael Collins"}
    ],
    "World War II": [
        {"question": "When did World War II begin?", "correct_answer": "1939"},
        {"question": "Who was the leader of Nazi Germany during World War II?", "correct_answer": "Adolf Hitler"},
        {"question": "What was the codename for the Allied invasion of Normandy?", "correct_answer": "Operation Overlord"},
        {"question": "What event directly led the United States to enter World War II?", "correct_answer": "The attack on Pearl Harbor"},
        {"question": "When did World War II end in Europe?", "correct_answer": "May 8, 1945"}
    ]
}

# Generic questions for any scenario
GENERIC_QUESTIONS = [
    {"question": "What were the main causes of this historical event?", "correct_answer": "Multiple complex factors"},
    {"question": "Who were the key leaders involved?", "correct_answer": "Various political and military figures"},
    {"question": "What was the global significance of this event?", "correct_answer": "It changed international relations"},
    {"question": "How did this event affect ordinary citizens?", "correct_answer": "It had profound social impacts"},
    {"question": "What long-term consequences resulted from this event?", "correct_answer": "It shaped future policies and events"}
]

def get_questions_for_scenario(scenario):
    """Get quiz questions for a specific scenario, falling back to generic ones if needed"""
    return QUIZ_QUESTIONS.get(scenario, GENERIC_QUESTIONS)

def generate_student_answer(correct_answer, is_correct):
    """Generate a student answer that is either correct or a plausible wrong answer"""
    if is_correct:
        return correct_answer
    
    # Generate a wrong answer
    wrong_answers = {
        "John F. Kennedy": ["Lyndon B. Johnson", "Richard Nixon", "Dwight Eisenhower"],
        "1962": ["1961", "1963", "1960"],
        "13": ["7", "21", "30"],
        "Nikita Khrushchev": ["Leonid Brezhnev", "Joseph Stalin", "Fidel Castro"],
        "Quarantine": ["Blockade", "Containment", "Embargo"],
        "Neil Armstrong": ["Buzz Aldrin", "Michael Collins", "John Glenn"],
        "Eagle": ["Columbia", "Apollo", "Challenger"],
        "1969": ["1968", "1970", "1971"],
        "Houston, Tranquility Base here. The Eagle has landed.": ["One small step for man, one giant leap for mankind", "We came in peace for all mankind", "The Eagle has landed"],
        "Michael Collins": ["Buzz Aldrin", "Alan Shepard", "Jim Lovell"],
        "1939": ["1938", "1940", "1941"],
        "Adolf Hitler": ["Benito Mussolini", "Joseph Stalin", "Winston Churchill"],
        "Operation Overlord": ["Operation Barbarossa", "D-Day", "Operation Market Garden"],
        "The attack on Pearl Harbor": ["The sinking of the Lusitania", "Germany's invasion of Poland", "The Battle of Britain"],
        "May 8, 1945": ["September 2, 1945", "April 30, 1945", "June 6, 1944"]
    }
    
    # Default wrong answers for generic questions or if no specific wrong answers are defined
    default_wrong_answers = [
        "This is incorrect",
        "Wrong historical interpretation",
        "Inaccurate historical analysis",
        "Misunderstanding of the events",
        "Historical misconception"
    ]
    
    potential_wrong_answers = wrong_answers.get(correct_answer, default_wrong_answers)
    return random.choice(potential_wrong_answers)

def populate_grades():
    """Add grade data for existing students and assignments"""
    with app.app_context():
        # Get all existing students and assignments
        students = Student.query.all()
        assignments = Assignment.query.all()
        
        if not students:
            print("No students found. Please create students first.")
            return
            
        if not assignments:
            print("No assignments found. Please create assignments first.")
            return
        
        print(f"Found {len(students)} students and {len(assignments)} assignments")
        
        # For each student, randomly enroll in some assignments and add grade data
        for student in students:
            print(f"Processing student: {student.name}")
            
            # Randomly select a subset of assignments for this student (between 1 and all)
            student_assignments = random.sample(
                assignments, 
                random.randint(1, len(assignments))
            )
            
            for assignment in student_assignments:
                print(f"  Adding data for assignment: {assignment.title}")
                
                # Create a session ID for this student-assignment pair
                session_id = str(uuid.uuid4())
                
                # Determine if the assignment is completed (80% chance)
                is_completed = random.random() < 0.8
                
                # Generate a score if completed (0-100)
                score = random.randint(60, 100) if is_completed else None
                
                # Calculate last scene (1-10, higher if completed)
                last_scene_id = random.randint(7, 10) if is_completed else random.randint(1, 7)
                
                # Check if this student-assignment pairing already exists
                existing = db.session.execute(
                    text("SELECT * FROM student_assignment_progress WHERE student_id = :student_id AND assignment_id = :assignment_id"),
                    {"student_id": student.id, "assignment_id": assignment.id}
                ).fetchone()
                
                if existing:
                    # Update existing record
                    db.session.execute(
                        text("""
                            UPDATE student_assignment_progress 
                            SET completed = :completed, score = :score, last_scene_id = :last_scene_id, 
                                current_session_id = :session_id, updated_at = :updated_at
                            WHERE student_id = :student_id AND assignment_id = :assignment_id
                        """),
                        {
                            "completed": is_completed,
                            "score": score,
                            "last_scene_id": last_scene_id,
                            "session_id": session_id,
                            "updated_at": datetime.datetime.utcnow(),
                            "student_id": student.id,
                            "assignment_id": assignment.id
                        }
                    )
                else:
                    # Add new record
                    db.session.execute(
                        text("""
                            INSERT INTO student_assignment_progress 
                            (student_id, assignment_id, current_session_id, completed, score, last_scene_id, created_at, updated_at)
                            VALUES (:student_id, :assignment_id, :session_id, :completed, :score, :last_scene_id, :created_at, :updated_at)
                        """),
                        {
                            "student_id": student.id,
                            "assignment_id": assignment.id,
                            "session_id": session_id,
                            "completed": is_completed,
                            "score": score,
                            "last_scene_id": last_scene_id,
                            "created_at": datetime.datetime.utcnow(),
                            "updated_at": datetime.datetime.utcnow()
                        }
                    )
                
                # Add quiz responses (more if completed)
                num_questions = random.randint(3, 5) if is_completed else random.randint(1, 3)  # Always at least 1
                
                # Delete existing responses for this student-assignment pair first
                QuestionResponse.query.filter_by(
                    student_id=student.id, 
                    assignment_id=assignment.id
                ).delete()
                
                # Get questions for this scenario
                scenario_questions = get_questions_for_scenario(assignment.scenario)
                
                print(f"    Adding {num_questions} quiz responses")
                
                # Add new quiz responses
                for i in range(num_questions):
                    # Select a question
                    question_data = scenario_questions[i % len(scenario_questions)]
                    
                    # Determine if the answer is correct (70% chance if completed, 40% if not)
                    is_correct = random.random() < (0.7 if is_completed else 0.4)
                    
                    # Generate the student's answer
                    student_answer = generate_student_answer(
                        question_data["correct_answer"], 
                        is_correct
                    )
                    
                    # Calculate a score for this response (5-10 if correct, 0-5 if incorrect)
                    response_score = random.randint(5, 10) if is_correct else random.randint(0, 5)
                    
                    # Create the response record
                    try:
                        # Verify the session exists or create it if needed
                        existing_session = GameSession.query.get(session_id)
                        if not existing_session:
                            # Create a minimal game session if one doesn't exist
                            game_session = GameSession(
                                id=session_id,
                                scenario=assignment.scenario,
                                current_scene_id=random.randint(1, 10),
                                student_id=student.id,
                                assignment_id=assignment.id
                            )
                            db.session.add(game_session)
                            db.session.flush()  # Ensure the session is in the database
                        
                        # Now create the quiz response with verified foreign keys
                        quiz_response = QuestionResponse(
                            student_id=student.id,
                            assignment_id=assignment.id,
                            session_id=session_id,
                            scene_id=random.randint(1, last_scene_id),
                            question_text=question_data["question"],
                            student_answer=student_answer,
                            is_correct=is_correct,
                            score=response_score,
                            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 14))
                        )
                        db.session.add(quiz_response)
                        print(f"      Added quiz response: '{question_data['question']}' - {'Correct' if is_correct else 'Incorrect'}")
                    except Exception as e:
                        print(f"Error creating quiz response: {e}")
                
        # Commit all changes
        db.session.commit()
        print("Successfully populated grade data for all students!")


if __name__ == "__main__":
    populate_grades() 
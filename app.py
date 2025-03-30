import json
import os
import uuid
from functools import wraps

# 1. Import Authlib
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS
from sqlalchemy import text

from api.media_generator import concatenate_videos, generate_scene_videos
from api.producer_agent import generate_scene_prompts
from api.writer_agent import generate_narrative
from database.models import (
    db,
    Session as GameSession,
    NarrativeData,
    ScenePrompt,
    MediaUrl,
    SceneCache,
    Teacher,
    Student,
    Assignment,
    student_assignment_progress,
    QuestionResponse,
)
import database
from api.tts_agent import generate_speech
from api.quiz_agent import generate_quiz_question, get_fallback_question

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.secret_key = os.environ.get("APP_SECRET_KEY", "fallback-secret-key")

# Initialize database with SQLAlchemy
database.init_app(app)

# Add Flask-Migrate support
from flask_migrate import Migrate

migrate = Migrate(app, db)

# ---------------------
# 2. Setup OAuth Client
# ---------------------
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    # This retrieves the Auth0 OIDC configuration dynamically
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# --------------------
# 3. Auth Decorator
# --------------------
def requires_auth(f):
    """Use this decorator on any route you want to protect."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            # Not logged in, redirect to login
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# --------------------
# 4. Auth Routes
# --------------------
@app.route("/login")
def login():
    """
    Redirects the user to Auth0's hosted login page.
    """
    # Store the role in session for later use
    role = request.args.get("role", "student")
    session["pending_role"] = role

    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback")
def callback():
    """
    Handles the callback from Auth0. It will exchange the 'code' for valid tokens,
    store them in session, and then redirect to your protected route.
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token

    # Get user details from Auth0
    userinfo = token.get("userinfo", {})
    auth0_id = userinfo.get("sub")
    email = userinfo.get("email", "")
    name = userinfo.get("name", "")

    # Get the pending role from session
    role = session.pop("pending_role", None)

    # Check if user exists in our database
    teacher = Teacher.query.filter_by(auth0_id=auth0_id).first()
    student = Student.query.filter_by(auth0_id=auth0_id).first()

    if teacher:
        # Existing teacher
        session["user_type"] = "teacher"
        session["user_id"] = teacher.id
        return redirect(url_for("dashboard"))  # Redirect to unified dashboard

    elif student:
        # Existing student
        session["user_type"] = "student"
        session["user_id"] = student.id
        return redirect(url_for("dashboard"))  # Redirect to unified dashboard

    else:
        # New user - create based on role selection
        if role == "teacher":
            new_teacher = Teacher(
                name=name,
                email=email,
                auth0_id=auth0_id,
                password="",  # Empty since Auth0 handles authentication
            )
            db.session.add(new_teacher)
            db.session.commit()

            session["user_type"] = "teacher"
            session["user_id"] = new_teacher.id
            return redirect(url_for("dashboard"))  # Redirect to unified dashboard

        elif role == "student":
            new_student = Student(
                name=name,
                email=email,
                auth0_id=auth0_id,
                grade_level=0,  # Default value
            )
            db.session.add(new_student)
            db.session.commit()

            session["user_type"] = "student"
            session["user_id"] = new_student.id
            return redirect(url_for("dashboard"))  # Redirect to unified dashboard

    # Default fallback
    return redirect(url_for("index"))


@app.route("/")
def index():
    """Render the role selection page."""
    if "user" in session and "user_type" in session:
        # If already logged in, redirect to the unified dashboard
        return redirect(url_for("dashboard"))

    return render_template("role_select.html")


@app.route("/view-scenarios")
def view_scenarios():
    """View all scenarios without requiring login."""
    return render_template("index.html")


@app.route("/dashboard")
@requires_auth
def dashboard():
    """Unified dashboard for both teachers and students."""
    user_type = session.get("user_type")
    user_id = session.get("user_id")
    
    if user_type == "teacher":
        teacher = Teacher.query.get(user_id)
        return render_template("dashboard.html", user=teacher, user_type="teacher")
    elif user_type == "student":
        student = Student.query.get(user_id)
        return render_template("dashboard.html", user=student, user_type="student")
    else:
        # If user type is not recognized, redirect to index
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """
    Logs the user out (clears local session) and also logs them out of Auth0.
    """
    session.clear()
    # For a full logout, redirect to Auth0's logout endpoint
    auth0_domain = os.environ.get("AUTH0_DOMAIN")
    client_id = os.environ.get("AUTH0_CLIENT_ID")
    return redirect(
        f"https://{auth0_domain}/v2/logout?"
        f"returnTo={url_for('index', _external=True)}&client_id={client_id}"
    )


@app.route("/api/start", methods=["POST"])
def start_game():
    """
    Start a new game session by creating a 'partial_narrative' that includes:
      - the scenario
      - no prior narrative yet
      - empty decision_history
    Look up (scenario, partial_narrative) in cache. If found, reuse. Otherwise, generate.
    """
    session_id = str(uuid.uuid4())
    session["session_id"] = session_id

    scenario = request.json.get("scenario", "Cuban Missile Crisis")
    print(f"\n=== Starting new game: {scenario} ===")

    # 1) Create an empty partial_narrative for the initial scene
    partial_narrative_obj = {
        "scenario": scenario,
        "last_narrative": None,  # no prior scene
        "decision_history": [],
    }
    partial_narrative_str = json.dumps(partial_narrative_obj)

    # 2) Create a record for this session using SQLAlchemy
    game_session = GameSession(
        id=session_id,
        scenario=scenario,
        current_scene_id=0,
        partial_narrative=partial_narrative_str,
    )
    db.session.add(game_session)
    db.session.commit()

    # 3) Check the cache using SQLAlchemy query
    cache_entry = SceneCache.query.filter_by(
        scenario=scenario, partial_narrative=partial_narrative_str
    ).first()

    if cache_entry:
        # Reuse what we previously generated
        print("Found cached initial scene for scenario:", scenario)
        new_narrative = cache_entry.next_narrative_obj
        scene_prompts = cache_entry.next_scene_prompts_obj
        media_data = cache_entry.next_media_urls_obj
        cached = True
    else:
        # Generate a new initial scene
        new_narrative = generate_narrative(None, None, scenario)
        scene_prompts = generate_scene_prompts(new_narrative["narrative"])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)

        # Generate audio for narrative
        audio_url = generate_speech(new_narrative["narrative"])

        media_data = {
            "individual_videos": video_urls,
            "combined_video": combined_video_url,
            "audio": audio_url,
        }

        # Store in scene_cache for next time
        new_cache = SceneCache(
            scenario=scenario,
            partial_narrative=partial_narrative_str,
            next_narrative=json.dumps(new_narrative),
            next_scene_prompts=json.dumps(scene_prompts),
            next_media_urls=json.dumps(media_data),
        )
        db.session.add(new_cache)
        db.session.commit()
        cached = False

    # 4) Update partial_narrative with the newly generated scene
    partial_narrative_obj["last_narrative"] = new_narrative
    updated_partial_narrative_str = json.dumps(partial_narrative_obj)

    # 5) Update the session record with the new data using SQLAlchemy
    game_session.current_scene_id = new_narrative["scene_id"]
    game_session.partial_narrative = updated_partial_narrative_str

    # Create related records
    narrative_data = NarrativeData(
        session_id=session_id, data=json.dumps(new_narrative)
    )

    scene_prompt = ScenePrompt(session_id=session_id, data=json.dumps(scene_prompts))

    media_url = MediaUrl(session_id=session_id, data=json.dumps(media_data))

    db.session.add_all([narrative_data, scene_prompt, media_url])
    db.session.commit()

    return jsonify(
        {
            "session_id": session_id,
            "narrative": new_narrative,
            "media": media_data["combined_video"],
            "audio": media_data.get("audio"),
            "cached": cached,
        }
    )


@app.route("/api/decision", methods=["POST"])
def make_decision():
    """
    Process the player's decision. We'll read 'partial_narrative' from the session row,
    update the decision_history, then check the cache using that as the key.
    If it doesn't exist, we generate the next scene. If it does, we reuse it.
    """
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"error": "No active session"}), 400

    decision_id = request.json.get("decision")
    current_scene_id = request.json.get("scene_id")

    # Query for session data using SQLAlchemy
    game_session = GameSession.query.get(session_id)
    if not game_session:
        return jsonify({"error": "Session not found"}), 404

    scenario = game_session.scenario
    partial_narrative_str = game_session.partial_narrative
    if not partial_narrative_str:
        return jsonify({"error": "No partial_narrative found in session"}), 400

    partial_narrative_obj = json.loads(partial_narrative_str)

    last_narrative = partial_narrative_obj["last_narrative"]
    decision_history = partial_narrative_obj["decision_history"]

    print(f"\n=== Player made decision {decision_id} at scene {current_scene_id} ===")
    selected_option = None
    if last_narrative and "options" in last_narrative:
        selected_option = next(
            (opt for opt in last_narrative["options"] if opt["id"] == decision_id), None
        )
    if selected_option:
        print(f"Selected: {selected_option['option']}")

    # Update decision history - use the same format as the original implementation
    decision_record = {
        "scene_id": last_narrative["scene_id"] if last_narrative else 0,
        "decision": decision_id,
        "decision_text": selected_option["option"] if selected_option else "",
    }
    decision_history.append(decision_record)
    partial_narrative_obj["decision_history"] = decision_history
    updated_partial_narrative_str = json.dumps(partial_narrative_obj)

    # Check the scene cache using SQLAlchemy
    cache_entry = SceneCache.query.filter_by(
        scenario=scenario, partial_narrative=updated_partial_narrative_str
    ).first()

    if cache_entry:
        # Found in cache, use the pre-generated content
        print("Found cached next scene")
        next_narrative = cache_entry.next_narrative_obj
        scene_prompts = cache_entry.next_scene_prompts_obj
        media_data = cache_entry.next_media_urls_obj
        cached = True
    else:
        # Generate a new scene
        print("Generating new scene")
        next_narrative = generate_narrative(last_narrative, decision_history, scenario)
        scene_prompts = generate_scene_prompts(next_narrative["narrative"])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)

        # Generate audio for narrative
        audio_url = generate_speech(new_narrative["narrative"])

        media_data = {
            "individual_videos": video_urls,
            "combined_video": combined_video_url,
            "audio": audio_url,
        }

        # Save to cache for future reuse
        new_cache = SceneCache(
            scenario=scenario,
            partial_narrative=updated_partial_narrative_str,
            next_narrative=json.dumps(next_narrative),
            next_scene_prompts=json.dumps(scene_prompts),
            next_media_urls=json.dumps(media_data),
        )
        db.session.add(new_cache)
        db.session.commit()
        cached = False

    # Prepare for the next scene by updating partial_narrative
    partial_narrative_obj["last_narrative"] = next_narrative
    game_session.partial_narrative = json.dumps(partial_narrative_obj)
    game_session.current_scene_id = next_narrative["scene_id"]

    # Update related data
    if game_session.narrative_data:
        game_session.narrative_data.data = json.dumps(next_narrative)
    else:
        narrative_data = NarrativeData(
            session_id=session_id, data=json.dumps(next_narrative)
        )
        db.session.add(narrative_data)

    if game_session.scene_prompts:
        game_session.scene_prompts.data = json.dumps(scene_prompts)
    else:
        scene_prompt = ScenePrompt(
            session_id=session_id, data=json.dumps(scene_prompts)
        )
        db.session.add(scene_prompt)

    if game_session.media_urls:
        game_session.media_urls.data = json.dumps(media_data)
    else:
        media_url = MediaUrl(session_id=session_id, data=json.dumps(media_data))
        db.session.add(media_url)

    db.session.commit()

    return jsonify(
        {
            "session_id": session_id,
            "narrative": next_narrative,
            "media": media_data["combined_video"],
            "audio": media_data.get("audio"),
            "cached": cached,
        }
    )


@app.route("/api/progress", methods=["GET"])
def get_progress():
    """Get the current progress of the game session."""
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"error": "No active session"}), 400

    # Query for session data using SQLAlchemy
    game_session = GameSession.query.get(session_id)
    if not game_session:
        return jsonify({"error": "Session not found"}), 404

    # Use our decision_history property
    decisions = game_session.decision_history

    return jsonify({"decisions": decisions})


@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    """Get all distinct scenarios from the database."""
    # Get distinct scenarios using SQLAlchemy
    scenarios = db.session.query(GameSession.scenario).distinct().all()
    scenario_list = [row[0] for row in scenarios]
    
    # Filter out the uppercase 'Apollo 11' scenario
    scenario_list = [scenario for scenario in scenario_list if scenario != "Apollo 11"]
    
    return jsonify({"scenarios": scenario_list})


@app.route("/api/scenarios", methods=["POST"])
def add_scenario():
    """Add a new scenario to the database."""
    scenario_name = request.json.get("name")
    if not scenario_name:
        return jsonify({"error": "No scenario name provided"}), 400

    # Check if scenario exists using SQLAlchemy
    existing = GameSession.query.filter_by(scenario=scenario_name).first()
    if existing:
        return jsonify({"success": False, "message": "Scenario already exists"}), 409

    # Create new session with this scenario
    new_id = str(uuid.uuid4())
    game_session = GameSession(id=new_id, scenario=scenario_name, current_scene_id=0)
    db.session.add(game_session)
    db.session.commit()

    return jsonify({"success": True, "scenario": scenario_name})


@app.route("/api/scenarios/<scenario_name>", methods=["DELETE"])
@requires_auth
def delete_scenario(scenario_name):
    """Delete a scenario from the database."""
    if not scenario_name:
        return jsonify({"error": "No scenario name provided"}), 400
        
    # Only teachers can delete scenarios
    if session.get("user_type") != "teacher":
        return jsonify({"error": "Only teachers can delete scenarios"}), 403

    # Delete scenario sessions using SQLAlchemy
    GameSession.query.filter_by(scenario=scenario_name).delete()
    db.session.commit()

    return jsonify(
        {"success": True, "message": f'Scenario "{scenario_name}" deleted successfully'}
    )


@app.route("/api/quiz", methods=["GET"])
def get_quiz():
    """Get a dynamic quiz question related to the current scenario/narrative."""
    session_id = session.get("session_id")

    try:
        if session_id:
            # Get the current session using SQLAlchemy
            game_session = GameSession.query.get(session_id)

            if game_session:
                scenario = game_session.scenario
                narrative = None

                # Get narrative data from the related table
                narrative_data_record = NarrativeData.query.filter_by(
                    session_id=session_id
                ).first()
                if narrative_data_record:
                    narrative_data = json.loads(narrative_data_record.data)
                    narrative = narrative_data.get("narrative")

                # Generate question based on context
                question = generate_quiz_question(
                    scenario=scenario, narrative=narrative
                )
                return jsonify({"question": question})

        # If no session or no data, generate a generic question
        question = generate_quiz_question()
        return jsonify({"question": question})

    except Exception as e:
        print(f"Error generating quiz question: {e}")
        # Fall back to static questions if generation fails
        return jsonify({"question": get_fallback_question()})


# --------------------------
# Assignment Management APIs
# --------------------------
import random
import string

def generate_access_code(length=6):
    """Generate a random access code for assignments"""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        # Check if code already exists
        existing = Assignment.query.filter_by(access_code=code).first()
        if not existing:
            return code


@app.route("/api/assignments", methods=["POST"])
@requires_auth
def create_assignment():
    """Create a new assignment with a scenario"""
    if session.get("user_type") != "teacher":
        return jsonify({"error": "Only teachers can create assignments"}), 403
    
    teacher_id = session.get("user_id")
    
    # Get scenario from the request
    scenario = request.json.get("scenario", "Apollo 11")
    title = request.json.get("title", f"Assignment: {scenario}")
    
    # Generate a unique access code
    access_code = generate_access_code()
    
    # Create the assignment
    assignment = Assignment(
        title=title,
        scenario=scenario,
        access_code=access_code,
        teacher_id=teacher_id
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    return jsonify({
        "success": True, 
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "scenario": assignment.scenario,
            "access_code": assignment.access_code
        }
    })


@app.route("/api/assignments", methods=["GET"])
@requires_auth
def get_teacher_assignments():
    """Get all assignments for the current teacher"""
    if session.get("user_type") != "teacher":
        return jsonify({"error": "Only teachers can view their assignments"}), 403
    
    teacher_id = session.get("user_id")
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    
    assignment_list = []
    for assignment in assignments:
        # Count enrolled students
        student_count = db.session.query(student_assignment_progress).filter_by(
            assignment_id=assignment.id).count()
            
        assignment_list.append({
            "id": assignment.id,
            "title": assignment.title,
            "scenario": assignment.scenario,
            "access_code": assignment.access_code,
            "created_at": assignment.created_at.isoformat(),
            "student_count": student_count,
            "is_active": assignment.is_active
        })
    
    return jsonify({"assignments": assignment_list})


@app.route("/api/assignments/<assignment_id>", methods=["GET"])
@requires_auth
def get_assignment_details(assignment_id):
    """Get details of a specific assignment including student progress"""
    if session.get("user_type") != "teacher":
        return jsonify({"error": "Only teachers can view assignment details"}), 403
    
    teacher_id = session.get("user_id")
    assignment = Assignment.query.filter_by(id=assignment_id, teacher_id=teacher_id).first()
    
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404
    
    # Get all students enrolled in this assignment
    student_progress = db.session.query(
        Student, student_assignment_progress
    ).join(
        student_assignment_progress, 
        Student.id == student_assignment_progress.c.student_id
    ).filter(
        student_assignment_progress.c.assignment_id == assignment_id
    ).all()
    
    students_data = []
    for student, progress in student_progress:
        students_data.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "completed": progress.completed,
            "score": progress.score,
            "last_scene_id": progress.last_scene_id,
            "last_updated": progress.updated_at.isoformat()
        })
    
    return jsonify({
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "scenario": assignment.scenario,
            "access_code": assignment.access_code,
            "created_at": assignment.created_at.isoformat(),
            "is_active": assignment.is_active,
            "students": students_data
        }
    })


@app.route("/api/join-assignment", methods=["POST"])
@requires_auth
def join_assignment():
    """Allow a student to join an assignment using an access code"""
    if session.get("user_type") != "student":
        return jsonify({"error": "Only students can join assignments"}), 403
    
    student_id = session.get("user_id")
    access_code = request.json.get("access_code")
    
    if not access_code:
        return jsonify({"error": "Access code is required"}), 400
    
    # Find the assignment by access code
    assignment = Assignment.query.filter_by(access_code=access_code, is_active=True).first()
    
    if not assignment:
        return jsonify({"error": "Invalid or expired access code"}), 404
    
    # Check if student is already enrolled
    existing = db.session.query(student_assignment_progress).filter_by(
        student_id=student_id, assignment_id=assignment.id).first()
    
    # Create a new session ID
    session_id = str(uuid.uuid4())
    
    if existing:
        # Student is already enrolled, but we'll create a new session for them
        # Update their current_session_id
        stmt = student_assignment_progress.update().where(
            (student_assignment_progress.c.student_id == student_id) & 
            (student_assignment_progress.c.assignment_id == assignment.id)
        ).values(current_session_id=session_id)
        db.session.execute(stmt)
    else:
        # Enroll the student
        stmt = student_assignment_progress.insert().values(
            student_id=student_id,
            assignment_id=assignment.id,
            current_session_id=session_id
        )
        db.session.execute(stmt)
    
    # Start a game session for this scenario with the student and assignment IDs
    game_session = GameSession(
        id=session_id,
        scenario=assignment.scenario,
        current_scene_id=0,
        student_id=student_id,
        assignment_id=assignment.id
    )
    db.session.add(game_session)
    db.session.commit()
    
    # Store the session ID
    session["session_id"] = session_id
    
    return jsonify({
        "success": True,
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "scenario": assignment.scenario,
            "teacher_name": assignment.teacher.name
        },
        "session_id": session_id
    })


@app.route("/api/student/assignments", methods=["GET"])
@requires_auth
def get_student_assignments():
    """Get all assignments for the current student"""
    if session.get("user_type") != "student":
        return jsonify({"error": "Only students can view their assignments"}), 403
    
    student_id = session.get("user_id")
    
    # Get assignment IDs for this student using parameterized query
    progress_records = db.session.execute(
        text("SELECT assignment_id, completed, score, last_scene_id FROM student_assignment_progress WHERE student_id = :student_id"),
        {"student_id": student_id}
    ).fetchall()
    
    # Create a dictionary of progress info keyed by assignment_id
    progress_by_assignment = {
        record[0]: {
            "completed": record[1],
            "score": record[2],
            "last_scene_id": record[3]
        }
        for record in progress_records
    }
    
    # Get the actual assignments
    assignment_ids = list(progress_by_assignment.keys())
    if not assignment_ids:
        return jsonify({"assignments": []})
    
    assignments = Assignment.query.filter(Assignment.id.in_(assignment_ids)).all()
    
    # Build the response
    assignment_list = []
    for assignment in assignments:
        progress = progress_by_assignment.get(assignment.id, {})
        assignment_list.append({
            "id": assignment.id,
            "title": assignment.title,
            "scenario": assignment.scenario,
            "teacher_name": assignment.teacher.name,
            "completed": progress.get("completed", False),
            "score": progress.get("score"),
            "last_scene_id": progress.get("last_scene_id", 0)
        })
    
    return jsonify({"assignments": assignment_list})


@app.route("/student/assignments")
@requires_auth
def student_assignments_page():
    """Show a student their assignments with play options"""
    if session.get("user_type") != "student":
        return redirect(url_for("dashboard"))
    
    student_id = session.get("user_id")
    student = Student.query.get(student_id)
    
    return render_template("student_assignments.html", user=student)


@app.route("/api/student/progress", methods=["GET"])
@requires_auth
def get_student_progress():
    """Get progress data for the current student including quiz results"""
    try:
        if session.get("user_type") != "student":
            return jsonify({"error": "Only students can view their progress"}), 403
        
        student_id = session.get("user_id")
        
        # Get all assignments for this student
        progress_records = db.session.execute(
            text("SELECT * FROM student_assignment_progress WHERE student_id = :student_id"),
            {"student_id": student_id}
        ).fetchall()
        
        # Get all quiz responses for this student
        quiz_responses = QuestionResponse.query.filter_by(student_id=student_id).all()
        
        # Organize quiz data by assignment
        quiz_data_by_assignment = {}
        for response in quiz_responses:
            if response.assignment_id not in quiz_data_by_assignment:
                quiz_data_by_assignment[response.assignment_id] = []
            
            quiz_data_by_assignment[response.assignment_id].append({
                "question": response.question_text,
                "answer": response.student_answer,
                "correct": response.is_correct,
                "score": response.score,
                "scene_id": response.scene_id,
                "date": response.created_at.isoformat()
            })
        
        # Process the assignments with progress data
        progress_data = []
        for record in progress_records:
            assignment_id = record.assignment_id
            assignment = Assignment.query.get(assignment_id)
            
            if assignment:
                progress_data.append({
                    "assignment_id": assignment_id,
                    "title": assignment.title,
                    "scenario": assignment.scenario,
                    "teacher_name": assignment.teacher.name,
                    "completed": record.completed,
                    "score": record.score,
                    "last_scene_id": record.last_scene_id,
                    "quiz_responses": quiz_data_by_assignment.get(assignment_id, [])
                })
        
        # Aggregate statistics
        total_assignments = len(progress_data)
        completed_assignments = sum(1 for item in progress_data if item["completed"])
        
        # Calculate average score safely
        scores = [item["score"] for item in progress_data if item["score"] is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Calculate quiz statistics safely
        total_questions = sum(len(item["quiz_responses"]) for item in progress_data)
        correct_answers = sum(sum(1 for q in item["quiz_responses"] if q["correct"]) for item in progress_data)
        quiz_accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        return jsonify({
            "progress_items": progress_data,
            "statistics": {
                "total_assignments": total_assignments,
                "completed_assignments": completed_assignments,
                "completion_rate": (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0,
                "average_score": avg_score,
                "total_questions_answered": total_questions,
                "correct_answers": correct_answers,
                "quiz_accuracy": quiz_accuracy
            }
        })
    except Exception as e:
        app.logger.error(f"Error in get_student_progress: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching progress data",
            "message": str(e),
            "progress_items": [],
            "statistics": {
                "total_assignments": 0,
                "completed_assignments": 0,
                "completion_rate": 0,
                "average_score": 0,
                "total_questions_answered": 0,
                "correct_answers": 0,
                "quiz_accuracy": 0
            }
        })


@app.route("/api/teacher/student-progress", methods=["GET"])
@requires_auth
def get_teacher_student_progress():
    """Get progress data for all students in a teacher's assignments"""
    try:
        if session.get("user_type") != "teacher":
            return jsonify({"error": "Only teachers can view student progress"}), 403
        
        teacher_id = session.get("user_id")
        app.logger.info(f"Fetching progress data for teacher ID: {teacher_id}")
        
        # Get all assignments for this teacher
        assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
        assignment_ids = [a.id for a in assignments]
        
        app.logger.info(f"Found {len(assignments)} assignments: {assignment_ids}")
        
        if not assignment_ids:
            # No assignments found, return empty data
            return jsonify({"assignments": [], "students": [], "quiz_data": {"total_questions": 0, "correct_answers": 0, "by_assignment": {}, "by_student": {}}})
        
        # Query all student progress records for the teacher's assignments with a proper SQL approach
        student_assignments_data = []
        
        # Instead of using placeholders with a direct list, use SQLAlchemy's ORM
        student_assignments_data = db.session.query(
            Student.id, 
            Student.name, 
            Student.email,
            student_assignment_progress.c.assignment_id,
            student_assignment_progress.c.completed,
            student_assignment_progress.c.score,
            student_assignment_progress.c.last_scene_id
        ).join(
            student_assignment_progress,
            Student.id == student_assignment_progress.c.student_id
        ).filter(
            student_assignment_progress.c.assignment_id.in_(assignment_ids)
        ).all()
        
        app.logger.info(f"Found {len(student_assignments_data)} student-assignment records")
        
        # Get all quiz responses for these assignments
        quiz_responses = QuestionResponse.query.filter(
            QuestionResponse.assignment_id.in_(assignment_ids)
        ).all()
        
        app.logger.info(f"Found {len(quiz_responses)} quiz responses")
        
        # Count student assignments and completed assignments by assignment ID
        assignment_counts = {}
        
        # Process students
        student_data = {}
        for row in student_assignments_data:
            student_id = row[0]
            student_name = row[1]
            student_email = row[2]
            assignment_id = row[3]
            completed = row[4]
            score = row[5]
            
            # Process for assignment counts
            if assignment_id not in assignment_counts:
                assignment_counts[assignment_id] = {
                    "total": 0,
                    "completed": 0
                }
            
            assignment_counts[assignment_id]["total"] += 1
            if completed:
                assignment_counts[assignment_id]["completed"] += 1
            
            # Process for student data
            if student_id not in student_data:
                student_data[student_id] = {
                    "id": student_id,
                    "name": student_name,
                    "email": student_email,
                    "assignments_completed": 0,
                    "total_assignments": 0,
                    "average_score": 0,
                    "scores": []
                }
            
            student_data[student_id]["total_assignments"] += 1
            if completed:
                student_data[student_id]["assignments_completed"] += 1
            
            if score is not None:
                student_data[student_id]["scores"].append(score)
        
        # Calculate average scores
        for student_id in student_data:
            scores = student_data[student_id]["scores"]
            if scores:
                student_data[student_id]["average_score"] = sum(scores) / len(scores)
            else:
                student_data[student_id]["average_score"] = 0
        
        # Process quiz data
        quiz_data = {
            "total_questions": len(quiz_responses),
            "correct_answers": sum(1 for r in quiz_responses if r.is_correct),
            "by_assignment": {},
            "by_student": {}
        }
        
        # Organize quiz data by assignment
        for response in quiz_responses:
            if response.assignment_id not in quiz_data["by_assignment"]:
                quiz_data["by_assignment"][response.assignment_id] = {
                    "total": 0,
                    "correct": 0
                }
            
            quiz_data["by_assignment"][response.assignment_id]["total"] += 1
            if response.is_correct:
                quiz_data["by_assignment"][response.assignment_id]["correct"] += 1
        
        # Organize quiz data by student
        for response in quiz_responses:
            if response.student_id not in quiz_data["by_student"]:
                quiz_data["by_student"][response.student_id] = {
                    "total": 0,
                    "correct": 0
                }
            
            quiz_data["by_student"][response.student_id]["total"] += 1
            if response.is_correct:
                quiz_data["by_student"][response.student_id]["correct"] += 1
        
        # Process assignments
        assignment_data = []
        for assignment in assignments:
            counts = assignment_counts.get(assignment.id, {"total": 0, "completed": 0})
            student_count = counts["total"]
            completion_count = counts["completed"]
            completion_rate = (completion_count / max(1, student_count)) * 100
            
            assignment_data.append({
                "id": assignment.id,
                "title": assignment.title,
                "scenario": assignment.scenario,
                "student_count": student_count,
                "completion_rate": completion_rate
            })
        
        return jsonify({
            "assignments": assignment_data,
            "students": list(student_data.values()),
            "quiz_data": quiz_data
        })
    
    except Exception as e:
        app.logger.error(f"Error in get_teacher_student_progress: {str(e)}")
        return jsonify({
            "error": "An error occurred while fetching progress data",
            "message": str(e),
            "assignments": [],
            "students": [],
            "quiz_data": {"total_questions": 0, "correct_answers": 0, "by_assignment": {}, "by_student": {}}
        })


if __name__ == "__main__":
    app.run(debug=True, port=5001)

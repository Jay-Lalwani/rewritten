import json
import os
import uuid
from functools import wraps

# 1. Import Authlib
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_cors import CORS

from api.media_generator import concatenate_videos, generate_scene_videos
from api.producer_agent import generate_scene_prompts
from api.writer_agent import generate_narrative
from database.models import db, Session as GameSession, NarrativeData, ScenePrompt, MediaUrl, SceneCache, Teacher, Student
import database
from api.tts_agent import generate_speech

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
        return redirect(url_for("teacher_dashboard"))
        
    elif student:
        # Existing student
        session["user_type"] = "student"
        session["user_id"] = student.id
        return redirect(url_for("student_dashboard"))
        
    else:
        # New user - create based on role selection
        if role == "teacher":
            new_teacher = Teacher(
                name=name,
                email=email,
                auth0_id=auth0_id,
                password=""  # Empty since Auth0 handles authentication
            )
            db.session.add(new_teacher)
            db.session.commit()
            
            session["user_type"] = "teacher"
            session["user_id"] = new_teacher.id
            return redirect(url_for("teacher_dashboard"))
            
        elif role == "student":
            new_student = Student(
                name=name,
                email=email,
                auth0_id=auth0_id,
                grade_level=0  # Default value
            )
            db.session.add(new_student)
            db.session.commit()
            
            session["user_type"] = "student"
            session["user_id"] = new_student.id
            return redirect(url_for("student_dashboard"))
    
    # Default fallback
    return redirect(url_for("index"))


@app.route("/")
def index():
    """Render the role selection page."""
    if "user" in session and "user_type" in session:
        # If already logged in, redirect to appropriate dashboard
        if session["user_type"] == "teacher":
            return redirect(url_for("teacher_dashboard"))
        elif session["user_type"] == "student":
            return redirect(url_for("student_dashboard"))
    
    return render_template("role_select.html")


@app.route("/view-scenarios")
def view_scenarios():
    """View all scenarios without requiring login."""
    return render_template("index.html")


@app.route("/teacher/dashboard")
@requires_auth
def teacher_dashboard():
    if session.get("user_type") != "teacher":
        return redirect(url_for("index"))
        
    teacher_id = session.get("user_id")
    teacher = Teacher.query.get(teacher_id)
    
    return render_template("teacher_dashboard.html", teacher=teacher)


@app.route("/student/dashboard")
@requires_auth
def student_dashboard():
    if session.get("user_type") != "student":
        return redirect(url_for("index"))
        
    student_id = session.get("user_id")
    student = Student.query.get(student_id)
    
    return render_template("student_dashboard.html", student=student)


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
        partial_narrative=partial_narrative_str
    )
    db.session.add(game_session)
    db.session.commit()

    # 3) Check the cache using SQLAlchemy query
    cache_entry = SceneCache.query.filter_by(
        scenario=scenario,
        partial_narrative=partial_narrative_str
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
            "audio": audio_url
        }

        # Store in scene_cache for next time
        new_cache = SceneCache(
            scenario=scenario,
            partial_narrative=partial_narrative_str,
            next_narrative=json.dumps(new_narrative),
            next_scene_prompts=json.dumps(scene_prompts),
            next_media_urls=json.dumps(media_data)
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
        session_id=session_id,
        data=json.dumps(new_narrative)
    )
    
    scene_prompt = ScenePrompt(
        session_id=session_id,
        data=json.dumps(scene_prompts)
    )
    
    media_url = MediaUrl(
        session_id=session_id,
        data=json.dumps(media_data)
    )
    
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
        "decision_text": selected_option["option"] if selected_option else ""
    }
    decision_history.append(decision_record)
    partial_narrative_obj["decision_history"] = decision_history
    updated_partial_narrative_str = json.dumps(partial_narrative_obj)

    # Check the scene cache using SQLAlchemy
    cache_entry = SceneCache.query.filter_by(
        scenario=scenario,
        partial_narrative=updated_partial_narrative_str
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
        next_narrative = generate_narrative(
            last_narrative, decision_history, scenario
        )
        scene_prompts = generate_scene_prompts(next_narrative["narrative"])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)
        
        # Generate audio for narrative
        audio_url = generate_speech(new_narrative["narrative"])

        media_data = {
            "individual_videos": video_urls,
            "combined_video": combined_video_url,
            "audio": audio_url
        }

        # Save to cache for future reuse
        new_cache = SceneCache(
            scenario=scenario,
            partial_narrative=updated_partial_narrative_str,
            next_narrative=json.dumps(next_narrative),
            next_scene_prompts=json.dumps(scene_prompts),
            next_media_urls=json.dumps(media_data)
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
            session_id=session_id,
            data=json.dumps(next_narrative)
        )
        db.session.add(narrative_data)
    
    if game_session.scene_prompts:
        game_session.scene_prompts.data = json.dumps(scene_prompts)
    else:
        scene_prompt = ScenePrompt(
            session_id=session_id, 
            data=json.dumps(scene_prompts)
        )
        db.session.add(scene_prompt)
    
    if game_session.media_urls:
        game_session.media_urls.data = json.dumps(media_data)
    else:
        media_url = MediaUrl(
            session_id=session_id,
            data=json.dumps(media_data)
        )
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
    game_session = GameSession(
        id=new_id,
        scenario=scenario_name,
        current_scene_id=0
    )
    db.session.add(game_session)
    db.session.commit()

    return jsonify({"success": True, "scenario": scenario_name})


@app.route("/api/scenarios/<scenario_name>", methods=["DELETE"])
def delete_scenario(scenario_name):
    """Delete a scenario from the database."""
    if not scenario_name:
        return jsonify({"error": "No scenario name provided"}), 400

    # Delete scenario sessions using SQLAlchemy
    GameSession.query.filter_by(scenario=scenario_name).delete()
    db.session.commit()

    return jsonify(
        {"success": True, "message": f'Scenario "{scenario_name}" deleted successfully'}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)

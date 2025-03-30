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
from database.db import get_db, init_db

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)
app.secret_key = os.environ.get("APP_SECRET_KEY", "fallback-secret-key")

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
    return redirect(url_for("index"))  # or any route you want after login


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


# Initialize database
with app.app_context():
    init_db()


@app.route("/")
# @requires_auth  # Auth0 authentication required
def index():
    """Render the main game page."""
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_game():
    """
    Start a new game session by creating a 'partial_narrative' that includes:
      - the scenario
      - no prior narrative yet
      - empty decision_history
    Look up (scenario, partial_narrative) in cache. If found, reuse. Otherwise, generate.
    """
    db = get_db()
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

    # 2) Create a record for this session (placeholder)
    db.execute(
        "INSERT INTO sessions (id, scenario, current_scene_id, partial_narrative) VALUES (?, ?, 0, ?)",
        (session_id, scenario, partial_narrative_str),
    )
    db.commit()

    # 3) Check the cache
    cache_row = db.execute(
        "SELECT next_narrative, next_scene_prompts, next_media_urls FROM scene_cache "
        "WHERE scenario = ? AND partial_narrative = ?",
        (scenario, partial_narrative_str),
    ).fetchone()

    if cache_row:
        # Reuse what we previously generated
        print("Found cached initial scene for scenario:", scenario)
        new_narrative = json.loads(cache_row["next_narrative"])
        scene_prompts = json.loads(cache_row["next_scene_prompts"])
        media_data = json.loads(cache_row["next_media_urls"])
        cached = True
    else:
        # Generate a new initial scene
        new_narrative = generate_narrative(None, None, scenario)
        scene_prompts = generate_scene_prompts(new_narrative["narrative"])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)

        media_data = {
            "individual_videos": video_urls,
            "combined_video": combined_video_url,
        }

        # Store in scene_cache for next time
        db.execute(
            "INSERT INTO scene_cache (scenario, partial_narrative, next_narrative, next_scene_prompts, next_media_urls) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                scenario,
                partial_narrative_str,
                json.dumps(new_narrative),
                json.dumps(scene_prompts),
                json.dumps(media_data),
            ),
        )
        db.commit()
        cached = False

    # 4) Update partial_narrative with the newly generated scene
    partial_narrative_obj["last_narrative"] = new_narrative
    updated_partial_narrative_str = json.dumps(partial_narrative_obj)

    # 5) Update the session record with the new data
    db.execute(
        "UPDATE sessions "
        "SET current_scene_id = ?, narrative_data = ?, scene_prompts = ?, media_urls = ?, partial_narrative = ? "
        "WHERE id = ?",
        (
            new_narrative["scene_id"],
            json.dumps(new_narrative),
            json.dumps(scene_prompts),
            json.dumps(media_data),
            updated_partial_narrative_str,
            session_id,
        ),
    )
    db.commit()

    return jsonify(
        {
            "session_id": session_id,
            "narrative": new_narrative,
            "media": media_data["combined_video"],
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
    db = get_db()
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"error": "No active session"}), 400

    decision_id = request.json.get("decision")
    current_scene_id = request.json.get("scene_id")

    session_data = db.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()

    if not session_data:
        return jsonify({"error": "Session not found"}), 404

    scenario = session_data["scenario"]
    partial_narrative_str = session_data["partial_narrative"]
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

    # 1) Add the new decision to the decision_history
    decision_history.append(
        {
            "scene_id": last_narrative["scene_id"] if last_narrative else 0,
            "decision": decision_id,
            "decision_text": selected_option["option"] if selected_option else "",
        }
    )

    # 2) The new partial_narrative includes the same scenario & last_narrative,
    #    but we haven't advanced to the new scene yet. So we look up the next scene in cache
    #    keyed by the entire partial_narrative including this updated decision_history.
    updated_partial_narrative_obj = {
        "scenario": scenario,
        "last_narrative": last_narrative,  # still the old scene
        "decision_history": decision_history,
    }
    updated_partial_narrative_str = json.dumps(updated_partial_narrative_obj)

    cache_row = db.execute(
        "SELECT next_narrative, next_scene_prompts, next_media_urls FROM scene_cache "
        "WHERE scenario = ? AND partial_narrative = ?",
        (scenario, updated_partial_narrative_str),
    ).fetchone()

    if cache_row:
        print("Found cached next scene for the existing partial_narrative + decision.")
        new_narrative = json.loads(cache_row["next_narrative"])
        scene_prompts = json.loads(cache_row["next_scene_prompts"])
        media_data = json.loads(cache_row["next_media_urls"])
        cached = True
    else:
        # Generate new scene
        new_narrative = generate_narrative(last_narrative, decision_id, None)
        scene_prompts = generate_scene_prompts(new_narrative["narrative"])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)

        media_data = {
            "individual_videos": video_urls,
            "combined_video": combined_video_url,
        }

        # Store in the cache
        db.execute(
            "INSERT INTO scene_cache (scenario, partial_narrative, next_narrative, next_scene_prompts, next_media_urls) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                scenario,
                updated_partial_narrative_str,
                json.dumps(new_narrative),
                json.dumps(scene_prompts),
                json.dumps(media_data),
            ),
        )
        db.commit()
        cached = False

    # 3) Now update partial_narrative so that last_narrative is set to the newly generated scene
    updated_partial_narrative_obj["last_narrative"] = new_narrative
    updated_partial_narrative_str = json.dumps(updated_partial_narrative_obj)

    # 4) Update the session's record
    #    Also reflect the new scene in narrative_data, scene_prompts, media_urls
    db.execute(
        "UPDATE sessions "
        "SET current_scene_id = ?, narrative_data = ?, scene_prompts = ?, media_urls = ?, "
        "    decision_history = ?, partial_narrative = ? "
        "WHERE id = ?",
        (
            new_narrative["scene_id"],
            json.dumps(new_narrative),
            json.dumps(scene_prompts),
            json.dumps(media_data),
            json.dumps(decision_history),
            updated_partial_narrative_str,
            session_id,
        ),
    )
    db.commit()

    return jsonify(
        {
            "narrative": new_narrative,
            "media": media_data["combined_video"],
            "cached": cached,
        }
    )


@app.route("/api/progress", methods=["GET"])
def get_progress():
    """Get the current progress of the game session."""
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"error": "No active session"}), 400

    db = get_db()
    progress_data = db.execute(
        "SELECT decision_history FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()

    if not progress_data or not progress_data["decision_history"]:
        return jsonify({"decisions": []})

    return jsonify({"decisions": json.loads(progress_data["decision_history"])})


@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    """Get all distinct scenarios from the database."""
    db = get_db()
    rows = db.execute("SELECT DISTINCT scenario FROM sessions").fetchall()
    scenario_list = [row["scenario"] for row in rows]

    return jsonify({"scenarios": scenario_list})


@app.route("/api/scenarios", methods=["POST"])
def add_scenario():
    """Add a new scenario to the database."""
    scenario_name = request.json.get("name")
    if not scenario_name:
        return jsonify({"error": "No scenario name provided"}), 400

    db = get_db()
    existing = db.execute(
        "SELECT 1 FROM sessions WHERE scenario = ?", (scenario_name,)
    ).fetchone()

    if existing:
        return jsonify({"success": False, "message": "Scenario already exists"}), 409

    new_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO sessions (id, scenario, current_scene_id) VALUES (?, ?, 0)",
        (new_id, scenario_name),
    )
    db.commit()

    return jsonify({"success": True, "scenario": scenario_name})


@app.route("/api/scenarios/<scenario_name>", methods=["DELETE"])
def delete_scenario(scenario_name):
    """Delete a scenario from the database."""
    if not scenario_name:
        return jsonify({"error": "No scenario name provided"}), 400

    db = get_db()
    db.execute("DELETE FROM sessions WHERE scenario = ?", (scenario_name,))
    db.commit()

    return jsonify(
        {"success": True, "message": f'Scenario "{scenario_name}" deleted successfully'}
    )


@app.route("/api/scenarios/<scenario_name>/preview", methods=["GET"])
def get_scenario_preview(scenario_name):
    """Get the preview image for a scenario.
    
    This finds the first frame image or uses the media URL from the scenario's data.
    """
    if not scenario_name:
        return jsonify({"error": "No scenario name provided"}), 400
        
    db = get_db()
    
    # First try to find any cache entries for this scenario
    cache_row = db.execute(
        "SELECT next_scene_prompts, next_media_urls FROM scene_cache "
        "WHERE scenario = ? LIMIT 1",
        (scenario_name,)
    ).fetchone()
    
    if cache_row:
        # Find the first frame from the cached scene prompts
        try:
            scene_prompts = json.loads(cache_row["next_scene_prompts"])
            media_data = json.loads(cache_row["next_media_urls"])
            
            # If we have individual videos, get the first one's corresponding first frame
            if "individual_videos" in media_data and media_data["individual_videos"]:
                # Get the video URL
                video_url = media_data["individual_videos"][0]["video_url"]
                
                # Convert to a preview image path (attempt to find the original first frame)
                # First check if the scene has a first_frame_prompt
                if "scenes" in scene_prompts and scene_prompts["scenes"]:
                    # The first frame would be in static/images with a UUID filename
                    # Try to find a matching image file
                    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
                    # Return a placeholder since we don't have a direct mapping from video to first frame
                    preview_url = "/static/images/placeholder.jpg"
                    return jsonify({"preview_url": preview_url})
                
                # If we can't find the specific first frame, generate a frame from the video
                video_path = os.path.join(os.path.dirname(__file__), video_url.lstrip('/'))
                if os.path.exists(video_path):
                    # Extract the first frame from the video using ffmpeg
                    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'previews')
                    os.makedirs(static_dir, exist_ok=True)
                    
                    preview_filename = f"{uuid.uuid4()}.jpg"
                    preview_path = os.path.join(static_dir, preview_filename)
                    preview_url = f"/static/previews/{preview_filename}"
                    
                    try:
                        # Use ffmpeg to extract the first frame
                        ffmpeg_cmd = ["ffmpeg", "-i", video_path, "-ss", "00:00:00", "-vframes", "1", preview_path]
                        import subprocess
                        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0 and os.path.exists(preview_path):
                            return jsonify({"preview_url": preview_url})
                    except Exception as e:
                        print(f"Error extracting frame: {e}")
            
            # If we have a combined video, just get a frame from that
            if "combined_video" in media_data and media_data["combined_video"]:
                # Same process as above but for the combined video
                video_path = os.path.join(os.path.dirname(__file__), media_data["combined_video"].lstrip('/'))
                if os.path.exists(video_path):
                    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'previews')
                    os.makedirs(static_dir, exist_ok=True)
                    
                    preview_filename = f"{uuid.uuid4()}.jpg"
                    preview_path = os.path.join(static_dir, preview_filename)
                    preview_url = f"/static/previews/{preview_filename}"
                    
                    try:
                        ffmpeg_cmd = ["ffmpeg", "-i", video_path, "-ss", "00:00:00", "-vframes", "1", preview_path]
                        import subprocess
                        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0 and os.path.exists(preview_path):
                            return jsonify({"preview_url": preview_url})
                    except Exception as e:
                        print(f"Error extracting frame: {e}")
                        
        except Exception as e:
            print(f"Error generating preview: {e}")
    
    # If we couldn't get a frame, return a placeholder
    return jsonify({"preview_url": "/static/images/placeholder.jpg"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)

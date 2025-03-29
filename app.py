import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
import uuid
import ast
from api.writer_agent import generate_narrative
from api.producer_agent import generate_scene_prompts
from api.media_generator import generate_scene_videos, concatenate_videos
from database.db import get_db, init_db, close_db

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder="static",
            template_folder="templates")
# Configure CORS to allow requests from the Next.js frontend
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Register database close function
app.teardown_appcontext(close_db)

# Register CLI command for database initialization
@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    print('Initialized the database.')

# Initialize database
with app.app_context():
    init_db()

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    """Start a new game session with a fresh narrative."""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    
    scenario = request.json.get('scenario', 'Cuban Missile Crisis')
    print(f"\n=== Starting new game: {scenario} ===")
    
    db = get_db()
    
    # Create a brand-new session record
    db.execute(
        'INSERT INTO sessions (id, scenario, current_scene_id) VALUES (?, ?, ?)',
        (session_id, scenario, 0)
    )
    db.commit()
    
    # Generate the initial narrative
    narrative_data = generate_narrative(None, None, scenario)
    narrative_str = str(narrative_data)
    
    # Check if we've already generated the same scenario, scene, and narrative
    cache_row = db.execute(
        'SELECT scene_prompts, media_urls FROM scene_cache WHERE scenario = ? AND scene_id = ? AND narrative_data = ?',
        (scenario, narrative_data['scene_id'], narrative_str)
    ).fetchone()
    
    if cache_row:
        # Reuse cached prompts and media
        print(f"Found cached media for scenario '{scenario}', scene {narrative_data['scene_id']}")
        scene_prompts = ast.literal_eval(cache_row['scene_prompts'])
        media_data = ast.literal_eval(cache_row['media_urls'])
        cached = True
    else:
        # Generate new prompts and media for this scene
        scene_prompts = generate_scene_prompts(narrative_data['narrative'])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)
        
        media_data = {
            'individual_videos': video_urls,
            'combined_video': combined_video_url
        }
        
        # Store in the cache for future reuse
        db.execute(
            'INSERT INTO scene_cache (scenario, scene_id, narrative_data, scene_prompts, media_urls) VALUES (?, ?, ?, ?, ?)',
            (scenario, narrative_data['scene_id'], narrative_str, str(scene_prompts), str(media_data))
        )
        db.commit()
        cached = False
    
    # Update the session record with the current scene data
    db.execute(
        'UPDATE sessions SET current_scene_id = ?, narrative_data = ?, scene_prompts = ?, media_urls = ? WHERE id = ?',
        (narrative_data['scene_id'], narrative_str, str(scene_prompts), str(media_data), session_id)
    )
    db.commit()
    
    return jsonify({
        'session_id': session_id,
        'narrative': narrative_data,
        'media': media_data['combined_video'],
        'cached': cached
    })

@app.route('/api/decision', methods=['POST'])
def make_decision():
    """Process a player's decision and move to the next narrative segment."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active session'}), 400
    
    decision_id = request.json.get('decision')
    current_scene_id = request.json.get('scene_id')
    
    db = get_db()
    session_data = db.execute(
        'SELECT * FROM sessions WHERE id = ?', (session_id,)
    ).fetchone()
    
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    scenario = session_data['scenario']
    old_narrative_data = ast.literal_eval(session_data['narrative_data'])
    
    print(f"\n=== Player made decision: {decision_id} ===")
    selected_option = next((opt for opt in old_narrative_data['options'] if opt['id'] == decision_id), None)
    if selected_option:
        print(f"Selected: {selected_option['option']}")
    
    # Generate the next narrative based on the decision
    new_narrative = generate_narrative(old_narrative_data, decision_id, None)
    new_narrative_str = str(new_narrative)
    
    print("\n=== NEW NARRATIVE ===")
    print(f"Scene {new_narrative['scene_id']}: {new_narrative['narrative']}")
    print("Options:")
    for option in new_narrative['options']:
        print(f"  {option['id']}. {option['option']}")
    print("========================\n")
    
    # Check the cache to see if this new narrative was generated before
    cache_row = db.execute(
        'SELECT scene_prompts, media_urls FROM scene_cache WHERE scenario = ? AND scene_id = ? AND narrative_data = ?',
        (scenario, new_narrative['scene_id'], new_narrative_str)
    ).fetchone()
    
    if cache_row:
        print(f"Found cached media for scenario '{scenario}', scene {new_narrative['scene_id']}")
        scene_prompts = ast.literal_eval(cache_row['scene_prompts'])
        media_data = ast.literal_eval(cache_row['media_urls'])
        cached = True
    else:
        # Generate new scene prompts and media
        scene_prompts = generate_scene_prompts(new_narrative['narrative'])
        video_urls = generate_scene_videos(scene_prompts)
        combined_video_url = concatenate_videos(video_urls)
        
        media_data = {
            'individual_videos': video_urls,
            'combined_video': combined_video_url
        }
        
        # Store in the cache
        db.execute(
            'INSERT INTO scene_cache (scenario, scene_id, narrative_data, scene_prompts, media_urls) VALUES (?, ?, ?, ?, ?)',
            (scenario, new_narrative['scene_id'], new_narrative_str, str(scene_prompts), str(media_data))
        )
        db.commit()
        cached = False
    
    # Update the decision history
    decision_history = session_data['decision_history']
    if decision_history:
        decision_history = ast.literal_eval(decision_history)
    else:
        decision_history = []
    
    decision_history.append({
        'scene_id': old_narrative_data['scene_id'],
        'decision': decision_id,
        'decision_text': selected_option['option'] if selected_option else ''
    })
    
    # Update session with the newly generated scene
    db.execute(
        'UPDATE sessions SET current_scene_id = ?, narrative_data = ?, scene_prompts = ?, media_urls = ?, decision_history = ? WHERE id = ?',
        (new_narrative['scene_id'], new_narrative_str, str(scene_prompts), str(media_data), str(decision_history), session_id)
    )
    db.commit()
    
    return jsonify({
        'narrative': new_narrative,
        'media': media_data['combined_video'],
        'cached': cached
    })

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get the current progress of the game session."""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active session'}), 400
    
    db = get_db()
    progress_data = db.execute(
        'SELECT decision_history FROM sessions WHERE id = ?', (session_id,)
    ).fetchone()
    
    if not progress_data or not progress_data['decision_history']:
        return jsonify({'decisions': []})
    
    decisions = ast.literal_eval(progress_data['decision_history'])
    return jsonify({'decisions': decisions})

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get all available scenarios."""
    default_scenarios = [
        "Cuban Missile Crisis",
        "Moon Landing Decision",
        "Fall of the Berlin Wall"
    ]
    
    return jsonify({
        'scenarios': default_scenarios
    })

@app.route('/api/scenarios', methods=['POST'])
def create_scenario():
    """Create a new scenario."""
    name = request.json.get('name')
    if not name:
        return jsonify({'success': False, 'message': 'Scenario name is required'}), 400
    
    # In a real implementation, we would store the scenario in the database
    # For now, just return success
    return jsonify({
        'success': True,
        'scenario': name,
        'message': f'Scenario "{name}" created successfully'
    })

@app.route('/api/scenarios/<name>', methods=['POST'])
def delete_scenario(name):
    """Delete a scenario."""
    # Check if this is a DELETE request (handled as POST with _method parameter)
    if request.json.get('_method', '').upper() != 'DELETE':
        return jsonify({'success': False, 'message': 'Invalid method'}), 400
    
    # In a real implementation, we would delete the scenario from the database
    # For now, just return success
    return jsonify({
        'success': True,
        'message': f'Scenario "{name}" deleted successfully'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)

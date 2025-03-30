import os
import sqlite3
import json
from flask import Flask
from .models import db, Session, NarrativeData, ScenePrompt, MediaUrl, SceneCache, Video

def migrate_old_to_new(app):
    """
    Migrate data from the old SQLite database to the new SQLAlchemy models.
    
    Args:
        app: Flask application instance with SQLAlchemy configured
    """
    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Define paths - use the backup database as source
    old_db_path = os.path.join(base_dir, 'backup', 'rewritten_old.db')
    new_db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    print(f"Migrating from {old_db_path} to {new_db_uri}")
    
    # Check if old database exists
    if not os.path.exists(old_db_path):
        print(f"Old database {old_db_path} not found. Nothing to migrate.")
        return
    
    try:
        # Connect to the old database
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
        old_cursor = old_conn.cursor()
        
        with app.app_context():
            # Check table structure
            try:
                old_cursor.execute("PRAGMA table_info(sessions)")
                columns = {col['name'] for col in old_cursor.fetchall()}
                print(f"Columns in old sessions table: {columns}")
                
                # We need at least these columns for basic migration
                required_cols = {'id', 'scenario', 'current_scene_id', 'partial_narrative'}
                if not required_cols.issubset(columns):
                    print(f"Old database missing required columns: {required_cols - columns}")
                    return
                    
            except sqlite3.Error as e:
                print(f"Error checking old database structure: {e}")
                return
                
            # Migrate sessions
            old_cursor.execute("SELECT * FROM sessions")
            sessions = old_cursor.fetchall()
            print(f"Found {len(sessions)} sessions to migrate")
            
            for session_data in sessions:
                # Check if this session already exists in the new database
                existing = Session.query.get(session_data['id'])
                if existing:
                    print(f"Session {session_data['id']} already exists in new database. Skipping.")
                    continue
                
                # Create new session object
                session = Session(
                    id=session_data['id'],
                    scenario=session_data['scenario'],
                    current_scene_id=session_data['current_scene_id'],
                    partial_narrative=session_data['partial_narrative']
                )
                db.session.add(session)
                
                # Create related objects if data exists
                if 'narrative_data' in session_data and session_data['narrative_data']:
                    narrative = NarrativeData(
                        session_id=session_data['id'],
                        data=session_data['narrative_data']
                    )
                    db.session.add(narrative)
                
                if 'scene_prompts' in session_data and session_data['scene_prompts']:
                    prompts = ScenePrompt(
                        session_id=session_data['id'],
                        data=session_data['scene_prompts']
                    )
                    db.session.add(prompts)
                
                if 'media_urls' in session_data and session_data['media_urls']:
                    media = MediaUrl(
                        session_id=session_data['id'],
                        data=session_data['media_urls']
                    )
                    db.session.add(media)
            
            # Migrate scene cache
            try:
                old_cursor.execute("SELECT * FROM scene_cache")
                cache_entries = old_cursor.fetchall()
                print(f"Found {len(cache_entries)} cache entries to migrate")
                
                for cache_data in cache_entries:
                    # Check if this cache entry already exists in the new database
                    existing = SceneCache.query.filter_by(
                        scenario=cache_data['scenario'],
                        partial_narrative=cache_data['partial_narrative']
                    ).first()
                    
                    if existing:
                        print(f"Cache entry for scenario '{cache_data['scenario']}' with same partial narrative already exists. Skipping.")
                        continue
                    
                    # Create new cache entry
                    cache = SceneCache(
                        scenario=cache_data['scenario'],
                        partial_narrative=cache_data['partial_narrative'],
                        next_narrative=cache_data['next_narrative'],
                        next_scene_prompts=cache_data['next_scene_prompts'],
                        next_media_urls=cache_data['next_media_urls']
                    )
                    db.session.add(cache)
            except sqlite3.Error as e:
                print(f"Error migrating scene cache: {e}")
            
            # Scan the videos directory and create Video records
            migrate_videos(app)
            
            # Commit all changes
            db.session.commit()
            print("Migration completed successfully")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        if 'db' in locals():
            db.session.rollback()
    finally:
        if 'old_conn' in locals():
            old_conn.close()

def migrate_videos(app):
    """
    Scan the videos directory and create Video records for all videos.
    """
    from .video_cache import VideoCache
    
    # Get videos directory
    videos_dir = VideoCache.get_static_video_dir()
    print(f"Scanning videos in {videos_dir}")
    
    # Get list of video files
    if not os.path.exists(videos_dir):
        print("Videos directory does not exist")
        return
    
    video_files = [f for f in os.listdir(videos_dir) if f.endswith(('.mp4', '.webm', '.mov'))]
    print(f"Found {len(video_files)} video files")
    
    # Create Video records
    for filename in video_files:
        # Check if video record already exists
        existing = Video.query.filter_by(filename=filename).first()
        if existing:
            print(f"Video record for {filename} already exists. Skipping.")
            continue
        
        # Create new video record
        video = Video(
            filename=filename,
            url_path=f"/static/videos/{filename}",
            is_combined=False  # Default assumption
        )
        db.session.add(video)
        print(f"Added video record for {filename}")

def run_migration():
    """
    Create a Flask app and run the migration.
    This function can be called from a command-line script.
    """
    app = Flask(__name__)
    
    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Set database URI with absolute path
    db_path = os.path.join(base_dir, 'rewritten', 'database', 'rewritten.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        migrate_old_to_new(app)

if __name__ == "__main__":
    run_migration() 
import sqlite3
import os
from flask import g, current_app

def get_db():
    """Connect to the database."""
    if 'db' not in g:
        if not os.path.exists('database'):
            os.makedirs('database')
        
        g.db = sqlite3.connect(
            'database/rewritten.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """Initialize the database."""
    db = get_db()
    
    # Create the main sessions table
    # (storing the current scene's data, plus a decision history)
    db.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            scenario TEXT,
            current_scene_id INTEGER,
            narrative_data TEXT,
            scene_prompts TEXT,
            media_urls TEXT,
            decision_history TEXT
        )
    ''')
    
    # Create a separate cache table for scenes that have been generated before
    # so we can reuse narratives, prompts, and media URLs for the same scenario/scene
    db.execute('''
        CREATE TABLE IF NOT EXISTS scene_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario TEXT,
            scene_id INTEGER,
            narrative_data TEXT,
            scene_prompts TEXT,
            media_urls TEXT,
            UNIQUE(scenario, scene_id, narrative_data)
        )
    ''')
    
    db.commit()

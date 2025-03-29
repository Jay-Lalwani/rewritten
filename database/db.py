import sqlite3
import os
from flask import g

def get_db():
    """Connect to the database."""
    if 'db' not in g:
        if not os.path.exists('rewritten/database'):
            os.makedirs('rewritten/database')
        
        g.db = sqlite3.connect(
            'rewritten/database/rewritten.db',
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
    
    # Main sessions table
    db.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            scenario TEXT,
            current_scene_id INTEGER,
            narrative_data TEXT,
            scene_prompts TEXT,
            media_urls TEXT,
            decision_history TEXT,
            partial_narrative TEXT
        )
    ''')
    
    # Scene cache table:
    #   scenario: name of the scenario
    #   partial_narrative: JSON-serialized object describing the entire game state so far (last_narrative + decision_history)
    #   next_narrative, next_scene_prompts, next_media_urls: the newly generated content for the "next" step
    db.execute('''
        CREATE TABLE IF NOT EXISTS scene_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario TEXT NOT NULL,
            partial_narrative TEXT NOT NULL,
            next_narrative TEXT NOT NULL,
            next_scene_prompts TEXT NOT NULL,
            next_media_urls TEXT NOT NULL,
            UNIQUE(scenario, partial_narrative)
        )
    ''')
    
    db.commit()

# Database Module

## Overview

This module handles all database-related operations for the application. It uses Flask-SQLAlchemy for object-relational mapping, providing a clean and intuitive interface for database operations.

## Database Location

The SQLite database file is stored at:
```
rewritten/database/rewritten.db
```

This location is explicitly set in the database initialization to ensure consistency across different environments.

## Models

The following models are defined:

- **Session**: Represents a game session, with relationships to narrative data, scene prompts, and media URLs.
- **NarrativeData**: Stores the narrative content for a session.
- **ScenePrompt**: Stores the scene prompts for a session.
- **MediaUrl**: Stores media URLs for a session.
- **SceneCache**: Caches generated scenes to avoid redundant generation.
- **Video**: Tracks video files for efficient caching and reuse.

## Video Caching

Video caching is managed through the `VideoCache` class in `video_cache.py`. It provides methods to:

1. Save videos to the filesystem and register them in the database
2. Retrieve videos by prompt or other criteria
3. Get filesystem paths to videos
4. Generate unique filenames
5. Clean up unused videos

## Migration

When upgrading from the old database schema to the new SQLAlchemy models, a migration process is available:

1. **Automatic Migration**: When the application starts, it automatically checks if migration is needed and runs it if necessary.

2. **Manual Migration**: You can manually run the migration script with:
   ```
   ./migrate_db.py
   ```

The migration process:
1. Reads data from the old SQLite tables
2. Creates corresponding records in the new SQLAlchemy models
3. Scans the videos directory to register existing videos in the database

## Usage

To use the database in your code:

```python
from database.models import db, Session, NarrativeData, ScenePrompt, MediaUrl, SceneCache, Video

# Query example
session = Session.query.get(session_id)

# Create example
new_session = Session(
    id=str(uuid.uuid4()),
    scenario="Example Scenario",
    current_scene_id=0,
    partial_narrative=json.dumps({
        "scenario": "Example Scenario",
        "last_narrative": None,
        "decision_history": []
    })
)
db.session.add(new_session)
db.session.commit()
```

For video caching:

```python
from database.video_cache import VideoCache

# Save a video to the cache
video = VideoCache.save_video(
    "/static/videos/example.mp4",
    scene_id=1,
    is_combined=False,
    original_prompt="Example prompt"
)

# Get a video by prompt
cached_video = VideoCache.get_video_by_prompt("Example prompt")
if cached_video:
    video_url = cached_video.url_path
else:
    # Generate new video...
``` 
# Database package initialization
import os
from flask import Flask
from .models import db as sqlalchemy_db
from .db import init_db, close_db


def init_app(app: Flask):
    """Initialize the application with SQLAlchemy database."""
    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Define path to database directory and ensure it exists
    db_dir = os.path.join(base_dir, "rewritten", "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # Configure SQLAlchemy with absolute path
    db_path = os.path.join(base_dir, "rewritten", "database", "rewritten.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy
    sqlalchemy_db.init_app(app)

    # Register the close_db function to be called when cleaning up after a request
    app.teardown_appcontext(close_db)

    with app.app_context():
        # Create SQLAlchemy tables
        sqlalchemy_db.create_all()

        # Initialize legacy SQLite tables
        init_db()

        # Check if we need to migrate data from old format
        if needs_migration():
            from .migrate import migrate_old_to_new

            migrate_old_to_new(app)


def needs_migration():
    """
    Check if we need to migrate data from old database format.
    Returns True if backup database exists and appears to have data.
    """
    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Path to the backup SQLite database
    backup_db_path = os.path.join(base_dir, "backup", "rewritten_old.db")

    # Check if backup database exists
    if os.path.exists(backup_db_path) and os.path.getsize(backup_db_path) > 0:
        print(f"Found backup database at {backup_db_path}")
        return True

    return False

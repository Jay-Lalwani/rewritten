#!/usr/bin/env python3
"""
Database Migration Script

This script migrates data from the old SQLite database format to the new SQLAlchemy models.
"""

import os
import sys
from flask import Flask
from database.models import db
from database.migrate import migrate_old_to_new


def run_migration():
    # Create a Flask app
    app = Flask(__name__)

    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Configure database
    db_dir = os.path.join(base_dir, "rewritten", "database")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # Set database URI with absolute path
    db_path = os.path.join(base_dir, "rewritten", "database", "rewritten.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Run migration
    with app.app_context():
        db.create_all()
        migrate_old_to_new(app)


if __name__ == "__main__":
    print("=== Database Migration Tool ===")

    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Check if backup database exists
    backup_db_path = os.path.join(base_dir, "backup", "rewritten_old.db")
    if not os.path.exists(backup_db_path):
        print(f"Backup database not found at: {backup_db_path}")

        # Check for old database in original location as fallback
        old_db_path = os.path.join(base_dir, "rewritten", "database", "rewritten.db")
        if os.path.exists(old_db_path):
            print(f"Found database at original location: {old_db_path}")
            print("Creating backup before proceeding...")

            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(base_dir, "backup")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)

            # Back up the old database
            import shutil

            shutil.copy2(old_db_path, backup_db_path)
            print(f"Database backed up to: {backup_db_path}")
        else:
            print("No database found to migrate. Will create a fresh database.")
            run_migration()
            sys.exit(0)

    # Ask for confirmation
    confirm = input(
        "This will migrate data from the old database format to the new SQLAlchemy models.\n"
        "Make sure you have a backup of your data before proceeding.\n"
        "Continue? (y/n): "
    )

    if confirm.lower() != "y":
        print("Migration cancelled.")
        sys.exit(0)

    # Run migration
    run_migration()

#!/usr/bin/env python3
"""
Database Directory Initialization Script

This script initializes the database directory structure.
Run it before starting the application for the first time.
"""

import os
import sys


def init_db_dir():
    """
    Create the database directory structure if it doesn't exist.
    """
    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Define the path to the database directory
    db_dir = os.path.join(base_dir, "rewritten", "database")

    # Create the directory if it doesn't exist
    if not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}")
        try:
            os.makedirs(db_dir, exist_ok=True)
            print("Database directory created successfully.")
        except Exception as e:
            print(f"Error creating database directory: {e}")
            sys.exit(1)
    else:
        print(f"Database directory already exists: {db_dir}")

    # Return the path for verification
    return db_dir


if __name__ == "__main__":
    print("Initializing database directory...")
    db_dir = init_db_dir()
    print(f"Database will be stored at: {os.path.join(db_dir, 'rewritten.db')}")
    print("Done.")

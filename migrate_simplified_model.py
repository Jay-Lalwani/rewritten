"""
Migration script to apply the simplified model changes to an existing database
while preserving all existing data.
"""

import os
import sqlite3
from flask import Flask
from database.models import db

def migrate_to_simplified_model():
    """Apply schema changes to remove classes while preserving assignments and other data"""
    print("Starting migration to simplified model...")
    
    # Get the absolute path to the project root directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Define database path
    db_path = os.path.join(base_dir, "rewritten", "database", "rewritten.db")
    
    # Verify database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
    
    # 1. Create backup before making changes
    backup_path = f"{db_path}.premigration.bak"
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Backed up existing database to {backup_path}")
    except Exception as e:
        print(f"Error backing up database: {e}")
        return
    
    # 2. Connect to the SQLite database directly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Check if class_id column exists in assignments table
        cursor.execute("PRAGMA table_info(assignments)")
        columns = cursor.fetchall()
        has_class_id = any(col[1] == 'class_id' for col in columns)
        
        if has_class_id:
            # Drop the foreign key constraint (not directly supported in SQLite)
            # Instead, we'll drop the column when we recreate the table
            
            # 3. Create a temporary table without the class_id column
            cursor.execute("""
                CREATE TABLE assignments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    scenario VARCHAR(100) NOT NULL,
                    access_code VARCHAR(10) NOT NULL UNIQUE,
                    teacher_id INTEGER NOT NULL,
                    created_at DATETIME,
                    due_date DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
                )
            """)
            
            # 4. Copy data from the old table to the new table
            cursor.execute("""
                INSERT INTO assignments_new (id, title, scenario, access_code, teacher_id, created_at, due_date, is_active)
                SELECT id, title, scenario, access_code, teacher_id, created_at, due_date, is_active
                FROM assignments
            """)
            
            # 5. Drop the old table and rename the new one
            cursor.execute("DROP TABLE assignments")
            cursor.execute("ALTER TABLE assignments_new RENAME TO assignments")
            
            print("Removed class_id column from assignments table")
        else:
            print("assignments table already has simplified schema")
        
        # 6. Drop class-related tables if they exist
        tables_to_drop = ['class_videos', 'student_class', 'classes']
        for table in tables_to_drop:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                cursor.execute(f"DROP TABLE {table}")
                print(f"Dropped {table} table")
            else:
                print(f"{table} table does not exist")
        
        # 7. Update Alembic version to mark this migration as complete
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        if cursor.fetchone():
            cursor.execute("UPDATE alembic_version SET version_num = 'simplify_model'")
        else:
            cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, PRIMARY KEY (version_num))")
            cursor.execute("INSERT INTO alembic_version VALUES ('simplify_model')")
        
        # Commit all changes
        conn.commit()
        print("Migration successful!")
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error during migration: {e}")
        print(f"Database has been rolled back. Original backup is at {backup_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_to_simplified_model() 
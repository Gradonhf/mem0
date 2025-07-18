#!/usr/bin/env python3
"""
Script to fix the apps table index:
- Drops the global unique index on apps.name (ix_apps_name)
- Adds a composite unique index on (owner_id, name) (idx_app_owner_name)

Usage:
    python fix_app_index.py
"""
import sqlite3
import os

DB_PATH = os.environ.get("OPENMEMORY_DB_PATH", "/usr/src/openmemory/openmemory.db")

def fix_indexes(db_path):
    conn = sqlite3.connect(db_path)
    try:
        print(f"Connecting to database: {db_path}")
        # Drop the global unique index if it exists
        conn.execute("DROP INDEX IF EXISTS ix_apps_name;")
        print("Dropped index: ix_apps_name (if it existed)")
        # Create the composite unique index
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_app_owner_name ON apps(owner_id, name);")
        print("Created unique index: idx_app_owner_name (owner_id, name)")
        conn.commit()
        print("Database migration completed successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_indexes(DB_PATH) 
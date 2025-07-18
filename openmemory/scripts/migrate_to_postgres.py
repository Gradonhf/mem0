#!/usr/bin/env python3
"""
Script to migrate data from SQLite to PostgreSQL.
This script will:
1. Connect to both databases
2. Transfer all data while maintaining relationships
3. Verify the migration

Usage:
    python scripts/migrate_to_postgres.py
"""
import os
import sys
import sqlite3
import psycopg2
from pathlib import Path
from datetime import datetime
import uuid

# Add the api directory to the Python path
api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))

# Database configurations
SQLITE_DB_PATH = "/usr/src/openmemory/openmemory.db"
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://openmemory:openmemory_password@localhost:5432/openmemory")

def get_sqlite_connection():
    """Get SQLite connection."""
    return sqlite3.connect(SQLITE_DB_PATH)

def get_postgres_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(POSTGRES_URL)

def migrate_users():
    """Migrate users from SQLite to PostgreSQL."""
    print("Migrating users...")
    
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get all users from SQLite
        sqlite_cursor.execute("SELECT id, user_id, name, email, metadata, created_at, updated_at FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            user_id, user_id_str, name, email, metadata, created_at, updated_at = user
            
            # Insert into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO users (id, user_id, name, email, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, user_id_str, name, email, metadata, created_at, updated_at))
        
        postgres_conn.commit()
        print(f"✅ Migrated {len(users)} users")
        
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def migrate_apps():
    """Migrate apps from SQLite to PostgreSQL."""
    print("Migrating apps...")
    
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get all apps from SQLite
        sqlite_cursor.execute("SELECT id, owner_id, name, description, metadata, is_active, created_at, updated_at FROM apps")
        apps = sqlite_cursor.fetchall()
        
        for app in apps:
            app_id, owner_id, name, description, metadata, is_active, created_at, updated_at = app
            
            # Insert into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO apps (id, owner_id, name, description, metadata, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (app_id, owner_id, name, description, metadata, is_active, created_at, updated_at))
        
        postgres_conn.commit()
        print(f"✅ Migrated {len(apps)} apps")
        
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def migrate_memories():
    """Migrate memories from SQLite to PostgreSQL."""
    print("Migrating memories...")
    
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get all memories from SQLite
        sqlite_cursor.execute("""
            SELECT id, user_id, app_id, content, vector, metadata, state, created_at, updated_at, archived_at, deleted_at 
            FROM memories
        """)
        memories = sqlite_cursor.fetchall()
        
        for memory in memories:
            (memory_id, user_id, app_id, content, vector, metadata, state, 
             created_at, updated_at, archived_at, deleted_at) = memory
            
            # Insert into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO memories (id, user_id, app_id, content, vector, metadata, state, created_at, updated_at, archived_at, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (memory_id, user_id, app_id, content, vector, metadata, state, 
                  created_at, updated_at, archived_at, deleted_at))
        
        postgres_conn.commit()
        print(f"✅ Migrated {len(memories)} memories")
        
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def migrate_categories():
    """Migrate categories from SQLite to PostgreSQL."""
    print("Migrating categories...")
    
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get all categories from SQLite
        sqlite_cursor.execute("SELECT id, name, description, created_at, updated_at FROM categories")
        categories = sqlite_cursor.fetchall()
        
        for category in categories:
            category_id, name, description, created_at, updated_at = category
            
            # Insert into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO categories (id, name, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, (category_id, name, description, created_at, updated_at))
        
        postgres_conn.commit()
        print(f"✅ Migrated {len(categories)} categories")
        
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def migrate_memory_categories():
    """Migrate memory-category relationships from SQLite to PostgreSQL."""
    print("Migrating memory-category relationships...")
    
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Get all memory-category relationships from SQLite
        sqlite_cursor.execute("SELECT memory_id, category_id FROM memory_categories")
        relationships = sqlite_cursor.fetchall()
        
        for relationship in relationships:
            memory_id, category_id = relationship
            
            # Insert into PostgreSQL
            postgres_cursor.execute("""
                INSERT INTO memory_categories (memory_id, category_id)
                VALUES (%s, %s)
                ON CONFLICT (memory_id, category_id) DO NOTHING
            """, (memory_id, category_id))
        
        postgres_conn.commit()
        print(f"✅ Migrated {len(relationships)} memory-category relationships")
        
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def verify_migration():
    """Verify that the migration was successful."""
    print("Verifying migration...")
    
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()
        
        # Check user counts
        sqlite_cursor.execute("SELECT COUNT(*) FROM users")
        sqlite_users = sqlite_cursor.fetchone()[0]
        
        postgres_cursor.execute("SELECT COUNT(*) FROM users")
        postgres_users = postgres_cursor.fetchone()[0]
        
        print(f"Users - SQLite: {sqlite_users}, PostgreSQL: {postgres_users}")
        
        # Check memory counts
        sqlite_cursor.execute("SELECT COUNT(*) FROM memories")
        sqlite_memories = sqlite_cursor.fetchone()[0]
        
        postgres_cursor.execute("SELECT COUNT(*) FROM memories")
        postgres_memories = postgres_cursor.fetchone()[0]
        
        print(f"Memories - SQLite: {sqlite_memories}, PostgreSQL: {postgres_memories}")
        
        if sqlite_users == postgres_users and sqlite_memories == postgres_memories:
            print("✅ Migration verification successful!")
        else:
            print("❌ Migration verification failed!")
            
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def main():
    """Run the complete migration."""
    print("Starting migration from SQLite to PostgreSQL...")
    print("=" * 50)
    
    try:
        migrate_users()
        migrate_apps()
        migrate_categories()
        migrate_memories()
        migrate_memory_categories()
        verify_migration()
        
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your configuration to use PostgreSQL")
        print("2. Restart your application")
        print("3. Test the application with the new database")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
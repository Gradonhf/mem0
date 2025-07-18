#!/usr/bin/env python3
"""
Script to check memory synchronization between SQLite and Qdrant databases.
This will help identify memories that exist in SQLite but not in Qdrant.

Usage:
    python scripts/check_memory_sync.py
"""
import os
import sys
import sqlite3
import requests
from pathlib import Path

# Add the api directory to the Python path
api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))

def get_sqlite_memories():
    """Get all memories from SQLite database."""
    db_path = "/usr/src/openmemory/openmemory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get memories with their app names
    cursor.execute("""
        SELECT m.id, m.content, a.name as app_name, u.user_id
        FROM memories m
        JOIN apps a ON m.app_id = a.id
        JOIN users u ON m.user_id = u.id
        WHERE m.state = 'active'
        ORDER BY a.name, m.created_at
    """)
    
    memories = cursor.fetchall()
    conn.close()
    return memories

def get_qdrant_memories():
    """Get all memories from Qdrant."""
    try:
        # Get Qdrant configuration from environment
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = os.getenv("QDRANT_PORT", "6333")
        collection_name = os.getenv("QDRANT_COLLECTION", "openmemory")
        
        # Get collection info
        url = f"http://{qdrant_host}:{qdrant_port}/collections/{collection_name}/points"
        response = requests.get(url, params={"limit": 1000})
        
        if response.status_code == 200:
            data = response.json()
            return data.get("result", {}).get("points", [])
        else:
            print(f"Error getting Qdrant data: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        return []

def check_sync():
    """Check synchronization between SQLite and Qdrant."""
    print("Checking memory synchronization between SQLite and Qdrant...")
    print("=" * 60)
    
    # Get memories from both databases
    sqlite_memories = get_sqlite_memories()
    qdrant_points = get_qdrant_memories()
    
    print(f"SQLite memories: {len(sqlite_memories)}")
    print(f"Qdrant points: {len(qdrant_points)}")
    print()
    
    # Group SQLite memories by app
    memories_by_app = {}
    for memory_id, content, app_name, user_id in sqlite_memories:
        if app_name not in memories_by_app:
            memories_by_app[app_name] = []
        memories_by_app[app_name].append({
            'id': memory_id,
            'content': content,
            'user_id': user_id
        })
    
    # Check each app
    for app_name, memories in memories_by_app.items():
        print(f"App: {app_name}")
        print(f"  Memories in SQLite: {len(memories)}")
        
        # Check which memories exist in Qdrant
        qdrant_ids = [point.get('id') for point in qdrant_points]
        missing_in_qdrant = []
        
        for memory in memories:
            if memory['id'] not in qdrant_ids:
                missing_in_qdrant.append(memory)
        
        if missing_in_qdrant:
            print(f"  ❌ Missing in Qdrant: {len(missing_in_qdrant)}")
            for memory in missing_in_qdrant:
                print(f"    - {memory['id']}: {memory['content'][:50]}...")
        else:
            print(f"  ✅ All memories synced with Qdrant")
        print()

if __name__ == "__main__":
    check_sync() 
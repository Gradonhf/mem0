#!/bin/bash

# SQLite Backup Script for OpenMemory
# Usage: ./scripts/backup_sqlite.sh

set -e

# Configuration
BACKUP_DIR="/backups/openmemory"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="openmemory_sqlite_${TIMESTAMP}.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get database path from DATABASE_URL or use default
if [ -z "$DATABASE_URL" ]; then
    DB_PATH="./openmemory.db"
else
    # Extract path from sqlite:///path format
    DB_PATH=$(echo "$DATABASE_URL" | sed 's/sqlite:\/\///')
fi

echo "Backing up SQLite database: $DB_PATH"

# Check if database file exists
if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database file not found: $DB_PATH"
    exit 1
fi

# Perform backup
cp "$DB_PATH" "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "Backup completed: $BACKUP_DIR/${BACKUP_FILE}.gz"

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "openmemory_sqlite_*.db.gz" -mtime +30 -delete

echo "Old backups cleaned up" 
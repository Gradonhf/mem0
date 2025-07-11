#!/bin/bash

# Master Backup Script for OpenMemory
# Usage: ./scripts/backup_all.sh

set -e

echo "Starting OpenMemory backup process..."

# Determine database type and run appropriate backup
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable not set"
    exit 1
fi

# Extract database type from DATABASE_URL
DB_TYPE=$(echo "$DATABASE_URL" | cut -d':' -f1)

case $DB_TYPE in
    "postgresql"|"postgres")
        echo "Backing up PostgreSQL database..."
        ./scripts/backup_postgresql.sh
        ;;
    "mysql")
        echo "Backing up MySQL database..."
        ./scripts/backup_mysql.sh
        ;;
    "sqlite")
        echo "Backing up SQLite database..."
        ./scripts/backup_sqlite.sh
        ;;
    *)
        echo "Error: Unsupported database type: $DB_TYPE"
        exit 1
        ;;
esac

# Backup Qdrant vector database
echo "Backing up Qdrant vector database..."
./scripts/backup_qdrant.sh

echo "All backups completed successfully!" 
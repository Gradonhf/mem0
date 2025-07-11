#!/bin/bash

# PostgreSQL Backup Script for OpenMemory
# Usage: ./scripts/backup_postgresql.sh

set -e

# Configuration
BACKUP_DIR="/backups/openmemory"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="openmemory_postgresql_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Extract database connection details from DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable not set"
    exit 1
fi

# Parse DATABASE_URL (format: postgresql://user:pass@host:port/db)
DB_URL=$(echo "$DATABASE_URL" | sed 's/postgresql:\/\///')
DB_USER=$(echo "$DB_URL" | cut -d':' -f1)
DB_PASS=$(echo "$DB_URL" | cut -d':' -f2 | cut -d'@' -f1)
DB_HOST_PORT=$(echo "$DB_URL" | cut -d'@' -f2 | cut -d'/' -f1)
DB_HOST=$(echo "$DB_HOST_PORT" | cut -d':' -f1)
DB_PORT=$(echo "$DB_HOST_PORT" | cut -d':' -f2)
DB_NAME=$(echo "$DB_URL" | cut -d'/' -f2)

# Set default port if not specified
if [ -z "$DB_PORT" ]; then
    DB_PORT=5432
fi

echo "Backing up PostgreSQL database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"

# Perform backup
PGPASSWORD="$DB_PASS" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --verbose \
    --clean \
    --if-exists \
    --create \
    > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "Backup completed: $BACKUP_DIR/${BACKUP_FILE}.gz"

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "openmemory_postgresql_*.sql.gz" -mtime +30 -delete

echo "Old backups cleaned up" 
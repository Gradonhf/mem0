#!/bin/bash

# MySQL Backup Script for OpenMemory
# Usage: ./scripts/backup_mysql.sh

set -e

# Configuration
BACKUP_DIR="/backups/openmemory"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="openmemory_mysql_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Extract database connection details from DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable not set"
    exit 1
fi

# Parse DATABASE_URL (format: mysql://user:pass@host:port/db)
DB_URL=$(echo "$DATABASE_URL" | sed 's/mysql:\/\///')
DB_USER=$(echo "$DB_URL" | cut -d':' -f1)
DB_PASS=$(echo "$DB_URL" | cut -d':' -f2 | cut -d'@' -f1)
DB_HOST_PORT=$(echo "$DB_URL" | cut -d'@' -f2 | cut -d'/' -f1)
DB_HOST=$(echo "$DB_HOST_PORT" | cut -d':' -f1)
DB_PORT=$(echo "$DB_HOST_PORT" | cut -d':' -f2)
DB_NAME=$(echo "$DB_URL" | cut -d'/' -f2)

# Set default port if not specified
if [ -z "$DB_PORT" ]; then
    DB_PORT=3306
fi

echo "Backing up MySQL database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"

# Perform backup
mysqldump \
    -h "$DB_HOST" \
    -P "$DB_PORT" \
    -u "$DB_USER" \
    -p"$DB_PASS" \
    --single-transaction \
    --routines \
    --triggers \
    "$DB_NAME" \
    > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "Backup completed: $BACKUP_DIR/${BACKUP_FILE}.gz"

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "openmemory_mysql_*.sql.gz" -mtime +30 -delete

echo "Old backups cleaned up" 
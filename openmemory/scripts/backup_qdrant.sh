#!/bin/bash

# Qdrant Vector Database Backup Script for OpenMemory
# Usage: ./scripts/backup_qdrant.sh

set -e

# Configuration
BACKUP_DIR="/backups/openmemory"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="openmemory_qdrant_${TIMESTAMP}.json"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get Qdrant configuration from environment
QDRANT_HOST=${QDRANT_HOST:-"localhost"}
QDRANT_PORT=${QDRANT_PORT:-6333}
QDRANT_COLLECTION=${QDRANT_COLLECTION:-"openmemory"}
QDRANT_API_KEY=${QDRANT_API_KEY:-""}

echo "Backing up Qdrant collection: $QDRANT_COLLECTION"
echo "Host: $QDRANT_HOST:$QDRANT_PORT"

# Build curl command
CURL_CMD="curl -s"
if [ -n "$QDRANT_API_KEY" ]; then
    CURL_CMD="$CURL_CMD -H 'api-key: $QDRANT_API_KEY'"
fi

# Get collection info
COLLECTION_INFO=$($CURL_CMD "http://$QDRANT_HOST:$QDRANT_PORT/collections/$QDRANT_COLLECTION")

if [ $? -ne 0 ]; then
    echo "Error: Could not connect to Qdrant at $QDRANT_HOST:$QDRANT_PORT"
    exit 1
fi

# Export collection data
COLLECTION_DATA=$($CURL_CMD "http://$QDRANT_HOST:$QDRANT_PORT/collections/$QDRANT_COLLECTION/points?limit=10000")

# Save backup
echo "$COLLECTION_DATA" > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "Backup completed: $BACKUP_DIR/${BACKUP_FILE}.gz"

# Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "openmemory_qdrant_*.json.gz" -mtime +30 -delete

echo "Old backups cleaned up" 
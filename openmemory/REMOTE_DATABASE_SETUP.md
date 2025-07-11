# Remote Database Setup Guide for OpenMemory

This guide explains how to configure OpenMemory to use remote databases and set up automated backups.

## 1. Remote SQL Database Setup

### Supported Databases
- **PostgreSQL** (Recommended for production)
- **MySQL**
- **SQLite** (Current default)

### PostgreSQL Setup

#### 1.1 Install PostgreSQL Dependencies
The required dependencies are already included in `requirements.txt`:
- `psycopg2-binary>=2.9.0` (PostgreSQL adapter)

#### 1.2 Configure Database URL
Update your `.env` file:

```bash
# PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database_name

# Example with environment variables
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

#### 1.3 Environment Variables for PostgreSQL
```bash
# Database Configuration
DB_USER=openmemory_user
DB_PASSWORD=your_secure_password
DB_HOST=your-postgres-host.com
DB_PORT=5432
DB_NAME=openmemory_db
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

### MySQL Setup

#### 1.1 Install MySQL Dependencies
MySQL support has been added to `requirements.txt`:
- `mysqlclient>=2.1.0` (MySQL adapter)

#### 1.2 Configure Database URL
```bash
# MySQL
DATABASE_URL=mysql://username:password@host:port/database_name

# Example
DATABASE_URL=mysql://openmemory_user:password@mysql-host:3306/openmemory_db
```

### 2. Remote Vector Database (Qdrant) Setup

#### 2.1 Configure Remote Qdrant
Update your `.env` file:

```bash
# Vector Store Configuration
QDRANT_HOST=your-qdrant-host.com
QDRANT_PORT=6333
QDRANT_COLLECTION=openmemory
```

#### 2.2 Qdrant Cloud Setup
For Qdrant Cloud, you'll need API key authentication:

```bash
# Qdrant Cloud Configuration
QDRANT_HOST=your-cluster.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your-qdrant-api-key
```

### 3. Docker Compose Configuration for Remote Databases

Update your `docker-compose.yml` to remove local database services:

```yaml
services:
  openmemory-mcp:
    image: mem0/openmemory-mcp
    build: api/
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - USER_ID=${USER_ID:-default_user}
      - DATABASE_URL=${DATABASE_URL}
      - QDRANT_HOST=${QDRANT_HOST}
      - QDRANT_PORT=${QDRANT_PORT}
      - QDRANT_API_KEY=${QDRANT_API_KEY}  # If using Qdrant Cloud
    env_file:
      - .env
    ports:
      - "8765:8765"
    volumes:
      - ./api:/usr/src/openmemory
    command: >
      sh -c "uvicorn main:app --host 0.0.0.0 --port 8765 --reload --workers 4"

  openmemory-ui:
    build:
      context: ui/
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
        NEXT_PUBLIC_USER_ID: ${NEXT_PUBLIC_USER_ID}
    image: mem0/openmemory-ui:latest
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8765}
      - NEXT_PUBLIC_USER_ID=${USER_ID:-default_user}
      - NODE_ENV=${NODE_ENV:-production}
    env_file:
      - .env
    depends_on:
      - openmemory-mcp

# Remove the mem0_store service since you're using remote Qdrant
```

## 4. Database Backup Setup

### 4.1 SQL Database Backup Scripts

#### PostgreSQL Backup Script
Create `scripts/backup_postgresql.sh`:

```bash
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
```

#### MySQL Backup Script
Create `scripts/backup_mysql.sh`:

```bash
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
```

#### SQLite Backup Script
Create `scripts/backup_sqlite.sh`:

```bash
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
```

### 4.2 Qdrant Vector Database Backup

Create `scripts/backup_qdrant.sh`:

```bash
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
```

### 4.3 Automated Backup Setup

#### Create a Master Backup Script
Create `scripts/backup_all.sh`:

```bash
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
```

#### Setup Cron Job for Automated Backups
Add to your crontab:

```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /path/to/openmemory/scripts/backup_all.sh >> /var/log/openmemory_backup.log 2>&1
```

### 4.4 Docker Backup Integration

Update your `docker-compose.yml` to include backup volumes:

```yaml
services:
  openmemory-mcp:
    image: mem0/openmemory-mcp
    build: api/
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - USER_ID=${USER_ID:-default_user}
      - DATABASE_URL=${DATABASE_URL}
      - QDRANT_HOST=${QDRANT_HOST}
      - QDRANT_PORT=${QDRANT_PORT}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    env_file:
      - .env
    ports:
      - "8765:8765"
    volumes:
      - ./api:/usr/src/openmemory
      - ./backups:/backups/openmemory  # Mount backup directory
    command: >
      sh -c "uvicorn main:app --host 0.0.0.0 --port 8765 --reload --workers 4"

volumes:
  backup_storage:
```

## 5. Migration Steps

### 5.1 From SQLite to Remote Database

1. **Create the remote database**
2. **Update environment variables**
3. **Run migrations**
4. **Test the connection**

```bash
# 1. Update your .env file with remote database URL
DATABASE_URL=postgresql://user:pass@host:port/db

# 2. Run database migrations
make migrate

# 3. Test the connection
docker compose exec api python -c "from app.database import engine; print('Database connection successful')"
```

### 5.2 From Local Qdrant to Remote Qdrant

1. **Export data from local Qdrant**
2. **Import data to remote Qdrant**
3. **Update environment variables**

```bash
# Export from local Qdrant
curl -s "http://localhost:6333/collections/openmemory/points?limit=10000" > qdrant_export.json

# Import to remote Qdrant (you'll need to use Qdrant's import tools)
# This depends on your Qdrant setup
```

## 6. Environment Configuration Examples

### Production Environment (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://openmemory_user:secure_password@db.example.com:5432/openmemory_prod
DB_USER=openmemory_user
DB_PASSWORD=secure_password
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=openmemory_prod

# Vector Store Configuration
QDRANT_HOST=qdrant.example.com
QDRANT_PORT=6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=openmemory_prod

# Application Configuration
OPENAI_API_KEY=sk-your-openai-api-key
USER_ID=production_user
ENVIRONMENT=production
```

### Development Environment (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/openmemory_dev

# Vector Store Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=openmemory_dev

# Application Configuration
OPENAI_API_KEY=sk-your-openai-api-key
USER_ID=developer
ENVIRONMENT=development
```

## 7. Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials
   - Check network connectivity
   - Ensure database server is running

2. **Qdrant Connection Issues**
   - Verify Qdrant host and port
   - Check API key if using Qdrant Cloud
   - Test connectivity with curl

3. **Migration Issues**
   - Ensure database exists
   - Check user permissions
   - Verify database URL format

### Testing Connections

```bash
# Test PostgreSQL connection
psql "$DATABASE_URL" -c "SELECT 1;"

# Test MySQL connection
mysql -h host -u user -p database -e "SELECT 1;"

# Test Qdrant connection
curl "http://$QDRANT_HOST:$QDRANT_PORT/collections"
```

## 8. Security Considerations

1. **Use strong passwords for database users**
2. **Enable SSL/TLS for database connections**
3. **Use environment variables for sensitive data**
4. **Regularly rotate API keys**
5. **Implement proper backup encryption**
6. **Use VPC/private networks when possible**

## 9. Performance Optimization

1. **Use connection pooling for databases**
2. **Implement proper indexing**
3. **Monitor query performance**
4. **Use read replicas for heavy read workloads**
5. **Implement caching strategies** 
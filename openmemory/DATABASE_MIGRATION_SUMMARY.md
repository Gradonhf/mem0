# OpenMemory Database Migration Summary

## Overview

This document summarizes the changes made to support remote databases and automated backups in OpenMemory.

## Changes Made

### 1. Database Support Enhancements

#### Added MySQL Support
- Added `mysqlclient>=2.1.0` to `api/requirements.txt`
- Updated `api/app/database.py` to support multiple database types
- Added proper connection handling for PostgreSQL, MySQL, and SQLite

#### Database Configuration
- Enhanced database connection logic to handle different database types
- Removed SQLite-specific `connect_args` for remote databases
- Added URL parsing to determine appropriate connection parameters

### 2. Backup System Implementation

#### Created Backup Scripts
- `scripts/backup_postgresql.sh` - PostgreSQL backup with compression
- `scripts/backup_mysql.sh` - MySQL backup with compression  
- `scripts/backup_sqlite.sh` - SQLite backup with compression
- `scripts/backup_qdrant.sh` - Qdrant vector database backup
- `scripts/backup_all.sh` - Master script that orchestrates all backups

#### Backup Features
- Automatic compression (gzip)
- Timestamp-based naming
- 30-day retention policy
- Error handling and validation
- Support for remote Qdrant with API key authentication

### 3. Configuration Management

#### Environment Variables
- `DATABASE_URL` - Supports PostgreSQL, MySQL, and SQLite URLs
- `QDRANT_HOST` - Remote Qdrant host
- `QDRANT_PORT` - Remote Qdrant port
- `QDRANT_API_KEY` - Qdrant Cloud API key (optional)

#### Docker Configuration
- Created `docker-compose.remote.yml` for remote database setups
- Added backup volume mounting
- Removed local Qdrant service dependency

### 4. Automation Tools

#### Makefile Commands
- `make backup` - Run full backup (SQL + Qdrant)
- `make backup-sql` - Backup SQL database only
- `make backup-qdrant` - Backup Qdrant vector database only

#### Setup Script
- `scripts/setup_remote_db.sh` - Interactive setup for remote databases
- Guides users through PostgreSQL, MySQL, and Qdrant configuration
- Updates `.env` file automatically

## Quick Start Guide

### 1. Setup Remote Databases

```bash
# Interactive setup
./scripts/setup_remote_db.sh

# Or manually update .env file
DATABASE_URL=postgresql://user:pass@host:port/db
QDRANT_HOST=your-qdrant-host.com
QDRANT_PORT=6333
```

### 2. Test Configuration

```bash
# Test database connection
make shell
python -c "from app.database import engine; print('Database connection successful')"

# Run migrations
make migrate
```

### 3. Start Application

```bash
# For remote databases
docker compose -f docker-compose.remote.yml up -d

# Or use the original compose file
make up
```

### 4. Setup Backups

```bash
# Test backup system
make backup

# Setup automated backups (add to crontab)
0 2 * * * /path/to/openmemory/scripts/backup_all.sh >> /var/log/openmemory_backup.log 2>&1
```

## Supported Database Configurations

### SQL Databases
- **PostgreSQL**: `postgresql://user:pass@host:port/db`
- **MySQL**: `mysql://user:pass@host:port/db`
- **SQLite**: `sqlite:///./openmemory.db` (default)

### Vector Database (Qdrant)
- **Local**: `QDRANT_HOST=localhost`
- **Remote**: `QDRANT_HOST=your-host.com`
- **Qdrant Cloud**: `QDRANT_HOST=cluster.qdrant.io` + `QDRANT_API_KEY=key`

## Backup Locations

All backups are stored in `/backups/openmemory/` with the following naming:
- SQL databases: `openmemory_[type]_[timestamp].sql.gz`
- Qdrant: `openmemory_qdrant_[timestamp].json.gz`

## Security Considerations

1. **Database Credentials**: Use environment variables, never hardcode
2. **API Keys**: Store Qdrant API keys securely
3. **Backup Encryption**: Consider encrypting backup files
4. **Network Security**: Use SSL/TLS for database connections
5. **Access Control**: Implement proper database user permissions

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify credentials and network connectivity
   - Check database server status
   - Ensure proper URL format

2. **Qdrant Connection Issues**
   - Test with curl: `curl http://host:port/collections`
   - Verify API key for Qdrant Cloud
   - Check firewall settings

3. **Backup Failures**
   - Ensure backup directory is writable
   - Check database user permissions
   - Verify Qdrant collection exists

### Testing Commands

```bash
# Test PostgreSQL
psql "$DATABASE_URL" -c "SELECT 1;"

# Test MySQL
mysql -h host -u user -p database -e "SELECT 1;"

# Test Qdrant
curl "http://$QDRANT_HOST:$QDRANT_PORT/collections"

# Test backup
make backup
```

## Migration Path

### From Local to Remote

1. **Setup remote databases**
2. **Update environment variables**
3. **Run database migrations**
4. **Test connections**
5. **Start application**
6. **Setup automated backups**

### Data Migration

```bash
# Export from local SQLite
sqlite3 openmemory.db .dump > backup.sql

# Import to PostgreSQL
psql "$DATABASE_URL" < backup.sql

# Export from local Qdrant
curl "http://localhost:6333/collections/openmemory/points?limit=10000" > qdrant_export.json
```

## Performance Considerations

1. **Connection Pooling**: Already implemented in SQLAlchemy
2. **Indexing**: Database indexes are created automatically
3. **Monitoring**: Monitor query performance and connection usage
4. **Scaling**: Consider read replicas for heavy workloads

## Documentation

- **Full Guide**: `REMOTE_DATABASE_SETUP.md`
- **Configuration**: `CONFIGURATION.md`
- **Backup Scripts**: `scripts/` directory
- **Examples**: `docker-compose.remote.yml`

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the full documentation
3. Test with the provided scripts
4. Verify environment configuration 
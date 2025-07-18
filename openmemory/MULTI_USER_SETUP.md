# Multi-User OpenMemory Setup Guide

This guide shows you how to set up multiple OpenMemory instances sharing a single PostgreSQL database, with proper user isolation.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ OpenMemory      │    │ OpenMemory      │    │ OpenMemory      │
│ Instance 1      │    │ Instance 2      │    │ Instance 3      │
│ (User A)        │    │ (User B)        │    │ (User C)        │
│ Port: 8765      │    │ Port: 8766      │    │ Port: 8767      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ PostgreSQL      │
                    │ Database        │
                    │ (Shared)        │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Qdrant          │
                    │ Vector Store    │
                    │ (Shared)        │
                    └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose installed
- OpenMemory codebase
- PostgreSQL client (optional, for direct database access)

## Step 1: Update Configuration

### Update API Configuration

Edit `api/config/default.json` to use PostgreSQL:

```json
{
    "database": {
        "url": "postgresql://openmemory:openmemory_password@postgres:5432/openmemory"
    },
    "vector_store": {
        "provider": "qdrant",
        "collection_name": "openmemory_shared",
        "host": "qdrant",
        "port": 6333,
        "embedding_model_dims": 1536
    }
}
```

### Update Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=postgresql://openmemory:openmemory_password@postgres:5432/openmemory

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=openmemory_shared

# User-specific settings
USER_ID=user_a
DEFAULT_APP_ID=user_a_app

# API Settings
API_HOST=0.0.0.0
API_PORT=8765
```

## Step 2: Migrate from SQLite to PostgreSQL

### Option A: Using the Migration Script

1. **Install PostgreSQL dependencies:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Run the migration script:**
   ```bash
   python scripts/migrate_to_postgres.py
   ```

### Option B: Manual Migration

1. **Start PostgreSQL:**
   ```bash
   docker compose -f docker-compose.multi-user.yml up postgres -d
   ```

2. **Create database schema:**
   ```bash
   docker compose exec postgres psql -U openmemory -d openmemory -c "
   CREATE TABLE IF NOT EXISTS users (
       id UUID PRIMARY KEY,
       user_id VARCHAR UNIQUE NOT NULL,
       name VARCHAR,
       email VARCHAR UNIQUE,
       metadata JSONB DEFAULT '{}',
       created_at TIMESTAMP DEFAULT NOW(),
       updated_at TIMESTAMP DEFAULT NOW()
   );
   "
   ```

3. **Run Alembic migrations:**
   ```bash
   docker compose exec openmemory-user-a alembic upgrade head
   ```

## Step 3: Deploy Multi-User Setup

### Start All Services

```bash
# Start the complete multi-user setup
docker compose -f docker-compose.multi-user.yml up -d
```

### Verify Services

```bash
# Check service status
docker compose -f docker-compose.multi-user.yml ps

# Check logs
docker compose -f docker-compose.multi-user.yml logs -f
```

## Step 4: Test User Isolation

### Test Different Users

1. **User A (Port 8765):**
   ```bash
   curl -X POST "http://localhost:8765/api/v1/memories/" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_a", "text": "This is user A memory", "app": "user_a_app"}'
   ```

2. **User B (Port 8766):**
   ```bash
   curl -X POST "http://localhost:8766/api/v1/memories/" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_b", "text": "This is user B memory", "app": "user_b_app"}'
   ```

3. **User C (Port 8767):**
   ```bash
   curl -X POST "http://localhost:8767/api/v1/memories/" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_c", "text": "This is user C memory", "app": "user_c_app"}'
   ```

### Verify Data Isolation

```bash
# Check User A memories
curl "http://localhost:8765/api/v1/memories/?user_id=user_a"

# Check User B memories  
curl "http://localhost:8766/api/v1/memories/?user_id=user_b"

# Check User C memories
curl "http://localhost:8767/api/v1/memories/?user_id=user_c"
```

## Step 5: Database Management

### Access PostgreSQL

```bash
# Connect to PostgreSQL
docker compose -f docker-compose.multi-user.yml exec postgres psql -U openmemory -d openmemory

# List all users
SELECT user_id, name, created_at FROM users;

# List all apps with owners
SELECT a.name as app_name, u.user_id as owner 
FROM apps a 
JOIN users u ON a.owner_id = u.id;

# Count memories per user
SELECT u.user_id, COUNT(m.id) as memory_count
FROM users u
LEFT JOIN memories m ON u.id = m.user_id
GROUP BY u.user_id;
```

### Backup and Restore

```bash
# Backup PostgreSQL
docker compose -f docker-compose.multi-user.yml exec postgres pg_dump -U openmemory openmemory > backup.sql

# Restore PostgreSQL
docker compose -f docker-compose.multi-user.yml exec -T postgres psql -U openmemory openmemory < backup.sql
```

## Step 6: Production Considerations

### Security

1. **Use strong passwords** for PostgreSQL
2. **Enable SSL** for database connections
3. **Use environment variables** for sensitive data
4. **Implement proper authentication** for API access

### Performance

1. **Connection pooling** for database connections
2. **Load balancing** for multiple instances
3. **Monitoring** and alerting
4. **Regular backups**

### Scaling

1. **Horizontal scaling** by adding more instances
2. **Database clustering** for high availability
3. **Caching layer** (Redis) for frequently accessed data
4. **CDN** for static assets

## Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   - Check PostgreSQL is running: `docker compose ps`
   - Verify connection string in configuration
   - Check network connectivity between containers

2. **Migration Issues:**
   - Ensure PostgreSQL is ready before running migrations
   - Check for data type compatibility
   - Verify foreign key constraints

3. **User Isolation Problems:**
   - Verify `user_id` filtering in queries
   - Check permission system configuration
   - Review access control rules

### Debug Commands

```bash
# Check container logs
docker compose -f docker-compose.multi-user.yml logs openmemory-user-a

# Check database connectivity
docker compose -f docker-compose.multi-user.yml exec openmemory-user-a python -c "
from app.database import SessionLocal
db = SessionLocal()
print('Database connection successful')
db.close()
"

# Check Qdrant connectivity
curl http://localhost:6333/collections
```

## Next Steps

1. **Customize user configurations** for your specific needs
2. **Set up monitoring** and logging
3. **Implement authentication** and authorization
4. **Configure backups** and disaster recovery
5. **Set up CI/CD** for automated deployments

## Support

For issues or questions:
- Check the logs: `docker compose logs`
- Review the configuration files
- Test individual components
- Consult the OpenMemory documentation 
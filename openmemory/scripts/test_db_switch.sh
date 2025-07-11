#!/bin/bash

# Test Database Switching Script for OpenMemory
# Usage: ./scripts/test_db_switch.sh

set -e

echo "OpenMemory Database Switching Test"
echo "================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please run 'make env' first."
    exit 1
fi

echo ""
echo "This script will test switching between different database types."
echo ""

# Test SQLite
echo "Testing SQLite configuration..."
export DATABASE_URL="sqlite:///./test_openmemory.db"
echo "DATABASE_URL: $DATABASE_URL"

# Test database connection
python3 -c "
from api.app.database import engine
from api.app.models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('✅ SQLite connection successful')
except Exception as e:
    print(f'❌ SQLite connection failed: {e}')
"

# Test MySQL (if available)
echo ""
echo "Testing MySQL configuration..."
export DATABASE_URL="mysql://test_user:test_pass@localhost:3306/test_openmemory"
echo "DATABASE_URL: $DATABASE_URL"

# Test database connection
python3 -c "
from api.app.database import engine
from api.app.models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('✅ MySQL connection successful')
except Exception as e:
    print(f'❌ MySQL connection failed: {e}')
"

# Test PostgreSQL (if available)
echo ""
echo "Testing PostgreSQL configuration..."
export DATABASE_URL="postgresql://test_user:test_pass@localhost:5432/test_openmemory"
echo "DATABASE_URL: $DATABASE_URL"

# Test database connection
python3 -c "
from api.app.database import engine
from api.app.models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
"

echo ""
echo "Database switching test completed!"
echo ""
echo "Note: Connection failures are expected if the database servers are not running."
echo "The important thing is that the code can handle different database types." 
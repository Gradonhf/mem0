#!/bin/bash

# Remote Database Setup Script for OpenMemory
# Usage: ./scripts/setup_remote_db.sh

set -e

echo "OpenMemory Remote Database Setup"
echo "================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please run 'make env' first."
    exit 1
fi

echo ""
echo "This script will help you configure OpenMemory to use remote databases."
echo ""

# Database type selection
echo "Select your SQL database type:"
echo "1) PostgreSQL (Recommended for production)"
echo "2) MySQL"
echo "3) Keep SQLite (local)"
read -p "Enter your choice (1-3): " db_choice

case $db_choice in
    1)
        echo ""
        echo "PostgreSQL Configuration"
        echo "======================="
        read -p "Enter PostgreSQL host: " pg_host
        read -p "Enter PostgreSQL port (default: 5432): " pg_port
        pg_port=${pg_port:-5432}
        read -p "Enter database name: " pg_db
        read -p "Enter username: " pg_user
        read -s -p "Enter password: " pg_pass
        echo ""
        
        DATABASE_URL="postgresql://${pg_user}:${pg_pass}@${pg_host}:${pg_port}/${pg_db}"
        ;;
    2)
        echo ""
        echo "MySQL Configuration"
        echo "=================="
        read -p "Enter MySQL host: " mysql_host
        read -p "Enter MySQL port (default: 3306): " mysql_port
        mysql_port=${mysql_port:-3306}
        read -p "Enter database name: " mysql_db
        read -p "Enter username: " mysql_user
        read -s -p "Enter password: " mysql_pass
        echo ""
        
        DATABASE_URL="mysql://${mysql_user}:${mysql_pass}@${mysql_host}:${mysql_port}/${mysql_db}"
        ;;
    3)
        echo "Keeping SQLite configuration..."
        DATABASE_URL="sqlite:///./openmemory.db"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Qdrant configuration
echo ""
echo "Qdrant Vector Database Configuration"
echo "==================================="
read -p "Enter Qdrant host (default: localhost): " qdrant_host
qdrant_host=${qdrant_host:-localhost}
read -p "Enter Qdrant port (default: 6333): " qdrant_port
qdrant_port=${qdrant_port:-6333}

read -p "Are you using Qdrant Cloud? (y/n): " use_qdrant_cloud
if [[ $use_qdrant_cloud =~ ^[Yy]$ ]]; then
    read -p "Enter Qdrant API key: " qdrant_api_key
    echo "QDRANT_API_KEY=${qdrant_api_key}" >> .env
fi

# Update .env file
echo ""
echo "Updating .env file..."

# Remove existing database and Qdrant configurations
sed -i '/^DATABASE_URL=/d' .env
sed -i '/^QDRANT_HOST=/d' .env
sed -i '/^QDRANT_PORT=/d' .env

# Add new configurations
echo "DATABASE_URL=${DATABASE_URL}" >> .env
echo "QDRANT_HOST=${qdrant_host}" >> .env
echo "QDRANT_PORT=${qdrant_port}" >> .env

echo ""
echo "Configuration updated successfully!"
echo ""
echo "Next steps:"
echo "1. Test your database connection:"
echo "   make shell"
echo "   python -c \"from app.database import engine; print('Database connection successful')\""
echo ""
echo "2. Run database migrations:"
echo "   make migrate"
echo ""
echo "3. Start the application:"
echo "   make up"
echo ""
echo "4. Test backups:"
echo "   make backup"
echo ""
echo "Configuration Summary:"
echo "====================="
echo "Database URL: ${DATABASE_URL}"
echo "Qdrant Host: ${qdrant_host}:${qdrant_port}"
if [[ $use_qdrant_cloud =~ ^[Yy]$ ]]; then
    echo "Qdrant Cloud: Yes (API key configured)"
fi 
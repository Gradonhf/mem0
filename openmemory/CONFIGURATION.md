# OpenMemory Configuration Guide

This document describes the new centralized configuration system for OpenMemory.

## Overview

OpenMemory now uses a unified configuration system that:
- Centralizes all configuration in JSON files
- Supports environment-specific overrides
- Allows environment variable overrides
- Provides sensible defaults
- Validates required configuration

## Configuration Sources (in order of precedence)

1. **Environment Variables** (highest priority)
2. **Environment-specific JSON files** (development.json, docker.json)
3. **Default JSON configuration** (default.json)
4. **Hardcoded defaults** (lowest priority)

## Quick Start

### Minimal Configuration
Only one setting is required:

```bash
export OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Using .env File
```bash
# Copy the example
cp env.example .env

# Edit with your settings
nano .env
```

## Configuration Files

### Default Configuration (`config/default.json`)
Contains all default settings for the application:

```json
{
  "app": {
    "name": "OpenMemory",
    "version": "1.0.0",
    "environment": "production"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8765,
    "workers": 4,
    "reload": false
  },
  "ui": {
    "port": 3000,
    "api_url": "http://localhost:8765"
  },
  "database": {
    "url": "sqlite:///./openmemory.db",
    "type": "sqlite"
  },
  "vector_store": {
    "provider": "qdrant",
    "host": "mem0_store",
    "port": 6333,
    "collection_name": "openmemory",
    "embedding_model_dims": 1536
  },
  "llm": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 2000,
    "api_key_env": "OPENAI_API_KEY"
  },
  "embedder": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "api_key_env": "OPENAI_API_KEY"
  },
  "user": {
    "default_id": "default_user",
    "default_app": "openmemory"
  }
}
```

### Environment-Specific Configurations

#### Development (`config/development.json`)
```json
{
  "app": {
    "environment": "development"
  },
  "api": {
    "reload": true,
    "workers": 1
  },
  "database": {
    "url": "sqlite:///./openmemory_dev.db"
  },
  "vector_store": {
    "host": "localhost"
  }
}
```

#### Docker (`config/docker.json`)
```json
{
  "app": {
    "environment": "docker"
  },
  "api": {
    "host": "0.0.0.0",
    "reload": false,
    "workers": 4
  },
  "vector_store": {
    "host": "mem0_store"
  },
  "ui": {
    "api_url": "http://openmemory-mcp:8765"
  }
}
```

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Variables

#### Application
- `ENVIRONMENT`: Environment name (development, docker, production)
- `USER_ID`: User identifier (defaults to system username)

#### API Configuration
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8765)
- `API_WORKERS`: Number of API workers (default: 4)

#### Database
- `DATABASE_URL`: Database connection string (default: sqlite:///./openmemory.db)

#### Vector Store (Qdrant)
- `QDRANT_HOST`: Qdrant host (default: mem0_store)
- `QDRANT_PORT`: Qdrant port (default: 6333)

#### LLM Configuration
- `LLM_MODEL`: LLM model name (default: gpt-4o-mini)
- `LLM_TEMPERATURE`: LLM temperature (default: 0.1)
- `LLM_MAX_TOKENS`: Maximum tokens (default: 2000)

#### Embedder Configuration
- `EMBEDDER_MODEL`: Embedder model name (default: text-embedding-3-small)

#### UI Configuration
- `NEXT_PUBLIC_API_URL`: API URL for frontend (default: http://localhost:8765)
- `NEXT_PUBLIC_USER_ID`: User ID for frontend (defaults to USER_ID)
- `NODE_ENV`: Node.js environment (default: production)

## Usage Examples

### Development Setup
```bash
export ENVIRONMENT=development
export OPENAI_API_KEY=sk-your-key
export USER_ID=developer
./start.sh
```

### Production Setup
```bash
export ENVIRONMENT=production
export OPENAI_API_KEY=sk-your-key
export USER_ID=production_user
export API_WORKERS=8
./start.sh
```

### Docker Compose with Custom Configuration
```yaml
services:
  openmemory-mcp:
    environment:
      - ENVIRONMENT=docker
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - USER_ID=${USER_ID}
      - API_WORKERS=4
      - QDRANT_HOST=mem0_store
```

## Configuration Validation

The system validates that all required configuration is present:
- Database URL
- LLM provider
- Embedder provider
- User ID

If validation fails, the application will show a clear error message.

## Migration from Old Configuration

### Old API Configuration
**Before:**
```python
# Hardcoded in Dockerfile
ENV API_KEY=sk-xxx

# Multiple config files
config.json
default_config.json
```

**After:**
```python
# Environment variable
export OPENAI_API_KEY=sk-xxx

# Single configuration system
config_manager.load_config()
```

### Old UI Configuration
**Before:**
```bash
# Entrypoint script
entrypoint.sh

# Multiple environment files
ui/.env
api/.env
```

**After:**
```bash
# Direct CMD in Dockerfile
CMD ["node", "server.js"]

# Single .env file
.env
```

## Troubleshooting

### Configuration Not Loading
1. Check that the `config/` directory exists
2. Verify JSON syntax in configuration files
3. Ensure environment variables are set correctly

### Environment Variables Not Working
1. Check that variables are exported in your shell
2. Verify variable names match exactly
3. Restart the application after changing variables

### Database Connection Issues
1. Verify `DATABASE_URL` is set correctly
2. Check file permissions for SQLite databases
3. Ensure database directory is writable

### Vector Store Connection Issues
1. Verify `QDRANT_HOST` and `QDRANT_PORT` are correct
2. Check that Qdrant service is running
3. Ensure network connectivity between services 
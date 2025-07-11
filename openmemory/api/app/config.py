import os
from app.config_manager import config_manager

# Load configuration based on environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
config = config_manager.load_config(ENVIRONMENT)

# Extract commonly used values
USER_ID = config["user"]["default_id"]
DEFAULT_APP_ID = config["user"]["default_app"]

# API configuration
API_HOST = config["api"]["host"]
API_PORT = config["api"]["port"]
API_WORKERS = config["api"]["workers"]
API_RELOAD = config["api"]["reload"]

# Database configuration
DATABASE_URL = config["database"]["url"]

# Vector store configuration
QDRANT_HOST = config["vector_store"]["host"]
QDRANT_PORT = config["vector_store"]["port"]
QDRANT_COLLECTION = config["vector_store"]["collection_name"]

# LLM configuration
LLM_PROVIDER = config["llm"]["provider"]
LLM_MODEL = config["llm"]["model"]
LLM_TEMPERATURE = config["llm"]["temperature"]
LLM_MAX_TOKENS = config["llm"]["max_tokens"]

# Embedder configuration
EMBEDDER_PROVIDER = config["embedder"]["provider"]
EMBEDDER_MODEL = config["embedder"]["model"]
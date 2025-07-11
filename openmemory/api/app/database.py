import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# load .env file (make sure you have DATABASE_URL set)
load_dotenv()

# Use centralized configuration
from app.config import DATABASE_URL

# Determine database type and set appropriate connect_args
def get_connect_args(database_url):
    """Get appropriate connect_args based on database type."""
    parsed_url = urlparse(database_url)
    
    if parsed_url.scheme == 'sqlite':
        return {"check_same_thread": False}  # Needed for SQLite
    elif parsed_url.scheme in ['postgresql', 'postgres']:
        return {}  # PostgreSQL doesn't need special args
    elif parsed_url.scheme == 'mysql':
        return {}  # MySQL doesn't need special args
    else:
        return {}  # Default for other databases

# SQLAlchemy engine & session
engine = create_engine(
    DATABASE_URL,
    connect_args=get_connect_args(DATABASE_URL)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

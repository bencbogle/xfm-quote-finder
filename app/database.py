"""
PostgreSQL database configuration and connection management.
Optimized for production deployment with connection pooling.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with connection pooling for production
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Additional connections when pool is exhausted
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_database():
    """Initialize PostgreSQL database tables and indexes."""
    with get_db_session() as session:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        # PostgreSQL schema
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS quotes (
                id SERIAL PRIMARY KEY,
                episode_id VARCHAR(50) NOT NULL,
                timestamp_sec INTEGER NOT NULL,
                speaker VARCHAR(200) NOT NULL,
                text TEXT NOT NULL,
                episode_name TEXT,
                spotify_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # PostgreSQL indexes
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_quotes_speaker 
            ON quotes(speaker);
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_quotes_episode_timestamp 
            ON quotes(episode_id, timestamp_sec);
        """))
        
        # PostgreSQL full-text search index
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_quotes_text_gin 
            ON quotes USING gin(to_tsvector('english', text));
        """))
        
        # Search log table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS search_log (
                id SERIAL PRIMARY KEY,
                ts INTEGER NOT NULL,
                query TEXT NOT NULL,
                topk INTEGER NOT NULL,
                ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Search analytics index
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_search_log_ts 
            ON search_log(ts);
        """))
        
        # Visitors tracking table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS visitors (
                id SERIAL PRIMARY KEY,
                ip VARCHAR(45) NOT NULL,
                user_agent TEXT,
                path VARCHAR(500),
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Visitors analytics indexes
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_visitors_ip 
            ON visitors(ip);
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_visitors_visited_at 
            ON visitors(visited_at);
        """))

def get_connection():
    """Get a raw database connection for complex queries."""
    return engine.connect()

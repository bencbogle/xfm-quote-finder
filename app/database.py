"""
PostgreSQL database configuration and connection management.
Optimized for production deployment with connection pooling.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to SQLite for local development
    DATABASE_URL = "sqlite:///./out/quotes.db"
    print("Warning: DATABASE_URL not set, using SQLite fallback")

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
    """Initialize database tables and indexes."""
    is_postgres = "postgresql" in DATABASE_URL.lower()
    
    with get_db_session() as session:
        if is_postgres:
            # PostgreSQL schema
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY,
                    episode_id VARCHAR(50) NOT NULL,
                    timestamp_sec INTEGER NOT NULL,
                    speaker VARCHAR(100) NOT NULL,
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
            
        else:
            # SQLite schema
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id TEXT NOT NULL,
                    timestamp_sec INTEGER NOT NULL,
                    speaker TEXT NOT NULL,
                    text TEXT NOT NULL,
                    episode_name TEXT,
                    spotify_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # SQLite indexes
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_quotes_speaker 
                ON quotes(speaker);
            """))
            
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_quotes_episode_timestamp 
                ON quotes(episode_id, timestamp_sec);
            """))
            
            # SQLite FTS5 virtual table
            session.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS quotes_fts USING fts5(
                    text, content='quotes', content_rowid='id'
                );
            """))
            
            # Search log table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS search_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts INTEGER NOT NULL,
                    query TEXT NOT NULL,
                    topk INTEGER NOT NULL,
                    ip TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
        
        # Common index for search analytics
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_search_log_ts 
            ON search_log(ts);
        """))

def get_connection():
    """Get a raw database connection for complex queries."""
    return engine.connect()

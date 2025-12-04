from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config

# Create engine
engine = create_engine(
    Config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Thread-safe session
Session = scoped_session(SessionLocal)

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database and create all tables"""
    try:
        from models import user, identifier, log
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def get_db():
    """Get database session"""
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    try:
        db = Session()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# Test on import
if __name__ != "__main__":
    test_connection()



# Third party imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import load_settings

settings = load_settings()
engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_db():
    """Create a database session.
    Yields:
        Session: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

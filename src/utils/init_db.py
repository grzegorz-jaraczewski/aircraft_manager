# Internal imports
from src.config.database import engine
from src.models import Base


def create_tables():
    """Creates all tables in the database."""
    Base.metadata.create_all(bind=engine)

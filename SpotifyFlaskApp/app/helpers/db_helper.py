# app/helpers/db_helper.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configs import Config

# Create engine and session
engine = create_engine(
    f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_URL}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}",
    pool_pre_ping=True,  # Ensures connections are checked before use
    pool_recycle=3600  # Recycle connections every hour to prevent stale connections
)
Session = sessionmaker(bind=engine)


def get_db_session():
    """
    Provides a transactional scope around a series of operations.
    """
    session = Session()
    try:
        yield session
    finally:
        session.close()

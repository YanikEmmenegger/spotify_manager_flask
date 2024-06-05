from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configs.config import Config

# Create engine and session
engine = create_engine(
    f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_URL}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}")
Session = sessionmaker(bind=engine)


def get_db_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()

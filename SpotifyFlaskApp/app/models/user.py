from sqlalchemy import Column, String, Boolean, Text, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    spotify_uuid = Column(String, primary_key=True, index=True)
    name = Column(String)
    active = Column(Boolean)
    spotify_key = Column(Text)
    uuid = Column(UUID, default=uuid.uuid4)

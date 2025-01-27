from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# Handle special Postgres URL format from Supabase
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Artist(Base):
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    bio = Column(String)
    genres = Column(String)
    social_media = relationship("SocialMedia", back_populates="artist", cascade="all, delete-orphan")
    platform_links = relationship("PlatformLink", back_populates="artist", cascade="all, delete-orphan")

class SocialMedia(Base):
    __tablename__ = 'social_media'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'))
    platform = Column(String)
    handle = Column(String)
    artist = relationship("Artist", back_populates="social_media")

class PlatformLink(Base):
    __tablename__ = 'platform_links'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, ForeignKey('artists.id'))
    platform = Column(String)
    url = Column(String)
    artist = relationship("Artist", back_populates="platform_links")

# Create tables
def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db() 
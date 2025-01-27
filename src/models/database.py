from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os

# Use environment variable for database URL in production
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/music_chat.db')

# SQLite for local development, PostgreSQL for production
if DATABASE_URL.startswith("sqlite"):
    DB_DIR = os.path.join(os.getcwd(), 'data')
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.join(DB_DIR, 'music_chat.db')
    DATABASE_URL = f"sqlite:///{DB_PATH}"

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
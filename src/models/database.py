from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
import os

# Use SQLite for simplicity
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./data.db')

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

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

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db()) 
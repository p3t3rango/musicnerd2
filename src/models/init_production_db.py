from database import init_db, Base, Artist, SocialMedia, PlatformLink
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def seed_production_database():
    """Populate production database with initial artist data"""
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Sample Artists data
        artists_data = [
            {
                "name": "Latasha",
                "bio": "LATASHA is a pioneering artist in the web3 music space.",
                "genres": "hip-hop,rap,web3",
                "socials": [
                    {"platform": "twitter", "handle": "latasha"}
                ],
                "links": [
                    {"platform": "spotify", "url": "https://open.spotify.com/artist/latasha"}
                ]
            }
            # Add other artists here
        ]
        
        for artist_data in artists_data:
            # Check if artist already exists
            existing = session.query(Artist).filter_by(name=artist_data["name"]).first()
            if existing:
                continue
                
            artist = Artist(
                name=artist_data["name"],
                bio=artist_data["bio"],
                genres=artist_data["genres"]
            )
            session.add(artist)
            
            # Add social media links
            for social in artist_data["socials"]:
                social_media = SocialMedia(
                    artist=artist,
                    platform=social["platform"],
                    handle=social["handle"]
                )
                session.add(social_media)
            
            # Add platform links
            for link in artist_data["links"]:
                platform_link = PlatformLink(
                    artist=artist,
                    platform=link["platform"],
                    url=link["url"]
                )
                session.add(platform_link)
        
        session.commit()
        print("Production database seeded successfully!")

if __name__ == "__main__":
    seed_production_database() 
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models.database import DB_PATH, Artist

def check_database():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        artists = session.query(Artist).all()
        for artist in artists:
            print(f"\nArtist: {artist.name}")
            print(f"Bio: {artist.bio}")
            print(f"Genres: {artist.genres}")
            print("\nSocial Media:")
            for social in artist.social_media:
                print(f"- {social.platform}: {social.handle}")
            print("\nPlatform Links:")
            for link in artist.platform_links:
                print(f"- {link.platform}: {link.url}")
            print("-" * 50)

if __name__ == "__main__":
    check_database() 
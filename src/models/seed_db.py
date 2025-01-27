from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models.database import Base, Artist, SocialMedia, PlatformLink, DATABASE_URL

def seed_database():
    """Populate database with sample artist data"""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        # Sample Artists data
        artists_data = [
            {
                "name": "Disclosure",
                "bio": "British electronic music duo consisting of brothers Howard and Guy Lawrence.",
                "genres": "house,uk garage,electronic",
                "socials": [
                    {"platform": "instagram", "handle": "disclosure"},
                    {"platform": "twitter", "handle": "disclosure"}
                ],
                "links": [
                    {"platform": "spotify", "url": "https://open.spotify.com/artist/6nS5roXSAGhTGr34W6n7Et"},
                    {"platform": "soundcloud", "url": "https://soundcloud.com/disclosure"}
                ]
            },
            {
                "name": "Bicep",
                "bio": "Belfast-born, London-based duo Matt McBriar and Andy Ferguson.",
                "genres": "electronic,techno,house",
                "socials": [
                    {"platform": "instagram", "handle": "bicepmusic"},
                    {"platform": "twitter", "handle": "bicepmusic"}
                ],
                "links": [
                    {"platform": "spotify", "url": "https://open.spotify.com/artist/73A3bLnfnz5BoQjb4gNCga"},
                    {"platform": "soundcloud", "url": "https://soundcloud.com/bicepmusic"}
                ]
            },
            {
                "name": "Fred Again",
                "bio": "Frederick John Philip Gibson, known professionally as Fred Again, is a British singer, songwriter, multi-instrumentalist, record producer and remixer.",
                "genres": "electronic,house,ambient",
                "socials": [
                    {"platform": "instagram", "handle": "fredagainagainagainagainagain"}
                ],
                "links": [
                    {"platform": "spotify", "url": "https://open.spotify.com/artist/4oLeXFyACqeem2VImYeBFe"}
                ]
            },
            {
                "name": "Latasha",
                "bio": "LATASHA is a pioneering artist in the web3 music space, known for her innovative approach to hip-hop and digital art.",
                "genres": "hip-hop,rap,web3",
                "socials": [
                    {"platform": "instagram", "handle": "latasha"},
                    {"platform": "twitter", "handle": "latasha"}
                ],
                "links": [
                    {"platform": "spotify", "url": "https://open.spotify.com/artist/latasha"},
                    {"platform": "soundcloud", "url": "https://soundcloud.com/latasha"}
                ]
            }
        ]

        # Add or update artists
        for artist_data in artists_data:
            # Check if artist exists
            artist = session.query(Artist).filter_by(name=artist_data["name"]).first()
            
            if not artist:
                # Create new artist if doesn't exist
                artist = Artist(
                    name=artist_data["name"],
                    bio=artist_data["bio"],
                    genres=artist_data["genres"]
                )
                session.add(artist)
                session.flush()  # To get the artist ID
            
            # Clear existing social media and links
            session.query(SocialMedia).filter_by(artist_id=artist.id).delete()
            session.query(PlatformLink).filter_by(artist_id=artist.id).delete()
            
            # Add social media
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
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 
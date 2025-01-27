from sqlalchemy import create_engine
from src.models.database import Base, DB_PATH

def init_database():
    """Initialize the database and create tables"""
    db_url = f"sqlite:///{DB_PATH}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    print(f"Database initialized successfully at {DB_PATH}!")

if __name__ == "__main__":
    init_database() 
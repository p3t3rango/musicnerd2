from .web_scraper import MusicNerdScraper
from .cache import Cache
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicNerdAPI:
    def __init__(self):
        self.scraper = MusicNerdScraper()
        self.cache = Cache()
        
    def get_artist_info(self, artist_name: str) -> Optional[Dict]:
        """
        Get artist information with caching
        """
        logger.info(f"Fetching info for artist: {artist_name}")
        
        # Check cache first
        cached_info = self.cache.get(artist_name)
        if cached_info:
            logger.info(f"Found cached info for {artist_name}")
            return cached_info
            
        # If not in cache, scrape and store
        logger.info(f"Attempting to scrape info for {artist_name}")
        info = self.scraper.scrape_artist(artist_name)
        if info:
            logger.info(f"Successfully scraped info for {artist_name}")
            self.cache.set(artist_name, info)
        else:
            logger.warning(f"Failed to scrape info for {artist_name}")
        return info 
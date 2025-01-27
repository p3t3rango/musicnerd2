from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
from langchain.tools import Tool
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import time
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.last_request_time = None
        self.min_interval = 60.0 / requests_per_minute  # seconds between requests
        
    def wait_if_needed(self):
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

class MusicNerdScraper:
    def __init__(self):
        self.base_url = "https://www.musicnerd.xyz"
        self.known_artist_ids = {
            "latasha": "3cd4c3e4-4bf4-4b92-9b72-07f9188bd4c6"
            # We can add more as we discover them
        }
        self.embeddings = HuggingFaceEmbeddings()
        self.llm = Ollama(model="deepseek-r1")
        self.db = None
        self.rate_limiter = RateLimiter(requests_per_minute=10)
        self.last_scrape_times = {}
        
    def should_rescrape(self, artist_name: str) -> bool:
        """Check if we should rescrape this artist based on time elapsed"""
        if artist_name not in self.last_scrape_times:
            return True
        
        last_scrape = self.last_scrape_times[artist_name]
        time_elapsed = datetime.now() - last_scrape
        return time_elapsed > timedelta(hours=24)  # Rescrape after 24 hours
        
    def test_website_access(self):
        """Test which URL structure works"""
        for url in self.base_urls:
            try:
                logger.info(f"Testing access to: {url}")
                response = requests.get(url, 
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; MusicNerdBot/1.0)'},
                    timeout=5
                )
                logger.info(f"Response status: {response.status_code}")
                if response.status_code == 200:
                    logger.info(f"Successfully accessed: {url}")
                    logger.info(f"Page title: {BeautifulSoup(response.text, 'html.parser').title}")
                    return url
            except Exception as e:
                logger.error(f"Error accessing {url}: {str(e)}")
        return None

    def scrape_artist(self, artist_name: str) -> Optional[Dict]:
        """
        Scrape and process artist information using UUID if known
        """
        try:
            logger.info(f"Attempting to scrape info for: {artist_name}")
            
            # Check if we have a known UUID for this artist
            artist_id = self.known_artist_ids.get(artist_name.lower())
            if artist_id:
                url = f"{self.base_url}/artist/{artist_id}"
            else:
                logger.info(f"No known UUID for {artist_name}")
                return None

            logger.info(f"Accessing URL: {url}")
            response = requests.get(url, 
                headers={'User-Agent': 'Mozilla/5.0 (compatible; MusicNerdBot/1.0)'},
                timeout=5
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract all text content
                text_content = soup.get_text()
                
                # Extract all relevant information
                info = {
                    "name": artist_name,
                    "url": url,
                    "raw_content": text_content,  # Include the raw content for LLM analysis
                    "social_links": {},
                    "platform_links": {},
                    "releases": [],
                    "bio": "",
                    "page_content": text_content[:1000]  # First 1000 chars for context
                }
                
                # Extract all links
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    text = link.text.strip()
                    
                    if href:
                        if any(platform in href.lower() for platform in ['instagram', 'twitter']):
                            info["social_links"][text] = href
                        elif any(platform in href.lower() for platform in ['spotify', 'soundcloud']):
                            info["platform_links"][text] = href
                
                logger.info(f"Successfully scraped information for {artist_name}")
                return info
            else:
                logger.error(f"Failed to access {url}")
                return None

        except Exception as e:
            logger.error(f"Error scraping artist {artist_name}: {str(e)}")
            return None 
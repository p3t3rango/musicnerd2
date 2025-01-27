from services.web_scraper import MusicNerdScraper
import asyncio
import json

async def test_scraping():
    scraper = MusicNerdScraper()
    
    # Test specific artist with known UUID
    artist = "latasha"
    print(f"\nTesting scraping for {artist}...")
    result = scraper.scrape_artist(artist)
    
    if result:
        print("\nFound information:")
        print(json.dumps(result, indent=2))  # Pretty print the JSON
        
        # Save to a file for inspection
        with open(f"data/cache/{artist}_info.json", 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved detailed information to data/cache/{artist}_info.json")
    else:
        print(f"\nNo information found for {artist}")

if __name__ == "__main__":
    asyncio.run(test_scraping()) 
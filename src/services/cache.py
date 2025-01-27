from typing import Dict, Optional
import json
import os
from datetime import datetime, timedelta

class Cache:
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Dict]:
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if not os.path.exists(cache_file):
                return None
                
            # Check if cache is older than specified hours
            if datetime.fromtimestamp(os.path.getmtime(cache_file)) < datetime.now() - timedelta(hours=max_age_hours):
                return None
                
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return None
            
    def set(self, key: str, value: Dict):
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            with open(cache_file, 'w') as f:
                json.dump(value, f)
        except:
            pass 
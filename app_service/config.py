import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
    SCRAPER_SERVICE_URL: str = os.getenv("SCRAPER_SERVICE_URL", "http://localhost:8003")
    
settings = Settings()
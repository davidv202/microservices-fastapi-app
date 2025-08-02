import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
    
settings = Settings()
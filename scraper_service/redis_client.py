import redis
import json
from datetime import timedelta
from typing import Optional, Dict, Any
from config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

def cache_company_data(idno: str, company_data: Dict[str, Any], expire_hours: int = 24):
    try:
        # Convert datetime objects to strings for JSON serialization
        serializable_data = {}
        for key, value in company_data.items():
            if hasattr(value, 'isoformat'):
                serializable_data[key] = value.isoformat()
            else:
                serializable_data[key] = value
        
        redis_client.setex(
            f"company:{idno}",
            timedelta(hours=expire_hours),
            json.dumps(serializable_data, default=str)
        )
    except Exception as e:
        print(f"Error caching data for IDNO {idno}: {str(e)}")

def get_cached_company_data(idno: str) -> Optional[Dict[str, Any]]:
    try:
        cached_data = redis_client.get(f"company:{idno}")
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"Error retrieving cached data for IDNO {idno}: {str(e)}")
        return None

def invalidate_company_cache(idno: str):
    try:
        redis_client.delete(f"company:{idno}")
    except Exception as e:
        print(f"Error invalidating cache for IDNO {idno}: {str(e)}")

def cache_scraping_status(idno: str, status: str, expire_minutes: int = 30):
    try:
        redis_client.setex(
            f"scraping_status:{idno}",
            timedelta(minutes=expire_minutes),
            status
        )
    except Exception as e:
        print(f"Error caching scraping status for IDNO {idno}: {str(e)}")

def get_scraping_status(idno: str) -> Optional[str]:
    try:
        return redis_client.get(f"scraping_status:{idno}")
    except Exception as e:
        print(f"Error retrieving scraping status for IDNO {idno}: {str(e)}")
        return None
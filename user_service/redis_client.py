import redis
import json
from datetime import datetime, timedelta, timezone
from config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

def cache_token(token: str, user_data: dict, expire_minutes: int = 30):

    redis_client.setex(
        f"token:{token}", 
        timedelta(minutes=expire_minutes), 
        json.dumps(user_data)
    )

def get_cached_token(token: str):

    cached_data = redis_client.get(f"token:{token}")
    if cached_data:
        return json.loads(cached_data)
    return None

def invalidate_token(token: str):

    redis_client.delete(f"token:{token}")

def cache_user_session(user_id: int, username: str, token: str):

    session_data = {
        "user_id": user_id,
        "username": username,
        "token": token,
        "login_time": json.dumps(datetime.now(timezone.utc), default=str)
    }
    
    cache_token(token, session_data, expire_minutes=30)

    redis_client.setex(
        f"user_session:{user_id}",
        timedelta(minutes=30),
        token
    )

def get_user_active_session(user_id: int):

    return redis_client.get(f"user_session:{user_id}")

def invalidate_user_session(user_id: int):

    token = get_user_active_session(user_id)
    if token:
        invalidate_token(token)
    
    redis_client.delete(f"user_session:{user_id}")
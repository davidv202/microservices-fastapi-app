from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException

from models import User
from schemas import UserRegister
from auth import get_password_hash, verify_password, create_access_token, verify_token
from redis_client import *

def register_user(user_data: UserRegister, db: Session):

    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User registered successfully", "user_id": db_user.id}

def authenticate_user(username: str, password: str, db: Session):

    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    
    cache_user_session(user.id, user.username, access_token)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

def verify_user_session(token: str):

    cached_user = get_cached_token(token)
    if not cached_user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {
        "valid": True,
        "username": cached_user["username"],
        "user_id": cached_user["user_id"]
    }

def logout_user(token: str):

    cached_user = get_cached_token(token)
    if cached_user:
        user_id = cached_user.get("user_id")
        invalidate_user_session(user_id)
        return {"message": "Logout successfully"}
    
    return {"message": "Session not found"}

def get_user_info(user_id: int, db: Session):

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

def get_current_user_info(token: str, db: Session):

    session_info = verify_user_session(token)
    return get_user_info(session_info["user_id"], db)

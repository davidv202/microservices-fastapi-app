from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import Base, engine
from database import get_db
from schemas import UserRegister, Token, UserResponse
from services import *

app = FastAPI(title="User Service", version="1.0.0")

Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/")
def health_check():
    return {"service": "User Service", "status": "running"}

@app.post("/register/")
def register(user: UserRegister, db: Session = Depends(get_db)):
    return register_user(user, db)

@app.post("/login", response_model=Token)
@app.post("/login/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    result = authenticate_user(form_data.username, form_data.password, db)
    return result

@app.get("/verify-token/")
def verify_token(token: str = Depends(oauth2_scheme)):
    return verify_user_session(token)

@app.post("/logout/")
def logout(token: str = Depends(oauth2_scheme)):
    return logout_user(token)

@app.get("/users/me/", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    session_info = verify_user_session(token)
    user = get_user_info(session_info["user_id"], db)
    return user

@app.get("/users/{user_id}/", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return get_user_info(user_id, db)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from config import settings

app = FastAPI(title="Gateway Service", version="1.0.0")

oauth2_scheme = HTTPBearer(auto_error=False)

@app.get("/")
def health_check():
    return {"service": "Gateway Service", "status": "running"}

# Auth endpoints - forward to user_service
@app.post("/auth/register")
async def register(user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.USER_SERVICE_URL}/register/", json=user_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

@app.post("/auth/login")
async def login(login_data: dict):
    async with httpx.AsyncClient() as client:
        form_data = {"username": login_data["username"], "password": login_data["password"]}
        response = await client.post(f"{settings.USER_SERVICE_URL}/login/", data=form_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Token required")
    
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.USER_SERVICE_URL}/logout/", headers={"Authorization": f"Bearer {token}"})
        return response.json()

@app.get("/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.USER_SERVICE_URL}/users/me/", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

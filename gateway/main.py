from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from config import settings

app = FastAPI(title="Gateway Service", version="1.0.0")

oauth2_scheme = HTTPBearer(auto_error=False)

@app.get("/")
def health_check():
    return {"service": "Gateway Service", "status": "running"}

# Auth endpoints - forward to app_service
@app.post("/auth/register/")
async def register(user_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.APP_SERVICE_URL}/auth/register/", json=user_data)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            return response.json()
    except httpx.RequestError:
       raise HTTPException(status_code=503, detail="App service unavailable")
    except Exception:
       raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/login/")
async def login(login_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.APP_SERVICE_URL}/auth/login/", json=login_data)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            return response.json()
    except httpx.RequestError:
       raise HTTPException(status_code=503, detail="App service unavailable")
    except Exception:
       raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/logout/")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        token = credentials.credentials
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.APP_SERVICE_URL}/auth/logout/", headers={"Authorization": f"Bearer {token}"})
            
            if response.status_code == 200:
                return {"message": "Logout successful"}
            else:
                raise HTTPException(status_code=response.status_code, detail="Logout failed")
    except httpx.RequestError:
       raise HTTPException(status_code=503, detail="App service unavailable")
    except Exception:
       raise HTTPException(status_code=500, detail="Internal server error")
        
@app.get("/auth/me/")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        token = credentials.credentials
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.APP_SERVICE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            return response.json()
    except httpx.RequestError:
       raise HTTPException(status_code=503, detail="App service unavailable")
    except Exception:
       raise HTTPException(status_code=500, detail="Internal server error")

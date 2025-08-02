from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from config import settings

app = FastAPI(title="App Service", version="1.0.0")

oauth2_scheme = HTTPBearer(auto_error=False)

@app.get("/")
def health_check():
    return {"service": "App Service", "status": "running"}

async def verify_token_with_user_service(token: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/verify-token/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="User service unavailable")

# Endpoints forwarded to user_service
@app.post("/auth/register/")
async def register_user(user_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/register/",
                json=user_data
                )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            
            return response.json()            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="User service unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")
        
@app.post("/auth/login/")
async def login_user(login_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            form_data = {
                "username": login_data["username"],
                "password": login_data["password"]
            }
            
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/login/", 
                data=form_data
                )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="User service unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")
    
@app.post("/auth/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Token required")
    
    try:
        token = credentials.credentials
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/logout/",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
 
            return response.json()
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="User service unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")
    
@app.get("/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        token = credentials.credentials
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.USER_SERVICE_URL}/users/me/",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            
            return response.json()
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="User service unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")
    
# Endpoints forwarded to scraper_service
@app.post("/scrape/")
async def scrape_company(
    scrape_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        token = credentials.credentials
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.SCRAPER_SERVICE_URL}/scrape/",
                json=scrape_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
            
            return response.json()
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Scraper service unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

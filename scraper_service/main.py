from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from schemas import ScrapeRequest, ScrapeResponse, CompanyData
from services import scrape_company_data, get_cached_result

app = FastAPI(title="Scraper Service", version="1.0.0")

Base.metadata.create_all(bind=engine)

oauth2_scheme = HTTPBearer(auto_error=False)

@app.get("/")
def health_check():
    return {"service": "Scraper Service", "status": "running"}

@app.post("/scrape/", response_model=ScrapeResponse)
async def scrape_company(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """
    Scrape company data by IDNO
    Authentication is handled by app_service before reaching here
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check cache first
    cached_result = get_cached_result(request.idno)
    if cached_result and not request.force_refresh:
        return ScrapeResponse(
            success=True,
            message="Data retrieved from cache",
            data=cached_result,
            cached=True
        )
    
    # Start background scraping task
    background_tasks.add_task(
        scrape_company_data,
        request.idno,
        db
    )
    
    return ScrapeResponse(
        success=True,
        message="Scraping started in background",
        data=None,
        cached=False
    )

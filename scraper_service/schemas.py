from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class ScrapeRequest(BaseModel):
    idno: str
    force_refresh: bool = False

class CompanyData(BaseModel):
    idno: str
    company_name: Optional[str] = None
    registration_date: Optional[date] = None
    status: Optional[str] = None
    address: Optional[str] = None
    activity_code: Optional[str] = None
    activity_description: Optional[str] = None
    legal_form: Optional[str] = None
    share_capital: Optional[str] = None
    founders: Optional[List[str]] = None
    scraped_at: datetime

    class Config:
        from_attributes = True

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[CompanyData] = None
    cached: bool
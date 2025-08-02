import httpx
import json
import re
from datetime import datetime, date
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from fake_useragent import UserAgent

from models import SourceData, TransformedData
from redis_client import cache_company_data, get_cached_company_data
from config import settings

async def scrape_company_data(idno: str, db: Session):
    
    try:
        # Extract phase
        raw_data = await extract_raw_data(idno)
        if not raw_data:
            return None
        
        # Load phase
        source_record = SourceData(
            idno=idno,
            url=raw_data["url"],
            raw_html=raw_data["html"],
            status_code=raw_data["status_code"]
        )
        db.add(source_record)
        db.commit()
        
        # Transform phase
        company_data = transform_company_data(raw_data["html"], idno)
        if company_data:
            transformed_record = TransformedData(**company_data)
            db.add(transformed_record)
            db.commit()

            cache_company_data(idno, company_data)
            
            return company_data
        
        return None
        
    except Exception as e:
        print(f"Error scraping data for IDNO {idno}: {str(e)}")
        return None

async def extract_raw_data(idno: str):
    
    base_url = "https://openmoney.md"
    search_url = f"{base_url}/companies/{idno}"
    user_agent = UserAgent()
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": user_agent.chrome
            }
            
            response = await client.get(search_url, headers=headers)
            
            if response.status_code == 200:
                return {
                    "html": response.text,
                    "url": search_url,
                    "status_code": response.status_code
                }
            else:
                print(f"Failed to fetch data for IDNO {idno}: Status {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Request error for IDNO {idno}: {str(e)}")
        return None

def get_cached_result(idno: str) -> Optional[Dict[str, Any]]:
    return get_cached_company_data(idno)

def cache_result(idno: str, data: Dict[str, Any]) -> None:
    cache_company_data(idno, data)
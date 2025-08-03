import re
import time
from datetime import datetime
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models import SourceData, TransformedData
from redis_client import cache_company_data, get_cached_company_data

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
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        url = f"https://openmoney.md/companies/{idno}"
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(3)
        
        html = driver.page_source
        return {
            "html": html,
            "url": url,
            "status_code": 200
        }
        
    finally:
        driver.quit()
    
def transform_company_data(html_content: str, idno: str):
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        text_content = soup.get_text()
        
        company_name = None
        h1_element = soup.find('h1')
        if h1_element:
            company_name = clean_text(h1_element.get_text())

        if not company_name:
            title_element = soup.find('title')
            if title_element:
                title_text = clean_text(title_element.get_text())
                if title_text:
                    company_name = title_text
        
        address = None

        all_text_elements = soup.find_all(text=True)
        
        found_address_label = False
        for i, element in enumerate(all_text_elements):
            text = clean_text(element)
            if not text:
                continue
                
            if text.lower() in ['adresa', 'address']:
                found_address_label = True
                continue

            if found_address_label:
                if text and len(text) > 10 and any(indicator in text.lower() for indicator in ['mun.', 'str.', 'bd.', 'chișinău', 'chisinau']):
                    print("Gasit cu 1")
                    address = text
                    break

        return {
            "idno": idno,
            "company_name": company_name,
            "address": address,
            "created_at": datetime.now()
        }
        
    except Exception as e:
        print(f"Error transforming HTML data for IDNO {idno}: {str(e)}")
        return None

def clean_text(text):
            if not text:
                return None
            return re.sub(r'\s+', ' ', text.strip())

def get_cached_result(idno: str) -> Optional[Dict[str, Any]]:
    return get_cached_company_data(idno)

def cache_result(idno: str, data: Dict[str, Any]) -> None:
    cache_company_data(idno, data)
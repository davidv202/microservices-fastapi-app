from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from sqlalchemy.sql import func
from database import Base

class SourceData(Base):
    __tablename__ = "source_data"
    
    id = Column(Integer, primary_key=True, index=True)
    idno = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    raw_html = Column(Text, nullable=False)
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class TransformedData(Base):
    __tablename__ = "transformed_data"
    
    id = Column(Integer, primary_key=True, index=True)
    idno = Column(String, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
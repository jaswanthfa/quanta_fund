from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import logging

# Database Configuration
DATABASE_URL = "postgresql://postgres:example@localhost:5432/postgres"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Base Model
Base = declarative_base()

# SQLAlchemy ORM Model for Filings
class Filing(Base):
    __tablename__ = "filings"
    filing_id = Column(String,primary_key=True, index=True)
    cik = Column(String)
    filer_name = Column(String, index=True)
    period_of_report = Column(Date)

# Pydantic Model for API Response
class FilingResponse(BaseModel):
    filing_id: str
    cik: int
    filer_name: str
    period_of_report: Optional[str]

# FastAPI App
app = FastAPI()

# Database Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("filings_search")


# Updated search endpoint with path parameter
@app.get("/filings/{filer_name}", response_model=List[FilingResponse])
def search_filings_by_filer_name(filer_name: str, db: Session = Depends(get_db)):
    try:
        # Log received filer_name for debugging
        logger.debug(f"Received filer_name: {filer_name}")
        
        # Step 1: Strip and validate the filer_name input
        filer_name = filer_name.strip()
        if not filer_name:
            raise HTTPException(status_code=400, detail="Filer name cannot be empty.")
        
        logger.debug(f"Validated filer_name: {filer_name}")
        
        # Step 2: Create search term with % for wildcard search
        search_term = f"%{filer_name}%"
        logger.debug(f"Search term created for query: {search_term}")
        
        # Step 3: Perform query with ILIKE (case-insensitive)
        filings = db.query(Filing).filter(Filing.filer_name.ilike(search_term)).all()
        
        # Step 4: Log the query results (if any)
        logger.debug(f"Found {len(filings)} filings")
        
        if not filings:
            raise HTTPException(status_code=404, detail="No filings found for this filer name.")
        
        # Step 5: Return response
        return [
            FilingResponse(
                filing_id=filing.filing_id,
                cik=filing.cik,
                filer_name=filing.filer_name,
                period_of_report=filing.period_of_report.strftime("%Y-%m-%d") if filing.period_of_report else None
            ) for filing in filings
        ]
    
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
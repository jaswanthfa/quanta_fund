from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, func, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import logging

# Database Configuration
DATABASE_URL = "postgresql://postgres:example@localhost:5432/postgres"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Base Model
Base = declarative_base()

# SQLAlchemy ORM Models
class Filing(Base):
    __tablename__ = "filings"
    filing_id = Column(String, primary_key=True, index=True)
    cik = Column(String)
    filer_name = Column(String, index=True)
    period_of_report = Column(Date)

class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True, index=True)
    filing_id = Column(String, index=True)
    value = Column(Float)

# Pydantic Models for API Response
class FilingResponse(BaseModel):
    filing_id: str
    cik: int
    filer_name: str
    period_of_report: Optional[str]

class QuarterlyHolding(BaseModel):
    filer_name: str
    quarter: str
    total_value: float
    total_holdings:int
    filing_id:str

# FastAPI App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # This allows all headers
)


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


# Endpoint to search filings by filer_name (Path Parameter)
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


# Endpoint to calculate total holdings value per quarter for a filer_name (Path Parameter)
@app.get("/manager/{filer_name}/", response_model=List[QuarterlyHolding])
def calculate_quarterly_total_value(
    filer_name: str,  # Path parameter for filer_name
    db: Session = Depends(get_db)
):
    try:
        # Step 1: Validate and strip input
        filer_name = filer_name.strip()
        if not filer_name:
            raise HTTPException(status_code=400, detail="Filer name cannot be empty.")
        
        # Step 2: Query to calculate quarterly holdings
        results = (
            db.query(
                Filing.filer_name,
                func.date_trunc('quarter', Filing.period_of_report).label("quarter"),
                func.sum(Holding.value).label("total_value"),
                func.count(Holding.filing_id).label("total_holdings"),
                Filing.filing_id.label("filing_id")
                
                
            )
            .join(Holding, Filing.filing_id == Holding.filing_id)
            .filter(Filing.filer_name.ilike(f"%{filer_name}%"),Filing.period_of_report >= "2014-01-01")
            .group_by(Filing.filer_name, func.date_trunc('quarter', Filing.period_of_report),Filing.filing_id)
            .order_by(func.date_trunc('quarter', Filing.period_of_report))
            .all()
        )
        
        # Step 3: Log and handle results
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No holdings found for filer_name '{filer_name}' starting from Q1 2014."
            )
        
        # Return results
        return [
            QuarterlyHolding(
                filer_name=result.filer_name,
                quarter = f"{result.quarter.year}-Q{(result.quarter.month - 1) // 3 + 1}",
                total_value=result.total_value,
                total_holdings=result.total_holdings,
                filing_id=result.filing_id
            )
            for result in results
        ]
    
    except Exception as e:
        logger.error(f"Error calculating quarterly holdings for '{filer_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
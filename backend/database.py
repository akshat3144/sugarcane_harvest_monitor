"""
Database configuration and session management
Using PostgreSQL with PostGIS extension for geospatial data
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - Update with your PostgreSQL credentials
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://username:password@localhost:5432/smart_farm_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Farm model with PostGIS geometry
class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(String, unique=True, index=True)
    name = Column(String)
    village = Column(String, index=True)
    division = Column(String)
    supervisor = Column(String)
    farmer_name = Column(String)
    area = Column(Float)
    crop_type = Column(String)
    
    # Geometry stored as PostGIS POLYGON
    geometry = Column(Geometry('POLYGON', srid=4326))
    
    # NDVI data
    recent_ndvi = Column(Float)
    prev_ndvi = Column(Float)
    ndvi_delta = Column(Float)
    harvest = Column(Integer, default=0)
    
    # Timestamps
    survey_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

# Utility function to convert coordinates to WKT
def coords_to_wkt(coords: list) -> str:
    """
    Convert list of [lat, lon] pairs to WKT POLYGON
    Example: [[19.234, 73.123], [19.236, 73.123], ...]
    Returns: "POLYGON((73.123 19.234, 73.123 19.236, ...))"
    """
    # Swap to lon, lat and format
    points = [f"{lon} {lat}" for lat, lon in coords]
    # Close the polygon
    if points[0] != points[-1]:
        points.append(points[0])
    return f"POLYGON(({', '.join(points)}))"

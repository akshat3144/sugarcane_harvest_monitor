"""
Database configuration and session management
Using PostgreSQL with PostGIS extension for geospatial data
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
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
    
    # Division and village information
    div_name = Column(String)
    vill_cd = Column(Integer, index=True)
    vill_name = Column(String, index=True)
    vill_code = Column(Integer)
    
    # Farm details
    supervisor_name = Column(String)
    farmer_name = Column(String)
    father_name = Column(String)
    plot_no = Column(Integer)
    gashti_no = Column(Integer)
    survey_date = Column(String)  # Stored as string to match source data format
    area = Column(Float)
    shar = Column(Integer)
    varieties = Column(String)
    crop_type = Column(String)
    
    # Boundary measurements
    east = Column(Integer)
    west = Column(Integer)
    north = Column(Integer)
    south = Column(Integer)
    wkt = Column(String)  # Original WKT string
    
    # Geometry stored as PostGIS POLYGON
    geometry = Column(Geometry('POLYGON', srid=4326))
    
    # NDVI data
    recent_date = Column(String)
    recent_ndvi = Column(Float)
    prev_date = Column(String)
    prev_ndvi = Column(Float)
    delta = Column(Float)
    harvest_flag = Column(Integer, default=0)
    
    # Timestamps
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
    """Create all tables and enable PostGIS extension"""
    try:
        # Enable PostGIS extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
            conn.commit()
            print("PostGIS extensions enabled")
    except Exception as e:
        print(f"PostGIS extension setup: {e}")
        # Continue anyway - extension might already exist or user lacks permissions
    
    # Create all tables
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

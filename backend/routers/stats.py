"""
Statistics and analytics endpoints
"""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db, Farm

router = APIRouter()

@router.get("/summary")
def stats_summary(village: str = Query(None), db: Session = Depends(get_db)):
    """Get dashboard stats from PostGIS database"""
    
    # Base query
    query = db.query(Farm)
    
    # Filter by village if specified
    if village and village.lower() != "all":
        query = query.filter(func.lower(Farm.vill_name) == village.lower())
    
    # Get total farms
    total_farms = query.count()
    
    if total_farms == 0:
        return {
            "total_farms": 0,
            "harvest_ready_count": 0,
            "harvest_ready_percentage": 0,
            "avg_ndvi": 0,
            "avg_ndvi_change": 0,
            "total_area": 0,
            "total_harvest_area": 0
        }
    
    # Get harvest ready count
    harvest_ready_count = query.filter(Farm.harvest_flag == 1).count()
    
    # Get average NDVI
    avg_ndvi_result = query.with_entities(
        func.avg(Farm.recent_ndvi)
    ).filter(Farm.recent_ndvi.isnot(None)).scalar()
    avg_ndvi = float(avg_ndvi_result) if avg_ndvi_result else 0
    
    # Get average NDVI change
    avg_ndvi_change_result = query.with_entities(
        func.avg(Farm.delta)
    ).filter(Farm.delta.isnot(None)).scalar()
    avg_ndvi_change = float(avg_ndvi_change_result) if avg_ndvi_change_result else 0
    
    # Get total area
    total_area_result = query.with_entities(
        func.sum(Farm.area)
    ).scalar()
    total_area = float(total_area_result) if total_area_result else 0
    
    # Get total harvest area
    total_harvest_area_result = query.filter(Farm.harvest_flag == 1).with_entities(
        func.sum(Farm.area)
    ).scalar()
    total_harvest_area = float(total_harvest_area_result) if total_harvest_area_result else 0
    
    return {
        "total_farms": total_farms,
        "harvest_ready_count": harvest_ready_count,
        "harvest_ready_percentage": (harvest_ready_count / total_farms * 100) if total_farms else 0,
        "avg_ndvi": round(avg_ndvi, 3),
        "avg_ndvi_change": round(avg_ndvi_change, 3),
        "total_area": round(total_area, 3),
        "total_harvest_area": round(total_harvest_area, 3)
    }



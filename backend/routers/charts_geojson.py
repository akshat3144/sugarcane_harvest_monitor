"""
Chart data endpoints for dashboard visualizations (PostGIS version)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db, Farm

router = APIRouter()

@router.get("/ndvi-by-village")
def ndvi_by_village(db: Session = Depends(get_db)):
    """Get average NDVI by village"""
    results = db.query(
        Farm.vill_name,
        func.avg(Farm.recent_ndvi).label('avg_ndvi')
    ).filter(
        Farm.recent_ndvi.isnot(None)
    ).group_by(
        Farm.vill_name
    ).order_by(
        Farm.vill_name
    ).all()
    
    if not results:
        return {"labels": [], "values": []}
    
    return {
        "labels": [r.vill_name for r in results],
        "values": [round(float(r.avg_ndvi), 3) for r in results]
    }

@router.get("/harvest-area-timeline")
def harvest_area_timeline(db: Session = Depends(get_db)):
    """Get harvest-ready area by village"""
    results = db.query(
        Farm.vill_name,
        func.sum(Farm.area).label('total_area')
    ).filter(
        Farm.harvest_flag == 1
    ).group_by(
        Farm.vill_name
    ).order_by(
        Farm.vill_name
    ).all()
    
    if not results:
        return {"labels": [], "values": []}
    
    return {
        "labels": [r.vill_name for r in results],
        "values": [round(float(r.total_area), 3) for r in results]
    }

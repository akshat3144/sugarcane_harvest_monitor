"""
Chart data endpoints for dashboard visualizations
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db, Farm
from ..models import ChartData

router = APIRouter()

@router.get("/ndvi-by-village", response_model=ChartData)
async def get_ndvi_by_village(db: Session = Depends(get_db)):
    """Get NDVI values grouped by village for bar chart"""
    results = db.query(
        Farm.village,
        func.avg(Farm.recent_ndvi).label('avg_ndvi')
    ).group_by(
        Farm.village
    ).order_by(
        Farm.village
    ).all()
    
    return ChartData(
        labels=[r.village for r in results],
        values=[float(r.avg_ndvi or 0) for r in results]
    )

@router.get("/harvest-area-timeline", response_model=ChartData)
async def get_harvest_area_timeline(db: Session = Depends(get_db)):
    """Get harvest area over time (simulated with villages)"""
    results = db.query(
        Farm.village,
        func.sum(Farm.area).label('total_area')
    ).filter(
        Farm.harvest == 1
    ).group_by(
        Farm.village
    ).all()
    
    return ChartData(
        labels=[r.village for r in results],
        values=[float(r.total_area or 0) for r in results]
    )

@router.get("/health-distribution", response_model=ChartData)
async def get_health_distribution(db: Session = Depends(get_db)):
    """Get distribution of farms by health status"""
    farms = db.query(Farm).all()
    
    health_categories = {
        "Excellent (≥0.7)": 0,
        "Good (0.6-0.7)": 0,
        "Moderate (0.5-0.6)": 0,
        "Poor (0.4-0.5)": 0,
        "Critical (<0.4)": 0
    }
    
    for farm in farms:
        ndvi = farm.recent_ndvi or 0
        if ndvi >= 0.7:
            health_categories["Excellent (≥0.7)"] += 1
        elif ndvi >= 0.6:
            health_categories["Good (0.6-0.7)"] += 1
        elif ndvi >= 0.5:
            health_categories["Moderate (0.5-0.6)"] += 1
        elif ndvi >= 0.4:
            health_categories["Poor (0.4-0.5)"] += 1
        else:
            health_categories["Critical (<0.4)"] += 1
    
    return ChartData(
        labels=list(health_categories.keys()),
        values=list(health_categories.values()),
        colors=["#22c55e", "#84cc16", "#eab308", "#f97316", "#ef4444"]
    )

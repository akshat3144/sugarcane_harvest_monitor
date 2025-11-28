from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from backend.database import get_db, Farm

router = APIRouter()

@router.get("/harvest-area-timeline")
def harvest_area_timeline(
    metric: str = Query("area", enum=["area", "count", "percent"]),
    db: Session = Depends(get_db)
):
    """Get harvest-ready metrics by village"""
    
    if metric == "area":
        # Sum of area for harvest-ready farms by village
        results = db.query(
            Farm.vill_name,
            func.sum(Farm.area).label('value')
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
            "values": [round(float(r.value), 3) for r in results]
        }
    
    elif metric == "count":
        # Count of harvest-ready farms by village
        results = db.query(
            Farm.vill_name,
            func.count(Farm.id).label('value')
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
            "values": [int(r.value) for r in results]
        }
    
    elif metric == "percent":
        # Percentage of harvest-ready farms by village
        results = db.query(
            Farm.vill_name,
            func.count(Farm.id).label('total'),
            func.sum(case((Farm.harvest_flag == 1, 1), else_=0)).label('harvested')
        ).group_by(
            Farm.vill_name
        ).order_by(
            Farm.vill_name
        ).all()
        
        if not results:
            return {"labels": [], "values": []}
        
        labels = [r.vill_name for r in results]
        values = [
            round((float(r.harvested) / float(r.total) * 100) if r.total > 0 else 0, 1)
            for r in results
        ]
        
        return {"labels": labels, "values": values}
    
    return {"labels": [], "values": []}

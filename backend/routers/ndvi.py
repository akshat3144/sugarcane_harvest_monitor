"""
NDVI data endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import pandas as pd

from database import get_db, Farm
from models import NDVIData, NDVIResponse

router = APIRouter()

def calculate_health_status(ndvi: float) -> str:
    """Determine health status from NDVI value"""
    if ndvi >= 0.7:
        return "excellent"
    elif ndvi >= 0.6:
        return "good"
    elif ndvi >= 0.5:
        return "moderate"
    elif ndvi >= 0.4:
        return "poor"
    else:
        return "critical"

def calculate_harvest_flag(recent_ndvi: float, prev_ndvi: float) -> bool:
    """
    Harvest prediction logic:
    Harvest = 1 if NDVI_t < 0.5 AND NDVI_t < NDVI_t-1
    """
    return recent_ndvi < 0.5 and recent_ndvi < prev_ndvi

@router.post("/update/{farm_id}")
async def update_farm_ndvi(
    farm_id: str,
    ndvi_data: NDVIData,
    db: Session = Depends(get_db)
):
    """Update NDVI data for a farm"""
    farm = db.query(Farm).filter(Farm.farm_id == farm_id).first()
    
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Update NDVI values
    farm.recent_ndvi = ndvi_data.recent_ndvi
    farm.prev_ndvi = ndvi_data.prev_ndvi
    farm.ndvi_delta = ndvi_data.delta
    
    # Calculate harvest flag
    farm.harvest = 1 if calculate_harvest_flag(
        ndvi_data.recent_ndvi,
        ndvi_data.prev_ndvi
    ) else 0
    
    db.commit()
    
    return {
        "message": "NDVI updated successfully",
        "farm_id": farm_id,
        "harvest_ready": farm.harvest == 1
    }

@router.post("/bulk-update")
async def bulk_update_ndvi(
    ndvi_list: List[NDVIData],
    db: Session = Depends(get_db)
):
    """Bulk update NDVI data from CSV processing"""
    updated = 0
    errors = []
    
    for ndvi_data in ndvi_list:
        try:
            farm = db.query(Farm).filter(
                Farm.farm_id == ndvi_data.farm_id
            ).first()
            
            if not farm:
                errors.append(f"Farm {ndvi_data.farm_id} not found")
                continue
            
            farm.recent_ndvi = ndvi_data.recent_ndvi
            farm.prev_ndvi = ndvi_data.prev_ndvi
            farm.ndvi_delta = ndvi_data.delta
            farm.harvest = 1 if calculate_harvest_flag(
                ndvi_data.recent_ndvi,
                ndvi_data.prev_ndvi
            ) else 0
            
            updated += 1
            
        except Exception as e:
            errors.append(f"Error updating {ndvi_data.farm_id}: {str(e)}")
    
    db.commit()
    
    return {
        "message": f"Updated {updated} farms",
        "updated": updated,
        "errors": errors
    }

@router.get("/{farm_id}", response_model=NDVIResponse)
async def get_farm_ndvi(farm_id: str, db: Session = Depends(get_db)):
    """Get NDVI data for a specific farm"""
    farm = db.query(Farm).filter(Farm.farm_id == farm_id).first()
    
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    return {
        "farm_id": farm.farm_id,
        "recent_ndvi": farm.recent_ndvi or 0,
        "prev_ndvi": farm.prev_ndvi or 0,
        "delta": farm.ndvi_delta or 0,
        "harvest_ready": farm.harvest == 1,
        "health_status": calculate_health_status(farm.recent_ndvi or 0)
    }

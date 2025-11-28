
"""
Farm management endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from geoalchemy2.functions import ST_AsGeoJSON, ST_Intersects, ST_MakeEnvelope
from backend.database import get_db, Farm
import json

router = APIRouter()

def farm_to_geojson_feature(farm: Farm, geom_json: str) -> dict:
    """Convert a Farm model to GeoJSON feature"""
    return {
        "type": "Feature",
        "geometry": json.loads(geom_json),
        "properties": {
            "farm_id": farm.farm_id,
            "Div_Name": farm.div_name,
            "Vill_Cd": farm.vill_cd,
            "Vill_Name": farm.vill_name,
            "Vill_Code": farm.vill_code,
            "Supervisor Name": farm.supervisor_name,
            "Farmer_Name": farm.farmer_name,
            "Father_Name": farm.father_name,
            "Plot No": farm.plot_no,
            "Gashti No.": farm.gashti_no,
            "Survey Date": farm.survey_date,
            "Area": farm.area,
            "Shar": farm.shar,
            "Varieties": farm.varieties,
            "Crop Type": farm.crop_type,
            "East": farm.east,
            "West": farm.west,
            "North": farm.north,
            "South": farm.south,
            "WKT": farm.wkt,
            "recent_date": farm.recent_date,
            "recent_ndvi": farm.recent_ndvi,
            "prev_date": farm.prev_date,
            "prev_ndvi": farm.prev_ndvi,
            "delta": farm.delta,
            "harvest_flag": farm.harvest_flag
        }
    }

@router.get("")
def list_farms(
    bbox: Optional[str] = Query(None, description="Bounding box: minx,miny,maxx,maxy"),
    village: Optional[str] = Query(None),
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of farms with optional filters"""
    query = db.query(Farm, ST_AsGeoJSON(Farm.geometry).label('geom_json'))
    
    # Filter by village
    if village:
        query = query.filter(Farm.vill_name == village)
    
    # Filter by bounding box
    if bbox:
        try:
            minx, miny, maxx, maxy = map(float, bbox.split(','))
            bbox_geom = ST_MakeEnvelope(minx, miny, maxx, maxy, 4326)
            query = query.filter(ST_Intersects(Farm.geometry, bbox_geom))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid bbox format. Use: minx,miny,maxx,maxy")
    
    # Pagination
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()
    
    features = [farm_to_geojson_feature(farm, geom_json) for farm, geom_json in results]
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/{farm_id}")
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    """Get a single farm by ID"""
    result = db.query(Farm, ST_AsGeoJSON(Farm.geometry).label('geom_json')).filter(
        Farm.farm_id == farm_id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Farm not found.")
    
    farm, geom_json = result
    return farm_to_geojson_feature(farm, geom_json)

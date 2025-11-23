
"""
Farm management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os
import json

router = APIRouter()

GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/farms_final.geojson')

# --- Only GeoJSON endpoints below ---

@router.get("")
def list_farms(
    bbox: Optional[str] = Query(None, description="Bounding box: minx,miny,maxx,maxy"),
    village: Optional[str] = Query(None),
    page: int = 1,
    page_size: int = 50
):
    if not os.path.exists(GEOJSON_PATH):
        raise HTTPException(status_code=404, detail="No data available.")
    with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    features = geojson.get('features', [])

    features = geojson.get('features', [])
    # Optionally filter by village
    if village:
        features = [feat for feat in features if feat['properties'].get('Vill_Name') == village]
    # Optionally filter by bbox
    if bbox:
        minx, miny, maxx, maxy = map(float, bbox.split(','))
        def in_bbox(feat):
            coords = feat['geometry']['coordinates'][0]
            return any(minx <= lon <= maxx and miny <= lat <= maxy for lon, lat in coords)
        features = [feat for feat in features if in_bbox(feat)]
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "type": "FeatureCollection",
        "features": features[start:end]
    }

@router.get("/{farm_id}")
def get_farm(farm_id: str):
    if not os.path.exists(GEOJSON_PATH):
        raise HTTPException(status_code=404, detail="No data available.")
    with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    features = geojson.get('features', [])
    for feat in features:
        if feat['properties'].get('farm_id') == farm_id:
            return feat
    raise HTTPException(status_code=404, detail="Farm not found.")

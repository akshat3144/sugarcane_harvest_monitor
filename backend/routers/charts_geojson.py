"""
Chart data endpoints for dashboard visualizations (GeoJSON version)
"""
from fastapi import APIRouter
import geopandas as gpd
import os

router = APIRouter()
GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/farms_final.geojson')

@router.get("/ndvi-by-village")
def ndvi_by_village():
    if not os.path.exists(GEOJSON_PATH):
        return {"labels": [], "values": []}
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'Vill_Name' not in gdf or 'recent_ndvi' not in gdf:
        return {"labels": [], "values": []}
    grouped = gdf.groupby('Vill_Name')['recent_ndvi'].mean().reset_index()
    return {
        "labels": grouped['Vill_Name'].tolist(),
        "values": grouped['recent_ndvi'].round(3).tolist()
    }

@router.get("/harvest-area-timeline")
def harvest_area_timeline():
    if not os.path.exists(GEOJSON_PATH):
        return {"labels": [], "values": []}
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'Vill_Name' not in gdf or 'Area' not in gdf or 'harvest_flag' not in gdf:
        return {"labels": [], "values": []}
    grouped = gdf[gdf['harvest_flag'] == 1].groupby('Vill_Name')['Area'].sum().reset_index()
    return {
        "labels": grouped['Vill_Name'].tolist(),
        "values": grouped['Area'].round(3).tolist()
    }

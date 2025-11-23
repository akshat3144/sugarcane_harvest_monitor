"""
Chart data endpoints for dashboard visualizations
"""

from fastapi import APIRouter
from ..models import ChartData
import geopandas as gpd
import os

router = APIRouter()

GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/farms_final.geojson')


@router.get("/ndvi-by-village", response_model=ChartData)
def get_ndvi_by_village():
    """Get NDVI values grouped by village for bar chart (GeoJSON)"""
    if not os.path.exists(GEOJSON_PATH):
        return ChartData(labels=[], values=[])
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'Vill_Name' not in gdf or 'recent_ndvi' not in gdf:
        return ChartData(labels=[], values=[])
    grouped = gdf.groupby('Vill_Name')['recent_ndvi'].mean().reset_index()
    return ChartData(
        labels=grouped['Vill_Name'].astype(str).tolist(),
        values=grouped['recent_ndvi'].fillna(0).astype(float).tolist()
    )


@router.get("/harvest-area-timeline", response_model=ChartData)
def get_harvest_area_timeline():
    """Get harvest area by village (GeoJSON)"""
    if not os.path.exists(GEOJSON_PATH):
        return ChartData(labels=[], values=[])
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'Vill_Name' not in gdf or 'Area' not in gdf or 'harvest_flag' not in gdf:
        return ChartData(labels=[], values=[])
    filtered = gdf[gdf['harvest_flag'] == 1]
    grouped = filtered.groupby('Vill_Name')['Area'].sum().reset_index()
    return ChartData(
        labels=grouped['Vill_Name'].astype(str).tolist(),
        values=grouped['Area'].fillna(0).astype(float).tolist()
    )


@router.get("/health-distribution", response_model=ChartData)
def get_health_distribution():
    """Get distribution of farms by health status (GeoJSON)"""
    if not os.path.exists(GEOJSON_PATH):
        return ChartData(labels=[], values=[], colors=[])
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'recent_ndvi' not in gdf:
        return ChartData(labels=[], values=[], colors=[])
    health_categories = {
        "Excellent (≥0.7)": 0,
        "Good (0.6-0.7)": 0,
        "Moderate (0.5-0.6)": 0,
        "Poor (0.4-0.5)": 0,
        "Critical (<0.4)": 0
    }
    for ndvi in gdf['recent_ndvi'].fillna(0):
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

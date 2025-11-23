"""
Statistics and analytics endpoints
"""

from fastapi import APIRouter, Query
import geopandas as gpd
import os

router = APIRouter()
GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/farms_final.geojson')

@router.get("/summary")
def stats_summary(village: str = Query(None)):
    """Get dashboard stats from GeoJSON"""
    if not os.path.exists(GEOJSON_PATH):
        return {
            "total_farms": 0,
            "harvest_ready_count": 0,
            "harvest_ready_percentage": 0,
            "avg_ndvi": 0,
            "avg_ndvi_change": 0,
            "total_area": 0,
            "total_harvest_area": 0
        }
    gdf = gpd.read_file(GEOJSON_PATH)
    if village and village.lower() != "all":
        gdf = gdf[gdf['Vill_Name'].str.lower() == village.lower()]
    total_farms = len(gdf)
    if 'harvest_flag' in gdf:
        harvest_ready = gdf.loc[gdf['harvest_flag'] == 1]
        harvest_ready_count = len(harvest_ready)
    else:
        harvest_ready = gdf.iloc[0:0]  # empty DataFrame
        harvest_ready_count = 0
    avg_ndvi = gdf['recent_ndvi'].mean() if 'recent_ndvi' in gdf else 0
    avg_ndvi_change = (gdf['recent_ndvi'] - gdf['prev_ndvi']).mean() if 'recent_ndvi' in gdf and 'prev_ndvi' in gdf else 0
    total_area = gdf['Area'].sum() if 'Area' in gdf else 0
    total_harvest_area = harvest_ready['Area'].sum() if 'Area' in gdf and not harvest_ready.empty else 0
    return {
        "total_farms": total_farms,
        "harvest_ready_count": harvest_ready_count,
        "harvest_ready_percentage": (harvest_ready_count / total_farms * 100) if total_farms else 0,
        "avg_ndvi": avg_ndvi or 0,
        "avg_ndvi_change": avg_ndvi_change or 0,
        "total_area": total_area or 0,
        "total_harvest_area": total_harvest_area or 0
    }



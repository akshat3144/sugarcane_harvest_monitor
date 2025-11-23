import geopandas as gpd
import os
from fastapi import APIRouter, Query

router = APIRouter()
GEOJSON_PATH = os.path.join(os.path.dirname(__file__), '../../data/farms_final.geojson')

@router.get("/harvest-area-timeline")
def harvest_area_timeline(metric: str = Query("area", enum=["area", "count", "percent"])):
    if not os.path.exists(GEOJSON_PATH):
        return {"labels": [], "values": []}
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'Vill_Name' not in gdf or 'harvest_flag' not in gdf:
        return {"labels": [], "values": []}
    filtered = gdf[gdf['harvest_flag'] == 1]
    labels = filtered['Vill_Name'].unique().tolist()
    if metric == "area":
        grouped = filtered.groupby('Vill_Name')['Area'].sum().reindex(labels, fill_value=0)
        values = grouped.round(3).tolist()
    elif metric == "count":
        grouped = filtered.groupby('Vill_Name').size().reindex(labels, fill_value=0)
        values = grouped.tolist()
    elif metric == "percent":
        total = gdf.groupby('Vill_Name').size().reindex(labels, fill_value=0)
        harvested = filtered.groupby('Vill_Name').size().reindex(labels, fill_value=0)
        values = [(harvested[l]/total[l]*100 if total[l] else 0) for l in labels]
        values = [round(v, 1) for v in values]
    else:
        values = []
    return {"labels": labels, "values": values}

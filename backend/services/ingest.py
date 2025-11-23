from typing import List, Tuple, Optional
import os

def full_pipeline(csv_path: str, geojson_path: str, ndvi_csv_path: str, final_geojson_path: str, log_path: Optional[str] = None) -> Tuple[int, int]:
    """
    Full pipeline: CSV -> GeoJSON -> NDVI extraction -> Merge -> Harvest flag -> Final GeoJSON
    1. Convert CSV to GeoJSON (polygons)
    2. Call NDVI extraction (external script)
    3. Merge NDVI results
    4. Apply harvest flag
    5. Save final GeoJSON
    """
    import subprocess
    # Step 1: CSV to GeoJSON
    n_ok, n_rej = csv_to_geojson(csv_path, geojson_path, log_path)

    # Step 2: NDVI extraction (call external script)
    if not os.path.exists(ndvi_csv_path):
        ndvi_script = os.path.join(os.path.dirname(__file__), 'ndvi_extraction.py')
        if not os.path.exists(ndvi_script):
            raise FileNotFoundError(f"NDVI extraction script not found: {ndvi_script}")
        result = subprocess.run([
            "python", ndvi_script, csv_path, ndvi_csv_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"NDVI extraction failed: {result.stderr}")
        if log_path:
            with open(log_path, 'a') as f:
                f.write(f"NDVI extraction output:\n{result.stdout}\n")

    # Step 3: Merge NDVI results
    gdf = gpd.read_file(geojson_path)
    ndvi = pd.read_csv(ndvi_csv_path)
    merged = gdf.merge(ndvi, on="farm_id", how="left")

    # Step 4: Apply harvest flag
    merged["harvest_flag"] = ((merged["recent_ndvi"] < 0.5) & (merged["recent_ndvi"] < merged["prev_ndvi"])).astype(int)

    # Step 5: Save final GeoJSON
    merged.to_file(final_geojson_path, driver="GeoJSON")

    if log_path:
        with open(log_path, 'a') as f:
            f.write(f"Merged and saved: {final_geojson_path}\n")
    return n_ok, n_rej
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import logging
from typing import List, Tuple, Optional
import os

REQUIRED_COLUMNS = [
    'Div_Name', 'Vill_Cd', 'Vill_Name', 'Vill_Code', 'Supervisor Name', 'farm_id',
    'Farmer_Name', 'Father_Name', 'Plot No', 'Gashti No.', 'Survey Date', 'Area',
    'Shar', 'Varieties', 'Crop Type', 'East', 'West', 'North', 'South',
    'Lang1', 'Long1', 'Lang2', 'Long2', 'Lang3', 'Long3', 'Lang4', 'Long4', 'WKT'
]

logger = logging.getLogger(__name__)


def extract_corners(row) -> List[Tuple[float, float]]:
    corners = []
    for i in range(1, 5):
        lat = row.get(f'Lang{i}')
        lon = row.get(f'Long{i}')
        if pd.notnull(lat) and pd.notnull(lon):
            try:
                corners.append((float(lon), float(lat)))
            except Exception:
                continue
    return corners


def row_to_polygon(row) -> Optional[Polygon]:
    corners = extract_corners(row)
    if len(corners) < 3:
        return None
    # Ensure closed polygon
    if corners[0] != corners[-1]:
        corners.append(corners[0])
    try:
        poly = Polygon(corners)
        if not poly.is_valid:
            return None
        return poly
    except Exception:
        return None


def csv_to_geojson(csv_path: str, geojson_path: str, log_path: Optional[str] = None) -> Tuple[int, int]:

    import difflib
    df = pd.read_csv(csv_path)
    # Normalize columns: strip, lower, remove extra spaces
    norm_map = {c: c.strip().lower().replace(' ', '') for c in df.columns}
    required_norm = {c: c.strip().lower().replace(' ', '') for c in REQUIRED_COLUMNS}
    col_map = {}
    for req, req_norm in required_norm.items():
        # Try exact match
        found = [orig for orig, norm in norm_map.items() if norm == req_norm]
        if found:
            col_map[req] = found[0]
            continue
        # Try fuzzy match (typos)
        close = difflib.get_close_matches(req_norm, norm_map.values(), n=1, cutoff=0.8)
        if close:
            # Map to the first close match
            orig = [orig for orig, norm in norm_map.items() if norm == close[0]][0]
            col_map[req] = orig
            continue
        col_map[req] = None
    missing_cols = [req for req, orig in col_map.items() if orig is None]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    # Rename columns in df to match required names
    df = df.rename(columns={v: k for k, v in col_map.items() if v is not None})

    features = []
    rejected = 0
    for idx, row in df.iterrows():
        poly = row_to_polygon(row)
        if poly is None:
            logger.warning(f"Row {idx} rejected: insufficient or invalid corners.")
            rejected += 1
            continue
        props = row.to_dict()
        for k in ['Lang1','Long1','Lang2','Long2','Lang3','Long3','Lang4','Long4']:
            props.pop(k, None)
        props['geometry'] = poly
        features.append(props)

    gdf = gpd.GeoDataFrame(features, geometry='geometry', crs='EPSG:4326')
    gdf.to_file(geojson_path, driver='GeoJSON')
    if log_path:
        with open(log_path, 'w') as f:
            f.write(f"Rejected rows: {rejected}\n")
    return len(features), rejected

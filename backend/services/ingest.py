from typing import List, Tuple, Optional
import os
from backend.database import SessionLocal, Farm
from geoalchemy2.shape import from_shape

def full_pipeline(csv_path: str, geojson_path: str, ndvi_csv_path: str, final_geojson_path: Optional[str] = None, log_path: Optional[str] = None) -> Tuple[int, int]:
    """
    Full pipeline: CSV -> Database (PostGIS)
    1. Convert CSV to GeoJSON (polygons, temporary)
    2. Call NDVI extraction (external script)
    3. Merge NDVI results
    4. Apply harvest flag
    5. Save to PostGIS database
    All data is now stored in PostgreSQL/PostGIS - no file dependencies
    """
    import subprocess
    # Step 1: CSV to GeoJSON (temporary)
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
    # Deduplicate NDVI results by farm_id (keep first)
    if 'farm_id' in ndvi.columns:
        ndvi = ndvi.drop_duplicates(subset='farm_id', keep='first').reset_index(drop=True)
    merged = gdf.merge(ndvi, on="farm_id", how="left")

    # Step 4: Apply harvest flag
    merged["harvest_flag"] = ((merged["recent_ndvi"] < 0.5) & (merged["recent_ndvi"] < merged["prev_ndvi"])).astype(int)

    # Step 5: Save to PostGIS database
    db = SessionLocal()
    try:
        # Clear all existing data (like the old file deletion behavior)
        if log_path:
            with open(log_path, 'a') as f:
                f.write("Clearing existing farm data from database...\n")
        
        deleted_count = db.query(Farm).delete()
        db.commit()
        
        if log_path:
            with open(log_path, 'a') as f:
                f.write(f"Deleted {deleted_count} existing farms\n")
        
        # Insert new data
        saved_count = 0
        for idx, row in merged.iterrows():
            farm_id = str(row['farm_id'])
            
            # Create new farm (no need to check for existing since we cleared all)
            farm = Farm(
                farm_id=farm_id,
                div_name=row.get('Div_Name'),
                vill_cd=row.get('Vill_Cd'),
                vill_name=row.get('Vill_Name'),
                vill_code=row.get('Vill_Code'),
                supervisor_name=row.get('Supervisor Name'),
                farmer_name=row.get('Farmer_Name'),
                father_name=row.get('Father_Name'),
                plot_no=row.get('Plot No'),
                gashti_no=row.get('Gashti No.'),
                survey_date=row.get('Survey Date'),
                area=row.get('Area'),
                shar=row.get('Shar'),
                varieties=row.get('Varieties'),
                crop_type=row.get('Crop Type'),
                east=row.get('East'),
                west=row.get('West'),
                north=row.get('North'),
                south=row.get('South'),
                wkt=row.get('WKT'),
                geometry=from_shape(row.geometry, srid=4326),
                recent_date=row.get('recent_date'),
                recent_ndvi=row.get('recent_ndvi'),
                prev_date=row.get('prev_date'),
                prev_ndvi=row.get('prev_ndvi'),
                delta=row.get('delta'),
                harvest_flag=int(row.get('harvest_flag', 0))
            )
            db.add(farm)
            
            saved_count += 1
            
            # Commit in batches
            if saved_count % 50 == 0:
                db.commit()
        
        db.commit()
        
        if log_path:
            with open(log_path, 'a') as f:
                f.write(f"Saved {saved_count} farms to PostGIS database\n")
        
    except Exception as e:
        db.rollback()
        if log_path:
            with open(log_path, 'a') as f:
                f.write(f"Error saving to database: {e}\n")
        raise
    finally:
        db.close()
    
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
    # Keep only the first occurrence of each unique farm_id
    if 'farm_id' in df.columns:
        df = df.drop_duplicates(subset='farm_id', keep='first').reset_index(drop=True)
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

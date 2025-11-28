# This file was moved from the project root to backend/services.
import ee
import pandas as pd
import sys
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Usage: python ndvi_extraction.py input_csv output_csv
if len(sys.argv) != 3:
    print("Usage: python ndvi_extraction.py input_csv output_csv")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

# Initialize Earth Engine
project_id = os.environ.get("EE_PROJECT_ID")
if not project_id:
    print(f"ERROR: EE_PROJECT_ID environment variable is not set", file=sys.stderr)
    print(f"Please set the EE_PROJECT_ID environment variable to your Earth Engine project ID", file=sys.stderr)
    sys.exit(1)

print(f"Initializing Earth Engine with project: {project_id}")
try:
    ee.Initialize(project=project_id)
    print(f"Earth Engine initialized successfully")
except Exception as e:
    print(f"ERROR: Earth Engine initialization failed: {e}", file=sys.stderr)
    print(f"Please ensure you are authenticated with Earth Engine", file=sys.stderr)
    sys.exit(1)

def mask_s2_clouds(image):
    scl = image.select('SCL')
    mask = scl.eq(4).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(1))
    return image.updateMask(mask)

def row_to_geometry(row):
    pts = []
    for i in (1, 2, 3, 4):
        lat = row.get(f'Lang{i}')
        lon = row.get(f'Long{i}')
        if pd.isna(lat) or pd.isna(lon):
            continue
        pts.append([float(lon), float(lat)])
    if len(pts) < 3:
        return None
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    return ee.Geometry.Polygon([pts])

def add_ndvi(img):
    ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return img.addBands(ndvi)

def get_recent_and_previous_ndvi(geometry, days_window=15):
    import datetime
    now = datetime.datetime.now(datetime.UTC)
    recent_start = now - datetime.timedelta(days=days_window)
    prev_start = now - datetime.timedelta(days=2 * days_window)
    s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
          .filterBounds(geometry)
          .filterDate(prev_start.isoformat(), now.isoformat())
          .map(mask_s2_clouds)
          .map(add_ndvi))
    recent_img = s2.filterDate(recent_start.isoformat(), now.isoformat()).median()
    prev_img   = s2.filterDate(prev_start.isoformat(), recent_start.isoformat()).median()
    recent_mean = recent_img.select('NDVI').reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        bestEffort=True
    ).get('NDVI')
    prev_mean = prev_img.select('NDVI').reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        bestEffort=True
    ).get('NDVI')
    def get_date(image):
        try:
            return ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        except:
            return None
    return {
        "recent_date": get_date(recent_img),
        "recent_ndvi": recent_mean.getInfo() if recent_mean else None,
        "prev_date": get_date(prev_img),
        "prev_ndvi": prev_mean.getInfo() if prev_mean else None
    }

def process_chunk(chunk, thread_id, output_csv):
    local_count = 0
    for _, row in chunk.iterrows():
        farm_id = row.get("farm_id")
        geom = row_to_geometry(row)
        if geom is None:
            print(f"[Thread {thread_id}] ⚠ Invalid geometry for farm {farm_id}")
            continue
        try:
            res = get_recent_and_previous_ndvi(geom)
        except Exception as e:
            print(f"[Thread {thread_id}] ❌ Error for farm {farm_id}: {e}")
            continue
        if not res["recent_ndvi"] or not res["prev_ndvi"]:
            print(f"[Thread {thread_id}] ⚠ No NDVI for {farm_id} (cloudy?)")
            continue
        delta = res["recent_ndvi"] - res["prev_ndvi"]
        with open(output_csv, "a") as f:
            f.write(f"{farm_id},{res['recent_date']},{res['recent_ndvi']},"
                    f"{res['prev_date']},{res['prev_ndvi']},{delta}\n")
        print(f"[Thread {thread_id}] Farm {farm_id} NDVI Change={delta:.3f}")
        local_count += 1
    return local_count

def main():
    print(f"Reading input CSV: {input_csv}")
    try:
        df = pd.read_csv(input_csv)
        print(f"Loaded {len(df)} rows from CSV")
    except Exception as e:
        print(f"ERROR: Failed to read CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(output_csv):
        with open(output_csv, "w") as f:
            f.write("farm_id,recent_date,recent_ndvi,prev_date,prev_ndvi,delta\n")
        print(f"Created output CSV: {output_csv}")
    num_threads = 10
    chunks = np.array_split(df, num_threads)
    import time
    start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(process_chunk, chunk, i + 1, output_csv)
            for i, chunk in enumerate(chunks)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    total = sum(results)
    elapsed = (time.time() - start) / 60
    print(f"\n==============================")
    print(f"   Completed NDVI extraction")
    print(f"   Farms processed: {total}")
    print(f"   Time taken: {elapsed:.2f} minutes")
    print(f"   Output saved to: {output_csv}")
    print(f"==============================\n")

if __name__ == "__main__":
    main()

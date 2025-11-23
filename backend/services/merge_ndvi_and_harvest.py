# This file was moved from the project root to backend/services.
import pandas as pd
import geopandas as gpd
import os

# Paths (edit as needed)
GEOJSON_PATH = "../../data/farms.geojson"  # Input polygons
NDVI_CSV_PATH = "../../data/ndvi_recent_prev.csv"  # NDVI extraction output
OUTPUT_PATH = "../../data/farms_final.geojson"  # Final merged output

# Load farm polygons
if not os.path.exists(GEOJSON_PATH):
    raise FileNotFoundError(f"Not found: {GEOJSON_PATH}")
gdf = gpd.read_file(GEOJSON_PATH)

# Load NDVI results
if not os.path.exists(NDVI_CSV_PATH):
    raise FileNotFoundError(f"Not found: {NDVI_CSV_PATH}")
ndvi = pd.read_csv(NDVI_CSV_PATH)

# Merge on farm_id
merged = gdf.merge(ndvi, on="farm_id", how="left")

# Add harvest flag: 1 if recent_ndvi < 0.5 and recent_ndvi < prev_ndvi, else 0
merged["harvest_flag"] = ((merged["recent_ndvi"] < 0.5) & (merged["recent_ndvi"] < merged["prev_ndvi"])).astype(int)

# Save to GeoJSON
merged.to_file(OUTPUT_PATH, driver="GeoJSON")

print(f"Merged and saved: {OUTPUT_PATH}")
print(merged[["farm_id", "recent_ndvi", "prev_ndvi", "delta", "harvest_flag"]].head())

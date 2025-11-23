from shapely.geometry import Polygon
from typing import Dict
import random
import datetime

def compute_ndvi_for_geometry(geometry: Polygon) -> Dict:
    """
    Mock NDVI computation. Replace this with real GEE code as needed.
    """
    # Use geometry.wkt as seed for reproducibility
    seed = hash(geometry.wkt) % 10000
    random.seed(seed)
    recent_ndvi = round(random.uniform(0.3, 0.9), 3)
    prev_ndvi = round(recent_ndvi - random.uniform(-0.1, 0.2), 3)
    recent_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    prev_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    delta = round(recent_ndvi - prev_ndvi, 3)
    return {
        "recent_date": recent_date,
        "recent_ndvi": recent_ndvi,
        "prev_date": prev_date,
        "prev_ndvi": prev_ndvi,
        "delta": delta
    }

# To use real GEE, replace the above with a function that calls GEE and returns the same dict keys.

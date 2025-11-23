import pytest
import pandas as pd
from shapely.geometry import Polygon
from backend.services import ingest

def make_row(**kwargs):
    # Fill all required columns with None by default
    row = {col: None for col in ingest.REQUIRED_COLUMNS}
    row.update(kwargs)
    return row

def test_polygon_normal_4_corners():
    row = make_row(
        Lang1=10, Long1=20,
        Lang2=10, Long2=21,
        Lang3=11, Long3=21,
        Lang4=11, Long4=20
    )
    poly = ingest.row_to_polygon(row)
    assert isinstance(poly, Polygon)
    assert len(poly.exterior.coords) == 5  # closed polygon

def test_polygon_missing_one_corner():
    row = make_row(
        Lang1=10, Long1=20,
        Lang2=10, Long2=21,
        Lang3=11, Long3=21
        # 4th corner missing
    )
    poly = ingest.row_to_polygon(row)
    assert isinstance(poly, Polygon)
    assert len(poly.exterior.coords) == 4

def test_polygon_all_corners_missing():
    row = make_row()
    poly = ingest.row_to_polygon(row)
    assert poly is None

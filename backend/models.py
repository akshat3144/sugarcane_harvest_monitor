"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FarmBase(BaseModel):
    farm_id: str
    name: str
    village: str
    division: Optional[str] = None
    supervisor: Optional[str] = None
    farmer_name: Optional[str] = None
    area: float
    crop_type: str = "sugarcane"
    survey_date: Optional[datetime] = None

class FarmCreate(FarmBase):
    """Farm creation model with 4 corner coordinates"""
    lang1: float
    long1: float
    lang2: float
    long2: float
    lang3: float
    long3: float
    lang4: float
    long4: float
    boundary_wkt: Optional[str] = None

class FarmResponse(FarmBase):
    """Farm response with computed polygon"""
    id: int
    geometry: dict  # GeoJSON polygon
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NDVIData(BaseModel):
    """NDVI measurement data"""
    farm_id: str
    recent_date: datetime
    recent_ndvi: float
    prev_date: datetime
    prev_ndvi: float
    delta: float
    harvest: int = Field(ge=0, le=1)  # 0 or 1

class NDVIResponse(BaseModel):
    farm_id: str
    recent_ndvi: float
    prev_ndvi: float
    delta: float
    harvest_ready: bool
    health_status: str  # "excellent", "good", "moderate", "poor", "critical"

class StatsResponse(BaseModel):
    """Summary statistics"""
    total_farms: int
    harvest_ready_count: int
    harvest_ready_percentage: float
    avg_ndvi: float
    avg_ndvi_change: float
    total_area: float
    total_harvest_area: float

class VillageStats(BaseModel):
    """Village-level statistics"""
    village: str
    farm_count: int
    avg_ndvi: float
    harvest_ready: int
    total_area: float

class ChartData(BaseModel):
    """Chart data for visualizations"""
    labels: List[str]
    values: List[float]
    colors: Optional[List[str]] = None

class GeoJSONFeature(BaseModel):
    """GeoJSON feature for map display"""
    type: str = "Feature"
    geometry: dict
    properties: dict

class GeoJSONResponse(BaseModel):
    """Complete GeoJSON FeatureCollection"""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

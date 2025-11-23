from pydantic import BaseModel, Field
from typing import Optional, List, Any

class NDVIHistory(BaseModel):
    recent_date: str
    recent_ndvi: float
    prev_date: str
    prev_ndvi: float
    delta: float

class FarmBase(BaseModel):
    farm_id: str
    vill_name: Optional[str]
    vill_code: Optional[str]
    supervisor_name: Optional[str]
    farmer_name: Optional[str]
    father_name: Optional[str]
    plot_no: Optional[str]
    gashti_no: Optional[str]
    survey_date: Optional[str]
    area: Optional[float]
    crop_type: Optional[str]
    varieties: Optional[str]
    shar: Optional[str]
    east: Optional[str]
    west: Optional[str]
    north: Optional[str]
    south: Optional[str]
    harvest_flag: Optional[int]

class FarmCreate(FarmBase):
    geometry: Any
    ndvi: Optional[NDVIHistory]

class FarmOut(FarmBase):
    id: int
    geometry: Any
    ndvi: Optional[NDVIHistory]

class JobStatus(BaseModel):
    job_id: str
    status: str
    logs: Optional[List[str]] = None
    result_file: Optional[str] = None

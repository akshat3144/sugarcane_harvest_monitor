"""
Sugarcane Harvest Monitor Prediction API
FastAPI backend for processing farm data and serving NDVI analytics
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
from datetime import datetime
import os

from backend.routers import upload
from backend.routers import farms
from backend.routers import stats
from backend.routers import charts_geojson as charts
from backend.routers import harvest_chart_api as harvest_chart
from backend.models import FarmCreate, FarmResponse, NDVIData, StatsResponse
from backend.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Sugarcane Harvest Monitor API",
    description="Agricultural intelligence API for NDVI monitoring and harvest prediction",
    version="1.0.0"
)

# CORS middleware - Update origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "https://lovableproject.com",
        "https://*.lovableproject.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Sugarcane Harvest Monitor API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Uploads"])
app.include_router(farms.router, prefix="/api/farms", tags=["Farms"])
# app.include_router(ndvi.router, prefix="/api/ndvi", tags=["NDVI"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
app.include_router(harvest_chart.router, prefix="/api/harvest_chart", tags=["HarvestChart"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

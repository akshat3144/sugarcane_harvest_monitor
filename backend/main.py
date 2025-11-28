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

from routers import upload
from routers import farms
from routers import stats
from routers import charts_geojson as charts
from routers import harvest_chart_api as harvest_chart
from models import FarmCreate, FarmResponse, NDVIData, StatsResponse
from database import init_db

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
        os.getenv("FRONTEND_URL", "")
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

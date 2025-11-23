# CNH Dashboard

A full-stack dashboard for farm management, NDVI analysis, and harvest monitoring. Built with React, FastAPI, and Google Earth Engine.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Folder Structure](#folder-structure)
- [Setup &amp; Installation](#setup--installation)
- [Backend Details](#backend-details)
- [NDVI Extraction Pipeline](#ndvi-extraction-pipeline)
- [Frontend Details](#frontend-details)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

CNH Dashboard is a web application for visualizing, analyzing, and managing farm data. It integrates satellite-based NDVI (Normalized Difference Vegetation Index) analysis to monitor crop health and supports CSV uploads for farm polygons. The dashboard provides real-time insights, harvest predictions, and interactive maps.

## Features

- Upload farm boundary CSVs and process them into GeoJSON.
- Automated NDVI extraction using Google Earth Engine and Sentinel-2 imagery.
- Harvest flagging based on NDVI trends.
- Responsive dashboard with charts, maps, and statistics.
- RESTful API for data access and integration.
- Data deduplication and robust error handling.

## Architecture

- **Frontend:** React, TypeScript, Tailwind CSS, Recharts
- **Backend:** FastAPI, Python, GeoPandas, Google Earth Engine (via `ee` Python API)
- **Data:** CSV, GeoJSON, NDVI CSV

## Folder Structure

```
├── backend/
│   ├── main.py           # FastAPI entrypoint
│   ├── models.py         # Data models
│   ├── routers/          # API endpoints
│   ├── services/         # Data processing scripts
│   │   ├── ingest.py     # Full pipeline logic
│   │   ├── ndvi_extraction.py # NDVI extraction (GEE)
│   │   └── merge_ndvi_and_harvest.py # Merging logic
│   └── ...
├── data/                 # Uploaded and processed data
│   ├── farms.geojson
│   ├── farms_final.geojson
│   ├── ndvi_recent_prev.csv
│   └── ...
├── src/                  # Frontend React app
│   ├── pages/
│   ├── components/
│   └── ...
├── public/
├── requirements.txt      # Python dependencies
├── package.json
├── README.md
└── ...
```

## Setup & Installation

### Environment Variables

Create a `.env` file in the project root with the following contents (edit as needed):

```dotenv
# Backend API URL for frontend
VITE_API_URL=http://localhost:8000/api

# Database Configuration
DATABASE_URL=postgresql://postgres:Akshat123@localhost:5432/cnh

# Google Earth Engine
# Initialize with: earthengine authenticate
EE_PROJECT_ID=your-project-id

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

### Prerequisites

- Python 3.9+
- Node.js 18+
- Google Earth Engine account and service credentials

### Backend Setup

1. Install Python dependencies (from the project root):
   ```sh
   pip install -r requirements.txt
   ```
2. Set up Google Earth Engine credentials:
   - Set the environment variable `EE_PROJECT_ID` to your GEE project.
   - Authenticate with GEE as needed.
3. **Run the backend from the project root:**
   ```sh
   uvicorn backend.main:app --reload
   ```

### Frontend Setup

1. Navigate to the project root:
   ```sh
   npm install
   npm run dev
   ```

## Backend Details

- **main.py:** FastAPI app, includes routers for upload, farms, NDVI, etc.
- **services/ingest.py:** Orchestrates the full data pipeline: CSV → GeoJSON → NDVI extraction → merge → harvest flag → final GeoJSON.
- **services/ndvi_extraction.py:** Uses Google Earth Engine to compute NDVI for each farm polygon over two time windows (recent and previous), outputs per-farm NDVI metrics.
- **services/merge_ndvi_and_harvest.py:** Merges NDVI results with farm polygons and computes harvest flags.
- **routers/upload.py:** Handles CSV uploads, triggers the pipeline, and ensures old data is overwritten.

## NDVI Extraction Pipeline

1. **CSV Upload:** User uploads a CSV with farm boundaries.
2. **CSV to GeoJSON:** Backend converts CSV to GeoJSON, deduplicating by `farm_id`.
3. **NDVI Extraction:**
   - For each farm, the backend calls `ndvi_extraction.py`.
   - The script uses GEE to fetch Sentinel-2 imagery, computes NDVI for recent and previous periods, and writes results to CSV.
   - NDVI results are deduplicated by `farm_id` before merging.
4. **Merge & Harvest Flag:** NDVI results are merged with farm polygons. A harvest flag is set if NDVI drops below a threshold and is decreasing.
5. **GeoJSON Output:** The final merged data is saved as `farms_final.geojson` for dashboard and API use.

## Frontend Details

- Built with React and TypeScript.
- Uses Tailwind CSS for styling and Recharts for data visualization.
- Fetches data from backend APIs for maps, charts, and stats.
- Responsive design for desktop and mobile.

## Data Flow

```
CSV Upload → CSV to GeoJSON → NDVI Extraction (GEE) → Merge → Harvest Flag → GeoJSON → Dashboard/API
```

## API Endpoints

- `POST /upload-csv` — Upload a new farm CSV (overwrites old data)
- `GET /farms` — List all farms (from final GeoJSON)
- `GET /farms/{farm_id}` — Get details for a specific farm
- `GET /jobs/{job_id}` — Check status of a background job
- Additional endpoints for NDVI, stats, and charts

## Customization

- **NDVI thresholds:** Adjust in `merge_ndvi_and_harvest.py` or pipeline logic.
- **Data columns:** Update `REQUIRED_COLUMNS` in `ingest.py` as needed.
- **Frontend:** Modify React components in `src/` for custom UI/UX.

## Troubleshooting

- **NDVI extraction errors:** Ensure GEE credentials are set and the farm polygons are valid.
- **Row count mismatch:** The pipeline now deduplicates by `farm_id` at all stages.
- **Server errors:** Check logs in `data/ingest.log` and backend terminal output.

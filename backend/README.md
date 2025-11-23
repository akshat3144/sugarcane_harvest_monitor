# Smart Farm Health & Harvest Prediction Backend

FastAPI backend for processing farm geospatial data and NDVI analytics.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL with PostGIS

```bash
# Install PostgreSQL and PostGIS
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib postgis

# macOS with Homebrew:
brew install postgresql postgis

# Create database
createdb smart_farm_db

# Enable PostGIS extension
psql smart_farm_db -c "CREATE EXTENSION postgis;"
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Initialize Google Earth Engine

```bash
earthengine authenticate
earthengine init --project=your-project-id
```

### 5. Run the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py script
python main.py
```

Server will start at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── models.py            # Pydantic models for validation
├── database.py          # SQLAlchemy database setup
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── routers/
│   ├── farms.py         # Farm CRUD endpoints
│   ├── ndvi.py          # NDVI data processing
│   ├── stats.py         # Statistics & analytics
│   └── charts.py        # Chart data endpoints
└── README.md
```

## 🔌 API Endpoints

### Farms
- `GET /api/farms/` - Get all farms
- `GET /api/farms/geojson` - Get farms as GeoJSON
- `GET /api/farms/{farm_id}` - Get single farm
- `POST /api/farms/` - Create new farm
- `POST /api/farms/upload-csv` - Bulk upload from CSV

### NDVI
- `POST /api/ndvi/update/{farm_id}` - Update farm NDVI
- `POST /api/ndvi/bulk-update` - Bulk NDVI update
- `GET /api/ndvi/{farm_id}` - Get farm NDVI data

### Statistics
- `GET /api/stats/summary` - Overall summary stats
- `GET /api/stats/by-village` - Village-level stats
- `GET /api/stats/harvest-ready` - Harvest-ready farms

### Charts
- `GET /api/charts/ndvi-by-village` - NDVI bar chart data
- `GET /api/charts/harvest-area-timeline` - Harvest timeline
- `GET /api/charts/health-distribution` - Health status pie chart

## 📊 Processing Pipeline

### 1. Upload Farm Data (CSV)

Your CSV should have these columns:
```
farm_id, name, Vill_Name, Area, Lang1, Long1, Lang2, Long2, Lang3, Long3, Lang4, Long4
```

Upload via:
```bash
curl -X POST http://localhost:8000/api/farms/upload-csv \
  -F "file=@clean.csv"
```

### 2. Run NDVI Extraction

Use your existing Earth Engine script to extract NDVI, then update via API:

```python
import requests

# After running your EE script and getting ndvi_recent_prev.csv
df = pd.read_csv("ndvi_recent_prev.csv")

ndvi_list = []
for _, row in df.iterrows():
    ndvi_list.append({
        "farm_id": row['farm_id'],
        "recent_date": row['recent_date'],
        "recent_ndvi": row['recent_ndvi'],
        "prev_date": row['prev_date'],
        "prev_ndvi": row['prev_ndvi'],
        "delta": row['delta'],
        "harvest": 1 if (row['recent_ndvi'] < 0.5 and 
                       row['recent_ndvi'] < row['prev_ndvi']) else 0
    })

response = requests.post(
    "http://localhost:8000/api/ndvi/bulk-update",
    json=ndvi_list
)
```

### 3. Query Data for Dashboard

```javascript
// Fetch farms GeoJSON
const response = await fetch('http://localhost:8000/api/farms/geojson');
const geojson = await response.json();

// Get summary stats
const stats = await fetch('http://localhost:8000/api/stats/summary');
const summary = await stats.json();
```

## 🔗 Frontend Integration

Update your React dashboard to use the API:

```typescript
// src/lib/api.ts
const API_BASE = 'http://localhost:8000/api';

export const fetchFarms = async () => {
  const response = await fetch(`${API_BASE}/farms/geojson`);
  return response.json();
};

export const fetchStats = async () => {
  const response = await fetch(`${API_BASE}/stats/summary`);
  return response.json();
};
```

## 🐳 Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## 📝 Notes

- **PostGIS Required**: Database must have PostGIS extension for geospatial queries
- **CORS**: Update `CORS_ORIGINS` in `.env` for production
- **Earth Engine**: Requires authentication and project setup
- **Performance**: Consider adding Redis caching for heavy queries

## 🆘 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Verify connection
psql -U username -d smart_farm_db
```

### Earth Engine Authentication
```bash
# Re-authenticate
earthengine authenticate

# Check credentials
ls ~/.config/earthengine/
```

### CORS Issues
Add your frontend URL to CORS origins in `main.py`:
```python
allow_origins=[
    "http://localhost:8080",
    "https://your-domain.com"
]
```

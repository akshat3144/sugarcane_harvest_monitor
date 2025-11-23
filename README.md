# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/e2454624-4e85-43cb-ac5a-9ad9444c0fa1

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/e2454624-4e85-43cb-ac5a-9ad9444c0fa1) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/e2454624-4e85-43cb-ac5a-9ad9444c0fa1) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)

## Backend CSV to GeoJSON Ingestion

This project ingests farm metadata from CSV, converts to GeoJSON, computes NDVI (mocked), and exposes a FastAPI backend for data upload and retrieval.

### Python dependencies

```
pip install fastapi uvicorn pandas geopandas shapely sqlalchemy geoalchemy2 alembic celery redis pytest httpx
```

### Database

- Set up PostgreSQL with PostGIS extension.
- Configure connection in `.env`.
- Run Alembic migrations (stubs provided).

### Running Locally

- Start backend:
  ```
  uvicorn backend.main:app --reload
  ```
- Start worker (if using Celery):
  ```
  celery -A backend.tasks worker --loglevel=info
  ```
- Run CLI ingestion:
  ```
  python scripts/process_local_csv.py --csv data/clean.csv
  ```
- Run tests:
  ```
  pytest
  ```

### NDVI Extraction

- The NDVI computation is mocked in `backend/services/ndvi.py`.
- To use real Google Earth Engine, replace the mock in `compute_ndvi_for_geometry` with GEE code and add credentials as needed.

### API Endpoints

- `POST /api/upload-csv` — Upload CSV, triggers ingestion, returns job id.
- `GET /api/jobs/{job_id}` — Get job status/logs.
- `GET /api/farms` — List farms (GeoJSON, paginated, filterable).
- `GET /api/farms/{farm_id}` — Get farm geometry + NDVI history.

### Data Validation

- At least 3 valid corners required per farm.
- Invalid rows are rejected and logged.
- Harvest flag: `1` if `recent_ndvi < 0.5` and `recent_ndvi < prev_ndvi`, else `0`.

### Where to Replace NDVI Mock

- See `backend/services/ndvi.py`, function `compute_ndvi_for_geometry`.

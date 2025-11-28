from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from backend.tasks import submit_job, get_job
from backend.services import ingest
import os

router = APIRouter()


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '../../data')

@router.post("/upload-csv")
def upload_csv(file: UploadFile = File(...)):
    # Ensure the upload directory exists at runtime
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, 'wb') as f:
        f.write(file.file.read())
    job_id = submit_job(run_ingest_job, file_path)
    return {"job_id": job_id}

def run_ingest_job(job, file_path):
    # Temporary processing files
    geojson_path = os.path.join(UPLOAD_DIR, 'farms_temp.geojson')
    ndvi_csv_path = os.path.join(UPLOAD_DIR, 'ndvi_temp.csv')
    log_path = os.path.join(UPLOAD_DIR, 'ingest.log')

    try:
        n_ok, n_rej = ingest.full_pipeline(
            file_path,
            geojson_path,
            ndvi_csv_path,
            None,  # No final geojson needed
            log_path
        )
        job.log(f"Rows processed: {n_ok}, rejected: {n_rej}")
        job.log(f"Data saved to PostGIS database")
        
        # Clean up temporary files
        for temp_file in [file_path, geojson_path, ndvi_csv_path]:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
        
        return "Database updated successfully"
    except Exception as e:
        job.log(str(e))
        raise

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "logs": job.logs,
        "result_file": job.result_file
    }

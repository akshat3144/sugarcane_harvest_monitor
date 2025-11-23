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
    geojson_path = os.path.join(UPLOAD_DIR, 'farms.geojson')
    ndvi_csv_path = os.path.join(UPLOAD_DIR, 'ndvi_recent_prev.csv')
    final_geojson_path = os.path.join(UPLOAD_DIR, 'farms_final.geojson')
    log_path = os.path.join(UPLOAD_DIR, 'ingest.log')

    # Remove old files if they exist
    for f in [geojson_path, ndvi_csv_path, final_geojson_path, log_path]:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception as e:
            pass  # Ignore errors in cleanup

    try:
        n_ok, n_rej = ingest.full_pipeline(
            file_path,
            geojson_path,
            ndvi_csv_path,
            final_geojson_path,
            log_path
        )
        job.log(f"Rows processed: {n_ok}, rejected: {n_rej}")
        return final_geojson_path
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

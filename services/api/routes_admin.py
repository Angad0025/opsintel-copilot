# =============================================================
# OpsIntel Copilot — Admin Routes
# =============================================================

from fastapi import APIRouter, Query
from services.api.databricks_client import trigger_pipeline_job, get_job_status

router = APIRouter()


@router.post("/databricks/run-job")
def run_databricks_job(job_id: str = Query(...)):
    """Trigger a Databricks pipeline job."""
    result = trigger_pipeline_job(job_id=job_id)
    return {
        "message": "Job triggered successfully",
        "run_id": result.get("run_id")
    }


@router.get("/databricks/job-status")
def check_job_status(run_id: str = Query(...)):
    """Check the status of a Databricks job run."""
    result = get_job_status(run_id=run_id)
    return {
        "run_id": run_id,
        "state": result.get("state", {}),
        "run_page_url": result.get("run_page_url")
    }
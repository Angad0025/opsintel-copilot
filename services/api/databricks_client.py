# =============================================================
# OpsIntel Copilot — Databricks Client
# Triggers Databricks jobs and checks status
# =============================================================

import requests
import logging
from services.api.secrets_client import get_databricks_config

logger = logging.getLogger(__name__)


def get_headers() -> dict:
    config = get_databricks_config()
    return {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json"
    }


def get_host() -> str:
    config = get_databricks_config()
    return config["host"]


def trigger_pipeline_job(job_id: str) -> dict:
    """Trigger a Databricks job run."""
    url = f"https://{get_host()}/api/2.1/jobs/run-now"
    response = requests.post(
        url,
        headers=get_headers(),
        json={"job_id": job_id}
    )
    response.raise_for_status()
    return response.json()


def get_job_status(run_id: str) -> dict:
    """Get the status of a Databricks job run."""
    url = f"https://{get_host()}/api/2.1/jobs/runs/get"
    response = requests.get(
        url,
        headers=get_headers(),
        params={"run_id": run_id}
    )
    response.raise_for_status()
    return response.json()


def list_recent_runs(job_id: str, limit: int = 10) -> dict:
    """List recent runs of a job."""
    url = f"https://{get_host()}/api/2.1/jobs/runs/list"
    response = requests.get(
        url,
        headers=get_headers(),
        params={"job_id": job_id, "limit": limit}
    )
    response.raise_for_status()
    return response.json()
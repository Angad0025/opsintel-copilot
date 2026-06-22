# =============================================================
# OpsIntel Copilot — Correlation Routes
# =============================================================

from fastapi import APIRouter, Query
from services.api.rds_client import fetch_correlations

router = APIRouter()


@router.get("/correlations")
def get_correlations(
    limit: int = Query(100, le=1000),
    correlation_type: str = Query(None)
):
    """
    Returns cross-domain correlation records.
    Links pipeline failures with security events.
    Optional filter by correlation_type.
    """
    data = fetch_correlations(limit=limit, correlation_type=correlation_type)
    return {
        "count": len(data),
        "correlations": data
    }
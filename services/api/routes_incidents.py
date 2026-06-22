# =============================================================
# OpsIntel Copilot — Incident Routes
# =============================================================

from fastapi import APIRouter, Query
from services.api.rds_client import fetch_incident_summary, fetch_security_alerts

router = APIRouter()


@router.get("/incidents")
def get_incidents(limit: int = Query(100, le=1000)):
    """
    Returns incident summary grouped by hour and region.
    Shows brute force, escalation, impossible travel, large export counts.
    """
    data = fetch_incident_summary(limit=limit)
    return {
        "count": len(data),
        "incidents": data
    }


@router.get("/security-alerts")
def get_security_alerts(
    limit: int = Query(100, le=1000),
    event_type: str = Query(None)
):
    """
    Returns individual security alert events.
    Optional filter by event_type (brute_force, escalation, etc.)
    """
    data = fetch_security_alerts(limit=limit, severity=event_type)
    return {
        "count": len(data),
        "alerts": data
    }
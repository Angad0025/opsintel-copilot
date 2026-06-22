# =============================================================
# OpsIntel Copilot — Timeline Routes
# =============================================================

from fastapi import APIRouter, Query
from services.api.rds_client import fetch_correlations, fetch_security_alerts

router = APIRouter()


@router.get("/timeline")
def get_timeline(limit: int = Query(50, le=500)):
    """
    Returns a chronological timeline of security events
    and correlations combined, sorted by time.
    """
    alerts = fetch_security_alerts(limit=limit)
    correlations = fetch_correlations(limit=limit)

    timeline = []

    for alert in alerts:
        timeline.append({
            "event_time": str(alert.get("event_time", "")),
            "event_type": "security_alert",
            "description": f"{alert.get('event_type')} — {alert.get('user_email')}",
            "severity": "high" if alert.get("is_escalation") or alert.get("is_brute_force") else "medium",
            "source": "security_alerts"
        })

    for corr in correlations:
        timeline.append({
            "event_time": str(corr.get("correlated_at", "")),
            "event_type": "correlation",
            "description": f"{corr.get('correlation_type')} — confidence: {corr.get('confidence_score')}",
            "severity": "high" if float(corr.get("confidence_score") or 0) > 0.8 else "medium",
            "source": "correlations"
        })

    timeline.sort(key=lambda x: x["event_time"], reverse=True)

    return {
        "count": len(timeline),
        "timeline": timeline[:limit]
    }
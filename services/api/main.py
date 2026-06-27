# =============================================================
# OpsIntel Copilot — FastAPI Main Application
# AWS-Native AI Investigation Platform
# =============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.api.routes_incidents import router as incidents_router
from services.api.routes_correlation import router as correlation_router
from services.api.routes_copilot import router as copilot_router
from services.api.routes_admin import router as admin_router
from services.api.routes_timeline import router as timeline_router
from services.api.rds_client import fetch_data_quality

app = FastAPI(
    title="OpsIntel Copilot API",
    description="AWS-Native AI Data Reliability & Security Investigation Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(incidents_router, tags=["Incidents"])
app.include_router(correlation_router, tags=["Correlations"])
app.include_router(copilot_router, tags=["Copilot"])
app.include_router(admin_router, tags=["Admin"])
app.include_router(timeline_router, tags=["Timeline"])


@app.get("/health")
def health_check():
    """Health check endpoint for ECS load balancer."""
    return {
        "status": "healthy",
        "service": "opsintel-copilot-api",
        "version": "1.0.0"
    }


@app.get("/data-quality")
def get_data_quality(limit: int = 100, flag: str = None):
    """Returns data quality results from RDS."""
    data = fetch_data_quality(limit=limit, flag=flag)
    return {
        "count": len(data),
        "results": data
    }
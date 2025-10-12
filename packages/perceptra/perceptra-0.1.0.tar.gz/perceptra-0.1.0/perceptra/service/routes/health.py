from fastapi import APIRouter, Depends, Request
from typing import Dict

from perceptra.service.models import HealthResponse
from perceptra.version import __version__

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """Service health check."""
    classifier = request.app.state.classifier if hasattr(request.app.state, 'classifier') else None
    
    if classifier is None:
        return HealthResponse(
            status="initializing",
            version=__version__,
            calibration_samples=0
        )
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        calibration_samples=classifier.store.count()
    )


@router.get("/ready")
async def readiness_check(request: Request):
    """Kubernetes readiness probe."""
    classifier = request.app.state.classifier if hasattr(request.app.state, 'classifier') else None
    
    if classifier is None or classifier.store.count() == 0:
        return {"ready": False, "reason": "No calibration samples loaded"}
    
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"alive": True}
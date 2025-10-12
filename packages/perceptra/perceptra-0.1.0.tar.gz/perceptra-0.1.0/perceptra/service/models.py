"""Pydantic models for API requests/responses."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Request for object classification."""
    k: int = Field(default=5, ge=1, le=50)
    metadata_hint: Optional[Dict] = None
    return_reasoning: bool = False


class NeighborResponse(BaseModel):
    """Nearest neighbor information."""
    label: str
    distance: float
    metadata: Optional[Dict] = None


class ClassificationResponse(BaseModel):
    """Classification result."""
    predicted_label: str
    confidence: float
    nearest_neighbors: List[NeighborResponse]
    reasoning: Optional[str] = None
    metadata: Optional[Dict] = None


class CalibrationAddRequest(BaseModel):
    """Request to add calibration samples."""
    labels: List[str]
    metadata: Optional[List[Dict]] = None


class CalibrationAddResponse(BaseModel):
    """Response after adding samples."""
    status: str
    added_count: int
    ids: List[str]
    total_samples: int


class CalibrationStatsResponse(BaseModel):
    """Calibration set statistics."""
    total_samples: int
    label_distribution: Dict[str, int]
    embedding_model: str
    embedding_dim: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    calibration_samples: int
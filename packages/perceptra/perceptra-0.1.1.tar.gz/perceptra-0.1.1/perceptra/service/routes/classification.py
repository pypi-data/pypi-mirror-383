from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from typing import Dict
import numpy as np

from perceptra.service.models import ClassificationRequest, ClassificationResponse, NeighborResponse
from perceptra.utils.image import decode_image

router = APIRouter()


def get_classifier(request: Request):
    """Get classifier from app state."""
    return request.app.state.classifier


@router.post("/", response_model=ClassificationResponse)
async def classify_object(
    image: UploadFile = File(...),
    k: int = 5,
    return_reasoning: bool = False,
    classifier = Depends(get_classifier),
    request: Request = None
):
    """Classify a waste object from image crop."""
    
    if classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    
    # Get config from app state
    config = request.app.state.config
    
    # Validate file size
    max_size = config.service.max_image_size_mb * 1024 * 1024
    
    # Read image
    image_bytes = await image.read()
    
    if len(image_bytes) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large. Max size: {config.service.max_image_size_mb}MB"
        )
    
    # Decode image
    try:
        image_array = decode_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    # Classify
    try:
        result = classifier.classify(
            image_crop=image_array,
            k=k,
            return_reasoning=return_reasoning
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
    
    # Convert to response model
    neighbors = [
        NeighborResponse(
            label=n.label,
            distance=n.distance,
            metadata=n.metadata if return_reasoning else None
        )
        for n in result.nearest_neighbors
    ]
    
    return ClassificationResponse(
        predicted_label=result.predicted_label,
        confidence=result.confidence,
        nearest_neighbors=neighbors,
        reasoning=result.reasoning,
        metadata=result.metadata
    )
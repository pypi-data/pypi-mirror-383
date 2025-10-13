from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body, Request
from typing import Dict, List
import json

from perceptra.service.models import (
    CalibrationAddRequest,
    CalibrationAddResponse,
    CalibrationStatsResponse
)
from perceptra.utils.image import decode_image

router = APIRouter()


def get_calibration_manager(request: Request):
    """Get calibration manager from app state."""
    return request.app.state.calibration_manager


@router.post("/add", response_model=CalibrationAddResponse)
async def add_calibration_samples(
    images: List[UploadFile] = File(...),
    labels: str = Body(...),
    metadata: str = Body(None),
    calibration_manager = Depends(get_calibration_manager)
):
    """Add new reference samples to calibration set."""
    
    if calibration_manager is None:
        raise HTTPException(status_code=503, detail="Calibration manager not initialized")
    
    # Parse labels
    try:
        labels_list = json.loads(labels)
    except:
        raise HTTPException(status_code=400, detail="Invalid labels JSON")
    
    if len(images) != len(labels_list):
        raise HTTPException(
            status_code=400,
            detail=f"Number of images ({len(images)}) must match labels ({len(labels_list)})"
        )
    
    # Parse metadata if provided
    metadata_list = None
    if metadata:
        try:
            metadata_list = json.loads(metadata)
        except:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    
    # Decode images
    image_arrays = []
    for img in images:
        image_bytes = await img.read()
        try:
            image_array = decode_image(image_bytes)
            image_arrays.append(image_array)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    # Add to calibration set
    try:
        result = calibration_manager.add_samples(
            images=image_arrays,
            labels=labels_list,
            metadata=metadata_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add samples: {str(e)}")
    
    return CalibrationAddResponse(**result)


@router.get("/stats", response_model=CalibrationStatsResponse)
async def get_calibration_stats(
    calibration_manager = Depends(get_calibration_manager)
):
    """Get statistics about the calibration set."""
    if calibration_manager is None:
        raise HTTPException(status_code=503, detail="Calibration manager not initialized")
    
    stats = calibration_manager.get_statistics()
    return CalibrationStatsResponse(**stats)


@router.post("/export")
async def export_calibration_set(
    path: str = Body(..., embed=True),
    calibration_manager = Depends(get_calibration_manager)
):
    """Export calibration set to disk."""
    try:
        result = calibration_manager.export_calibration_set(path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.delete("/samples")
async def delete_calibration_samples(
    sample_ids: List[str] = Body(...),
    calibration_manager = Depends(get_calibration_manager)
):
    """Delete samples from calibration set."""
    try:
        result = calibration_manager.delete_samples(sample_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
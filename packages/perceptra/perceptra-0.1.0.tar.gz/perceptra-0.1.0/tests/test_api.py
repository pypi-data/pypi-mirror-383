"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image
import numpy as np


def test_health_endpoint(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health/")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "calibration_samples" in data


def test_liveness_endpoint(test_client):
    """Test liveness probe."""
    response = test_client.get("/health/live")
    
    assert response.status_code == 200
    assert response.json()["alive"] is True


def test_readiness_endpoint(test_client):
    """Test readiness probe."""
    response = test_client.get("/health/ready")
    
    assert response.status_code == 200
    assert "ready" in response.json()


def create_test_image():
    """Create test image bytes."""
    img = Image.fromarray(
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    )
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_classification_endpoint_no_calibration(test_client):
    """Test classification without calibration data."""
    img_bytes = create_test_image()
    
    response = test_client.post(
        "/classify/",
        files={"image": ("test.jpg", img_bytes, "image/jpeg")},
        data={"k": "5", "return_reasoning": "false"}  # String values for form data
    )
    
    # Should return unknown if no calibration data
    assert response.status_code == 200
    data = response.json()
    assert "predicted_label" in data
    assert "confidence" in data
    assert data["predicted_label"] == "unknown"  # No calibration data

def test_calibration_stats_endpoint(test_client):
    """Test calibration statistics endpoint."""
    response = test_client.get("/calibration/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_samples" in data
    assert "label_distribution" in data
    assert "embedding_model" in data

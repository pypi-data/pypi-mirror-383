"""Tests for DINOv2 embeddings."""

import pytest
import numpy as np


def test_dinov2_initialization():
    """Test DINOv2 initialization."""
    try:
        from perceptra.core.embeddings.dinov2 import DINOv2Embedding
        
        encoder = DINOv2Embedding(
            model_name="dinov2_vits14",
            device="cpu"
        )
        
        assert encoder.embedding_dim == 384
        assert encoder.model_name == "dinov2_vits14"
    except ImportError:
        pytest.skip("PyTorch not available")


def test_dinov2_encode():
    """Test DINOv2 encoding."""
    try:
        from perceptra.core.embeddings.dinov2 import DINOv2Embedding
        
        encoder = DINOv2Embedding(
            model_name="dinov2_vits14",
            device="cpu"
        )
        
        images = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        embeddings = encoder.encode(images)
        
        assert embeddings.shape == (3, 384)
        assert embeddings.dtype == np.float32
        
        # Check normalization
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(3), decimal=5)
    except ImportError:
        pytest.skip("PyTorch not available")


def test_dinov2_batch_encode():
    """Test batch encoding."""
    try:
        from perceptra.core.embeddings.dinov2 import DINOv2Embedding
        
        encoder = DINOv2Embedding(
            model_name="dinov2_vits14",
            device="cpu"
        )
        
        images = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            for _ in range(50)
        ]
        
        embeddings = encoder.encode_batch(images, batch_size=16)
        
        assert embeddings.shape[0] == 50
        assert embeddings.shape[1] == 384
    except ImportError:
        pytest.skip("PyTorch not available")


def test_dinov2_patch_tokens():
    """Test patch token extraction."""
    try:
        from perceptra.core.embeddings.dinov2 import DINOv2Embedding
        
        encoder = DINOv2Embedding(device="cpu")
        
        images = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)]
        
        cls_emb, patch_emb = encoder.encode_with_patch_tokens(images)
        
        assert cls_emb.shape[0] == 1
        if patch_emb is not None:
            assert patch_emb.shape[0] == 1
            assert patch_emb.ndim == 3
    except ImportError:
        pytest.skip("PyTorch not available")


def test_dinov2_similarity():
    """Test similarity computation."""
    try:
        from perceptra.core.embeddings.dinov2 import DINOv2Embedding
        
        encoder = DINOv2Embedding(device="cpu")
        
        img1 = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)]
        img2 = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)]
        
        similarity = encoder.compute_similarity(img1, img2)
        
        assert similarity.shape == (1, 1)
        assert -1 <= similarity[0, 0] <= 1
    except ImportError:
        pytest.skip("PyTorch not available")
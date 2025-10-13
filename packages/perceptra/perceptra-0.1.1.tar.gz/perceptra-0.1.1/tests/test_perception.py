"""Tests for perception encoder."""

import pytest
import numpy as np
from perceptra.core.embeddings.perception import PerceptionEmbedding


@pytest.mark.skipif(
    not hasattr(PerceptionEmbedding, '__init__'),
    reason="PyTorch not installed"
)
def test_perception_initialization():
    """Test perception encoder initialization."""
    try:
        encoder = PerceptionEmbedding(model_name="perception-v1", device="cpu")
        assert encoder.embedding_dim == 512
        assert encoder.model_name == "perception-v1"
    except ImportError:
        pytest.skip("PyTorch not available")


@pytest.mark.skipif(
    not hasattr(PerceptionEmbedding, '__init__'),
    reason="PyTorch not installed"
)
def test_perception_encode():
    """Test perception encoding."""
    try:
        encoder = PerceptionEmbedding(device="cpu")
        
        images = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        embeddings = encoder.encode(images)
        
        assert embeddings.shape == (3, 512)
        assert embeddings.dtype == np.float32
        
        # Check normalization
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(3), decimal=5)
    except ImportError:
        pytest.skip("PyTorch not available")


@pytest.mark.skipif(
    not hasattr(PerceptionEmbedding, '__init__'),
    reason="PyTorch not installed"
)
def test_perception_save_load(tmp_path):
    """Test saving and loading perception model."""
    try:
        encoder = PerceptionEmbedding(device="cpu")
        
        # Save model
        save_path = tmp_path / "perception.pth"
        encoder.save_model(str(save_path))
        
        assert save_path.exists()
        
        # Load in new encoder
        new_encoder = PerceptionEmbedding(
            device="cpu",
            pretrained_path=str(save_path)
        )
        
        # Test that both produce same embeddings
        test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        emb1 = encoder.encode([test_img])
        emb2 = new_encoder.encode([test_img])
        
        np.testing.assert_array_almost_equal(emb1, emb2, decimal=5)
    except ImportError:
        pytest.skip("PyTorch not available")
"""Tests for Meta Perception Encoder."""

import pytest
import numpy as np


@pytest.mark.skipif(
    True,  # Skip by default as it requires HuggingFace access
    reason="Requires HuggingFace model access"
)
def test_meta_perception_initialization():
    """Test Meta Perception Encoder initialization."""
    from perceptra.core.embeddings.meta_perception import MetaPerceptionEmbedding
    
    encoder = MetaPerceptionEmbedding(
        model_name="PE-Core-L14-336",
        device="cpu"
    )
    
    assert encoder.embedding_dim == 1024
    assert encoder.model_name == "PE-Core-L14-336"


@pytest.mark.skipif(
    True,
    reason="Requires HuggingFace model access"
)
def test_meta_perception_encode():
    """Test Meta Perception encoding."""
    from perceptra.core.embeddings.meta_perception import MetaPerceptionEmbedding
    
    encoder = MetaPerceptionEmbedding(
        model_name="PE-Core-B16-224",
        device="cpu"
    )
    
    images = [
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        for _ in range(3)
    ]
    
    embeddings = encoder.encode(images)
    
    assert embeddings.shape == (3, 768)
    assert embeddings.dtype == np.float32
    
    # Check normalization
    norms = np.linalg.norm(embeddings, axis=1)
    np.testing.assert_array_almost_equal(norms, np.ones(3), decimal=5)


@pytest.mark.skipif(
    True,
    reason="Requires HuggingFace model access"
)
def test_meta_perception_batch_encode():
    """Test batch encoding."""
    from perceptra.core.embeddings.meta_perception import MetaPerceptionEmbedding
    
    encoder = MetaPerceptionEmbedding(device="cpu")
    
    images = [
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        for _ in range(50)
    ]
    
    embeddings = encoder.encode_batch(images, batch_size=16)
    
    assert embeddings.shape[0] == 50
    assert embeddings.shape[1] == encoder.embedding_dim

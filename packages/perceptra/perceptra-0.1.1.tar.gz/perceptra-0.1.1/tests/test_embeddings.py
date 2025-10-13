"""Embedding backend tests."""

import pytest
import numpy as np
from perceptra.core.embeddings.base import EmbeddingBackend


class DummyEmbedding(EmbeddingBackend):
    """Dummy embedding for testing."""
    
    @property
    def embedding_dim(self):
        return 64
    
    def encode(self, images):
        return np.random.randn(len(images), 64).astype(np.float32)


def test_embedding_backend_interface():
    """Test embedding backend interface."""
    embedder = DummyEmbedding("dummy", "cpu")
    
    assert embedder.model_name == "dummy"
    assert embedder.device == "cpu"
    assert embedder.embedding_dim == 64


def test_embedding_encode():
    """Test embedding encoding."""
    embedder = DummyEmbedding("dummy", "cpu")
    
    images = [
        np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        for _ in range(3)
    ]
    
    embeddings = embedder.encode(images)
    
    assert embeddings.shape == (3, 64)
    assert embeddings.dtype == np.float32
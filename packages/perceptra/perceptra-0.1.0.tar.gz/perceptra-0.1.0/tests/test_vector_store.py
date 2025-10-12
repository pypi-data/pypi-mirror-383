"""Tests for vector stores."""

import pytest
import numpy as np
from perceptra.core.vector_store.faiss_store import FAISSVectorStore


def test_faiss_store_insert_search():
    """Test FAISS store insert and search."""
    dim = 128
    store = FAISSVectorStore(dim=dim)
    
    # Insert vectors
    embeddings = np.random.randn(10, dim).astype(np.float32)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    metadata = [{"label": f"class_{i % 3}", "id": i} for i in range(10)]
    
    ids = store.insert(embeddings, metadata)
    
    assert len(ids) == 10
    assert store.count() == 10
    
    # Search
    query = np.random.randn(dim).astype(np.float32)
    query /= np.linalg.norm(query)
    
    distances, neighbors_meta = store.search(query, k=5)
    
    assert len(distances) == 5
    assert len(neighbors_meta) == 5
    assert all(isinstance(m, dict) for m in neighbors_meta)


def test_faiss_store_save_load(tmp_path):
    """Test saving and loading FAISS store."""
    dim = 64
    store = FAISSVectorStore(dim=dim)
    
    # Add data
    embeddings = np.random.randn(5, dim).astype(np.float32)
    metadata = [{"label": "test", "id": i} for i in range(5)]
    store.insert(embeddings, metadata)
    
    # Save
    save_path = tmp_path / "test.index"
    store.save(str(save_path))
    
    # Load into new store
    new_store = FAISSVectorStore(dim=dim)
    new_store.load(str(save_path))
    
    assert new_store.count() == 5
    assert new_store.get_label_distribution() == {"test": 5}

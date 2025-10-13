"""Tests for Qdrant vector store."""

import pytest
import numpy as np
from perceptra.core.vector_store.qdrant_store import QdrantVectorStore


@pytest.mark.skipif(
    not hasattr(QdrantVectorStore, '__init__'),
    reason="Qdrant not installed"
)
def test_qdrant_initialization():
    """Test Qdrant store initialization."""
    try:
        store = QdrantVectorStore(
            dim=128,
            collection_name="test_collection",
            in_memory=True
        )
        
        assert store.dim == 128
        assert store.collection_name == "test_collection"
        assert store.count() == 0
    except ImportError:
        pytest.skip("Qdrant not available")


@pytest.mark.skipif(
    not hasattr(QdrantVectorStore, '__init__'),
    reason="Qdrant not installed"
)
def test_qdrant_insert_search():
    """Test Qdrant insert and search."""
    try:
        store = QdrantVectorStore(dim=128, in_memory=True)
        
        # Insert vectors
        embeddings = np.random.randn(10, 128).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        metadata = [
            {
                "label": f"class_{i % 3}",
                "id": i,
                "value": i * 10
            }
            for i in range(10)
        ]
        
        ids = store.insert(embeddings, metadata)
        
        assert len(ids) == 10
        assert store.count() == 10
        
        # Search
        query = np.random.randn(128).astype(np.float32)
        query /= np.linalg.norm(query)
        
        distances, neighbors_meta = store.search(query, k=5)
        
        assert len(distances) == 5
        assert len(neighbors_meta) == 5
        assert all(isinstance(m, dict) for m in neighbors_meta)
    except ImportError:
        pytest.skip("Qdrant not available")


@pytest.mark.skipif(
    not hasattr(QdrantVectorStore, '__init__'),
    reason="Qdrant not installed"
)
def test_qdrant_filtering():
    """Test Qdrant advanced filtering."""
    try:
        store = QdrantVectorStore(dim=64, in_memory=True)
        
        # Add data with metadata
        embeddings = np.random.randn(20, 64).astype(np.float32)
        embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        metadata = []
        for i in range(20):
            meta = {
                "label": "pipe" if i < 10 else "bottle",
                "length_cm": 10.0 + i,
                "color": "gray" if i % 2 == 0 else "white",
                "location": "beach" if i < 15 else "river"
            }
            metadata.append(meta)
        
        store.insert(embeddings, metadata)
        
        # Test exact match filter
        query = np.random.randn(64).astype(np.float32)
        query /= np.linalg.norm(query)
        
        distances, neighbors = store.search(
            query,
            k=10,
            filter_dict={"label": "pipe"}
        )
        
        assert all(n["label"] == "pipe" for n in neighbors)
        
        # Test range filter
        distances, neighbors = store.search(
            query,
            k=10,
            filter_dict={"length_cm": {"gte": 15, "lte": 20}}
        )
        
        for n in neighbors:
            assert 15 <= n["length_cm"] <= 20
        
        # Test multiple value filter
        distances, neighbors = store.search(
            query,
            k=10,
            filter_dict={"color": ["gray", "white"]}
        )
        
        assert all(n["color"] in ["gray", "white"] for n in neighbors)
    except ImportError:
        pytest.skip("Qdrant not available")


@pytest.mark.skipif(
    not hasattr(QdrantVectorStore, '__init__'),
    reason="Qdrant not installed"
)
def test_qdrant_delete():
    """Test Qdrant delete operation."""
    try:
        store = QdrantVectorStore(dim=64, in_memory=True)
        
        # Insert data
        embeddings = np.random.randn(5, 64).astype(np.float32)
        metadata = [{"label": "test", "id": i} for i in range(5)]
        
        ids = store.insert(embeddings, metadata)
        assert store.count() == 5
        
        # Delete some points
        deleted = store.delete(ids[:2])
        assert deleted == 2
        assert store.count() == 3
    except ImportError:
        pytest.skip("Qdrant not available")


@pytest.mark.skipif(
    not hasattr(QdrantVectorStore, '__init__'),
    reason="Qdrant not installed"
)
def test_qdrant_label_distribution():
    """Test label distribution retrieval."""
    try:
        store = QdrantVectorStore(dim=64, in_memory=True)
        
        # Insert data
        embeddings = np.random.randn(15, 64).astype(np.float32)
        metadata = (
            [{"label": "pipe"} for _ in range(5)] +
            [{"label": "bottle"} for _ in range(7)] +
            [{"label": "can"} for _ in range(3)]
        )
        
        store.insert(embeddings, metadata)
        
        distribution = store.get_label_distribution()
        
        assert distribution["pipe"] == 5
        assert distribution["bottle"] == 7
        assert distribution["can"] == 3
    except ImportError:
        pytest.skip("Qdrant not available")

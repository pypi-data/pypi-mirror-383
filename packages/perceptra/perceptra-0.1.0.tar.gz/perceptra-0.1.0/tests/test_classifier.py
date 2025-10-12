"""Tests for classifier."""

import pytest
import numpy as np

from perceptra.core.classifier import ObjectClassifier
from perceptra.core.vector_store.faiss_store import FAISSVectorStore
from perceptra.config import ClassifierConfig


def test_classifier_initialization(mock_embedder):
    """Test classifier initialization."""
    store = FAISSVectorStore(dim=mock_embedder.embedding_dim)
    config = ClassifierConfig()
    
    classifier = ObjectClassifier(mock_embedder, store, config)
    
    assert classifier.embedder == mock_embedder
    assert classifier.store == store
    assert classifier.config == config


def test_classification_with_calibration(mock_embedder, sample_images, sample_labels):
    """Test classification with calibration set."""
    store = FAISSVectorStore(dim=mock_embedder.embedding_dim)
    config = ClassifierConfig()
    
    # Add calibration samples
    embeddings = mock_embedder.encode(sample_images)
    metadata = [{"label": label} for label in sample_labels]
    store.insert(embeddings, metadata)
    
    classifier = ObjectClassifier(mock_embedder, store, config)
    
    # Classify
    test_image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    result = classifier.classify(test_image, k=3)
    
    assert result.predicted_label in sample_labels + [config.unknown_label]
    assert 0 <= result.confidence <= 1
    assert len(result.nearest_neighbors) <= 3


def test_classification_empty_store(mock_embedder):
    """Test classification with empty calibration set."""
    from perceptra.core.vector_store.faiss_store import FAISSVectorStore
    from perceptra.core.classifier import ObjectClassifier
    from perceptra.config import ClassifierConfig
    
    store = FAISSVectorStore(dim=mock_embedder.embedding_dim)
    config = ClassifierConfig()
    
    classifier = ObjectClassifier(mock_embedder, store, config)
    
    test_image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    result = classifier.classify(test_image, k=3)
    
    assert result.predicted_label == config.unknown_label
    assert result.confidence == 0.0
    assert len(result.nearest_neighbors) == 0
    assert result.reasoning == "No similar objects found in calibration set"

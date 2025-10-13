"""PERCEPTRA - Vector-based waste classification system."""

from perceptra.version import __version__
from perceptra.config import (
    PERCEPTRAConfig,
    EmbeddingConfig,
    VectorStoreConfig,
    ClassifierConfig,
    CalibrationConfig,
    ServiceConfig,
    load_config
)
from perceptra.core.classifier import ObjectClassifier, ClassificationResult
from perceptra.core.calibration import CalibrationManager
from perceptra.core.embeddings.base import EmbeddingBackend
from perceptra.core.vector_store.base import VectorStore

# Conditional imports for optional dependencies
try:
    from perceptra.core.embeddings.clip import CLIPEmbedding
    __all_embeddings__ = ["EmbeddingBackend", "CLIPEmbedding"]
except ImportError:
    __all_embeddings__ = ["EmbeddingBackend"]

try:
    from perceptra.core.vector_store.faiss_store import FAISSVectorStore
    __all_stores__ = ["VectorStore", "FAISSVectorStore"]
except ImportError:
    __all_stores__ = ["VectorStore"]

__all__ = [
    "__version__",
    "PERCEPTRAConfig",
    "EmbeddingConfig",
    "VectorStoreConfig",
    "ClassifierConfig",
    "CalibrationConfig",
    "ServiceConfig",
    "load_config",
    "ObjectClassifier",
    "ClassificationResult",
    "CalibrationManager",
] + __all_embeddings__ + __all_stores__
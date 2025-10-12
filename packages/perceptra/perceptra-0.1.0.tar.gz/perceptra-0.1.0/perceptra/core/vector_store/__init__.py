"""Vector store implementations."""

from perceptra.core.vector_store.base import VectorStore

__all__ = ["VectorStore"]

try:
    from perceptra.core.vector_store.faiss_store import FAISSVectorStore
    __all__.append("FAISSVectorStore")
except ImportError:
    pass

"""Embedding backends."""

from perceptra.core.embeddings.base import EmbeddingBackend

__all__ = ["EmbeddingBackend"]

try:
    from perceptra.core.embeddings.clip import CLIPEmbedding
    __all__.append("CLIPEmbedding")
except ImportError:
    pass
"""Base class for embedding backends."""

from abc import ABC, abstractmethod
from typing import List
import numpy as np


class EmbeddingBackend(ABC):
    """Abstract interface for embedding models."""
    
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
    
    @abstractmethod
    def encode(self, images: List[np.ndarray]) -> np.ndarray:
        """Generate embeddings for image crops.
        
        Args:
            images: List of image arrays [H, W, C] in RGB format
        
        Returns:
            embeddings: Array of shape [N, embedding_dim]
        """
        pass
    
    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Dimension of embedding vectors."""
        pass
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess single image. Override if needed."""
        return image
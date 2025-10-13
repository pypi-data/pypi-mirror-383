"""Base class for vector stores."""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import numpy as np


class VectorStore(ABC):
    """Abstract interface for vector databases."""
    
    @abstractmethod
    def insert(self, embeddings: np.ndarray, metadata: List[Dict]) -> List[str]:
        """Insert embeddings with metadata.
        
        Args:
            embeddings: Array of shape [N, dim]
            metadata: List of metadata dicts for each embedding
        
        Returns:
            ids: List of unique identifiers for inserted vectors
        """
        pass
    
    @abstractmethod
    def search(
        self, 
        query: np.ndarray, 
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Tuple[np.ndarray, List[Dict]]:
        """Find k-nearest neighbors.
        
        Args:
            query: Query embedding of shape [dim]
            k: Number of neighbors to retrieve
            filter_dict: Optional metadata filters
        
        Returns:
            distances: Array of shape [k]
            metadata: List of metadata dicts for each neighbor
        """
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> int:
        """Delete vectors by IDs.
        
        Returns:
            Number of deleted vectors
        """
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Persist vector store to disk."""
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """Load vector store from disk."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Return total number of vectors."""
        pass
    
    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of labels in the store."""
        return {}
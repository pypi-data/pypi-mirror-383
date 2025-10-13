"""FAISS-based vector store implementation."""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pickle
from pathlib import Path

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from perceptra.core.vector_store.base import VectorStore


class FAISSVectorStore(VectorStore):
    """FAISS-based in-memory vector store with metadata."""
    
    def __init__(
        self, 
        dim: int,
        index_type: str = "Flat",
        metric: str = "cosine"
    ):
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS not installed. Install with: pip install perceptra[faiss]"
            )
        
        self.dim = dim
        self.metric = metric
        
        # Create FAISS index
        if metric == "cosine":
            # Cosine similarity = inner product on normalized vectors
            self.index = faiss.IndexFlatIP(dim)
        elif metric == "l2":
            if index_type == "Flat":
                self.index = faiss.IndexFlatL2(dim)
            elif index_type == "HNSW":
                self.index = faiss.IndexHNSWFlat(dim, 32)
            else:
                raise ValueError(f"Unsupported index type: {index_type}")
        else:
            raise ValueError(f"Unsupported metric: {metric}")
        
        # Store metadata separately
        self.metadata_store: List[Dict] = []
        self.id_to_idx: Dict[str, int] = {}
        self._next_id = 0
    
    def insert(self, embeddings: np.ndarray, metadata: List[Dict]) -> List[str]:
        """Insert embeddings into FAISS index."""
        assert len(embeddings) == len(metadata), "Mismatch between embeddings and metadata"
        
        # Normalize for cosine similarity
        if self.metric == "cosine":
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / (norms + 1e-8)
        
        # Add to index
        embeddings = embeddings.astype('float32')
        self.index.add(embeddings)
        
        # Generate IDs and store metadata
        ids = []
        for meta in metadata:
            id_str = f"vec_{self._next_id}"
            self.id_to_idx[id_str] = len(self.metadata_store)
            self.metadata_store.append({**meta, "_id": id_str})
            ids.append(id_str)
            self._next_id += 1
        
        return ids
    
    def search(
        self,
        query: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Tuple[np.ndarray, List[Dict]]:
        """Search for nearest neighbors."""

        # Handle empty store
        if self.count() == 0:
            return np.array([]), []

        # Normalize query for cosine similarity
        if self.metric == "cosine":
            query = query / (np.linalg.norm(query) + 1e-8)
        
        query = query.astype('float32').reshape(1, -1)
        
        # Search (retrieve more if filtering)
        search_k = k * 10 if filter_dict else k

        # FAISS requires k > 0
        if search_k == 0:
            return np.array([]), []

        distances, indices = self.index.search(query, search_k)
        
        # Get metadata
        results_meta = []
        results_dist = []
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                break
            
            meta = self.metadata_store[idx]
            
            # Apply filters
            if filter_dict and not self._matches_filter(meta, filter_dict):
                continue
            
            results_meta.append(meta)
            results_dist.append(dist)
            
            if len(results_meta) >= k:
                break
        
        return np.array(results_dist), results_meta
    
    def _matches_filter(self, meta: Dict, filter_dict: Dict) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_dict.items():
            if key not in meta or meta[key] != value:
                return False
        return True
    
    def delete(self, ids: List[str]) -> int:
        """Delete vectors by ID (mark as deleted in metadata)."""
        deleted = 0
        for id_str in ids:
            if id_str in self.id_to_idx:
                idx = self.id_to_idx[id_str]
                self.metadata_store[idx]["_deleted"] = True
                deleted += 1
        return deleted
    
    def save(self, path: str) -> None:
        """Save index and metadata to disk."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(path_obj))
        
        # Save metadata
        meta_path = path_obj.with_suffix('.meta.pkl')
        with open(meta_path, 'wb') as f:
            pickle.dump({
                'metadata_store': self.metadata_store,
                'id_to_idx': self.id_to_idx,
                'next_id': self._next_id,
                'dim': self.dim,
                'metric': self.metric
            }, f)
    
    def load(self, path: str) -> None:
        """Load index and metadata from disk."""
        path_obj = Path(path)
        
        # Load FAISS index
        self.index = faiss.read_index(str(path_obj))
        
        # Load metadata
        meta_path = path_obj.with_suffix('.meta.pkl')
        with open(meta_path, 'rb') as f:
            data = pickle.load(f)
            self.metadata_store = data['metadata_store']
            self.id_to_idx = data['id_to_idx']
            self._next_id = data['next_id']
            self.dim = data['dim']
            self.metric = data['metric']
    
    def count(self) -> int:
        """Return number of vectors."""
        return self.index.ntotal
    
    def get_label_distribution(self) -> Dict[str, int]:
        """Get label counts."""
        from collections import Counter
        labels = [m.get('label', 'unknown') for m in self.metadata_store 
                  if not m.get('_deleted', False)]
        return dict(Counter(labels))
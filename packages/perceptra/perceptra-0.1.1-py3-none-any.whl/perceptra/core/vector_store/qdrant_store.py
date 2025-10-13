"""Qdrant vector store implementation."""

from typing import Dict, List, Tuple, Optional
import numpy as np
import uuid

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
        Range
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from perceptra.core.vector_store.base import VectorStore


class QdrantVectorStore(VectorStore):
    """Qdrant-based vector store with advanced filtering.
    
    Qdrant is a production-grade vector database with:
    - Advanced filtering on metadata
    - Distributed deployment support
    - HNSW index for fast similarity search
    - Payload (metadata) support
    - REST API for remote access
    """
    
    def __init__(
        self,
        dim: int,
        collection_name: str = "perceptra_objects",
        metric: str = "cosine",
        host: str = "localhost",
        port: int = 6333,
        url: str = None,
        api_key: str = None,
        in_memory: bool = False
    ):
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "Qdrant not installed. "
                "Install with: pip install perceptra[qdrant]"
            )
        
        self.dim = dim
        self.collection_name = collection_name
        self.metric = metric
        
        # Initialize Qdrant client
        if in_memory:
            self.client = QdrantClient(":memory:")
        elif url:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            self.client = QdrantClient(host=host, port=port, api_key=api_key)
        
        # Map metric to Qdrant distance
        metric_map = {
            "cosine": Distance.COSINE,
            "l2": Distance.EUCLID,
            "dot": Distance.DOT
        }
        
        if metric not in metric_map:
            raise ValueError(f"Unsupported metric: {metric}")
        
        self.qdrant_distance = metric_map[metric]
        
        # Create collection if it doesn't exist
        self._initialize_collection()
    
    def _initialize_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dim,
                    distance=self.qdrant_distance
                )
            )
            print(f"Created Qdrant collection: {self.collection_name}")
    
    def insert(self, embeddings: np.ndarray, metadata: List[Dict]) -> List[str]:
        """Insert embeddings with metadata into Qdrant.
        
        Args:
            embeddings: Array of shape [N, dim]
            metadata: List of metadata dicts for each embedding
        
        Returns:
            List of point IDs (UUIDs)
        """
        assert len(embeddings) == len(metadata), "Mismatch between embeddings and metadata"
        
        # Normalize for cosine similarity
        if self.metric == "cosine":
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / (norms + 1e-8)
        
        # Create points
        points = []
        ids = []
        
        for i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
            point_id = str(uuid.uuid4())
            ids.append(point_id)
            
            # Ensure metadata values are JSON-serializable
            clean_meta = self._clean_metadata(meta)
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload=clean_meta
                )
            )
        
        # Batch insert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return ids
    
    def _clean_metadata(self, metadata: Dict) -> Dict:
        """Clean metadata to ensure JSON compatibility."""
        clean = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean[key] = value
            elif isinstance(value, (list, tuple)):
                clean[key] = list(value)
            elif isinstance(value, dict):
                clean[key] = self._clean_metadata(value)
            elif value is None:
                clean[key] = None
            else:
                clean[key] = str(value)
        return clean
    
    def search(
        self,
        query: np.ndarray,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Tuple[np.ndarray, List[Dict]]:
        """Search for nearest neighbors with optional filtering.
        
        Args:
            query: Query embedding of shape [dim]
            k: Number of neighbors to retrieve
            filter_dict: Optional filters, e.g.:
                {
                    "label": "pipe",
                    "length_cm": {"gte": 10, "lte": 20},
                    "color": ["gray", "white"]
                }
        
        Returns:
            distances: Array of distances/scores
            metadata: List of metadata dicts
        """
        # Check if collection is empty
        collection_info = self.client.get_collection(self.collection_name)
        if collection_info.points_count == 0:
            return np.array([]), []
        
        # Normalize query for cosine similarity
        if self.metric == "cosine":
            query = query / (np.linalg.norm(query) + 1e-8)
        
        # Build Qdrant filter
        qdrant_filter = None
        if filter_dict:
            qdrant_filter = self._build_filter(filter_dict)
        
        # Search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query.tolist(),
            limit=k,
            query_filter=qdrant_filter
        )
        
        # Extract results
        distances = []
        metadata_list = []
        
        for hit in search_result:
            distances.append(hit.score)
            metadata_list.append(hit.payload)
        
        return np.array(distances), metadata_list
    
    def _build_filter(self, filter_dict: Dict) -> Filter:
        """Build Qdrant filter from dictionary.
        
        Supports:
            - Exact match: {"label": "pipe"}
            - List match: {"color": ["gray", "white"]}
            - Range: {"length_cm": {"gte": 10, "lte": 20}}
        """
        must_conditions = []
        
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                # Range filter
                if "gte" in value or "lte" in value or "gt" in value or "lt" in value:
                    range_filter = {}
                    if "gte" in value:
                        range_filter["gte"] = value["gte"]
                    if "lte" in value:
                        range_filter["lte"] = value["lte"]
                    if "gt" in value:
                        range_filter["gt"] = value["gt"]
                    if "lt" in value:
                        range_filter["lt"] = value["lt"]
                    
                    must_conditions.append(
                        FieldCondition(key=key, range=Range(**range_filter))
                    )
            elif isinstance(value, list):
                # Multiple values (OR)
                for v in value:
                    must_conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=v))
                    )
            else:
                # Exact match
                must_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
        
        if must_conditions:
            return Filter(must=must_conditions)
        return None
    
    def delete(self, ids: List[str]) -> int:
        """Delete vectors by IDs.
        
        Returns:
            Number of deleted vectors
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
        return len(ids)
    
    def save(self, path: str) -> None:
        """Save collection snapshot.
        
        Note: For Qdrant, this creates a snapshot on the server.
        Use backup/restore features for production.
        """
        try:
            snapshot = self.client.create_snapshot(
                collection_name=self.collection_name
            )
            print(f"Created snapshot: {snapshot.name}")
            print(f"Note: Snapshot saved on Qdrant server, not to local path")
        except Exception as e:
            print(f"Warning: Could not create snapshot: {e}")
    
    def load(self, path: str) -> None:
        """Load collection from snapshot.
        
        Note: For Qdrant, this would typically be done via server API.
        """
        print(f"Note: Qdrant load should be done via server snapshot restore")
    
    def count(self) -> int:
        """Return total number of vectors."""
        collection_info = self.client.get_collection(self.collection_name)
        return collection_info.points_count
    
    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of labels in the store.
        
        Note: This requires scrolling through all points.
        May be slow for large collections.
        """
        from collections import Counter
        
        labels = []
        offset = None
        
        while True:
            # Scroll through points
            records, offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            if not records:
                break
            
            for record in records:
                if 'label' in record.payload:
                    labels.append(record.payload['label'])
            
            if offset is None:
                break
        
        return dict(Counter(labels))
    
    def clear_collection(self) -> None:
        """Delete all points in the collection."""
        self.client.delete_collection(self.collection_name)
        self._initialize_collection()
        print(f"Cleared collection: {self.collection_name}")

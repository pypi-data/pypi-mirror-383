"""Calibration set management."""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
import numpy as np

from perceptra.core.embeddings.base import EmbeddingBackend
from perceptra.core.vector_store.base import VectorStore
from perceptra.config import CalibrationConfig


class CalibrationManager:
    """Manages calibration set lifecycle."""
    
    def __init__(
        self,
        embedding_backend: EmbeddingBackend,
        vector_store: VectorStore,
        config: CalibrationConfig
    ):
        self.embedder = embedding_backend
        self.store = vector_store
        self.config = config
        self._insert_count = 0
    
    def add_samples(
        self,
        images: List[np.ndarray],
        labels: List[str],
        metadata: Optional[List[Dict]] = None
    ) -> Dict:
        """Add reference samples to calibration set.
        
        Args:
            images: List of RGB image arrays
            labels: Corresponding labels
            metadata: Optional metadata dicts per sample
        
        Returns:
            Status dict with added IDs
        """
        if len(images) != len(labels):
            raise ValueError("Number of images must match number of labels")
        
        # Generate embeddings
        embeddings = self.embedder.encode(images)
        
        # Enrich metadata
        enriched_metadata = []
        for i, label in enumerate(labels):
            meta = {
                'label': label,
                'embedding_model': self.embedder.model_name,
                'added_at': datetime.now().isoformat(),
            }
            if metadata and i < len(metadata):
                meta.update(metadata[i])
            enriched_metadata.append(meta)
        
        # Insert into vector store
        ids = self.store.insert(embeddings, enriched_metadata)
        
        # Auto-save if configured
        self._insert_count += len(ids)
        if self._insert_count % self.config.auto_save_interval == 0:
            self._auto_save()
        
        return {
            'status': 'success',
            'added_count': len(ids),
            'ids': ids,
            'total_samples': self.store.count()
        }
    
    def update_sample(self, sample_id: str, metadata: Dict) -> Dict:
        """Update metadata for existing sample."""
        # Note: FAISS doesn't support in-place updates easily
        # This is a placeholder for stores that support it
        return {'status': 'not_implemented'}
    
    def delete_samples(self, sample_ids: List[str]) -> Dict:
        """Remove samples from calibration set."""
        deleted = self.store.delete(sample_ids)
        return {
            'status': 'success',
            'deleted_count': deleted,
            'total_samples': self.store.count()
        }
    
    def export_calibration_set(self, path: str) -> Dict:
        """Export calibration set to disk."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Save vector store
        self.store.save(str(path_obj))
        
        # Save config metadata
        config_path = path_obj.with_suffix('.config.json')
        with open(config_path, 'w') as f:
            json.dump({
                'embedding_model': self.embedder.model_name,
                'embedding_dim': self.embedder.embedding_dim,
                'total_samples': self.store.count(),
                'label_distribution': self.store.get_label_distribution(),
                'exported_at': datetime.now().isoformat()
            }, f, indent=2)
        
        return {
            'status': 'success',
            'path': str(path_obj),
            'samples_exported': self.store.count()
        }
    
    def import_calibration_set(self, path: str) -> Dict:
        """Import pre-built calibration set."""
        self.store.load(path)
        
        return {
            'status': 'success',
            'samples_loaded': self.store.count(),
            'label_distribution': self.store.get_label_distribution()
        }
    
    def get_statistics(self) -> Dict:
        """Get calibration set statistics."""
        return {
            'total_samples': self.store.count(),
            'label_distribution': self.store.get_label_distribution(),
            'embedding_model': self.embedder.model_name,
            'embedding_dim': self.embedder.embedding_dim
        }
    
    def _auto_save(self) -> None:
        """Auto-save with backup if enabled."""
        if not self.config.backup_enabled:
            return
        
        backup_dir = Path("./data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"calibration_{timestamp}.index"
        
        self.store.save(str(backup_path))
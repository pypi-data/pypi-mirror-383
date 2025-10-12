"""Main classifier implementation."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
import numpy as np

from perceptra.core.embeddings.base import EmbeddingBackend
from perceptra.core.vector_store.base import VectorStore
from perceptra.core.confidence import ConfidenceCalibrator
from perceptra.config import ClassifierConfig


@dataclass
class NeighborInfo:
    """Information about a nearest neighbor."""
    label: str
    distance: float
    metadata: Dict
    

@dataclass
class ClassificationResult:
    """Result of object classification."""
    predicted_label: str
    confidence: float
    nearest_neighbors: List[NeighborInfo]
    reasoning: Optional[str] = None
    metadata: Optional[Dict] = None


class ObjectClassifier:
    """Main classifier using vector retrieval."""
    
    def __init__(
        self,
        embedding_backend: EmbeddingBackend,
        vector_store: VectorStore,
        config: ClassifierConfig
    ):
        self.embedder = embedding_backend
        self.store = vector_store
        self.config = config
        self.confidence_calibrator = ConfidenceCalibrator()
    
    def classify(
        self,
        image_crop: np.ndarray,
        k: int = None,
        metadata_hint: Optional[Dict] = None,
        return_reasoning: bool = False
    ) -> ClassificationResult:
        """Classify a detected waste object.
        
        Args:
            image_crop: Detection crop [H, W, C] in RGB
            k: Number of neighbors (default: from config)
            metadata_hint: Optional hints (e.g., estimated_length_cm, color)
            return_reasoning: Include explanation in result
        
        Returns:
            ClassificationResult with prediction and confidence
        """
        k = k or self.config.default_k
        
        # 1. Generate embedding
        embedding = self.embedder.encode([image_crop])[0]
        
        # 2. Retrieve neighbors
        distances, neighbors_meta = self.store.search(embedding, k=k * 2)  # Get extra for filtering
        
        # 3. Apply metadata filtering if hints provided
        if metadata_hint and self.config.enable_metadata_filtering:
            neighbors_meta, distances = self._filter_by_metadata(
                neighbors_meta, distances, metadata_hint
            )
        
        # Ensure we have at least some neighbors
        if len(neighbors_meta) == 0:
            return ClassificationResult(
                predicted_label=self.config.unknown_label,
                confidence=0.0,
                nearest_neighbors=[],
                reasoning="No similar objects found in calibration set"
            )
        
        # Take top k after filtering
        neighbors_meta = neighbors_meta[:k]
        distances = distances[:k]
        
        # 4. Aggregate labels with distance-weighted voting
        label_scores = self._aggregate_labels(neighbors_meta, distances)
        
        # 5. Get prediction
        predicted_label = max(label_scores, key=label_scores.get)
        raw_confidence = label_scores[predicted_label]
        
        # 6. Calibrate confidence
        label_agreement = self._compute_agreement(neighbors_meta, predicted_label)
        calibrated_confidence = self.confidence_calibrator.calibrate(
            raw_score=raw_confidence,
            min_distance=float(distances[0]),
            label_agreement=label_agreement
        )
        
        # 7. Apply threshold
        if calibrated_confidence < self.config.min_confidence_threshold:
            predicted_label = self.config.unknown_label
        
        # 8. Build result
        neighbor_infos = [
            NeighborInfo(
                label=meta['label'],
                distance=float(dist),
                metadata=meta
            )
            for meta, dist in zip(neighbors_meta, distances)
        ]
        
        reasoning = None
        if return_reasoning:
            reasoning = self._generate_reasoning(
                neighbors_meta, distances, predicted_label, calibrated_confidence
            )
        
        return ClassificationResult(
            predicted_label=predicted_label,
            confidence=float(calibrated_confidence),
            nearest_neighbors=neighbor_infos,
            reasoning=reasoning,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'k': k,
                'metadata_hint': metadata_hint,
                'raw_confidence': float(raw_confidence)
            }
        )
    
    def _aggregate_labels(
        self, 
        neighbors_meta: List[Dict], 
        distances: np.ndarray
    ) -> Dict[str, float]:
        """Aggregate neighbor labels with distance weighting."""
        label_scores = defaultdict(float)
        
        for meta, dist in zip(neighbors_meta, distances):
            # Convert distance to similarity (exponential decay)
            similarity = np.exp(-dist / self.config.temperature)
            label_scores[meta['label']] += similarity
        
        # Normalize
        total = sum(label_scores.values())
        if total > 0:
            return {k: v / total for k, v in label_scores.items()}
        return {}
    
    def _filter_by_metadata(
        self,
        neighbors_meta: List[Dict],
        distances: np.ndarray,
        hint: Dict
    ) -> tuple:
        """Filter neighbors by metadata compatibility."""
        filtered_meta = []
        filtered_dist = []
        
        for meta, dist in zip(neighbors_meta, distances):
            if self._metadata_compatible(meta, hint):
                filtered_meta.append(meta)
                filtered_dist.append(dist)
        
        if not filtered_meta:
            return neighbors_meta, distances
        
        return filtered_meta, np.array(filtered_dist)
    
    def _metadata_compatible(self, meta: Dict, hint: Dict) -> bool:
        """Check metadata compatibility with tolerance."""
        # Length check with ±30% tolerance
        if 'estimated_length_cm' in hint and 'length_cm' in meta:
            ratio = hint['estimated_length_cm'] / (meta['length_cm'] + 1e-6)
            if not (0.7 <= ratio <= 1.3):
                return False
        
        # Exact color match
        if 'color' in hint and 'color' in meta:
            if hint['color'].lower() != meta['color'].lower():
                return False
        
        # Material match
        if 'material' in hint and 'material' in meta:
            if hint['material'].lower() != meta['material'].lower():
                return False
        
        return True
    
    def _compute_agreement(self, neighbors_meta: List[Dict], label: str) -> float:
        """Compute fraction of neighbors with given label."""
        if not neighbors_meta:
            return 0.0
        matches = sum(1 for m in neighbors_meta if m['label'] == label)
        return matches / len(neighbors_meta)
    
    def _generate_reasoning(
        self,
        neighbors_meta: List[Dict],
        distances: np.ndarray,
        predicted_label: str,
        confidence: float
    ) -> str:
        """Generate human-readable explanation."""
        n = len(neighbors_meta)
        label_counts = defaultdict(int)
        for m in neighbors_meta:
            label_counts[m['label']] += 1
        
        reasoning = f"Classified as '{predicted_label}' with {confidence:.1%} confidence. "
        reasoning += f"Based on {n} similar objects: "
        
        label_parts = [f"{count} {label}" for label, count in label_counts.items()]
        reasoning += ", ".join(label_parts) + ". "
        
        reasoning += f"Nearest neighbor distance: {distances[0]:.3f}."
        
        return reasoning
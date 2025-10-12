"""Confidence calibration for classification."""

import numpy as np
from typing import List, Dict, Optional


class ConfidenceCalibrator:
    """Calibrate raw similarity scores to probabilities."""
    
    def __init__(self):
        self.calibration_curve = None
        self.max_distance = 2.0  # For normalized embeddings
        self.is_trained = False
    
    def calibrate(
        self,
        raw_score: float,
        min_distance: float,
        label_agreement: float
    ) -> float:
        """Multi-factor confidence calibration.
        
        Args:
            raw_score: Distance-weighted voting score [0, 1]
            min_distance: Distance to nearest neighbor
            label_agreement: Fraction of top-k with same label [0, 1]
        
        Returns:
            Calibrated confidence [0, 1]
        """
        # Combine factors with weights
        distance_score = 1.0 - (min_distance / self.max_distance)
        distance_score = max(0.0, min(1.0, distance_score))
        
        combined_score = (
            0.5 * raw_score +
            0.3 * distance_score +
            0.2 * label_agreement
        )
        
        # Apply calibration curve if trained
        if self.is_trained and self.calibration_curve is not None:
            try:
                from sklearn.isotonic import IsotonicRegression
                return float(self.calibration_curve.predict([combined_score])[0])
            except:
                pass
        
        return float(combined_score)
    
    def train(self, validation_predictions: List[Dict]) -> Dict:
        """Train calibration curve on validation data.
        
        Args:
            validation_predictions: List of dicts with:
                - raw_confidence: float
                - predicted_label: str
                - true_label: str
        
        Returns:
            Training statistics
        """
        try:
            from sklearn.isotonic import IsotonicRegression
        except ImportError:
            return {'status': 'error', 'message': 'scikit-learn not installed'}
        
        if len(validation_predictions) < 10:
            return {'status': 'error', 'message': 'Need at least 10 validation samples'}
        
        scores = [p['raw_confidence'] for p in validation_predictions]
        correct = [
            int(p['predicted_label'] == p['true_label']) 
            for p in validation_predictions
        ]
        
        self.calibration_curve = IsotonicRegression(out_of_bounds='clip')
        self.calibration_curve.fit(scores, correct)
        self.is_trained = True
        
        # Compute calibration metrics
        calibrated_scores = self.calibration_curve.predict(scores)
        
        return {
            'status': 'success',
            'samples_used': len(validation_predictions),
            'accuracy': np.mean(correct),
            'mean_confidence_before': np.mean(scores),
            'mean_confidence_after': np.mean(calibrated_scores)
        }
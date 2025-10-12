"""Metrics and monitoring utilities."""

from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Define metrics
classifications_total = Counter(
    'perceptra_classifications_total',
    'Total number of classifications performed',
    ['predicted_label']
)

classification_duration = Histogram(
    'perceptra_classification_duration_seconds',
    'Time spent on classification',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

calibration_samples = Gauge(
    'perceptra_calibration_samples_total',
    'Total number of calibration samples',
    ['label']
)

confidence_scores = Histogram(
    'perceptra_confidence_scores',
    'Distribution of confidence scores',
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)


def track_classification_time(func):
    """Decorator to track classification duration."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        classification_duration.observe(duration)
        
        if hasattr(result, 'predicted_label'):
            classifications_total.labels(
                predicted_label=result.predicted_label
            ).inc()
            
            if hasattr(result, 'confidence'):
                confidence_scores.observe(result.confidence)
        
        return result
    return wrapper


def update_calibration_metrics(label_distribution: dict):
    """Update calibration sample metrics."""
    for label, count in label_distribution.items():
        calibration_samples.labels(label=label).set(count)

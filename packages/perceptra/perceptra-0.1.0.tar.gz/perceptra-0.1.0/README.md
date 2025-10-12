<p align="center">
  <img src="docs/assets/perceptra_logo_white.jpg" alt="PERCEPTRA Logo" width="420"/>
</p>

<h1 align="center">PERCEPTRA</h1>

<p align="center">
  <b>Production-ready object classification via vector retrieval</b>
</p>

<p align="center">
  🔍 <a href="#features">Features</a> • 
  ⚙️ <a href="#installation">Installation</a> • 
  🚀 <a href="#quick-start">Quick Start</a> • 
  📈 <a href="#architecture">Architecture</a> • 
  🧩 <a href="#api-reference">API</a> • 
  🧠 <a href="#development">Development</a>
</p>

---

# PERCEPTRA

Production-ready  object classification via vector retrieval.

## Features

- 🔍 **Vector-based Classification**: Use embedding similarity for robust object recognition
- 🔌 **Pluggable Architecture**: Swap embedding models (CLIP, custom) and vector stores (FAISS, Qdrant)
- 📊 **Metadata Fusion**: Combine visual similarity with physical properties (length, color)
- 🎯 **Calibrated Confidence**: Reliable uncertainty estimates via multi-factor calibration
- 🚀 **Production-Ready**: FastAPI service with health checks, logging, and Docker support
- 📈 **Incremental Learning**: Add new samples without retraining
- 🛠️ **CLI Tools**: Command-line interface for calibration and inference

## Installation

### Basic Installation
```bash
pip install perceptra
```

### With CLIP Support
```bash
pip install perceptra[clip]
```

### Full Installation (Development)
```bash
pip install perceptra[all]
```

### From Source
```bash
git clone https://github.com/tannousgeagea/perceptra.git
cd perceptra
pip install -e ".[all]"
```

## Quick Start

### Library Usage

```python
from perceptra import (
    ObjectClassifier,
    CalibrationManager,
    CLIPEmbedding,
    FAISSVectorStore,
    load_config
)
import numpy as np
from PIL import Image

# 1. Initialize components
config = load_config("config/default.yaml")

embedder = CLIPEmbedding(
    model_name=config.embedding.model_name,
    device=config.embedding.device
)

vector_store = FAISSVectorStore(
    dim=embedder.embedding_dim,
    metric="cosine"
)

classifier = ObjectClassifier(
    embedding_backend=embedder,
    vector_store=vector_store,
    config=config.classifier
)

calibration_manager = CalibrationManager(
    embedding_backend=embedder,
    vector_store=vector_store,
    config=config.calibration
)

# 2. Build calibration set
pipe_img = np.array(Image.open("samples/pipe1.jpg"))
bottle_img = np.array(Image.open("samples/bottle1.jpg"))

calibration_manager.add_samples(
    images=[pipe_img, bottle_img],
    labels=["pipe", "bottle"],
    metadata=[
        {"length_cm": 15.0, "color": "gray", "material": "PVC"},
        {"length_cm": 8.0, "color": "transparent", "material": "plastic"}
    ]
)

# 3. Classify new detection
detection = np.array(Image.open("detections/unknown_object.jpg"))

result = classifier.classify(
    image_crop=detection,
    k=5,
    metadata_hint={"estimated_length_cm": 14.0},
    return_reasoning=True
)

print(f"Predicted: {result.predicted_label}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Reasoning: {result.reasoning}")

# 4. Save calibration set
calibration_manager.export_calibration_set("data/my_calibration.index")
```

### Service Usage

Start the FastAPI service:

```bash
# Using CLI
perceptra serve --config config/default.yaml --port 8000

# Using Python
python -m uvicorn perceptra.service.app:app --host 0.0.0.0 --port 8000

# Using Docker
docker-compose up
```

Classify via API:

```bash
# Classify an object
curl -X POST "http://localhost:8000/classify" \
  -F "image=@detection.jpg" \
  -F "k=5" \
  -F "return_reasoning=true"

# Response:
{
  "predicted_label": "pipe",
  "confidence": 0.87,
  "nearest_neighbors": [
    {"label": "pipe", "distance": 0.12},
    {"label": "pipe", "distance": 0.18},
    {"label": "bottle", "distance": 0.45}
  ],
  "reasoning": "Classified as 'pipe' with 87% confidence. Based on 5 similar objects: 3 pipe, 2 bottle."
}
```

Add calibration samples via API:

```bash
curl -X POST "http://localhost:8000/calibration/add" \
  -F "images=@pipe1.jpg" \
  -F "images=@pipe2.jpg" \
  -F 'labels=["pipe", "pipe"]' \
  -F 'metadata=[{"length_cm": 15}, {"length_cm": 20}]'
```

Get calibration statistics:

```bash
curl "http://localhost:8000/calibration/stats"

# Response:
{
  "total_samples": 150,
  "label_distribution": {
    "pipe": 45,
    "bottle": 38,
    "can": 32,
    "bag": 35
  },
  "embedding_model": "ViT-B-32",
  "embedding_dim": 512
}
```

### CLI Usage

```bash
# Classify a single image
perceptra classify detection.jpg --k 5

# Build calibration set from directory
perceptra calibrate ./calibration_images ./labels.json --config config/default.yaml

# Start service
perceptra serve --host 0.0.0.0 --port 8000
```

## Configuration

PERCEPTRA uses hierarchical configuration with YAML files and environment variables.

### Priority Order
1. Environment variables (highest)
2. YAML config file
3. Default values (lowest)

### Example Configuration

```yaml
embedding:
  backend: clip  # clip | perception
  model_name: ViT-B-32
  device: cpu  # cpu | cuda
  batch_size: 32

vector_store:
  backend: faiss  # faiss | qdrant
  index_type: Flat  # Flat | HNSW | IVF
  metric: cosine  # cosine | l2
  persistence_path: ./data/vector_store.index

classifier:
  min_confidence_threshold: 0.6
  default_k: 5
  temperature: 1.0
  enable_metadata_filtering: true
  unknown_label: unknown

calibration:
  auto_save_interval: 100
  backup_enabled: true

service:
  host: 0.0.0.0
  port: 8000
  max_image_size_mb: 10
  enable_cors: true
  log_level: INFO
```

### Environment Variables

Prefix with `PERCEPTRA_` and use `__` for nesting:

```bash
export PERCEPTRA_EMBEDDING__DEVICE=cuda
export PERCEPTRA_CLASSIFIER__MIN_CONFIDENCE_THRESHOLD=0.7
export PERCEPTRA_SERVICE__PORT=9000
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PERCEPTRA System                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌─────────────────┐             │
│  │  Embedding   │─────▶│  Vector Store   │             │
│  │   Backend    │      │   (FAISS/Qdrant)│             │
│  │  (CLIP/etc)  │      └────────┬────────┘             │
│  └──────────────┘               │                       │
│                                  │                       │
│                          ┌───────▼────────┐             │
│  New Detection ─────────▶│  Classifier    │             │
│                          │  • k-NN search │             │
│                          │  • Metadata    │             │
│                          │    filtering   │             │
│                          │  • Confidence  │             │
│                          │    calibration │             │
│                          └───────┬────────┘             │
│                                  │                       │
│                          ┌───────▼────────┐             │
│                          │ Classification │             │
│                          │    Result      │             │
│                          └────────────────┘             │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                  Access Interfaces                       │
│  • Python Library  • FastAPI Service  • CLI Tools       │
└─────────────────────────────────────────────────────────┘
```

## API Reference

### Classification Endpoint

**POST** `/classify`

Classify a object from an image crop.

**Request:**
- `image`: Image file (multipart/form-data)
- `k`: Number of neighbors (default: 5)
- `return_reasoning`: Include explanation (default: false)

**Response:**
```json
{
  "predicted_label": "pipe",
  "confidence": 0.87,
  "nearest_neighbors": [...],
  "reasoning": "...",
  "metadata": {...}
}
```

### Calibration Endpoints

**POST** `/calibration/add`

Add samples to calibration set.

**GET** `/calibration/stats`

Get calibration statistics.

**POST** `/calibration/export`

Export calibration set.

**DELETE** `/calibration/samples`

Delete samples by ID.

### Health Endpoints

**GET** `/health` - Service health check

**GET** `/health/ready` - Readiness probe (K8s)

**GET** `/health/live` - Liveness probe (K8s)

## Development

### Setup Development Environment

```bash
git clone https://github.com/tannousgeagea/perceptra.git
cd perceptra

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
pytest tests/ -v --cov=perceptra
```

### Code Quality

```bash
# Format code
black perceptra/ tests/

# Lint
ruff check perceptra/ tests/

# Type check
mypy perceptra/
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t perceptra:latest .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data perceptra:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: perceptra-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: perceptra
  template:
    metadata:
      labels:
        app: perceptra
    spec:
      containers:
      - name: perceptra
        image: perceptra:latest
        ports:
        - containerPort: 8000
        env:
        - name: PERCEPTRA_EMBEDDING__DEVICE
          value: "cpu"
        volumeMounts:
        - name: data
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: perceptra-data-pvc
```

## Performance Optimization

### GPU Acceleration

```yaml
embedding:
  device: cuda  # Enable GPU
  batch_size: 64  # Increase batch size
```

### Vector Store Optimization

```yaml
vector_store:
  index_type: HNSW  # Fast approximate search
  # or IVF for large datasets
```

### Production Tuning

```yaml
classifier:
  min_confidence_threshold: 0.7  # Higher precision
  default_k: 10  # More neighbors

service:
  workers: 4  # Multiple workers
```

## Monitoring

PERCEPTRA exposes Prometheus-compatible metrics:

- `perceptra_classifications_total`: Total classifications
- `perceptra_classification_duration_seconds`: Classification latency
- `perceptra_calibration_samples_total`: Total calibration samples
- `perceptra_confidence_scores`: Confidence score distribution

Access metrics at: `http://localhost:8000/metrics`

## Troubleshooting

### Issue: Low Confidence Scores

**Solution**: Add more diverse calibration samples for each class.

```python
# Add more samples with variations
calibration_manager.add_samples(
    images=[pipe_img1, pipe_img2, pipe_img3],
    labels=["pipe", "pipe", "pipe"],
    metadata=[
        {"length_cm": 10, "color": "white"},
        {"length_cm": 20, "color": "gray"},
        {"length_cm": 15, "color": "black"}
    ]
)
```

### Issue: Slow Classification

**Solutions**:
1. Use GPU: `PERCEPTRA_EMBEDDING__DEVICE=cuda`
2. Use approximate search: `index_type: HNSW`
3. Reduce k: `default_k: 3`

### Issue: High Memory Usage

**Solutions**:
1. Use quantized index (FAISS)
2. Reduce batch size
3. Use lower-dimensional embeddings

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Citation

```bibtex
@software{perceptra,
  title={PERCEPTRA: Vector-based Object Classification},
  author={Your Team},
  year={2025},
  url={https://github.com/tannousgeagea/perceptra}
}
```

## Support

- Documentation: https://docs.example.com
- Issues: https://github.com/tannousgeagea/perceptra/issues
- Email: tannousgeagea@hotmail.com

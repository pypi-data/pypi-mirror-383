"""CLI commands for PERCEPTRA."""

import click
from pathlib import Path

from perceptra.config import load_config
from perceptra.core.embeddings.clip import CLIPEmbedding
from perceptra.core.vector_store.faiss_store import FAISSVectorStore
from perceptra.core.classifier import ObjectClassifier
from perceptra.core.calibration import CalibrationManager


@click.group()
def cli():
    """Object Retriever CLI."""
    pass


@cli.command()
@click.option('--config', type=str, help='Path to config file')
@click.option('--host', default='0.0.0.0', help='Service host')
@click.option('--port', default=8000, help='Service port')
def serve(config, host, port):
    """Start PERCEPTRA service."""
    import uvicorn
    from perceptra.service.app import app
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--config', type=str, help='Path to config file')
@click.option('--k', default=5, help='Number of neighbors')
def classify(image_path, config, k):
    """Classify a single image."""
    from PIL import Image
    import numpy as np
    
    # Load config
    cfg = load_config(config)
    
    # Initialize components
    embedder = CLIPEmbedding(cfg.embedding.model_name, cfg.embedding.device)
    store = FAISSVectorStore(embedder.embedding_dim)
    
    # Load calibration set
    if Path(cfg.vector_store.persistence_path).exists():
        store.load(cfg.vector_store.persistence_path)
        click.echo(f"Loaded {store.count()} calibration samples")
    else:
        click.echo("No calibration set found!", err=True)
        return
    
    classifier = ObjectClassifier(embedder, store, cfg.classifier)
    
    # Load and classify image
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    
    result = classifier.classify(img_array, k=k, return_reasoning=True)
    
    # Display result
    click.echo(f"\nPredicted: {result.predicted_label}")
    click.echo(f"Confidence: {result.confidence:.2%}")
    click.echo(f"\nNearest neighbors:")
    for i, n in enumerate(result.nearest_neighbors, 1):
        click.echo(f"  {i}. {n.label} (distance: {n.distance:.3f})")
    
    if result.reasoning:
        click.echo(f"\nReasoning: {result.reasoning}")


@cli.command()
@click.argument('images_dir', type=click.Path(exists=True))
@click.argument('labels_file', type=click.Path(exists=True))
@click.option('--config', type=str, help='Path to config file')
def calibrate(images_dir, labels_file, config):
    """Add samples to calibration set."""
    import json
    from PIL import Image
    import numpy as np
    
    # Load config
    cfg = load_config(config)
    
    # Initialize components
    embedder = CLIPEmbedding(cfg.embedding.model_name, cfg.embedding.device)
    store = FAISSVectorStore(embedder.embedding_dim)
    
    # Load existing calibration if available
    if Path(cfg.vector_store.persistence_path).exists():
        store.load(cfg.vector_store.persistence_path)
        click.echo(f"Loaded existing calibration with {store.count()} samples")
    
    calibration_mgr = CalibrationManager(embedder, store, cfg.calibration)
    
    # Load labels
    with open(labels_file, 'r') as f:
        labels_data = json.load(f)  # Expected: [{"file": "img1.jpg", "label": "pipe"}, ...]
    
    # Load images
    images = []
    labels = []
    for item in labels_data:
        img_path = Path(images_dir) / item['file']
        if not img_path.exists():
            click.echo(f"Warning: {img_path} not found, skipping")
            continue
        
        img = Image.open(img_path).convert('RGB')
        images.append(np.array(img))
        labels.append(item['label'])
    
    # Add to calibration
    result = calibration_mgr.add_samples(images, labels)
    
    click.echo(f"\nAdded {result['added_count']} samples")
    click.echo(f"Total samples: {result['total_samples']}")
    
    # Save
    calibration_mgr.export_calibration_set(cfg.vector_store.persistence_path)
    click.echo(f"Saved to {cfg.vector_store.persistence_path}")


if __name__ == '__main__':
    cli()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from perceptra.config import load_config
from perceptra.core.classifier import ObjectClassifier
from perceptra.core.calibration import CalibrationManager
from perceptra.core.embeddings.clip import CLIPEmbedding
from perceptra.core.vector_store.faiss_store import FAISSVectorStore
from perceptra.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # Startup
    config = load_config()
    
    setup_logging(config.service.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing Perceptra service...")
    
    # Initialize components
    embedder = CLIPEmbedding(
        model_name=config.embedding.model_name,
        device=config.embedding.device
    )
    
    vector_store = FAISSVectorStore(
        dim=embedder.embedding_dim,
        index_type=config.vector_store.index_type,
        metric=config.vector_store.metric
    )
    
    # Load existing calibration set if available
    from pathlib import Path
    if Path(config.vector_store.persistence_path).exists():
        logger.info(f"Loading calibration set from {config.vector_store.persistence_path}")
        vector_store.load(config.vector_store.persistence_path)
    
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
    
    # Store in app state
    app.state.config = config
    app.state.classifier = classifier
    app.state.calibration_manager = calibration_manager
    
    logger.info(f"Service initialized with {vector_store.count()} calibration samples")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Perceptra service...")
    
    # Save calibration set
    vector_store.save(config.vector_store.persistence_path)
    logger.info("Calibration set saved")


app = FastAPI(
    title="Perceptra API",
    version="0.1.0",
    description="Vector-based waste object classification service",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from perceptra.service.routes import health, classification, calibration

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(classification.router, prefix="/classify", tags=["classification"])
app.include_router(calibration.router, prefix="/calibration", tags=["calibration"])
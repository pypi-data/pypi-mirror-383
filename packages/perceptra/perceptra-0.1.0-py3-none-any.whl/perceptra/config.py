"""Configuration management for PERCEPTRA."""

from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
import yaml


class EmbeddingConfig(BaseSettings):
    backend: str = Field(default="clip", description="Embedding backend: clip, perception")
    model_name: str = Field(default="ViT-B/32")
    device: str = Field(default="cpu")
    batch_size: int = Field(default=32)


class VectorStoreConfig(BaseSettings):
    backend: str = Field(default="faiss")
    index_type: str = Field(default="Flat")
    metric: str = Field(default="cosine")
    persistence_path: str = Field(default="./data/vector_store.index")
    

class ClassifierConfig(BaseSettings):
    min_confidence_threshold: float = Field(default=0.6)
    default_k: int = Field(default=5)
    temperature: float = Field(default=1.0)
    enable_metadata_filtering: bool = Field(default=True)
    unknown_label: str = Field(default="unknown")


class CalibrationConfig(BaseSettings):
    auto_save_interval: int = Field(default=100)
    backup_enabled: bool = Field(default=True)
    validation_split: float = Field(default=0.15)


class ServiceConfig(BaseSettings):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    max_image_size_mb: int = Field(default=10)
    enable_cors: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    workers: int = Field(default=1)


class PERCEPTRAConfig(BaseSettings):
    """Main configuration for PERCEPTRA system."""

    model_config = ConfigDict(
        env_prefix="PERCEPTRA_",
        env_nested_delimiter="__"
    )

    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    classifier: ClassifierConfig = Field(default_factory=ClassifierConfig)
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)


def load_config(config_path: Optional[str] = None) -> PERCEPTRAConfig:
    """Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to YAML config file. If None, uses defaults.
    
    Returns:
        PERCEPTRAConfig instance
    """
    if config_path:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return PERCEPTRAConfig(**config_dict)
    return PERCEPTRAConfig()
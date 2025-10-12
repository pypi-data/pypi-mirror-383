"""Logging configuration."""

import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO"):
    """Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "wor.log")
        ]
    )
    
    # Set library log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
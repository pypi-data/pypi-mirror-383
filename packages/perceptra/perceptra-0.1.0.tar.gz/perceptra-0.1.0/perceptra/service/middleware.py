"""FastAPI middleware."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"({duration:.3f}s) {request.url.path}"
        )
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Track request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        from perceptra.utils.metrics import classification_duration
        
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Track classification endpoint metrics
        if request.url.path.startswith("/classify"):
            classification_duration.observe(duration)
        
        return response
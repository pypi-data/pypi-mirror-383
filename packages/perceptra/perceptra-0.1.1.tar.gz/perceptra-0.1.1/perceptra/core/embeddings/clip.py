"""CLIP-based embedding backend."""

from typing import List
import numpy as np

try:
    import torch
    import open_clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

from perceptra.core.embeddings.base import EmbeddingBackend


class CLIPEmbedding(EmbeddingBackend):
    """OpenCLIP-based embedding model."""
    
    def __init__(self, model_name: str = "ViT-B-32", device: str = "cpu"):
        if not CLIP_AVAILABLE:
            raise ImportError(
                "CLIP dependencies not installed. "
                "Install with: pip install perceptra[clip]"
            )
        
        super().__init__(model_name, device)
        
        self.model, _, self.preprocess_fn = open_clip.create_model_and_transforms(
            model_name, pretrained="openai", device=device
        )
        self.model.eval()
        
        self._embedding_dim = self.model.visual.output_dim
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
    @torch.no_grad()
    def encode(self, images: List[np.ndarray]) -> np.ndarray:
        """Encode images using CLIP visual encoder.
        
        Args:
            images: List of RGB images as numpy arrays
        
        Returns:
            Normalized embeddings of shape [N, embedding_dim]
        """
        # Preprocess images
        from PIL import Image
        pil_images = [Image.fromarray(img) for img in images]
        preprocessed = torch.stack([self.preprocess_fn(img) for img in pil_images])
        preprocessed = preprocessed.to(self.device)
        
        # Extract features
        embeddings = self.model.encode_image(preprocessed)
        
        # Normalize
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        
        return embeddings.cpu().numpy()
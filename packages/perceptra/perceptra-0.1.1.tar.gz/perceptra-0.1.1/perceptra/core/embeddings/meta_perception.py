"""Meta's Perception Encoder (PE) embedding backend.

Uses Meta's Perception Encoder models which are specifically designed
for image understanding and visual embedding tasks.

Models available:
- PE-Core-L14-336: Large model, 336px input, 1024-d embeddings
- PE-Core-B16-224: Base model, 224px input, 768-d embeddings
"""

from typing import List
import numpy as np

try:
    import torch
    import open_clip
    import torch.nn.functional as F
    from transformers import AutoModel, AutoImageProcessor
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from perceptra.core.embeddings.base import EmbeddingBackend


class MetaPerceptionEmbedding(EmbeddingBackend):
    """Meta's Perception Encoder from Facebook Research.
    
    The Perception Encoder (PE) is designed for:
    - Dense visual understanding
    - Object-centric embeddings
    - Fine-grained image features
    - Zero-shot transfer to downstream tasks
    
    Available models:
    - facebook/PE-Core-L14-336: 1024-d embeddings, 336x336 input
    - facebook/PE-Core-B16-224: 768-d embeddings, 224x224 input
    """
    
    AVAILABLE_MODELS = {
        "PE-Core-L14-336": {
            "model_id": "hf-hub:timm/PE-Core-L-14-336",
            "embedding_dim": 1024,
            "input_size": 336
        },
        "PE-Core-B16-224": {
            "model_id": "hf-hub:timm/PE-Core-B16-224",
            "embedding_dim": 768,
            "input_size": 224
        }
    }
    
    def __init__(
        self,
        model_name: str = "PE-Core-L14-336",
        device: str = "cpu",
        trust_remote_code: bool = True
    ):
        """Initialize Meta Perception Encoder.
        
        Args:
            model_name: Model variant (PE-Core-L14-336, PE-Core-B16-224)
            device: Device to run on (cpu, cuda)
            trust_remote_code: Trust remote code from HuggingFace
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch and transformers not installed. "
                "Install with: pip install torch transformers"
            )
        
        super().__init__(model_name, device)
        
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Model {model_name} not supported. "
                f"Choose from: {list(self.AVAILABLE_MODELS.keys())}"
            )
        
        self.device_obj = torch.device(device)
        self.model_config = self.AVAILABLE_MODELS[model_name]
        self._embedding_dim = self.model_config["embedding_dim"]
        
        # Load model and processor
        self._load_model(trust_remote_code)
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
    def _load_model(self, trust_remote_code: bool) -> None:
        """Load Perception Encoder model from HuggingFace."""
        model_id = self.model_config["model_id"]
        
        print(f"Loading Meta Perception Encoder: {model_id}")
        
        try:

            self.model, _, self.processor = open_clip.create_model_and_transforms(model_id)
            self.model.to(self.device_obj)
            self.model.eval()
            
            print(f"✓ Loaded Perception Encoder ({self._embedding_dim}-d embeddings)")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("\nTip: Make sure you have access to the model on HuggingFace.")
            print("You may need to:")
            print("1. Login: huggingface-cli login")
            print("2. Accept model terms on HuggingFace model page")
            raise
    
    def _preprocess_images(self, images: List[np.ndarray]) -> torch.Tensor:
        """Preprocess images using the model's processor.
        
        Args:
            images: List of RGB images [H, W, 3] in range [0, 255]
        
        Returns:
            Preprocessed tensor ready for model
        """
        # Convert numpy arrays to PIL Images
        pil_images = [Image.fromarray(img) for img in images]
        
        # Process with model's processor
        tensors = [self.processor(img) for img in pil_images]
        
        # Stack into batch
        batch = torch.stack(tensors).to(self.device_obj)
        
        return batch
        
    @torch.no_grad()
    def encode(self, images: List[np.ndarray]) -> np.ndarray:
        """Encode images using Meta's Perception Encoder.
        
        Args:
            images: List of RGB images as numpy arrays [H, W, 3]
        
        Returns:
            Normalized embeddings of shape [N, embedding_dim]
        """
        # Preprocess images
        inputs = self._preprocess_images(images)
        
        # Forward pass through the model
        outputs = self.model(inputs)
        
        # Extract embeddings
        # The model typically returns pooled output or last hidden state
        if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
            embeddings = outputs.pooler_output
        elif hasattr(outputs, 'last_hidden_state'):
            # Use CLS token or mean pooling
            embeddings = outputs.last_hidden_state[:, 0, :]  # CLS token
        else:
            # Fallback: use the first output
            embeddings = outputs[0] if isinstance(outputs, tuple) else outputs
            if embeddings.dim() == 3:  # [B, N, D]
                embeddings = embeddings[:, 0, :]  # Take first token
        
        # L2 normalize
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
    def encode_batch(
        self, 
        images: List[np.ndarray], 
        batch_size: int = 32
    ) -> np.ndarray:
        """Encode images in batches for efficiency.
        
        Args:
            images: List of RGB images
            batch_size: Number of images to process at once
        
        Returns:
            Normalized embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            embeddings = self.encode(batch)
            all_embeddings.append(embeddings)
        
        return np.concatenate(all_embeddings, axis=0)
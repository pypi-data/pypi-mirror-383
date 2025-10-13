"""DINOv2 embedding backend (Meta's self-supervised vision model).

DINOv2 is Meta's state-of-the-art self-supervised vision transformer,
trained on 142M images without labels. Excellent for dense visual features.
"""

from typing import List
import numpy as np

try:
    import torch
    import torch.nn.functional as F
    from torchvision import transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from perceptra.core.embeddings.base import EmbeddingBackend


class DINOv2Embedding(EmbeddingBackend):
    """Meta's DINOv2 self-supervised vision encoder.
    
    DINOv2 models from Meta AI:
    - dinov2_vits14: Small, 384-d embeddings, fastest
    - dinov2_vitb14: Base, 768-d embeddings, balanced
    - dinov2_vitl14: Large, 1024-d embeddings, high quality
    - dinov2_vitg14: Giant, 1536-d embeddings, best quality
    
    All models use 14x14 patch size and 518x518 image resolution.
    
    Advantages:
    - Self-supervised pretraining (no manual labels needed)
    - Excellent for fine-grained object features
    - Fast inference
    - Strong transfer learning capabilities
    - Works great for object detection and retrieval
    """
    
    AVAILABLE_MODELS = {
        "dinov2_vits14": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vits14",
            "embedding_dim": 384,
            "image_size": 518
        },
        "dinov2_vitb14": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vitb14",
            "embedding_dim": 768,
            "image_size": 518
        },
        "dinov2_vitl14": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vitl14",
            "embedding_dim": 1024,
            "image_size": 518
        },
        "dinov2_vitg14": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vitg14",
            "embedding_dim": 1536,
            "image_size": 518
        },
        # Register variants with different backbones
        "dinov2_vits14_reg": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vits14_reg",
            "embedding_dim": 384,
            "image_size": 518
        },
        "dinov2_vitb14_reg": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vitb14_reg",
            "embedding_dim": 768,
            "image_size": 518
        },
        "dinov2_vitl14_reg": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vitl14_reg",
            "embedding_dim": 1024,
            "image_size": 518
        },
        "dinov2_vitg14_reg": {
            "torch_hub": "facebookresearch/dinov2",
            "model_name": "dinov2_vitg14_reg",
            "embedding_dim": 1536,
            "image_size": 518
        }
    }
    
    def __init__(
        self,
        model_name: str = "dinov2_vitb14",
        device: str = "cpu",
        use_registers: bool = False
    ):
        """Initialize DINOv2 encoder.
        
        Args:
            model_name: Model variant (dinov2_vits14, dinov2_vitb14, dinov2_vitl14, dinov2_vitg14)
            device: Device to run on (cpu, cuda)
            use_registers: Use register tokens variant (better for dense predictions)
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch and torchvision not installed. "
                "Install with: pip install torch torchvision"
            )
        
        # Add _reg suffix if using registers
        if use_registers and not model_name.endswith("_reg"):
            model_name = f"{model_name}_reg"
        
        super().__init__(model_name, device)
        
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Model {model_name} not supported. "
                f"Choose from: {list(self.AVAILABLE_MODELS.keys())}"
            )
        
        self.device_obj = torch.device(device)
        self.model_config = self.AVAILABLE_MODELS[model_name]
        self._embedding_dim = self.model_config["embedding_dim"]
        
        # Load model
        self._load_model()
        
        # Image preprocessing
        self.image_size = self.model_config["image_size"]
        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size), interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
    def _load_model(self) -> None:
        """Load DINOv2 model from torch hub."""
        print(f"Loading DINOv2 model: {self.model_name}")
        
        try:
            # Load from torch hub
            self.model = torch.hub.load(
                self.model_config["torch_hub"],
                self.model_config["model_name"]
            )
            
            self.model.to(self.device_obj)
            self.model.eval()
            
            print(f"✓ Loaded DINOv2 ({self._embedding_dim}-d embeddings)")
            
        except Exception as e:
            print(f"Error loading DINOv2 model: {e}")
            print("\nTip: Make sure you have internet connection for first-time download.")
            print("The model will be cached in ~/.cache/torch/hub/")
            raise
    
    def _preprocess_images(self, images: List[np.ndarray]) -> torch.Tensor:
        """Preprocess images for DINOv2.
        
        Args:
            images: List of RGB images [H, W, 3] in range [0, 255]
        
        Returns:
            Preprocessed tensor [N, 3, 518, 518]
        """
        # Convert to PIL Images
        pil_images = [Image.fromarray(img) for img in images]
        
        # Apply transforms
        tensors = [self.transform(img) for img in pil_images]
        
        # Stack into batch
        batch = torch.stack(tensors).to(self.device_obj)
        
        return batch
    
    @torch.no_grad()
    def encode(self, images: List[np.ndarray]) -> np.ndarray:
        """Encode images using DINOv2.
        
        Args:
            images: List of RGB images as numpy arrays [H, W, 3]
        
        Returns:
            Normalized embeddings of shape [N, embedding_dim]
        """
        # Preprocess images
        batch = self._preprocess_images(images)
        
        # Forward pass - get CLS token embeddings
        # DINOv2 returns dict with 'x_norm_clstoken' and 'x_norm_patchtokens'
        output = self.model(batch)
        
        # Extract CLS token embedding
        if isinstance(output, dict):
            embeddings = output['x_norm_clstoken']
        elif isinstance(output, tuple):
            # Some versions return tuple
            embeddings = output[0]
        else:
            embeddings = output
        
        # L2 normalize (DINOv2 already outputs normalized features, but ensure)
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
    def encode_with_patch_tokens(self, images: List[np.ndarray]) -> tuple:
        """Encode images and return both CLS and patch tokens.
        
        Useful for dense prediction tasks or spatial reasoning.
        
        Args:
            images: List of RGB images
        
        Returns:
            Tuple of (cls_embeddings, patch_embeddings)
            - cls_embeddings: [N, embedding_dim]
            - patch_embeddings: [N, num_patches, embedding_dim]
        """
        batch = self._preprocess_images(images)
        
        with torch.no_grad():
            output = self.model(batch)
            
            if isinstance(output, dict):
                cls_embeddings = output['x_norm_clstoken']
                patch_embeddings = output['x_norm_patchtokens']
            else:
                # Fallback
                cls_embeddings = output
                patch_embeddings = None
            
            # Normalize
            cls_embeddings = F.normalize(cls_embeddings, p=2, dim=1)
            
            if patch_embeddings is not None:
                patch_embeddings = F.normalize(patch_embeddings, p=2, dim=2)
        
        cls_numpy = cls_embeddings.cpu().numpy()
        patch_numpy = patch_embeddings.cpu().numpy() if patch_embeddings is not None else None
        
        return cls_numpy, patch_numpy
    
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
    
    def get_attention_maps(self, images: List[np.ndarray]) -> np.ndarray:
        """Extract attention maps from the model.
        
        Useful for visualization and interpretability.
        
        Args:
            images: List of RGB images
        
        Returns:
            Attention maps [N, num_heads, num_patches, num_patches]
        """
        batch = self._preprocess_images(images)
        
        # Store attention maps
        attention_maps = []
        
        def hook_fn(module, input, output):
            # Extract attention weights from the last layer
            attention_maps.append(output)
        
        # Register hook on last attention layer
        # Note: This is model-specific and might need adjustment
        handle = None
        for name, module in self.model.named_modules():
            if 'attn' in name and 'blocks' in name:
                handle = module.register_forward_hook(hook_fn)
        
        with torch.no_grad():
            _ = self.model(batch)
        
        if handle:
            handle.remove()
        
        if attention_maps:
            return attention_maps[-1].cpu().numpy()
        return None
    
    def compute_similarity(
        self,
        images1: List[np.ndarray],
        images2: List[np.ndarray]
    ) -> np.ndarray:
        """Compute pairwise cosine similarity between two sets of images.
        
        Args:
            images1: First set of images
            images2: Second set of images
        
        Returns:
            Similarity matrix [len(images1), len(images2)]
        """
        emb1 = self.encode(images1)
        emb2 = self.encode(images2)
        
        # Compute cosine similarity
        similarity = np.dot(emb1, emb2.T)
        
        return similarity

"""Perception encoder embedding backend."""

from typing import List
import numpy as np

try:
    import torch
    import torch.nn as nn
    from torchvision import transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from perceptra.core.embeddings.base import EmbeddingBackend


class PerceptionEmbedding(EmbeddingBackend):
    """Custom perception encoder for waste object embeddings.
    
    This is a lightweight CNN-based encoder optimized for waste object features.
    Can be trained on domain-specific data for better performance.
    """
    
    def __init__(
        self, 
        model_name: str = "perception-v1",
        device: str = "cpu",
        pretrained_path: str = None
    ):
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch not installed. "
                "Install with: pip install torch torchvision"
            )
        
        super().__init__(model_name, device)
        
        self.device_obj = torch.device(device)
        self._embedding_dim = 512
        
        # Build model
        self.model = self._build_model()
        self.model.to(self.device_obj)
        self.model.eval()
        
        # Load pretrained weights if provided
        if pretrained_path:
            self._load_pretrained(pretrained_path)
        
        # Image preprocessing
        self.preprocess = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
    def _build_model(self) -> nn.Module:
        """Build the perception encoder architecture.
        
        Architecture:
            - Efficient CNN backbone (MobileNetV3 style)
            - Feature pyramid for multi-scale perception
            - Attention mechanism for waste-specific features
            - Global pooling + FC for embedding
        """
        
        class PerceptionEncoder(nn.Module):
            def __init__(self, embedding_dim=512):
                super().__init__()
                
                # Efficient CNN backbone
                self.backbone = nn.Sequential(
                    # Stage 1: 224x224 -> 112x112
                    nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1, bias=False),
                    nn.BatchNorm2d(32),
                    nn.ReLU(inplace=True),
                    
                    # Stage 2: 112x112 -> 56x56
                    self._inverted_residual(32, 64, stride=2, expand_ratio=4),
                    self._inverted_residual(64, 64, stride=1, expand_ratio=4),
                    
                    # Stage 3: 56x56 -> 28x28
                    self._inverted_residual(64, 128, stride=2, expand_ratio=4),
                    self._inverted_residual(128, 128, stride=1, expand_ratio=4),
                    self._inverted_residual(128, 128, stride=1, expand_ratio=4),
                    
                    # Stage 4: 28x28 -> 14x14
                    self._inverted_residual(128, 256, stride=2, expand_ratio=6),
                    self._inverted_residual(256, 256, stride=1, expand_ratio=6),
                    self._inverted_residual(256, 256, stride=1, expand_ratio=6),
                    
                    # Stage 5: 14x14 -> 7x7
                    self._inverted_residual(256, 512, stride=2, expand_ratio=6),
                    self._inverted_residual(512, 512, stride=1, expand_ratio=6),
                )
                
                # Spatial attention for waste-specific features
                self.attention = nn.Sequential(
                    nn.AdaptiveAvgPool2d(1),
                    nn.Conv2d(512, 256, kernel_size=1),
                    nn.ReLU(inplace=True),
                    nn.Conv2d(256, 512, kernel_size=1),
                    nn.Sigmoid()
                )
                
                # Global pooling and embedding
                self.global_pool = nn.AdaptiveAvgPool2d(1)
                self.embedding_head = nn.Sequential(
                    nn.Linear(512, embedding_dim),
                    nn.BatchNorm1d(embedding_dim),
                )
            
            def _inverted_residual(self, in_channels, out_channels, stride, expand_ratio):
                """Inverted residual block (MobileNetV2 style)."""
                hidden_dim = in_channels * expand_ratio
                use_residual = stride == 1 and in_channels == out_channels
                
                layers = []
                
                # Expand
                if expand_ratio != 1:
                    layers.extend([
                        nn.Conv2d(in_channels, hidden_dim, kernel_size=1, bias=False),
                        nn.BatchNorm2d(hidden_dim),
                        nn.ReLU(inplace=True),
                    ])
                
                # Depthwise
                layers.extend([
                    nn.Conv2d(
                        hidden_dim, hidden_dim, kernel_size=3,
                        stride=stride, padding=1, groups=hidden_dim, bias=False
                    ),
                    nn.BatchNorm2d(hidden_dim),
                    nn.ReLU(inplace=True),
                ])
                
                # Project
                layers.extend([
                    nn.Conv2d(hidden_dim, out_channels, kernel_size=1, bias=False),
                    nn.BatchNorm2d(out_channels),
                ])
                
                block = nn.Sequential(*layers)
                
                if use_residual:
                    return lambda x: x + block(x)
                else:
                    return block
            
            def forward(self, x):
                # Extract features
                features = self.backbone(x)
                
                # Apply attention
                attention_weights = self.attention(features)
                features = features * attention_weights
                
                # Global pooling
                features = self.global_pool(features)
                features = features.view(features.size(0), -1)
                
                # Get embedding
                embedding = self.embedding_head(features)
                
                return embedding
        
        return PerceptionEncoder(self._embedding_dim)
    
    def _load_pretrained(self, path: str) -> None:
        """Load pretrained weights."""
        try:
            checkpoint = torch.load(path, map_location=self.device_obj)
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
            print(f"Loaded pretrained weights from {path}")
        except Exception as e:
            print(f"Warning: Could not load pretrained weights: {e}")
    
    @torch.no_grad()
    def encode(self, images: List[np.ndarray]) -> np.ndarray:
        """Encode images using perception encoder.
        
        Args:
            images: List of RGB images as numpy arrays [H, W, 3]
        
        Returns:
            Normalized embeddings of shape [N, embedding_dim]
        """
        # Preprocess images
        preprocessed = []
        for img in images:
            img_tensor = self.preprocess(img)
            preprocessed.append(img_tensor)
        
        batch = torch.stack(preprocessed).to(self.device_obj)
        
        # Extract embeddings
        embeddings = self.model(batch)
        
        # L2 normalize
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
    def save_model(self, path: str) -> None:
        """Save model weights."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'embedding_dim': self._embedding_dim,
            'model_name': self.model_name
        }, path)
        print(f"Model saved to {path}")
    
    def train_model(
        self,
        train_loader,
        val_loader,
        num_epochs: int = 10,
        learning_rate: float = 1e-3,
        save_path: str = None
    ) -> dict:
        """Fine-tune the perception encoder on domain-specific data.
        
        Args:
            train_loader: PyTorch DataLoader for training
            val_loader: PyTorch DataLoader for validation
            num_epochs: Number of training epochs
            learning_rate: Learning rate for optimizer
            save_path: Path to save best model
        
        Returns:
            Training history dictionary
        """
        self.model.train()
        
        # Triplet loss for metric learning
        criterion = nn.TripletMarginLoss(margin=1.0)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=num_epochs
        )
        
        history = {'train_loss': [], 'val_loss': []}
        best_val_loss = float('inf')
        
        for epoch in range(num_epochs):
            # Training
            train_loss = 0.0
            self.model.train()
            
            for batch in train_loader:
                anchor, positive, negative = batch
                anchor = anchor.to(self.device_obj)
                positive = positive.to(self.device_obj)
                negative = negative.to(self.device_obj)
                
                optimizer.zero_grad()
                
                anchor_emb = self.model(anchor)
                positive_emb = self.model(positive)
                negative_emb = self.model(negative)
                
                loss = criterion(anchor_emb, positive_emb, negative_emb)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            history['train_loss'].append(train_loss)
            
            # Validation
            val_loss = 0.0
            self.model.eval()
            
            with torch.no_grad():
                for batch in val_loader:
                    anchor, positive, negative = batch
                    anchor = anchor.to(self.device_obj)
                    positive = positive.to(self.device_obj)
                    negative = negative.to(self.device_obj)
                    
                    anchor_emb = self.model(anchor)
                    positive_emb = self.model(positive)
                    negative_emb = self.model(negative)
                    
                    loss = criterion(anchor_emb, positive_emb, negative_emb)
                    val_loss += loss.item()
            
            val_loss /= len(val_loader)
            history['val_loss'].append(val_loss)
            
            scheduler.step()
            
            print(f"Epoch {epoch+1}/{num_epochs} - "
                  f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            # Save best model
            if save_path and val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_model(save_path)
                print(f"Best model saved (val_loss: {val_loss:.4f})")
        
        self.model.eval()
        return history

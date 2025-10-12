"""Image processing utilities."""

import numpy as np
from PIL import Image
import io


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Decode image bytes to numpy array.
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        RGB image array [H, W, 3]
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    return np.array(img)


def resize_image(image: np.ndarray, max_size: int = 512) -> np.ndarray:
    """Resize image while maintaining aspect ratio.
    
    Args:
        image: Input image [H, W, C]
        max_size: Maximum dimension
    
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    if max(h, w) <= max_size:
        return image
    
    if h > w:
        new_h = max_size
        new_w = int(w * (max_size / h))
    else:
        new_w = max_size
        new_h = int(h * (max_size / w))
    
    img_pil = Image.fromarray(image)
    img_pil = img_pil.resize((new_w, new_h), Image.LANCZOS)
    
    return np.array(img_pil)
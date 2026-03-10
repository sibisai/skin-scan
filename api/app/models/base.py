"""
Base Classifier Interface
All model classifiers should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from PIL import Image
import torch
import io


class BaseClassifier(ABC):
    """
    Abstract base class for medical image classifiers.
    Extend this class to add new classification models.
    """
    
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.class_names: List[str] = []
        self.model_name: str = ""
        self.gradcam_visualizer = None
    
    @abstractmethod
    def load_model(self, weights_path: str, config_path: str) -> None:
        """Load model weights and configuration."""
        pass
    
    @abstractmethod
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for model input."""
        pass
    
    @abstractmethod
    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """Run prediction on image."""
        pass
    
    @abstractmethod
    def get_gradcam(
        self, 
        image_bytes: bytes, 
        target_class: Optional[int] = None,
        output_type: str = "all"
    ) -> Dict[str, Any]:
        """Generate Grad-CAM visualization."""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata."""
        return {
            "model_name": self.model_name,
            "classes": self.class_names,
            "num_classes": len(self.class_names),
            "device": str(self.device)
        }


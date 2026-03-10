"""
Grad-CAM Visualization Module
Generates heatmap visualizations showing which regions the model focuses on.
"""

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional
import io
import base64


class GradCAM:
    """
    Grad-CAM implementation for CNN visualization.
    Works with EfficientNet and other architectures with convolutional backbones.
    """
    
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        """
        Initialize Grad-CAM.
        
        Args:
            model: The neural network model
            target_layer: The convolutional layer to visualize (usually the last conv layer)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self._register_hooks()
    
    def _register_hooks(self):
        """Register forward and backward hooks on the target layer."""
        
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate(
        self, 
        input_tensor: torch.Tensor, 
        target_class: Optional[int] = None
    ) -> np.ndarray:
        """
        Generate Grad-CAM heatmap.
        
        Args:
            input_tensor: Preprocessed input image tensor (1, C, H, W)
            target_class: Class index to visualize. If None, uses predicted class.
            
        Returns:
            Heatmap as numpy array (H, W) with values in [0, 1]
        """
        self.model.eval()
        
        # Forward pass
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Backward pass
        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)
        
        # Generate heatmap
        # Global average pooling of gradients
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        
        # Weighted combination of activation maps
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        
        # ReLU and normalize
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()
        
        # Normalize to [0, 1]
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        
        return cam
    

class GradCAMVisualizer:
    """
    High-level visualizer that generates various Grad-CAM outputs.
    """
    
    def __init__(
        self, 
        model: torch.nn.Module,
        target_layer: torch.nn.Module,
        image_size: int = 224,
        mean: list = [0.485, 0.456, 0.406],
        std: list = [0.229, 0.224, 0.225]
    ):
        """
        Initialize the visualizer.
        
        Args:
            model: The neural network model
            target_layer: The convolutional layer to visualize
            image_size: Size images are resized to
            mean: Normalization mean values
            std: Normalization std values
        """
        self.model = model
        self.gradcam = GradCAM(model, target_layer)
        self.image_size = image_size
        self.mean = np.array(mean)
        self.std = np.array(std)
    
    def _denormalize(self, tensor: torch.Tensor) -> np.ndarray:
        """Convert normalized tensor back to displayable image."""
        img = tensor.squeeze().detach().cpu().numpy().transpose(1, 2, 0)
        img = img * self.std + self.mean
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
        return img
    
    def _apply_heatmap(
        self, 
        image: np.ndarray, 
        heatmap: np.ndarray,
        alpha: float = 0.4,
        colormap: int = cv2.COLORMAP_JET
    ) -> np.ndarray:
        """
        Overlay heatmap on original image.
        
        Args:
            image: Original image (H, W, 3) in RGB
            heatmap: Grad-CAM heatmap (H, W) normalized to [0, 1]
            alpha: Transparency of heatmap overlay
            colormap: OpenCV colormap to use
            
        Returns:
            Overlaid image as numpy array
        """
        # Resize heatmap to image size
        heatmap_resized = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(
            (heatmap_resized * 255).astype(np.uint8), 
            colormap
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Blend with original image
        overlaid = (1 - alpha) * image + alpha * heatmap_colored
        overlaid = np.clip(overlaid, 0, 255).astype(np.uint8)
        
        return overlaid
    
    def generate_visualization(
        self,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None,
        output_type: str = "all"
    ) -> dict:
        """
        Generate Grad-CAM visualization(s).
        
        Args:
            input_tensor: Preprocessed input image tensor (1, C, H, W)
            target_class: Class to visualize. If None, uses predicted class.
            output_type: One of "heatmap", "overlay", "all"
            
        Returns:
            Dictionary containing requested visualizations as PIL Images
        """
        # Generate heatmap
        heatmap = self.gradcam.generate(input_tensor, target_class)
        
        # Get original image
        original = self._denormalize(input_tensor)
        
        results = {}
        
        if output_type in ["heatmap", "all"]:
            # Pure heatmap
            heatmap_resized = cv2.resize(heatmap, (self.image_size, self.image_size))
            heatmap_colored = cv2.applyColorMap(
                (heatmap_resized * 255).astype(np.uint8), 
                cv2.COLORMAP_JET
            )
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            results["heatmap"] = Image.fromarray(heatmap_colored)
        
        if output_type in ["overlay", "all"]:
            # Overlay on original
            overlaid = self._apply_heatmap(original, heatmap)
            results["overlay"] = Image.fromarray(overlaid)
        
        if output_type == "all":
            # Original image
            results["original"] = Image.fromarray(original)
            
            # Side-by-side comparison
            comparison = self._create_comparison(
                original, 
                heatmap,
                results["overlay"]
            )
            results["comparison"] = comparison
        
        return results
    
    def _create_comparison(
        self, 
        original: np.ndarray, 
        heatmap: np.ndarray,
        overlay: Image.Image
    ) -> Image.Image:
        """Create side-by-side comparison image."""
        h, w = original.shape[:2]
        
        # Create heatmap image
        heatmap_resized = cv2.resize(heatmap, (w, h))
        heatmap_colored = cv2.applyColorMap(
            (heatmap_resized * 255).astype(np.uint8), 
            cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Create comparison (original | heatmap | overlay)
        overlay_np = np.array(overlay)
        
        # Add labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        label_height = 30
        
        comparison = np.zeros((h + label_height, w * 3, 3), dtype=np.uint8)
        comparison.fill(255)  # White background
        
        # Add images
        comparison[label_height:, :w] = original
        comparison[label_height:, w:2*w] = heatmap_colored
        comparison[label_height:, 2*w:] = overlay_np
        
        # Add labels
        cv2.putText(comparison, "Original", (w//2 - 40, 20), font, 0.6, (0, 0, 0), 2)
        cv2.putText(comparison, "Grad-CAM", (w + w//2 - 45, 20), font, 0.6, (0, 0, 0), 2)
        cv2.putText(comparison, "Overlay", (2*w + w//2 - 35, 20), font, 0.6, (0, 0, 0), 2)
        
        return Image.fromarray(comparison)


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()


def base64_to_image(b64_string: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data))

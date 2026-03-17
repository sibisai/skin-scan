"""
Model Visualization Module
Grad-CAM for CNNs, attention-map extraction for Vision Transformers.
"""

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import cv2
from typing import Optional
import io
import base64


class GradCAM:
    """Grad-CAM for CNNs (EfficientNet, ResNet, etc.)."""

    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.gradients = None
        self.activations = None

        target_layer.register_forward_hook(
            lambda m, i, o: setattr(self, 'activations', o.detach())
        )
        target_layer.register_full_backward_hook(
            lambda m, gi, go: setattr(self, 'gradients', go[0].detach())
        )

    def generate(self, input_tensor: torch.Tensor, target_class: Optional[int] = None) -> np.ndarray:
        self.model.eval()
        output = self.model(input_tensor)

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = F.relu((weights * self.activations).sum(dim=1, keepdim=True))
        cam = cam.squeeze().cpu().numpy()
        return _normalize(cam)


class ViTAttentionMap:
    """
    Attention-based visualization for Vision Transformers (DINOv2).
    Extracts CLS→patch attention weights from the last encoder layer's
    self-attention, which directly shows what spatial regions the model
    uses for classification. No backward pass needed.
    """

    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.attention_weights = None

        # Enable attention output so self-attention returns (context, attn_probs)
        # instead of just (context,). Does not affect last_hidden_state.
        model.dinov2.config.output_attentions = True

        target_layer.register_forward_hook(
            lambda m, i, o: setattr(self, 'attention_weights', o[1].detach())
        )

    def generate(self, input_tensor: torch.Tensor, target_class: Optional[int] = None) -> np.ndarray:
        self.model.eval()

        with torch.no_grad():
            self.model(input_tensor)

        # attention_probs shape: (batch, num_heads, seq_len, seq_len)
        # where seq_len = 1 CLS + 256 patches (224/14 = 16, 16*16 = 256)
        attn = self.attention_weights[0]  # (num_heads, 257, 257)

        # CLS token's attention to each patch token (skip CLS→CLS at index 0)
        cls_attn = attn[:, 0, 1:]  # (num_heads, 256)

        cls_attn = cls_attn.mean(dim=0)  # (256,) average across heads

        num_patches = int(cls_attn.shape[0] ** 0.5)
        cam = cls_attn.reshape(num_patches, num_patches).cpu().numpy()
        return _normalize(cam)


def _normalize(cam: np.ndarray) -> np.ndarray:
    return (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)


def _colorize_heatmap(heatmap: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize a grayscale heatmap and apply JET colormap, returning an RGB array."""
    resized = cv2.resize(heatmap, (width, height))
    colored = cv2.applyColorMap((resized * 255).astype(np.uint8), cv2.COLORMAP_JET)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)


class GradCAMVisualizer:
    """High-level visualizer that generates various Grad-CAM outputs."""

    _DEFAULT_MEAN = [0.485, 0.456, 0.406]
    _DEFAULT_STD = [0.229, 0.224, 0.225]

    def __init__(
        self,
        model: torch.nn.Module,
        target_layer: torch.nn.Module,
        image_size: int = 224,
        mean: Optional[list] = None,
        std: Optional[list] = None,
        model_type: str = "cnn"
    ):
        self.model = model
        self.image_size = image_size
        self.mean = np.array(mean if mean is not None else self._DEFAULT_MEAN)
        self.std = np.array(std if std is not None else self._DEFAULT_STD)

        if model_type == "vit":
            self.gradcam = ViTAttentionMap(model, target_layer)
        else:
            self.gradcam = GradCAM(model, target_layer)

    def _denormalize(self, tensor: torch.Tensor) -> np.ndarray:
        img = tensor.squeeze().detach().cpu().numpy().transpose(1, 2, 0)
        img = img * self.std + self.mean
        return np.clip(img * 255, 0, 255).astype(np.uint8)

    def _apply_heatmap(self, image: np.ndarray, heatmap: np.ndarray, alpha: float = 0.4) -> np.ndarray:
        heatmap_colored = _colorize_heatmap(heatmap, image.shape[1], image.shape[0])
        overlaid = (1 - alpha) * image + alpha * heatmap_colored
        return np.clip(overlaid, 0, 255).astype(np.uint8)

    def generate_visualization(
        self,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None,
        output_type: str = "all"
    ) -> dict:
        heatmap = self.gradcam.generate(input_tensor, target_class)
        original = self._denormalize(input_tensor)
        results = {}

        if output_type in ["heatmap", "all"]:
            colored = _colorize_heatmap(heatmap, self.image_size, self.image_size)
            results["heatmap"] = Image.fromarray(colored)

        if output_type in ["overlay", "all"]:
            results["overlay"] = Image.fromarray(self._apply_heatmap(original, heatmap))

        if output_type == "all":
            results["original"] = Image.fromarray(original)
            results["comparison"] = self._create_comparison(original, heatmap, results["overlay"])

        return results

    def _create_comparison(
        self, original: np.ndarray, heatmap: np.ndarray, overlay: Image.Image
    ) -> Image.Image:
        h, w = original.shape[:2]
        heatmap_colored = _colorize_heatmap(heatmap, w, h)
        overlay_np = np.array(overlay)

        label_height = 30
        comparison = np.full((h + label_height, w * 3, 3), 255, dtype=np.uint8)

        comparison[label_height:, :w] = original
        comparison[label_height:, w:2*w] = heatmap_colored
        comparison[label_height:, 2*w:] = overlay_np

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(comparison, "Original", (w//2 - 40, 20), font, 0.6, (0, 0, 0), 2)
        cv2.putText(comparison, "Attention", (w + w//2 - 45, 20), font, 0.6, (0, 0, 0), 2)
        cv2.putText(comparison, "Overlay", (2*w + w//2 - 35, 20), font, 0.6, (0, 0, 0), 2)

        return Image.fromarray(comparison)


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode()

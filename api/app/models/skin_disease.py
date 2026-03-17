"""
Skin Disease Classifier -- DINOv2 ViT-B/14

6-class classification of skin photographs:
acne, eczema, fungal, healthy, psoriasis, scabies

Trained on SCIN + SkinDisNet (smartphone photos).
"""

import torch
import torch.nn as nn
from torchvision import transforms
from transformers import AutoModel
from PIL import Image
import json
import io
from typing import Dict, Any, Optional

from .base import BaseClassifier
from ..utils.gradcam import GradCAMVisualizer, image_to_base64


class SkinDiseaseClassifier(BaseClassifier):
    """Skin disease classifier using DINOv2 ViT-B/14."""

    def __init__(self):
        super().__init__()
        self.model_name = "skin_disease"
        self.image_size = 224
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        self.transform = None

    def load_model(self, weights_path: str, config_path: str) -> None:
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.class_names = config['class_names']
        self.image_size = config.get('input_size', 224)

        normalize = config.get('normalize', {})
        self.mean = normalize.get('mean', self.mean)
        self.std = normalize.get('std', self.std)

        self.model = _DINOv2Classifier(
            config['backbone'], len(self.class_names), config.get('hidden_dim', 768)
        )
        self.model.load_state_dict(
            torch.load(weights_path, map_location=self.device, weights_only=True)
        )
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std),
        ])

        self.gradcam_visualizer = GradCAMVisualizer(
            model=self.model,
            target_layer=self.model.dinov2.encoder.layer[-1].attention.attention,
            image_size=self.image_size,
            mean=self.mean,
            std=self.std,
            model_type="vit",
        )
        print(f"Skin disease model loaded on {self.device}")

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return self.transform(image).unsqueeze(0).to(self.device)

    def _run_inference(self, image_bytes: bytes):
        """Shared preprocessing + forward pass. Returns (input_tensor, predicted_idx, confidence, probs_dict)."""
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = self.preprocess(image)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = probabilities.max(1)

        probs_dict = dict(zip(self.class_names, (float(p) for p in probabilities[0])))
        return input_tensor, predicted.item(), confidence.item(), probs_dict

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        _, predicted, confidence, probs_dict = self._run_inference(image_bytes)
        return {
            "model": self.model_name,
            "prediction": self.class_names[predicted],
            "confidence": confidence,
            "probabilities": probs_dict,
        }

    def get_gradcam(
        self,
        image_bytes: bytes,
        target_class: Optional[int] = None,
        output_type: str = "all",
    ) -> Dict[str, Any]:
        input_tensor, predicted, confidence, probs_dict = self._run_inference(image_bytes)

        if target_class is None:
            target_class = predicted

        visualizations = self.gradcam_visualizer.generate_visualization(
            input_tensor, target_class=target_class, output_type=output_type
        )

        return {
            "model": self.model_name,
            "prediction": self.class_names[predicted],
            "confidence": confidence,
            "probabilities": probs_dict,
            "visualized_class": self.class_names[target_class],
            "visualized_class_index": target_class,
            "images": {name: image_to_base64(img) for name, img in visualizations.items()},
        }


class _DINOv2Classifier(nn.Module):
    """DINOv2 backbone + linear classifier head (matches notebook architecture)."""

    def __init__(self, backbone_name: str, num_classes: int, hidden_dim: int = 768):
        super().__init__()
        self.dinov2 = AutoModel.from_pretrained(
            backbone_name, attn_implementation="eager"
        )
        for param in self.dinov2.parameters():
            param.requires_grad = False
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        outputs = self.dinov2(pixel_values)
        cls_token = outputs.last_hidden_state[:, 0]
        return self.classifier(cls_token)

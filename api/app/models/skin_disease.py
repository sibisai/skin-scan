"""
Skin Disease Classifier

Multi-class classification of skin photographs:
- Eczema (including dermatitis)
- Fungal (tinea, ringworm)
- Acne
- Psoriasis
- Scabies
- Healthy

Trained on: SCIN + SkinDisNet (smartphone photos)
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import json
import io
from typing import Dict, Any, Optional

from .base import BaseClassifier
from ..utils.gradcam import GradCAMVisualizer, image_to_base64


class SkinDiseaseClassifier(BaseClassifier):
    """Skin disease classifier using EfficientNet-V2-S."""

    def __init__(self):
        super().__init__()
        self.model_name = "skin_disease"
        self.image_size = 224
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        self.transform = None
        self.config = None

    def _build_model(self, num_classes: int) -> nn.Module:
        model = models.efficientnet_v2_s(weights=None)
        num_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(p=0.15),
            nn.Linear(512, num_classes)
        )
        return model

    def load_model(self, weights_path: str, config_path: str) -> None:
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.class_names = self.config['class_names']
        self.image_size = self.config.get('input_size', 224)

        normalize_config = self.config.get('normalize', {})
        self.mean = normalize_config.get('mean', [0.485, 0.456, 0.406])
        self.std = normalize_config.get('std', [0.229, 0.224, 0.225])

        self.model = self._build_model(len(self.class_names))
        self.model.load_state_dict(
            torch.load(weights_path, map_location=self.device, weights_only=True)
        )
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std)
        ])

        target_layer = self.model.features[-1]
        self.gradcam_visualizer = GradCAMVisualizer(
            model=self.model,
            target_layer=target_layer,
            image_size=self.image_size,
            mean=self.mean,
            std=self.std
        )
        print(f"Skin disease model loaded on {self.device}")

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        tensor = self.transform(image)
        return tensor.unsqueeze(0).to(self.device)

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = self.preprocess(image)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = probabilities.max(1)

        probs_dict = {
            name: float(prob)
            for name, prob in zip(self.class_names, probabilities[0].tolist())
        }

        return {
            "model": self.model_name,
            "prediction": self.class_names[predicted.item()],
            "confidence": float(confidence.item()),
            "probabilities": probs_dict
        }

    def get_gradcam(
        self,
        image_bytes: bytes,
        target_class: Optional[int] = None,
        output_type: str = "all"
    ) -> Dict[str, Any]:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = self.preprocess(image)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = probabilities.max(1)

        if target_class is None:
            target_class = predicted.item()

        input_tensor.requires_grad_(True)
        visualizations = self.gradcam_visualizer.generate_visualization(
            input_tensor,
            target_class=target_class,
            output_type=output_type
        )

        images_b64 = {name: image_to_base64(img) for name, img in visualizations.items()}

        probs_dict = {
            name: float(prob)
            for name, prob in zip(self.class_names, probabilities[0].tolist())
        }

        return {
            "model": self.model_name,
            "prediction": self.class_names[predicted.item()],
            "confidence": float(confidence.item()),
            "probabilities": probs_dict,
            "visualized_class": self.class_names[target_class],
            "visualized_class_index": target_class,
            "images": images_b64
        }

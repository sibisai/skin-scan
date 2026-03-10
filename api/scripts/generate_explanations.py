"""
Batch generate LLM explanations for all sample images.
Run this once to get real, image-specific explanations for Learn Mode.

Usage:
  cd api
  python scripts/generate_explanations.py

Output:
  Prints JavaScript object to paste into sampleData.js
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "samples"

# Sample images structure (matches sampleData.js)
SAMPLE_IMAGES = {
    "brain_tumor": [
        {"id": "glioma_1", "label": "Glioma", "path": "brain_tumor/glioma_1.jpg"},
        {"id": "glioma_2", "label": "Glioma", "path": "brain_tumor/glioma_2.jpg"},
        {"id": "meningioma_1", "label": "Meningioma", "path": "brain_tumor/meningioma_1.jpg"},
        {"id": "meningioma_2", "label": "Meningioma", "path": "brain_tumor/meningioma_2.jpg"},
        {"id": "pituitary_1", "label": "Pituitary", "path": "brain_tumor/pituitary_1.jpg"},
        {"id": "pituitary_2", "label": "Pituitary", "path": "brain_tumor/pituitary_2.jpg"},
        {"id": "notumor_1", "label": "No Tumor", "path": "brain_tumor/notumor_1.jpg"},
        {"id": "notumor_2", "label": "No Tumor", "path": "brain_tumor/notumor_2.jpg"},
    ],
    "pneumonia": [
        {"id": "normal_1", "label": "Normal", "path": "pneumonia/normal_1.jpg"},
        {"id": "normal_2", "label": "Normal", "path": "pneumonia/normal_2.jpg"},
        {"id": "pneumonia_1", "label": "Pneumonia", "path": "pneumonia/pneumonia_1.jpg"},
        {"id": "pneumonia_2", "label": "Pneumonia", "path": "pneumonia/pneumonia_2.jpg"},
    ],
    "retinal_oct": [
        {"id": "cnv_1", "label": "CNV", "path": "retinal_oct/cnv_1.jpg"},
        {"id": "cnv_2", "label": "CNV", "path": "retinal_oct/cnv_2.jpg"},
        {"id": "dme_1", "label": "DME", "path": "retinal_oct/dme_1.jpg"},
        {"id": "dme_2", "label": "DME", "path": "retinal_oct/dme_2.jpg"},
        {"id": "drusen_1", "label": "Drusen", "path": "retinal_oct/drusen_1.jpg"},
        {"id": "drusen_2", "label": "Drusen", "path": "retinal_oct/drusen_2.jpg"},
        {"id": "normal_1", "label": "Normal", "path": "retinal_oct/normal_1.jpg"},
        {"id": "normal_2", "label": "Normal", "path": "retinal_oct/normal_2.jpg"},
    ],
    "bone_fracture": [
        {"id": "fractured_1", "label": "Fractured", "path": "bone_fracture/fractured_1.jpg"},
        {"id": "fractured_2", "label": "Fractured", "path": "bone_fracture/fractured_2.jpg"},
        {"id": "fractured_3", "label": "Fractured", "path": "bone_fracture/fractured_3.jpg"},
        {"id": "fractured_4", "label": "Fractured", "path": "bone_fracture/fractured_4.jpg"},
        {"id": "normal_1", "label": "Not Fractured", "path": "bone_fracture/normal_1.jpg"},
        {"id": "normal_2", "label": "Not Fractured", "path": "bone_fracture/normal_2.jpg"},
        {"id": "normal_3", "label": "Not Fractured", "path": "bone_fracture/normal_3.jpg"},
        {"id": "normal_4", "label": "Not Fractured", "path": "bone_fracture/normal_4.jpg"},
    ],
}


def check_api():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if not data.get("llm_enabled"):
                print("WARNING: LLM not enabled. Set ANTHROPIC_API_KEY in .env")
                return False
            return True
    except requests.ConnectionError:
        pass
    
    print(f"ERROR: Cannot connect to API at {API_URL}")
    print("Make sure the API is running: uvicorn app.main:app --reload")
    return False


def get_explanation(model: str, image_path: Path) -> dict:
    """
    Get prediction and explanation for a single image.
    Returns dict with prediction, confidence, and explanation.
    """
    if not image_path.exists():
        return {"error": f"File not found: {image_path}"}
    
    # Step 1: Get Grad-CAM prediction
    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f, "image/jpeg")}
        response = requests.post(
            f"{API_URL}/predict/{model}/gradcam",
            files=files
        )
    
    if response.status_code != 200:
        return {"error": f"Gradcam failed: {response.text}"}
    
    result = response.json()
    prediction = result["prediction"]
    confidence = result["confidence"]
    comparison_b64 = result["images"].get("comparison")
    
    if not comparison_b64:
        return {"error": "No comparison image returned"}
    
    # Step 2: Get explanation
    comparison_bytes = base64.b64decode(comparison_b64)
    
    files = {"file": ("comparison.png", comparison_bytes, "image/png")}
    params = {"prediction": prediction, "confidence": str(confidence)}
    
    response = requests.post(
        f"{API_URL}/explain/{model}",
        files=files,
        params=params
    )
    
    if response.status_code != 200:
        return {"error": f"Explanation failed: {response.text}"}
    
    explanation_data = response.json()
    
    return {
        "prediction": prediction,
        "confidence": confidence,
        "explanation": explanation_data.get("explanation", "")
    }


def main():
    print("=" * 60)
    print("MedLens - Batch Generate Explanations")
    print("=" * 60)
    
    # Check API
    if not check_api():
        sys.exit(1)
    
    print(f"\nSamples directory: {SAMPLES_DIR}")
    
    if not SAMPLES_DIR.exists():
        print(f"ERROR: Samples directory not found: {SAMPLES_DIR}")
        print("Update SAMPLES_DIR path in this script.")
        sys.exit(1)
    
    # Generate explanations
    explanations = {}
    total = sum(len(samples) for samples in SAMPLE_IMAGES.values())
    current = 0
    
    print(f"\nGenerating explanations for {total} images...")
    print("This will take ~{} minutes\n".format(total * 4 // 60 + 1))
    
    for model, samples in SAMPLE_IMAGES.items():
        print(f"\n[{model}]")
        
        for sample in samples:
            current += 1
            image_path = SAMPLES_DIR / sample["path"]
            key = f"{model}_{sample['id']}"
            
            print(f"  ({current}/{total}) {sample['id']}...", end=" ", flush=True)
            
            result = get_explanation(model, image_path)
            
            if "error" in result:
                print(f"ERROR: {result['error']}")
                explanations[key] = f"[Error generating explanation for {sample['label']}]"
            else:
                print(f"OK ({result['prediction']}, {result['confidence']*100:.1f}%)")
                explanations[key] = result["explanation"]
    
    # Output as JavaScript
    print("\n" + "=" * 60)
    print("COPY THE FOLLOWING INTO sampleData.js:")
    print("=" * 60 + "\n")
    
    print("// Pre-cached LLM explanations for Learn Mode (auto-generated)")
    print("// Generated by: python scripts/generate_explanations.py")
    print("export const cachedExplanations = {")
    
    for key, explanation in explanations.items():
        # Escape quotes and newlines
        escaped = explanation.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        print(f'  "{key}": "{escaped}",')
    
    print("};")
    
    # Also save as JSON for backup
    output_file = Path(__file__).parent / "cached_explanations.json"
    with open(output_file, "w") as f:
        json.dump(explanations, f, indent=2)
    
    print(f"\n\nAlso saved to: {output_file}")
    print("Done!")


if __name__ == "__main__":
    main()
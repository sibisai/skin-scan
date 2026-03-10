"""
Batch generate Grad-CAM overlay images for all sample images.
Run this once to pre-cache overlays for instant quiz feedback.

Usage:
  cd api
  python scripts/generate_overlays.py

Output:
  Saves overlay images to frontend/public/samples/overlays/
"""

import os
import sys
import base64
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "samples"
OUTPUT_DIR = SAMPLES_DIR / "overlays"

# Sample images structure (matches sampleData.js)
SAMPLE_IMAGES = {
    "brain_tumor": [
        {"id": "glioma_1", "path": "brain_tumor/glioma_1.jpg"},
        {"id": "glioma_2", "path": "brain_tumor/glioma_2.jpg"},
        {"id": "meningioma_1", "path": "brain_tumor/meningioma_1.jpg"},
        {"id": "meningioma_2", "path": "brain_tumor/meningioma_2.jpg"},
        {"id": "pituitary_1", "path": "brain_tumor/pituitary_1.jpg"},
        {"id": "pituitary_2", "path": "brain_tumor/pituitary_2.jpg"},
        {"id": "notumor_1", "path": "brain_tumor/notumor_1.jpg"},
        {"id": "notumor_2", "path": "brain_tumor/notumor_2.jpg"},
    ],
    "pneumonia": [
        {"id": "normal_1", "path": "pneumonia/normal_1.jpg"},
        {"id": "normal_2", "path": "pneumonia/normal_2.jpg"},
        {"id": "pneumonia_1", "path": "pneumonia/pneumonia_1.jpg"},
        {"id": "pneumonia_2", "path": "pneumonia/pneumonia_2.jpg"},
    ],
    "retinal_oct": [
        {"id": "cnv_1", "path": "retinal_oct/cnv_1.jpg"},
        {"id": "cnv_2", "path": "retinal_oct/cnv_2.jpg"},
        {"id": "dme_1", "path": "retinal_oct/dme_1.jpg"},
        {"id": "dme_2", "path": "retinal_oct/dme_2.jpg"},
        {"id": "drusen_1", "path": "retinal_oct/drusen_1.jpg"},
        {"id": "drusen_2", "path": "retinal_oct/drusen_2.jpg"},
        {"id": "normal_1", "path": "retinal_oct/normal_1.jpg"},
        {"id": "normal_2", "path": "retinal_oct/normal_2.jpg"},
    ],
    "bone_fracture": [
        {"id": "fractured_1", "path": "bone_fracture/fractured_1.jpg"},
        {"id": "fractured_2", "path": "bone_fracture/fractured_2.jpg"},
        {"id": "fractured_3", "path": "bone_fracture/fractured_3.jpg"},
        {"id": "fractured_4", "path": "bone_fracture/fractured_4.jpg"},
        {"id": "normal_1", "path": "bone_fracture/normal_1.jpg"},
        {"id": "normal_2", "path": "bone_fracture/normal_2.jpg"},
        {"id": "normal_3", "path": "bone_fracture/normal_3.jpg"},
        {"id": "normal_4", "path": "bone_fracture/normal_4.jpg"},
    ],
}


def check_api():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def generate_overlay(model: str, image_path: Path) -> bytes | None:
    """
    Generate Grad-CAM overlay for a single image.
    Returns overlay image bytes or None on error.
    """
    if not image_path.exists():
        print(f"File not found: {image_path}")
        return None
    
    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f, "image/jpeg")}
        response = requests.post(
            f"{API_URL}/predict/{model}/gradcam",
            files=files
        )
    
    if response.status_code != 200:
        print(f"API error: {response.text}")
        return None
    
    result = response.json()
    overlay_b64 = result.get("images", {}).get("overlay")
    
    if not overlay_b64:
        print("No overlay in response")
        return None
    
    return base64.b64decode(overlay_b64)


def main():
    print("=" * 60)
    print("MedLens - Generate Grad-CAM Overlays")
    print("=" * 60)
    
    # Check API
    if not check_api():
        print(f"\nERROR: Cannot connect to API at {API_URL}")
        print("Make sure the API is running: uvicorn app.main:app --reload")
        sys.exit(1)
    
    print(f"\n✓ API connected")
    print(f"Samples directory: {SAMPLES_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    if not SAMPLES_DIR.exists():
        print(f"\nERROR: Samples directory not found: {SAMPLES_DIR}")
        sys.exit(1)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready")
    
    # Generate overlays
    total = sum(len(samples) for samples in SAMPLE_IMAGES.values())
    current = 0
    success = 0
    failed = 0
    
    print(f"\nGenerating {total} overlays...\n")
    
    for model, samples in SAMPLE_IMAGES.items():
        print(f"[{model}]")
        
        for sample in samples:
            current += 1
            image_path = SAMPLES_DIR / sample["path"]
            output_filename = f"{model}_{sample['id']}.png"
            output_path = OUTPUT_DIR / output_filename
            
            print(f"  ({current}/{total}) {sample['id']}...", end=" ", flush=True)
            
            # Skip if already exists
            if output_path.exists():
                print("SKIPPED (exists)")
                success += 1
                continue
            
            overlay_bytes = generate_overlay(model, image_path)
            
            if overlay_bytes:
                with open(output_path, "wb") as f:
                    f.write(overlay_bytes)
                print(f"OK ({len(overlay_bytes) // 1024}KB)")
                success += 1
            else:
                print("FAILED")
                failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Complete! {success}/{total} overlays generated")
    if failed > 0:
        print(f"Failed: {failed}")
    print(f"\nOverlays saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
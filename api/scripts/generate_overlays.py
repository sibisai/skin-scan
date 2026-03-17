"""
Batch generate Grad-CAM overlay images for all sample images.
Run this once to pre-cache overlays for instant quiz feedback.

Usage:
  cd api
  python scripts/generate_overlays.py

Output:
  Saves overlay images to frontend/public/samples/overlays/
"""

import sys
import base64
import requests
from pathlib import Path

API_URL = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "samples"
OUTPUT_DIR = SAMPLES_DIR / "overlays"

# Matches sampleData.js
SAMPLE_IMAGES = {
    "skin_disease": [
        {"id": "acne_1", "path": "skin_disease/acne_1.jpg"},
        {"id": "acne_2", "path": "skin_disease/acne_2.jpg"},
        {"id": "eczema_1", "path": "skin_disease/eczema_1.jpg"},
        {"id": "eczema_2", "path": "skin_disease/eczema_2.jpg"},
        {"id": "fungal_1", "path": "skin_disease/fungal_1.jpg"},
        {"id": "fungal_2", "path": "skin_disease/fungal_2.jpg"},
        {"id": "healthy_1", "path": "skin_disease/healthy_1.jpg"},
        {"id": "healthy_2", "path": "skin_disease/healthy_2.jpg"},
        {"id": "psoriasis_1", "path": "skin_disease/psoriasis_1.jpg"},
        {"id": "psoriasis_2", "path": "skin_disease/psoriasis_2.jpg"},
        {"id": "scabies_1", "path": "skin_disease/scabies_1.jpg"},
        {"id": "scabies_2", "path": "skin_disease/scabies_2.jpg"},
    ],
}


def check_api():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def generate_overlay(model: str, image_path: Path) -> bytes | None:
    """Generate Grad-CAM overlay for a single image."""
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
    print("SkinScan - Generate Grad-CAM Overlays")
    print("=" * 60)
    
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
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory ready")
    
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
            
            if output_path.exists():
                print("SKIPPED (exists)")
                success += 1
                continue
            
            overlay_bytes = generate_overlay(model, image_path)
            
            if overlay_bytes:
                output_path.write_bytes(overlay_bytes)
                print(f"OK ({len(overlay_bytes) // 1024}KB)")
                success += 1
            else:
                print("FAILED")
                failed += 1
    
    print("\n" + "=" * 60)
    print(f"Complete! {success}/{total} overlays generated")
    if failed > 0:
        print(f"Failed: {failed}")
    print(f"\nOverlays saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
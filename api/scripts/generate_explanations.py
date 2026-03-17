"""
Batch generate LLM explanations for all sample images.
Run this once to get real, image-specific explanations for Learn Mode.

Usage:
  cd api
  python scripts/generate_explanations.py

Output:
  Prints JavaScript object to paste into sampleData.js
"""

import sys
import base64
import requests
from pathlib import Path

API_URL = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "samples"

# Matches sampleData.js
SAMPLE_IMAGES = {
    "skin_disease": [
        {"id": "acne_1", "label": "Acne", "path": "skin_disease/acne_1.jpg"},
        {"id": "acne_2", "label": "Acne", "path": "skin_disease/acne_2.jpg"},
        {"id": "eczema_1", "label": "Eczema", "path": "skin_disease/eczema_1.jpg"},
        {"id": "eczema_2", "label": "Eczema", "path": "skin_disease/eczema_2.jpg"},
        {"id": "fungal_1", "label": "Fungal", "path": "skin_disease/fungal_1.jpg"},
        {"id": "fungal_2", "label": "Fungal", "path": "skin_disease/fungal_2.jpg"},
        {"id": "healthy_1", "label": "Healthy", "path": "skin_disease/healthy_1.jpg"},
        {"id": "healthy_2", "label": "Healthy", "path": "skin_disease/healthy_2.jpg"},
        {"id": "psoriasis_1", "label": "Psoriasis", "path": "skin_disease/psoriasis_1.jpg"},
        {"id": "psoriasis_2", "label": "Psoriasis", "path": "skin_disease/psoriasis_2.jpg"},
        {"id": "scabies_1", "label": "Scabies", "path": "skin_disease/scabies_1.jpg"},
        {"id": "scabies_2", "label": "Scabies", "path": "skin_disease/scabies_2.jpg"},
    ],
}


def check_api():
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
    """Get prediction and explanation for a single image."""
    if not image_path.exists():
        return {"error": f"File not found: {image_path}"}
    
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
    print("SkinScan - Batch Generate Explanations")
    print("=" * 60)
    
    if not check_api():
        sys.exit(1)
    
    print(f"\nSamples directory: {SAMPLES_DIR}")
    
    if not SAMPLES_DIR.exists():
        print(f"ERROR: Samples directory not found: {SAMPLES_DIR}")
        print("Update SAMPLES_DIR path in this script.")
        sys.exit(1)
    
    explanations = {}
    total = sum(len(samples) for samples in SAMPLE_IMAGES.values())
    current = 0
    
    print(f"\nGenerating explanations for {total} images...")
    print(f"This will take ~{total * 4 // 60 + 1} minutes\n")
    
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
    print("\nDone!")


if __name__ == "__main__":
    main()
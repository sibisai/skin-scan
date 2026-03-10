"""
Medical Image Analysis API
Extensible API for medical image classification with Grad-CAM visualization.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import base64
import os

from dotenv import load_dotenv
load_dotenv()

from app.models import SkinDiseaseClassifier
from app.utils.llm import generate_explanation, get_fallback_explanation

# ============================================================================
# Model Registry - Add new models here
# ============================================================================

MODELS: Dict[str, Any] = {}

def load_models():
    """Load skin disease model at startup."""
    weights_dir = os.getenv("WEIGHTS_DIR", "./weights")

    skin_weights = os.path.join(weights_dir, "skin_disease_model.pth")
    skin_config = os.path.join(weights_dir, "skin_disease_config.json")

    if os.path.exists(skin_weights) and os.path.exists(skin_config):
        try:
            classifier = SkinDiseaseClassifier()
            classifier.load_model(skin_weights, skin_config)
            MODELS["skin_disease"] = classifier
            print("Skin disease model loaded")
        except Exception as e:
            print(f"Failed to load skin disease model: {e}")
    else:
        print(f"Skin disease model files not found in {weights_dir}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Load models
    print("=" * 50)
    print("Loading models...")
    load_models()
    print(f"Loaded {len(MODELS)} model(s): {list(MODELS.keys())}")
    
    # Check LLM availability
    if os.getenv("ANTHROPIC_API_KEY"):
        print("✓ Anthropic API key configured")
    else:
        print("⚠ Anthropic API key not set - explanations will use fallback")
    print("=" * 50)
    yield
    # Shutdown: Cleanup if needed
    print("Shutting down...")


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="SkinScan API",
    description="""
    Skin disease classification API with Grad-CAM visualization.

    ## Model
    - **skin_disease**: Detects eczema, fungal, acne, psoriasis, scabies, healthy skin

    ## Features
    - Image classification with confidence scores
    - Grad-CAM visualization showing AI focus areas
    - AI-generated explanations
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """API root - health check."""
    return {
        "status": "healthy",
        "service": "SkinScan API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "models_loaded": len(MODELS),
        "available_models": list(MODELS.keys()),
        "llm_enabled": bool(os.getenv("ANTHROPIC_API_KEY"))
    }


@app.get("/models", tags=["Info"])
async def list_models():
    """List all available models and their details."""
    models_info = {}
    for name, model in MODELS.items():
        models_info[name] = model.get_model_info()
    return {"models": models_info}


@app.get("/models/{model_name}", tags=["Info"])
async def get_model_info(model_name: str):
    """Get detailed information about a specific model."""
    if model_name not in MODELS:
        raise HTTPException(
            status_code=404, 
            detail=f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
        )
    return MODELS[model_name].get_model_info()


# ============================================================================
# Prediction Endpoints
# ============================================================================

@app.post("/predict/{model_name}", tags=["Prediction"])
async def predict(
    model_name: str,
    file: UploadFile = File(..., description="Image file to classify")
):
    """
    Run classification on an uploaded image.
    
    Returns prediction with confidence scores for all classes.
    """
    # Validate model
    if model_name not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Run prediction
        result = MODELS[model_name].predict(image_bytes)
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/{model_name}/gradcam", tags=["Prediction"])
async def predict_with_gradcam(
    model_name: str,
    file: UploadFile = File(..., description="Image file to classify"),
    output_type: str = Query(
        default="all",
        description="Visualization type: 'heatmap', 'overlay', or 'all'"
    ),
    target_class: Optional[int] = Query(
        default=None,
        description="Class index to visualize. If not provided, uses predicted class."
    ),
    include_explanation: bool = Query(
        default=False,
        description="Whether to include AI-generated explanation (adds latency)"
    )
):
    """
    Run classification with Grad-CAM visualization.
    
    Returns prediction with confidence scores, base64-encoded visualization images.
    Set include_explanation=true to also get AI explanation (slower).
    
    **Output types:**
    - `heatmap`: Just the Grad-CAM heatmap
    - `overlay`: Heatmap overlaid on original image
    - `all`: Original, heatmap, overlay, and side-by-side comparison
    """
    # Validate model
    if model_name not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
        )
    
    # Validate output type
    if output_type not in ["heatmap", "overlay", "all"]:
        raise HTTPException(
            status_code=400,
            detail="output_type must be 'heatmap', 'overlay', or 'all'"
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Run prediction with Grad-CAM
        result = MODELS[model_name].get_gradcam(
            image_bytes,
            target_class=target_class,
            output_type=output_type
        )
        
        # Generate explanation if requested (adds latency)
        if include_explanation:
            comparison_b64 = result["images"].get("comparison")
            original_b64 = result["images"].get("original")
            overlay_b64 = result["images"].get("overlay")
            
            explanation = generate_explanation(
                model_name=model_name,
                prediction=result["prediction"],
                confidence=result["confidence"],
                probabilities=result["probabilities"],
                original_image_b64=original_b64,
                overlay_image_b64=overlay_b64,
                comparison_image_b64=comparison_b64,
            )
            
            # Use fallback if LLM fails
            if explanation is None:
                explanation = get_fallback_explanation(
                    model_name=model_name,
                    prediction=result["prediction"],
                    confidence=result["confidence"]
                )
            
            result["explanation"] = explanation
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/explain/{model_name}", tags=["Explanation"])
async def explain_prediction(
    model_name: str,
    prediction: str = Query(..., description="The predicted class"),
    confidence: float = Query(..., description="Confidence score (0-1)"),
    file: UploadFile = File(..., description="Comparison image (original + overlay side-by-side)"),
):
    """
    Generate an AI explanation for a prediction.
    
    Call this after /predict/{model_name}/gradcam to get a detailed
    explanation while showing results immediately to the user.
    
    Send the comparison image (side-by-side original and overlay) for best results.
    """
    # Validate model
    if model_name not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    try:
        # Read image bytes and convert to base64
        image_bytes = await file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Generate explanation
        explanation = generate_explanation(
            model_name=model_name,
            prediction=prediction,
            confidence=confidence,
            probabilities={},  # Not needed for explanation
            comparison_image_b64=image_b64,
        )
        
        # Use fallback if LLM fails
        if explanation is None:
            explanation = get_fallback_explanation(
                model_name=model_name,
                prediction=prediction,
                confidence=confidence
            )
        
        return {"explanation": explanation}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@app.post("/predict/{model_name}/gradcam/image", tags=["Prediction"])
async def predict_gradcam_image(
    model_name: str,
    file: UploadFile = File(..., description="Image file to classify"),
    image_type: str = Query(
        default="comparison",
        description="Image to return: 'original', 'heatmap', 'overlay', or 'comparison'"
    ),
    target_class: Optional[int] = Query(
        default=None,
        description="Class index to visualize. If not provided, uses predicted class."
    )
):
    """
    Run classification and return Grad-CAM visualization as an image file.
    
    Use this endpoint when you want to display the visualization directly
    (e.g., in an <img> tag) rather than receiving base64 data.
    """
    # Validate model
    if model_name not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
        )
    
    # Map image_type to output_type
    type_map = {
        "original": "all",
        "heatmap": "heatmap", 
        "overlay": "overlay",
        "comparison": "all"
    }
    
    if image_type not in type_map:
        raise HTTPException(
            status_code=400,
            detail="image_type must be 'original', 'heatmap', 'overlay', or 'comparison'"
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Run prediction with Grad-CAM
        result = MODELS[model_name].get_gradcam(
            image_bytes,
            target_class=target_class,
            output_type=type_map[image_type]
        )
        
        # Get requested image
        image_key = image_type if image_type != "comparison" else "comparison"
        if image_key not in result["images"]:
            # Fallback for heatmap/overlay only modes
            image_key = list(result["images"].keys())[0]
        
        image_b64 = result["images"][image_key]
        image_data = base64.b64decode(image_b64)
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "X-Prediction": result["prediction"],
                "X-Confidence": str(result["confidence"]),
                "X-Model": model_name
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ============================================================================
# Run with: uvicorn app.main:app --reload
# ============================================================================
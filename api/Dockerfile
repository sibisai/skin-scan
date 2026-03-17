# SkinScan API
# Optimized for Fly.io deployment

FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV WEIGHTS_DIR=/app/weights

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

# Install PyTorch CPU version (smaller image size for deployment)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements (torch already satisfied from CPU install above)
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download HuggingFace model during build to avoid cold-start latency
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('Jayanth2002/dinov2-base-finetuned-SkinDisease')"

# Copy application code
COPY app/ ./app/

# Copy model weights
COPY weights/ ./weights/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

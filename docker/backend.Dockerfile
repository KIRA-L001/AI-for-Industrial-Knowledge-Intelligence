# ─────────────────────────────────────────────────────────────
# KIRA backend — FastAPI + Celery worker share this image.
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TORCH_HOME=/tmp/torch

# System deps: OCR (tesseract), PDF/image handling, build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        poppler-utils \
        tesseract-ocr \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Lean default install — no torch/sentence-transformers (the app falls back to
# deterministic offline embedders/rerankers). To enable real ML models, also run:
#   pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1
#   pip install -r requirements-ml.txt
COPY apps/backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY apps/backend/ ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

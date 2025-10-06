# Simple Dockerfile for the FastAPI backend
# Adjust the uvicorn entrypoint (backend.main:app) if your app module or callable differs.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps required to build some wheels (adjust if you don't need them)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential gcc git \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt

# Copy the backend source
COPY backend /app/backend

EXPOSE 8000

# Default command — change backend.main:app to the correct module:callable if needed
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

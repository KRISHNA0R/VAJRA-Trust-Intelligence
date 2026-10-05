# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for OpenCV and other libraries)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    curl \
    git \
    wget \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY configs/requirements.txt /app/configs/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r configs/requirements.txt

# Copy all application code and model files
# This includes:
# - Application source code (app/)
# - Model files (models/trufor.pth.tar, models/vendors/DeepfakeBench/*)
# - Configuration files (configs/)
# - TruFor framework (TruFor-main/)
# NOTE: Ensure model files are in models/ directory before building the image
COPY . .

# Create necessary runtime directories
RUN mkdir -p logs data/jobs temp

# Expose port
EXPOSE 8000

# Set environment variables
ENV MODEL_PATH=models/trufor.pth.tar \
    HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "-m", "app.main"]



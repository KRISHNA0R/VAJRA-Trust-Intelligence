#!/bin/bash

echo "============================================"
echo " Deepfake Detector - Local Startup"
echo "============================================"
echo
echo "WARNING: Docker deployment is RECOMMENDED!"
echo "This script is for advanced users only."
echo
read -p "Press Enter to continue..."

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        echo "Please ensure Python 3.11+ is installed"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r configs/requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if model weights exist
if [ ! -f "models/trufor.pth.tar" ]; then
    echo "ERROR: models/trufor.pth.tar not found!"
    echo "Please download model weights first."
    echo "See: WEIGHTS_DOWNLOAD_GUIDE.md"
    exit 1
fi

# Start the server
echo
echo "Starting server..."
echo "Access at: http://localhost:8000/web/index_main.html"
echo
python scripts/start_trufor.py



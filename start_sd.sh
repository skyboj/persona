#!/bin/bash

# Script to start Automatic1111 Stable Diffusion WebUI
# Make sure to update the path to your Automatic1111 installation

AUTOMATIC1111_PATH="/path/to/stable-diffusion-webui"  # UPDATE THIS PATH

echo "Starting Automatic1111 Stable Diffusion WebUI..."

# Check if Automatic1111 directory exists
if [ ! -d "$AUTOMATIC1111_PATH" ]; then
    echo "Error: Automatic1111 not found at $AUTOMATIC1111_PATH"
    echo "Please update the AUTOMATIC1111_PATH in this script"
    exit 1
fi

# Navigate to Automatic1111 directory
cd "$AUTOMATIC1111_PATH"

# Start Automatic1111 with API enabled
echo "Starting with API enabled..."
./webui.sh --api --listen --port 7860

echo "Automatic1111 started successfully!"
echo "Access the WebUI at: http://127.0.0.1:7860"
echo "API endpoint: http://127.0.0.1:7860/sdapi/v1/" 
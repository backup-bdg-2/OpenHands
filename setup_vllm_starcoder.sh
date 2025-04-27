#!/bin/bash

# Setup script for vLLM with StarCoder
# This script installs vLLM and sets up the StarCoder model

# Exit on error
set -e

echo "Setting up vLLM with StarCoder for Backdoor AI..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Install vLLM
echo "Installing vLLM..."
pip install vllm

# Check if CUDA is available
if python3 -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    echo "CUDA is available. You can run StarCoder on GPU."
else
    echo "WARNING: CUDA is not available. StarCoder will run on CPU, which may be very slow."
    echo "Consider using a machine with a GPU for better performance."
fi

# Set up environment variables
echo "Setting up environment variables..."
export VLLM_API_URL="http://localhost:8000/v1/completions"

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo "WARNING: HF_TOKEN environment variable is not set."
    echo "You may need to set this to access the StarCoder model."
    echo "Visit https://huggingface.co/bigcode/starcoder to accept the license and get a token."
    echo "Then set the token with: export HF_TOKEN=your_token_here"
fi

echo "Setup complete!"
echo ""
echo "To start the vLLM server with StarCoder, run:"
echo "vllm serve bigcode/starcoder --port 8000"
echo ""
echo "If you have limited GPU memory, you can use a quantized version:"
echo "vllm serve bigcode/starcoder --port 8000 --quantization awq"
echo ""
echo "Make sure to set the HF_TOKEN environment variable if you haven't already:"
echo "export HF_TOKEN=your_token_here"
echo ""
echo "Once the server is running, you can start Backdoor AI!"

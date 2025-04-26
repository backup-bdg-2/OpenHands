#!/bin/bash
# Script to help deploy OpenHands to Render.com

# Print banner
echo "=================================================="
echo "OpenHands Deployment Helper for Render.com"
echo "=================================================="
echo ""

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo "render-cli is not installed. You can deploy manually by following the instructions in RENDER_DEPLOYMENT.md"
    echo "Alternatively, you can install render-cli with: npm install -g @render/cli"
    echo ""
    echo "Continuing with manual deployment instructions..."
else
    echo "render-cli is installed. You can use it to deploy directly from the command line."
    echo "Run: render blueprint create"
    echo ""
fi

# Print deployment instructions
echo "To deploy OpenHands to Render.com:"
echo ""
echo "1. Make sure you have a Render.com account"
echo "2. Log in to your Render.com dashboard"
echo "3. Click 'New' and select 'Blueprint'"
echo "4. Connect your GitHub account if you haven't already"
echo "5. Select the repository containing OpenHands"
echo "6. Render will automatically detect the render.yaml file and set up the services"
echo "7. Click 'Apply' to start the deployment process"
echo ""
echo "For more detailed instructions, see RENDER_DEPLOYMENT.md"
echo ""

# Check if config.toml exists and has the correct model
if [ -f "config.toml" ]; then
    model=$(grep "model" config.toml | head -1 | cut -d'"' -f2)
    echo "Current model in config.toml: $model"
    
    if [[ "$model" == *"meta-llama/CodeLlama-13b-Instruct-hf"* ]]; then
        echo "✅ Model is correctly set to CodeLlama-13b-Instruct-hf"
    else
        echo "❌ Model is not set to CodeLlama-13b-Instruct-hf. Please update config.toml."
    fi
    
    # Check if API key is set
    if grep -q "api_key" config.toml; then
        echo "✅ API key is set in config.toml"
    else
        echo "❌ API key is not set in config.toml. Please add your Hugging Face API key."
    fi
else
    echo "❌ config.toml not found. Please create it with the correct model and API key."
fi

echo ""
echo "=================================================="
echo "Deployment preparation complete!"
echo "=================================================="
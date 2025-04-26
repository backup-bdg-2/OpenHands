# Deploying OpenHands to Render.com

This guide explains how to deploy OpenHands to Render.com using the free tier.

## Prerequisites

1. A Render.com account
2. Your Hugging Face API key (you'll need to replace the placeholder in render.yaml)

## Deployment Steps

### 1. Fork or Clone the Repository

Make sure you have a copy of the OpenHands repository in your GitHub account.

### 2. Connect to Render.com

1. Log in to your Render.com account
2. Go to the Dashboard
3. Click "New" and select "Blueprint"
4. Connect your GitHub account if you haven't already
5. Select the repository containing OpenHands
6. Render will automatically detect the `render.yaml` file and set up the services

### 3. Configure Environment Variables

The `render.yaml` file already includes the necessary environment variables:

- `LLM_MODEL`: Set to `huggingface/meta-llama/CodeLlama-13b-Instruct-hf`
- `LLM_API_KEY`: Your Hugging Face API key
- `LLM_TEMPERATURE`: Set to 0.1
- `LLM_MAX_OUTPUT_TOKENS`: Set to 1024

### 4. Deploy

1. Click "Apply" to start the deployment process
2. Render will build and deploy both the backend and frontend services
3. Once deployment is complete, you can access your OpenHands instance at the URL provided by Render

## Configuration Details

### Backend Service

- **Environment**: Python
- **Build Command**: Uses Poetry installed in a temporary directory to avoid read-only filesystem issues
- **Start Command**: `poetry run python -m openhands.server.main`
- **Plan**: Free tier

### Frontend Service

- **Environment**: Node.js
- **Build Command**: `cd frontend && npm install && npm run build`
- **Start Command**: `cd frontend && npm run preview -- --port $PORT --host 0.0.0.0`
- **Plan**: Free tier

## Important Notes About Render.com

- Render.com uses a read-only filesystem for most directories
- Always use `/tmp` for any temporary files or installations during the build process
- The home directory and most system directories are read-only

## Limitations on Free Tier

- Services on the free tier will spin down after 15 minutes of inactivity
- They will spin back up when a new request comes in, but there may be a delay
- Free tier has limited resources, which may affect performance with complex tasks
- Free tier is limited to 750 hours of usage per month

## Troubleshooting

If you encounter issues during deployment:

1. Check the build logs in Render.com dashboard
2. Ensure your Hugging Face API key is valid
3. Verify that the Hugging Face model is accessible with your API key
4. Check if the services are properly connected (frontend should be able to communicate with backend)
5. If you see filesystem errors, make sure any file operations are using the `/tmp` directory

For more detailed logs, you can access the logs section for each service in the Render dashboard.

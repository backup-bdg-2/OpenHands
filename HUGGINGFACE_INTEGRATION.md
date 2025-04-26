# Hugging Face Integration for OpenHands

This document explains how OpenHands has been configured to use Hugging Face's CodeLlama-13b-Instruct-hf model for AI-powered software development assistance.

## Configuration

The integration uses the following configuration:

1. **Model**: `huggingface/meta-llama/CodeLlama-13b-Instruct-hf`
   - A powerful code-focused LLM from Meta
   - 13 billion parameters optimized for code understanding and generation
   - Fine-tuned with instruction following capabilities
2. **API Key**: Your Hugging Face API key (replace the placeholder in config.toml)
3. **Temperature**: 0.1 (low temperature for more deterministic outputs)
4. **Max Output Tokens**: 1024 (sufficient for most code generation tasks)

## Files Modified/Created

1. **config.toml**: Main configuration file for OpenHands with Hugging Face settings
2. **render.yaml**: Configuration for deploying to Render.com
3. **RENDER_DEPLOYMENT.md**: Instructions for deploying to Render.com
4. **test_hf_integration.py**: Script to test the Hugging Face integration
5. **deploy_to_render.sh**: Helper script for deployment
6. **HUGGINGFACE_INTEGRATION.md**: This file

## How It Works

OpenHands uses [LiteLLM](https://github.com/BerriAI/litellm) as an abstraction layer for various LLM providers. LiteLLM supports Hugging Face models through its API.

The configuration in `config.toml` sets up OpenHands to use the Hugging Face model with your API key. The model name format `huggingface/meta-llama/CodeLlama-13b-Instruct-hf` tells LiteLLM to use the Hugging Face provider with the specified model.

## Testing the Integration

You can test the integration by running:

```bash
python test_hf_integration.py
```

This script will:
1. Load the configuration from `config.toml`
2. Initialize the LLM with the Hugging Face model
3. Send a test prompt to the model
4. Print the response

## Deployment

For deployment instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

You can also use the helper script:

```bash
./deploy_to_render.sh
```

## Troubleshooting

If you encounter issues with the Hugging Face integration:

1. **API Key Issues**: 
   - Ensure your Hugging Face API key is valid and has access to the CodeLlama-13b-Instruct-hf model
   - Check that the API key is correctly set in both `config.toml` and environment variables
   - Verify API key permissions in your Hugging Face account settings

2. **Model Access**: 
   - Verify you have access to the model on Hugging Face (you may need to accept the model's terms of use)
   - Some models require explicit approval before they can be accessed via API
   - Visit the model page on Hugging Face and check for any usage restrictions

3. **Configuration**: 
   - Check that `config.toml` has the correct model name and API key
   - Ensure the model name format is correct: `huggingface/meta-llama/CodeLlama-13b-Instruct-hf`
   - Verify that environment variables aren't overriding your configuration

4. **Dependencies**: 
   - Ensure all dependencies are installed (`pip install -e .` or `poetry install`)
   - Make sure you have the latest version of LiteLLM that supports Hugging Face
   - Check for any Python version compatibility issues

5. **Rate Limits and Quotas**:
   - Be aware of Hugging Face's rate limits and quotas for API usage
   - Monitor your usage in the Hugging Face dashboard
   - Consider implementing backoff strategies for high-volume usage

## Resources

- [Hugging Face Documentation](https://huggingface.co/docs)
- [CodeLlama-13b-Instruct-hf Model](https://huggingface.co/meta-llama/CodeLlama-13b-Instruct-hf)
- [LiteLLM Documentation](https://docs.litellm.ai/docs/)
- [OpenHands Documentation](https://docs.all-hands.dev/)
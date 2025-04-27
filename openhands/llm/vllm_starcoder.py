import os
import warnings
from typing import Any, Dict, List, Optional

import httpx
from pydantic import SecretStr

from openhands.core.config import LLMConfig
from openhands.core.exceptions import LLMNoResponseError
from openhands.core.logger import openhands_logger as logger
from openhands.core.message import Message
from openhands.llm.debug_mixin import DebugMixin
from openhands.llm.metrics import Metrics
from openhands.llm.retry_mixin import RetryMixin

# Define constants for vLLM StarCoder integration
VLLM_API_URL = "http://localhost:8000/v1/completions"
STARCODER_MODEL = "bigcode/starcoder"
HF_TOKEN_ENV = "HF_TOKEN"

class VLLMStarCoder(RetryMixin, DebugMixin):
    """
    A class that integrates with vLLM running the StarCoder model.
    This is a hardcoded implementation that only works with the StarCoder model.
    """

    def __init__(
        self,
        config: LLMConfig,
        metrics: Metrics | None = None,
        retry_listener: Any = None,
    ):
        """Initialize the VLLMStarCoder instance.

        Args:
            config: The LLM configuration.
            metrics: The metrics to use.
            retry_listener: Optional callback for retry events.
        """
        self.metrics = metrics if metrics is not None else Metrics(model_name=STARCODER_MODEL)
        self.config = config
        self.retry_listener = retry_listener
        
        # Override config values with hardcoded StarCoder settings
        self.config.model = STARCODER_MODEL
        self.config.base_url = os.environ.get("VLLM_API_URL", VLLM_API_URL)
        
        # Check if HF_TOKEN is set in environment
        if HF_TOKEN_ENV not in os.environ:
            logger.warning(f"{HF_TOKEN_ENV} environment variable not set. You may need this for accessing the StarCoder model.")
        
        logger.info(f"Initialized VLLMStarCoder with base URL: {self.config.base_url}")

    async def generate(
        self, 
        messages: List[Message] | Message,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the StarCoder model using vLLM.

        Args:
            messages: The messages to generate a response for.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            **kwargs: Additional arguments to pass to the vLLM API.

        Returns:
            A dictionary containing the generated response.
        """
        if isinstance(messages, Message):
            messages = [messages]
            
        # Format messages for the model
        formatted_messages = self.format_messages_for_llm(messages)
        prompt = self._convert_messages_to_prompt(formatted_messages)
        
        # Log the prompt
        self.log_prompt(formatted_messages)
        
        # Prepare the request
        request_data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "model": STARCODER_MODEL,
        }
        
        # Add any additional parameters
        request_data.update(kwargs)
        
        # Make the request to vLLM
        try:
            headers = {}
            hf_token = os.environ.get(HF_TOKEN_ENV)
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.base_url,
                    json=request_data,
                    headers=headers,
                    timeout=self.config.timeout or 60,
                )
                
            if response.status_code != 200:
                error_msg = f"vLLM API returned status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise LLMNoResponseError(error_msg)
                
            response_data = response.json()
            
            # Format the response to match the expected structure
            result = {
                "id": response_data.get("id", "unknown"),
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response_data.get("choices", [{}])[0].get("text", ""),
                        },
                        "finish_reason": response_data.get("choices", [{}])[0].get("finish_reason", "stop"),
                    }
                ],
                "usage": {
                    "prompt_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response_data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": response_data.get("usage", {}).get("total_tokens", 0),
                },
            }
            
            return result
            
        except httpx.TimeoutException:
            error_msg = "Request to vLLM API timed out"
            logger.error(error_msg)
            raise LLMNoResponseError(error_msg)
        except Exception as e:
            error_msg = f"Error calling vLLM API: {str(e)}"
            logger.error(error_msg)
            raise LLMNoResponseError(error_msg)

    def _convert_messages_to_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """Convert a list of messages to a prompt string for StarCoder.

        Args:
            messages: A list of message dictionaries.

        Returns:
            A prompt string formatted for StarCoder.
        """
        prompt = ""
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"<system>\n{content}\n</system>\n\n"
            elif role == "user":
                prompt += f"<human>\n{content}\n</human>\n\n"
            elif role == "assistant":
                prompt += f"<assistant>\n{content}\n</assistant>\n\n"
            else:
                # For any other role, just add the content
                prompt += f"{content}\n\n"
                
        # Add the final assistant prompt
        prompt += "<assistant>\n"
        
        return prompt

    def format_messages_for_llm(self, messages: Message | List[Message]) -> List[Dict[str, Any]]:
        """Format messages for the LLM.

        Args:
            messages: A message or list of messages.

        Returns:
            A list of message dictionaries.
        """
        if isinstance(messages, Message):
            messages = [messages]
            
        # Convert Message objects to dictionaries
        return [message.model_dump() for message in messages]

    def get_token_count(self, messages: List[Dict] | List[Message]) -> int:
        """Get the number of tokens in a list of messages.

        Args:
            messages: A list of messages.

        Returns:
            The number of tokens.
        """
        # For simplicity, we'll estimate token count based on characters
        # A more accurate implementation would use a proper tokenizer
        if isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], Message):
                messages = self.format_messages_for_llm(messages)  # type: ignore
                
        total_chars = 0
        for message in messages:
            if isinstance(message, dict):
                content = message.get("content", "")
                if isinstance(content, str):
                    total_chars += len(content)
                    
        # Rough estimate: 4 characters per token
        return total_chars // 4

    def reset(self) -> None:
        """Reset the metrics."""
        self.metrics.reset()

    def __str__(self) -> str:
        return f"VLLMStarCoder(model={STARCODER_MODEL}, base_url={self.config.base_url})"

    def __repr__(self) -> str:
        return str(self)

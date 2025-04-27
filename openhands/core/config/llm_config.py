from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field, SecretStr, ValidationError

from openhands.core.logger import LOG_DIR
from openhands.core.logger import openhands_logger as logger


class LLMConfig(BaseModel):
    """Configuration for the LLM model.

    Attributes:
        model: The model to use (hardcoded to StarCoder).
        api_key: The API key to use.
        base_url: The base URL for the API. This is necessary for local LLMs.
        api_version: The version of the API.
        num_retries: The number of retries to attempt.
        retry_multiplier: The multiplier for the exponential backoff.
        retry_min_wait: The minimum time to wait between retries, in seconds.
        retry_max_wait: The maximum time to wait between retries, in seconds.
        timeout: The timeout for the API.
        max_message_chars: The approximate max number of characters in the content of an event included in the prompt to the LLM.
        temperature: The temperature for the API.
        max_output_tokens: The maximum number of output tokens. This is sent to the LLM.
        log_completions: Whether to log LLM completions to the state.
        log_completions_folder: The folder to log LLM completions to. Required if log_completions is True.
    """

    # Hardcoded to use StarCoder model
    model: str = Field(default='bigcode/starcoder')
    api_key: SecretStr | None = Field(default=None)
    base_url: str | None = Field(default="http://localhost:8000/v1/completions")
    api_version: str | None = Field(default=None)
    # total wait time: 5 + 10 + 20 + 30 = 65 seconds
    num_retries: int = Field(default=4)
    retry_multiplier: float = Field(default=2)
    retry_min_wait: int = Field(default=5)
    retry_max_wait: int = Field(default=30)
    timeout: int | None = Field(default=None)
    max_message_chars: int = Field(
        default=30_000
    )  # maximum number of characters in an observation's content when sent to the llm
    temperature: float = Field(default=0.1)
    max_output_tokens: int | None = Field(default=1024)
    log_completions: bool = Field(default=False)
    log_completions_folder: str = Field(default=os.path.join(LOG_DIR, 'completions'))

    model_config = {'extra': 'forbid'}

    @classmethod
    def from_toml_section(cls, data: dict) -> dict[str, LLMConfig]:
        """
        Create a mapping of LLMConfig instances from a toml dictionary representing the [llm] section.
        
        Note: This method is maintained for compatibility, but all configurations will use the hardcoded
        StarCoder model regardless of what's specified in the config file.

        Returns:
            dict[str, LLMConfig]: A mapping where the key "llm" corresponds to the default configuration.
        """
        # Always return the hardcoded configuration
        logger.warning("Using hardcoded StarCoder model configuration regardless of config file settings")
        return {"llm": cls()}

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook."""
        super().model_post_init(__context)
        
        # Ensure the model is always set to StarCoder
        self.model = 'bigcode/starcoder'
        self.base_url = os.environ.get("VLLM_API_URL", "http://localhost:8000/v1/completions")

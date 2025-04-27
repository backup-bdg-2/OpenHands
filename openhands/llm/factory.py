from typing import Any, Optional

from openhands.core.config import LLMConfig
from openhands.core.logger import openhands_logger as logger
from openhands.llm.metrics import Metrics
from openhands.llm.vllm_starcoder import VLLMStarCoder

def create_llm(
    config: LLMConfig,
    metrics: Optional[Metrics] = None,
    retry_listener: Any = None,
) -> VLLMStarCoder:
    """Create a new LLM instance.
    
    This factory always returns a VLLMStarCoder instance, regardless of the config.
    
    Args:
        config: The LLM configuration.
        metrics: Optional metrics instance.
        retry_listener: Optional retry listener.
        
    Returns:
        A VLLMStarCoder instance.
    """
    logger.info("Creating VLLMStarCoder instance (hardcoded model)")
    return VLLMStarCoder(config, metrics, retry_listener)

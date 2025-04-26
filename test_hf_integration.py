#!/usr/bin/env python3
"""
Test script to verify Hugging Face integration with OpenHands.
This script loads the configuration from config.toml and tests the LLM integration.
"""

import os
import sys
from pydantic import SecretStr

# Add the current directory to the path so we can import openhands
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openhands.core.config import load_app_config
from openhands.llm.llm import LLM
from openhands.core.message import Message

def test_huggingface_integration():
    """Test the Hugging Face integration with OpenHands."""
    print("Loading configuration from config.toml...")
    config = load_app_config()
    
    # Get the LLM configuration
    llm_config = config.get_llm_config()
    
    # Print the configuration
    print(f"Model: {llm_config.model}")
    print(f"API Key: {'*' * 8 + llm_config.api_key.get_secret_value()[-4:] if llm_config.api_key else 'Not set'}")
    print(f"Temperature: {llm_config.temperature}")
    print(f"Max Output Tokens: {llm_config.max_output_tokens}")
    
    # Create the LLM
    print("\nInitializing LLM...")
    llm = LLM(config=llm_config)
    
    # Test the LLM with a simple prompt
    print("\nTesting LLM with a simple prompt...")
    messages = [
        Message(role="system", content="You are a helpful AI assistant."),
        Message(role="user", content="Write a simple Python function to calculate the factorial of a number.")
    ]
    
    try:
        response = llm.completion(messages=messages)
        print("\nResponse from LLM:")
        print(response.choices[0].message.content)
        print("\nHugging Face integration test successful!")
    except Exception as e:
        print(f"\nError testing LLM: {e}")
        print("\nHugging Face integration test failed.")

if __name__ == "__main__":
    test_huggingface_integration()
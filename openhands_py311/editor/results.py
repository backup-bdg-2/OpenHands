"""
Results for the editor module.

This module provides result classes for the editor module.
"""

from typing import Any, Dict, Optional

class ToolResult:
    """Result of a tool operation.
    
    Attributes:
        success: Whether the operation was successful.
        message: Message describing the result.
        data: Additional data about the result.
    """
    
    def __init__(self, success: bool = True, message: str = "", data: Optional[Dict[str, Any]] = None):
        """Initialize a ToolResult.
        
        Args:
            success: Whether the operation was successful.
            message: Message describing the result.
            data: Additional data about the result.
        """
        self.success = success
        self.message = message
        self.data = data or {}

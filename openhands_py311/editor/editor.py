"""
Editor implementation for OpenHands Python 3.11 compatibility.

This module provides the OHEditor class for file editing functionality compatible with Python 3.11.11.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

from openhands_py311.editor.exceptions import ToolError
from openhands_py311.editor.results import ToolResult

class OHEditor:
    """Editor implementation for Python 3.11.
    
    This class provides file editing functionality compatible with Python 3.11.11.
    """
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize the editor.
        
        Args:
            workspace_dir: Optional workspace directory. If not provided, the current directory is used.
        """
        self.workspace_dir = workspace_dir or os.getcwd()
    
    def read_file(self, file_path: str) -> str:
        """Read the content of a file.
        
        Args:
            file_path: Path to the file to read.
            
        Returns:
            The content of the file as a string.
            
        Raises:
            ToolError: If the file cannot be read.
        """
        try:
            full_path = self._get_full_path(file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ToolError(f"Error reading file {file_path}: {str(e)}")
    
    def write_file(self, file_path: str, content: str) -> ToolResult:
        """Write content to a file.
        
        Args:
            file_path: Path to the file to write.
            content: Content to write to the file.
            
        Returns:
            ToolResult: Result of the operation.
            
        Raises:
            ToolError: If the file cannot be written.
        """
        try:
            full_path = self._get_full_path(file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                message=f"File {file_path} written successfully.",
                data={"file_path": file_path}
            )
        except Exception as e:
            raise ToolError(f"Error writing file {file_path}: {str(e)}")
    
    def edit_file(self, file_path: str, edit_fn) -> ToolResult:
        """Edit a file using the provided edit function.
        
        Args:
            file_path: Path to the file to edit.
            edit_fn: Function that takes the file content as input and returns the edited content.
            
        Returns:
            ToolResult: Result of the operation.
            
        Raises:
            ToolError: If the file cannot be edited.
        """
        try:
            full_path = self._get_full_path(file_path)
            
            # Read the file
            content = self.read_file(file_path)
            
            # Apply the edit function
            edited_content = edit_fn(content)
            
            # Write the edited content back to the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(edited_content)
            
            return ToolResult(
                success=True,
                message=f"File {file_path} edited successfully.",
                data={"file_path": file_path}
            )
        except Exception as e:
            raise ToolError(f"Error editing file {file_path}: {str(e)}")
    
    def _get_full_path(self, file_path: str) -> str:
        """Get the full path to a file.
        
        Args:
            file_path: Path to the file, relative to the workspace directory.
            
        Returns:
            The full path to the file.
        """
        if os.path.isabs(file_path):
            return file_path
        
        return os.path.join(self.workspace_dir, file_path)

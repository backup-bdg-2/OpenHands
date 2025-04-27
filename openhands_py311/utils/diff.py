"""
Diff utility for OpenHands Python 3.11 compatibility.

This module provides diff functionality compatible with Python 3.11.11.
"""

import difflib
from typing import List, Optional, Tuple, Union

def get_diff(original: str, updated: str, context_lines: int = 3) -> str:
    """Get the diff between two strings.
    
    Args:
        original: Original string.
        updated: Updated string.
        context_lines: Number of context lines to include in the diff.
        
    Returns:
        Unified diff as a string.
    """
    original_lines = original.splitlines(keepends=True)
    updated_lines = updated.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile='original',
        tofile='updated',
        n=context_lines
    )
    
    return ''.join(diff)

"""
Diff utility for OpenHands Python 3.11 compatibility.

This module provides diff functionality compatible with Python 3.11.11.
"""

import difflib
import os
import re
from typing import Dict, List, Optional, Tuple, Union, Any

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

def get_diff_with_line_numbers(original: str, updated: str, context_lines: int = 3) -> str:
    """Get the diff between two strings with line numbers.
    
    Args:
        original: Original string.
        updated: Updated string.
        context_lines: Number of context lines to include in the diff.
        
    Returns:
        Unified diff as a string with line numbers.
    """
    original_lines = original.splitlines()
    updated_lines = updated.splitlines()
    
    # Generate the diff
    diff = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile='original',
        tofile='updated',
        n=context_lines,
        lineterm=''
    )
    
    # Process the diff to add line numbers
    result = []
    line_num_original = 0
    line_num_updated = 0
    
    for line in diff:
        if line.startswith('---') or line.startswith('+++'):
            result.append(line)
        elif line.startswith('@@'):
            # Parse the hunk header to get the starting line numbers
            match = re.match(r'^@@ -(\d+),\d+ \+(\d+),\d+ @@', line)
            if match:
                line_num_original = int(match.group(1)) - 1
                line_num_updated = int(match.group(2)) - 1
            result.append(line)
        elif line.startswith('-'):
            line_num_original += 1
            result.append(f"{line_num_original:4d} {line}")
        elif line.startswith('+'):
            line_num_updated += 1
            result.append(f"{line_num_updated:4d} {line}")
        elif line.startswith(' '):
            line_num_original += 1
            line_num_updated += 1
            result.append(f"{line_num_original:4d} {line}")
    
    return '\n'.join(result)

def get_diff_stats(original: str, updated: str) -> Dict[str, int]:
    """Get statistics about the diff between two strings.
    
    Args:
        original: Original string.
        updated: Updated string.
        
    Returns:
        Dictionary with statistics about the diff:
        - added_lines: Number of added lines
        - removed_lines: Number of removed lines
        - changed_lines: Number of changed lines
        - unchanged_lines: Number of unchanged lines
    """
    original_lines = original.splitlines()
    updated_lines = updated.splitlines()
    
    # Generate the diff
    diff = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile='original',
        tofile='updated',
        n=0,
        lineterm=''
    )
    
    # Count the lines
    added_lines = 0
    removed_lines = 0
    
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            added_lines += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed_lines += 1
    
    # Calculate changed and unchanged lines
    unchanged_lines = min(len(original_lines), len(updated_lines)) - removed_lines
    changed_lines = removed_lines
    
    return {
        'added_lines': added_lines,
        'removed_lines': removed_lines,
        'changed_lines': changed_lines,
        'unchanged_lines': unchanged_lines
    }

def get_file_diff(original_file: str, updated_file: str, context_lines: int = 3) -> str:
    """Get the diff between two files.
    
    Args:
        original_file: Path to the original file.
        updated_file: Path to the updated file.
        context_lines: Number of context lines to include in the diff.
        
    Returns:
        Unified diff as a string.
    """
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original = f.read()
        
        with open(updated_file, 'r', encoding='utf-8') as f:
            updated = f.read()
        
        return get_diff(original, updated, context_lines)
    except Exception as e:
        return f"Error generating diff: {str(e)}"

def apply_patch(original: str, patch: str) -> str:
    """Apply a unified diff patch to a string.
    
    Args:
        original: Original string.
        patch: Unified diff patch to apply.
        
    Returns:
        The updated string after applying the patch.
    """
    original_lines = original.splitlines()
    result_lines = original_lines.copy()
    
    # Parse the patch
    current_line = 0
    for line in patch.splitlines():
        if line.startswith('@@'):
            # Parse the hunk header to get the starting line number
            match = re.match(r'^@@ -(\d+),\d+ \+\d+,\d+ @@', line)
            if match:
                current_line = int(match.group(1)) - 1
        elif line.startswith('-'):
            # Remove a line
            if current_line < len(result_lines) and result_lines[current_line] == line[1:]:
                result_lines.pop(current_line)
            else:
                # If the line doesn't match, we can't apply the patch
                raise ValueError(f"Patch cannot be applied: line {current_line + 1} doesn't match")
        elif line.startswith('+'):
            # Add a line
            result_lines.insert(current_line, line[1:])
            current_line += 1
        elif line.startswith(' '):
            # Context line, just advance the current line
            current_line += 1
    
    return '\n'.join(result_lines)

"""
File editor module for OpenHands Python 3.11 compatibility.

This module provides file editing functionality compatible with Python 3.11.11.
"""

import os
import re
import tempfile
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Tuple

from openhands_py311.editor.editor import OHEditor
from openhands_py311.editor.exceptions import ToolError
from openhands_py311.editor.results import ToolResult
from openhands_py311.utils.diff import get_diff

# Create a global singleton instance of the editor
_editor = OHEditor()

def _apply_edit_snippet(original_content: str, edit_snippet: str) -> str:
    """Apply an edit snippet to the original content.
    
    This function intelligently applies an edit snippet to the original content.
    It parses the edit snippet to identify unchanged sections (marked with comments)
    and applies only the changes.
    
    Args:
        original_content: The original content of the file.
        edit_snippet: The edit snippet to apply.
        
    Returns:
        The updated content after applying the edit snippet.
    """
    # If the file is empty or doesn't exist, just return the edit snippet
    if not original_content:
        return edit_snippet
    
    # If the edit snippet is empty, return the original content
    if not edit_snippet:
        return original_content
    
    # Detect the comment style based on file content or edit snippet
    comment_styles = {
        '#': r'#\s*\.\.\.\s*(.+?)\s*\.\.\.\s*',  # Python, Ruby, Shell
        '//': r'//\s*\.\.\.\s*(.+?)\s*\.\.\.\s*',  # JavaScript, TypeScript, C, C++, Swift
        '--': r'--\s*\.\.\.\s*(.+?)\s*\.\.\.\s*',  # Lua
        '/*': r'/\*\s*\.\.\.\s*(.+?)\s*\.\.\.\s*\*/',  # CSS, multiline comments
        '<!--': r'<!--\s*\.\.\.\s*(.+?)\s*\.\.\.\s*-->',  # HTML, XML
    }
    
    # Determine the comment style to use
    comment_style = None
    for style, pattern in comment_styles.items():
        if style in edit_snippet:
            comment_style = style
            pattern = pattern
            break
    
    # If no comment style detected, default to Python
    if not comment_style:
        comment_style = '#'
        pattern = comment_styles['#']
    
    # Check if the edit snippet contains any comment markers
    contains_markers = False
    for style, pattern in comment_styles.items():
        if re.search(pattern, edit_snippet):
            contains_markers = True
            break
    
    # If no markers found, treat it as a full replacement
    if not contains_markers:
        return edit_snippet
    
    # Split the edit snippet into sections
    sections = []
    current_pos = 0
    
    # Find all comment markers in the edit snippet
    markers = []
    for style, pattern in comment_styles.items():
        markers.extend(re.finditer(pattern, edit_snippet))
    
    # Sort markers by their position in the edit snippet
    markers.sort(key=lambda m: m.start())
    
    # Process each marker
    for marker in markers:
        # Add the content before the marker
        if marker.start() > current_pos:
            sections.append({
                'type': 'content',
                'text': edit_snippet[current_pos:marker.start()]
            })
        
        # Add the marker
        sections.append({
            'type': 'marker',
            'text': marker.group(1)  # The text inside the marker
        })
        
        current_pos = marker.end()
    
    # Add any remaining content
    if current_pos < len(edit_snippet):
        sections.append({
            'type': 'content',
            'text': edit_snippet[current_pos:]
        })
    
    # Now apply the sections to the original content
    result = []
    original_lines = original_content.splitlines()
    
    # Process each section
    for section in sections:
        if section['type'] == 'marker':
            # This is a marker for unchanged content
            marker_text = section['text'].lower()
            
            # Special case for "existing imports", "imports", etc.
            if 'import' in marker_text:
                # Find import statements in the original content
                import_pattern = r'^(?:from|import)\s+.+$'
                import_lines = []
                for line in original_lines:
                    if re.match(import_pattern, line.strip()):
                        import_lines.append(line)
                
                if import_lines:
                    result.extend(import_lines)
            
            # Special case for "existing code", "rest of code", etc.
            elif any(x in marker_text for x in ['existing code', 'rest of code', 'rest of file']):
                # Include all original content
                result.extend(original_lines)
            
            # Special case for "function body", "method body", etc.
            elif any(x in marker_text for x in ['function body', 'method body']):
                # Try to find the function/method body
                # This is a simplified approach and might need enhancement for complex cases
                in_body = False
                indent = 0
                body_lines = []
                
                for line in original_lines:
                    if not in_body and re.match(r'^(\s*)def\s+', line):
                        in_body = True
                        indent = len(re.match(r'^(\s*)', line).group(1))
                    elif in_body:
                        line_indent = len(re.match(r'^(\s*)', line).group(1))
                        if line.strip() and line_indent <= indent:
                            in_body = False
                        else:
                            body_lines.append(line)
                
                if body_lines:
                    result.extend(body_lines)
            
            # Default case: try to find a section that matches the marker text
            else:
                # This is a simplified approach and might need enhancement for complex cases
                result.extend(original_lines)
        
        else:
            # This is content to be inserted
            result.extend(section['text'].splitlines())
    
    return '\n'.join(result)

def file_editor(file_path: str, edit_snippet: str) -> Dict:
    """Edit a file using the provided edit snippet.
    
    This function provides an intelligent file editing capability that can apply
    targeted changes to specific portions of a file based on the edit snippet.
    
    Args:
        file_path: Path to the file to edit.
        edit_snippet: Edit snippet to apply to the file.
        
    Returns:
        Dict: Result of the operation.
        
    Raises:
        ToolError: If the file cannot be edited.
    """
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Read the file
            original_content = _editor.read_file(file_path)
            
            # Create a backup of the original file
            backup_path = f"{file_path}.bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Apply the edit snippet intelligently
            updated_content = _apply_edit_snippet(original_content, edit_snippet)
            
            # Generate a diff for logging/debugging
            diff = get_diff(original_content, updated_content)
            
            # Write the updated content back to the file
            result = _editor.write_file(file_path, updated_content)
            
            # Add the diff to the result data
            result.data['diff'] = diff
            
            # Clean up the backup if everything went well
            if os.path.exists(backup_path):
                os.remove(backup_path)
        else:
            # Create the file with the edit snippet
            # For new files, we just use the edit snippet as is
            result = _editor.write_file(file_path, edit_snippet)
            result.data['diff'] = get_diff("", edit_snippet)
        
        return {
            "success": result.success,
            "message": result.message,
            "file_path": file_path,
            "diff": result.data.get('diff', '')
        }
    except Exception as e:
        # If there was an error and we have a backup, restore it
        backup_path = f"{file_path}.bak"
        if os.path.exists(backup_path):
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                os.remove(backup_path)
            except Exception as restore_error:
                raise ToolError(f"Error editing file {file_path} and failed to restore backup: {str(e)}. Restore error: {str(restore_error)}")
        
        raise ToolError(f"Error editing file {file_path}: {str(e)}")

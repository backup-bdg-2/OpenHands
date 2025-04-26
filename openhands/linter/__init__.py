"""Linter module for OpenHands.

Part of this Linter module is adapted from Aider (Apache 2.0 License, [original
code](https://github.com/paul-gauthier/aider/blob/main/aider/linter.py)).
- Please see the [original repository](https://github.com/paul-gauthier/aider) for more information.
- The detailed implementation of the linter can be found at: https://github.com/All-Hands-AI/openhands-aci.
"""

try:
    from openhands_aci.linter import DefaultLinter, LintResult
    __all__ = ['DefaultLinter', 'LintResult']
except ImportError:
    import logging
    import os
    import re
    import subprocess
    import tempfile
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Dict, List, Optional, Tuple, Union
    
    logging.warning("openhands_aci module not found. Using enhanced fallback linter implementation.")
    
    @dataclass
    class LintResult:
        """Enhanced fallback implementation of LintResult.
        
        This class represents the result of a linting operation, including any errors or warnings found.
        
        Attributes:
            success (bool): Whether the linting operation was successful (no errors).
            errors (List[Dict]): List of error dictionaries with details about each error.
            warnings (List[Dict]): List of warning dictionaries with details about each warning.
            line (Optional[int]): Line number where an error was found (if applicable).
            column (Optional[int]): Column number where an error was found (if applicable).
            message (Optional[str]): Error message (if applicable).
            file_path (Optional[str]): Path to the file that was linted (if applicable).
        """
        success: bool = True
        errors: List[Dict] = None
        warnings: List[Dict] = None
        line: Optional[int] = None
        column: Optional[int] = None
        message: Optional[str] = None
        file_path: Optional[str] = None
        
        def __init__(
            self, 
            success: bool = True, 
            errors: List[Dict] = None, 
            warnings: List[Dict] = None,
            line: Optional[int] = None,
            column: Optional[int] = None,
            message: Optional[str] = None,
            file_path: Optional[str] = None
        ):
            self.success = success
            self.errors = errors or []
            self.warnings = warnings or []
            self.line = line
            self.column = column
            self.message = message
            self.file_path = file_path
        
        def __bool__(self) -> bool:
            """Return True if there are errors (not successful)."""
            return not self.success
        
        def __len__(self) -> int:
            """Return the number of errors."""
            return len(self.errors)
        
        def add_error(self, line: int, column: int, message: str, file_path: Optional[str] = None) -> None:
            """Add an error to the result.
            
            Args:
                line: Line number where the error was found.
                column: Column number where the error was found.
                message: Error message.
                file_path: Path to the file where the error was found.
            """
            error = {
                "line": line,
                "column": column,
                "message": message,
                "file_path": file_path
            }
            self.errors.append(error)
            self.success = False
            
            # Update the instance attributes with the first error's details
            if len(self.errors) == 1:
                self.line = line
                self.column = column
                self.message = message
                self.file_path = file_path
        
        def add_warning(self, line: int, column: int, message: str, file_path: Optional[str] = None) -> None:
            """Add a warning to the result.
            
            Args:
                line: Line number where the warning was found.
                column: Column number where the warning was found.
                message: Warning message.
                file_path: Path to the file where the warning was found.
            """
            warning = {
                "line": line,
                "column": column,
                "message": message,
                "file_path": file_path
            }
            self.warnings.append(warning)
    
    class DefaultLinter:
        """Enhanced fallback implementation of DefaultLinter.
        
        This class provides linting functionality for code files, detecting syntax errors
        and other issues. It supports multiple languages including Python, JavaScript, TypeScript,
        and others based on file extension.
        """
        def __init__(self):
            """Initialize the linter with supported language configurations."""
            self.language_configs = {
                "py": {
                    "command": ["python", "-m", "pyflakes"],
                    "regex": r"^(.+):(\d+):(\d+): (.+)$",
                },
                "js": {
                    "command": ["node", "--check"],
                    "regex": r"^(.+):(\d+):(\d+): (.+)$",
                },
                "ts": {
                    "command": ["node", "--check"],
                    "regex": r"^(.+):(\d+):(\d+): (.+)$",
                },
                "jsx": {
                    "command": ["node", "--check"],
                    "regex": r"^(.+):(\d+):(\d+): (.+)$",
                },
                "tsx": {
                    "command": ["node", "--check"],
                    "regex": r"^(.+):(\d+):(\d+): (.+)$",
                },
            }
            
        def _get_language_from_file(self, file_path: str) -> Optional[str]:
            """Determine the language from the file extension.
            
            Args:
                file_path: Path to the file.
                
            Returns:
                The language extension or None if not supported.
            """
            ext = os.path.splitext(file_path)[1].lstrip('.')
            return ext if ext in self.language_configs else None
            
        def _check_syntax(self, code: str, language: str) -> List[LintResult]:
            """Check the syntax of the provided code.
            
            Args:
                code: The code to check.
                language: The language of the code.
                
            Returns:
                A list of LintResult objects with any errors found.
            """
            results = []
            
            # Basic syntax check using Python's ast module for Python code
            if language == "py":
                import ast
                
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    result = LintResult(success=False)
                    result.add_error(
                        line=e.lineno or 1,
                        column=e.offset or 1,
                        message=f"SyntaxError: {str(e)}"
                    )
                    results.append(result)
            
            # For other languages, perform a basic structure check
            else:
                # Check for mismatched brackets, parentheses, etc.
                brackets = {'(': ')', '[': ']', '{': '}'}
                stack = []
                lines = code.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for col_num, char in enumerate(line, 1):
                        if char in brackets:
                            stack.append((char, line_num, col_num))
                        elif char in brackets.values():
                            if not stack or brackets[stack[-1][0]] != char:
                                result = LintResult(success=False)
                                result.add_error(
                                    line=line_num,
                                    column=col_num,
                                    message=f"Mismatched bracket: '{char}'"
                                )
                                results.append(result)
                            else:
                                stack.pop()
                
                # Check for unclosed brackets
                if stack:
                    for bracket, line_num, col_num in stack:
                        result = LintResult(success=False)
                        result.add_error(
                            line=line_num,
                            column=col_num,
                            message=f"Unclosed bracket: '{bracket}'"
                        )
                        results.append(result)
            
            return results
            
        def lint(self, file_path_or_code: str, language: Optional[str] = None) -> List[LintResult]:
            """Lint the provided file or code string.
            
            Args:
                file_path_or_code: Either a path to a file or a string of code.
                language: Optional language identifier. If not provided, will be inferred from file extension.
                
            Returns:
                A list of LintResult objects with any errors found.
            """
            # Determine if input is a file path or code string
            is_file_path = os.path.exists(file_path_or_code) and not file_path_or_code.count('\n') > 0
            
            if is_file_path:
                file_path = file_path_or_code
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                except Exception as e:
                    result = LintResult(success=False)
                    result.add_error(
                        line=1,
                        column=1,
                        message=f"Error reading file: {str(e)}",
                        file_path=file_path
                    )
                    return [result]
                
                # Determine language from file extension if not provided
                if not language:
                    language = self._get_language_from_file(file_path)
            else:
                code = file_path_or_code
                file_path = None
                
                # If language not provided for code string, default to Python
                if not language:
                    language = "py"
            
            # If language is not supported, return success
            if not language or language not in self.language_configs:
                return []
                
            # Perform syntax check
            results = self._check_syntax(code, language)
            
            # If no errors found, return empty list (success)
            if not results:
                return []
                
            # Update file_path in results if available
            if file_path:
                for result in results:
                    for error in result.errors:
                        error["file_path"] = file_path
                    for warning in result.warnings:
                        warning["file_path"] = file_path
            
            return results
            
        def lint_file_diff(self, original_file: str, updated_file: str) -> List[LintResult]:
            """Lint the diff between two files.
            
            This method compares the linting results of the original and updated files
            and returns only the new errors introduced in the updated file.
            
            Args:
                original_file: Path to the original file.
                updated_file: Path to the updated file.
                
            Returns:
                A list of LintResult objects with any new errors found.
            """
            # Get language from file extension
            language = self._get_language_from_file(updated_file)
            if not language:
                return []
                
            # Lint both files
            original_results = self.lint(original_file, language)
            updated_results = self.lint(updated_file, language)
            
            # If no errors in updated file, return empty list
            if not updated_results:
                return []
                
            # Extract error messages from original file
            original_errors = set()
            for result in original_results:
                for error in result.errors:
                    error_key = (error.get("line"), error.get("column"), error.get("message"))
                    original_errors.add(error_key)
            
            # Filter out errors that were already present in the original file
            new_results = []
            for result in updated_results:
                new_result = LintResult(success=True, file_path=result.file_path)
                
                for error in result.errors:
                    error_key = (error.get("line"), error.get("column"), error.get("message"))
                    if error_key not in original_errors:
                        new_result.add_error(
                            line=error.get("line", 1),
                            column=error.get("column", 1),
                            message=error.get("message", "Unknown error"),
                            file_path=error.get("file_path")
                        )
                
                if not new_result.success:
                    new_results.append(new_result)
            
            return new_results
    
    __all__ = ['DefaultLinter', 'LintResult']

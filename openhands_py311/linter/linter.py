"""
Linter implementation for OpenHands Python 3.11 compatibility.

This module provides linting functionality compatible with Python 3.11.11.
"""

import os
import re
import subprocess
import tempfile
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

@dataclass
class LintResult:
    """Implementation of LintResult for Python 3.11.
    
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
    """Implementation of DefaultLinter for Python 3.11.
    
    This class provides linting functionality for code files, detecting syntax errors
    and other issues. It supports multiple languages including Python, JavaScript, TypeScript,
    Swift, C++, Lua, Luau, and others based on file extension.
    """
    def __init__(self):
        """Initialize the linter with supported language configurations."""
        self.language_configs = {
            # Python
            "py": {
                "command": ["python", "-m", "pyflakes"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "check_command": ["python", "-m", "py_compile"],
                "comment_style": "#",
            },
            # JavaScript
            "js": {
                "command": ["eslint", "--format", "compact"],
                "regex": r"^(.+): line (\d+), col (\d+), (.+)$",
                "check_command": ["node", "--check"],
                "comment_style": "//",
            },
            # TypeScript
            "ts": {
                "command": ["eslint", "--format", "compact"],
                "regex": r"^(.+): line (\d+), col (\d+), (.+)$",
                "check_command": ["tsc", "--noEmit"],
                "comment_style": "//",
            },
            # JSX
            "jsx": {
                "command": ["eslint", "--format", "compact"],
                "regex": r"^(.+): line (\d+), col (\d+), (.+)$",
                "check_command": ["node", "--check"],
                "comment_style": "//",
            },
            # TSX
            "tsx": {
                "command": ["eslint", "--format", "compact"],
                "regex": r"^(.+): line (\d+), col (\d+), (.+)$",
                "check_command": ["tsc", "--noEmit"],
                "comment_style": "//",
            },
            # Swift
            "swift": {
                "command": ["swiftlint", "lint", "--quiet"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "check_command": ["swift", "-syntax-only"],
                "comment_style": "//",
            },
            # C++
            "cpp": {
                "command": ["clang-tidy", "-quiet"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "check_command": ["clang++", "-fsyntax-only", "-std=c++17"],
                "comment_style": "//",
            },
            # C
            "c": {
                "command": ["clang-tidy", "-quiet"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "check_command": ["clang", "-fsyntax-only"],
                "comment_style": "//",
            },
            # Lua
            "lua": {
                "command": ["luacheck", "--no-color"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "check_command": ["luac", "-p"],
                "comment_style": "--",
            },
            # Luau (Roblox Lua)
            "luau": {
                "command": ["luau-analyze"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "check_command": ["luau", "--parse"],
                "comment_style": "--",
            },
            # HTML
            "html": {
                "command": ["htmlhint"],
                "regex": r"^(.+): line (\d+), col (\d+), (.+)$",
                "comment_style": "<!--",
            },
            # CSS
            "css": {
                "command": ["stylelint"],
                "regex": r"^(.+):(\d+):(\d+): (.+)$",
                "comment_style": "/*",
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
    
    def _is_tool_available(self, command: str) -> bool:
        """Check if a command-line tool is available.
        
        Args:
            command: The command to check.
            
        Returns:
            True if the tool is available, False otherwise.
        """
        return shutil.which(command) is not None
    
    def _check_syntax_with_external_tool(self, code: str, language: str) -> List[LintResult]:
        """Check syntax using an external tool.
        
        Args:
            code: The code to check.
            language: The language of the code.
            
        Returns:
            A list of LintResult objects with any errors found.
        """
        results = []
        config = self.language_configs.get(language)
        
        if not config or not config.get("check_command"):
            return results
        
        check_command = config["check_command"]
        
        # Check if the command is available
        if not self._is_tool_available(check_command[0]):
            # Fall back to basic syntax check
            return self._check_basic_syntax(code, language)
        
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(suffix=f".{language}", mode="w", delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Run the check command
            process = subprocess.run(
                check_command + [temp_file_path],
                capture_output=True,
                text=True,
                check=False
            )
            
            # If the command failed, parse the error output
            if process.returncode != 0:
                result = LintResult(success=False)
                
                # Try to extract line and column information from the error output
                error_lines = process.stderr.splitlines() or process.stdout.splitlines()
                for error_line in error_lines:
                    # Try to match the error line with the regex pattern
                    match = re.search(config.get("regex", r"^(.+):(\d+):(\d+): (.+)$"), error_line)
                    if match:
                        result.add_error(
                            line=int(match.group(2)),
                            column=int(match.group(3)),
                            message=match.group(4),
                            file_path=temp_file_path
                        )
                    else:
                        # If no match, add a generic error
                        result.add_error(
                            line=1,
                            column=1,
                            message=error_line,
                            file_path=temp_file_path
                        )
                
                results.append(result)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        return results
    
    def _check_basic_syntax(self, code: str, language: str) -> List[LintResult]:
        """Check the syntax of the provided code using basic checks.
        
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
            
            # Get the comment style for the language
            comment_style = self.language_configs.get(language, {}).get("comment_style", "//")
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if comment_style == "#" and "#" in line:
                    line = line.split("#")[0]
                elif comment_style == "//" and "//" in line:
                    line = line.split("//")[0]
                elif comment_style == "--" and "--" in line:
                    line = line.split("--")[0]
                
                # Check for string literals to avoid checking brackets inside strings
                in_string = False
                string_char = None
                
                for col_num, char in enumerate(line, 1):
                    # Handle string literals
                    if char in ['"', "'"]:
                        if not in_string:
                            in_string = True
                            string_char = char
                        elif char == string_char:
                            in_string = False
                            string_char = None
                        continue
                    
                    # Skip characters inside string literals
                    if in_string:
                        continue
                    
                    # Check brackets
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
            
            # Language-specific checks
            if language in ["swift", "cpp", "c"]:
                # Check for missing semicolons in C-like languages
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and preprocessor directives
                    if (comment_style == "//" and "//" in line) or line.strip().startswith("#"):
                        continue
                    
                    # Check if line should end with semicolon
                    line = line.strip()
                    if (line and 
                        not line.endswith(";") and 
                        not line.endswith("{") and 
                        not line.endswith("}") and
                        not line.endswith(":") and
                        not line.startswith("#")):
                        
                        # Exclude function declarations and control structures
                        if not any(keyword in line for keyword in ["if", "else", "for", "while", "switch", "case", "func", "class", "struct"]):
                            result = LintResult(success=False)
                            result.add_error(
                                line=line_num,
                                column=len(line),
                                message="Missing semicolon at end of line"
                            )
                            results.append(result)
            
            elif language in ["lua", "luau"]:
                # Check for common Lua syntax errors
                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if "--" in line:
                        line = line.split("--")[0]
                    
                    # Check for misuse of '=' instead of '==' in conditions
                    if "if" in line and "=" in line and "==" not in line and "~=" not in line:
                        result = LintResult(success=False)
                        result.add_error(
                            line=line_num,
                            column=line.find("="),
                            message="Possible use of assignment (=) instead of equality (==) in condition"
                        )
                        results.append(result)
        
        return results
    
    def _check_syntax(self, code: str, language: str) -> List[LintResult]:
        """Check the syntax of the provided code.
        
        This method first tries to use an external tool if available,
        and falls back to basic syntax checking if not.
        
        Args:
            code: The code to check.
            language: The language of the code.
            
        Returns:
            A list of LintResult objects with any errors found.
        """
        # First try with external tool
        results = self._check_syntax_with_external_tool(code, language)
        
        # If no results or external tool not available, fall back to basic checks
        if not results:
            results = self._check_basic_syntax(code, language)
        
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

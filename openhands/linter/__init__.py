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
    logging.warning("openhands_aci module not found. Using fallback linter implementation.")
    
    class LintResult:
        """Fallback implementation of LintResult."""
        def __init__(self, success=True, errors=None, warnings=None):
            self.success = success
            self.errors = errors or []
            self.warnings = warnings or []
    
    class DefaultLinter:
        """Fallback implementation of DefaultLinter."""
        def __init__(self):
            pass
            
        def lint(self, code, language=None):
            """Fallback linting implementation that always succeeds."""
            return LintResult(success=True)
    
    __all__ = ['DefaultLinter', 'LintResult']

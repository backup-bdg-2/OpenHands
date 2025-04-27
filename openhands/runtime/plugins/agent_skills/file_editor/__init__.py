"""This file imports a global singleton of the `EditTool` class as well as raw functions that expose
its __call__.
The implementation of the `EditTool` class can be found in the openhands_py311 module.
"""

from openhands_py311.editor import file_editor

__all__ = ['file_editor']

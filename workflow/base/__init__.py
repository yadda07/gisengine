"""Base Classes for Workflow Contributors

This module provides base classes that contributors can extend to create
custom workflow components, panels, and nodes.

All base classes follow GISENGINE standards and provide:
- Consistent API patterns
- Built-in validation
- Integration with the extension system
- Testing framework compatibility
"""

from .base_component import BaseWorkflowComponent
from .base_panel import BasePanel
from .base_node import BaseNode

__all__ = [
    'BaseWorkflowComponent',
    'BasePanel', 
    'BaseNode'
]

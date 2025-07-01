"""
Professional Workflow Designer Module
Enterprise-grade workflow canvas and components for GISENGINE

Architecture:
- canvas: Core workflow canvas with grid and interaction handling
- components: Node and connection components
- panels: UI panels (search, properties, etc.)
- designer: Main workflow designer window
"""

# Core canvas
from .canvas import ProfessionalWorkflowCanvas

# Components
from .components import (
    ProfessionalWorkflowNode,
    ConnectionPort,
    Connection
)

# UI Panels
from .panels import (
    ProfessionalSearchPanel,
    PropertiesPanel
)

# Main designer
from .designer import ProfessionalWorkflowDesigner

__all__ = [
    'ProfessionalWorkflowCanvas',
    'ProfessionalWorkflowNode',
    'ConnectionPort', 
    'Connection',
    'ProfessionalSearchPanel',
    'PropertiesPanel',
    'ProfessionalWorkflowDesigner'
]

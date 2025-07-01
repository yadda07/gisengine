"""GISENGINE Workflow Module

Professional workflow designer for creating and managing data processing workflows.
Designed for contributor-friendly development with clear architectural separation.

Architecture:
- Core interfaces (stable): Designer, Canvas
- Component system (extensible): Nodes, Connections, Ports  
- Panel system (extensible): Search, Properties

For contributors:
- Extend existing components for new functionality
- Follow established patterns and conventions
- All code in English, professional style, no emojis
"""

# Import core components with fallback handling
try:
    from .designer import ProfessionalWorkflowDesigner
except ImportError:
    ProfessionalWorkflowDesigner = None

try:
    from .canvas import ProfessionalWorkflowCanvas
except ImportError:
    ProfessionalWorkflowCanvas = None

try:
    from .components import WorkflowNode, NodePort, Connection
except ImportError:
    WorkflowNode = NodePort = Connection = None

try:
    from .panels import ProfessionalSearchPanel, PropertiesPanel
except ImportError:
    ProfessionalSearchPanel = PropertiesPanel = None

# Aliases for stable API
WorkflowDesigner = ProfessionalWorkflowDesigner
WorkflowCanvas = ProfessionalWorkflowCanvas
SearchPanel = ProfessionalSearchPanel

# Public API for contributors
__all__ = [
    # Core interfaces (stable - protected zone)
    'WorkflowDesigner',
    'WorkflowCanvas',
    # Component system (contribution zone)
    'WorkflowNode',
    'NodePort', 
    'Connection',
    # Panel system (extensible)
    'SearchPanel',
    'PropertiesPanel'
]

# Module metadata
__version__ = '1.0.0'
__author__ = 'GISENGINE Team'
__description__ = 'Professional workflow designer for QGIS'

"""
GISENGINE Core Module
Zone protégée - Interfaces et logique core stable
"""

from .interfaces import IComponent, IReader, ITransformer, IWriter, ComponentMetadata
from .registry import ComponentRegistry
from .engine import WorkflowEngine
from .loader import PluginLoader
from .events import EventSystem
from .exceptions import GISEngineException

__all__ = [
    'IComponent', 'IReader', 'ITransformer', 'IWriter', 'ComponentMetadata',
    'ComponentRegistry', 'WorkflowEngine', 'PluginLoader', 'EventSystem',
    'GISEngineException'
]

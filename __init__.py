"""
GISENGINE - Modern QGIS Plugin for Workflow Design
"""

__version__ = "1.0.0"
__author__ = "GISENGINE Team"

from .core import ComponentRegistry, WorkflowEngine, PluginLoader
from .gisengine_plugin import GISENGINEPlugin

# Instance globale du registry (singleton pattern)
_registry = None

def get_registry() -> ComponentRegistry:
    """Retourne l'instance globale du registry"""
    global _registry
    if _registry is None:
        _registry = ComponentRegistry()
    return _registry

def initialize():
    """Initialise GISENGINE avec chargement automatique des composants"""
    registry = get_registry()
    loader = PluginLoader(registry)
    loader.load_all()
    return registry

def classFactory(iface):
    """Factory function required by QGIS to create the plugin instance"""
    return GISENGINEPlugin(iface)

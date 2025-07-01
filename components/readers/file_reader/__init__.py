"""
File Reader Component
"""

from .component import FileReaderComponent

def register_components(registry):
    """Enregistre les composants de ce module"""
    registry.register(FileReaderComponent)

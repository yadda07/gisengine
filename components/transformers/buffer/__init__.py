"""
Buffer Transformer Component
"""

from .component import BufferTransformerComponent

def register_components(registry):
    """Enregistre les composants de ce module"""
    registry.register(BufferTransformerComponent)

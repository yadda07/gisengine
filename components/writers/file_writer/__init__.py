"""
File Writer Component
"""

from .component import FileWriterComponent

def register_components(registry):
    registry.register(FileWriterComponent)

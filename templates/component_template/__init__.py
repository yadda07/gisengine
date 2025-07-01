"""
Template de composant GISENGINE
Point d'entrée du composant template
"""

from .component import MyComponentTemplate
from .ui import MyComponentTemplateUI

# Métadonnées du composant (chargées depuis metadata.json)
__component_name__ = "MyComponentTemplate"
__component_version__ = "1.0.0"
__component_author__ = "Votre Nom"

# Export des classes principales
__all__ = [
    'MyComponentTemplate',
    'MyComponentTemplateUI'
]

# Configuration pour le registry GISENGINE
COMPONENT_CONFIG = {
    'component_class': MyComponentTemplate,
    'ui_class': MyComponentTemplateUI,
    'metadata_file': 'metadata.json',
    'test_file': 'tests.py',
    'category': 'template',
    'enabled': True
}

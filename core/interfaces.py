"""
Interfaces standards pour tous les composants GISENGINE
🔒 CORE STABLE - Ne pas modifier sans RFC
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ComponentType(Enum):
    """Types de composants supportés"""
    READER = "reader"
    TRANSFORMER = "transformer" 
    WRITER = "writer"

@dataclass
class ComponentMetadata:
    """Métadonnées standard pour tous les composants"""
    id: str                        # Identifiant unique (ex: "core.file_reader")
    name: str                      # Nom affiché
    description: str               # Description complète
    category: str                  # Catégorie (ex: "Input/Output")
    type: ComponentType            # Type de composant
    version: str                   # Version sémantique (ex: "1.0.0")
    author: str                    # Auteur/Organisation
    license: str                   # License (ex: "MIT")
    homepage: Optional[str] = None # Page web
    repository: Optional[str] = None # Repository Git
    dependencies: List[str] = None # Dépendances Python
    icon: Optional[str] = None     # Chemin vers icône
    tags: List[str] = None         # Tags pour recherche

class IComponent(ABC):
    """Interface standard que TOUS les composants doivent implémenter"""
    
    @abstractmethod
    def get_metadata(self) -> ComponentMetadata:
        """Retourne les métadonnées du composant"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[Dict]:
        """Retourne la liste des paramètres configurables"""
        pass
    
    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Valide les entrées avant exécution"""
        pass
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any], context: 'ExecutionContext') -> Dict[str, Any]:
        """Exécute le composant avec les inputs donnés"""
        pass
    
    @abstractmethod
    def get_ui_widget(self) -> 'QWidget':
        """Retourne le widget de configuration UI"""
        pass

class IReader(IComponent):
    """Interface spécialisée pour les composants de lecture"""
    pass

class ITransformer(IComponent):
    """Interface spécialisée pour les transformers"""
    pass

class IWriter(IComponent):
    """Interface spécialisée pour les composants d'écriture"""
    pass

class ExecutionContext:
    """Contexte d'exécution partagé entre composants"""
    
    def __init__(self):
        self.temp_dir = None
        self.progress_callback = None
        self.logger = None
        self.metadata = {}

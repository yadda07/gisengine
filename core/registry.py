"""
Registry centralisé thread-safe pour tous les composants
🔒 CORE STABLE
"""

import threading
import logging
from typing import Dict, List, Optional, Type
from .interfaces import IComponent, ComponentMetadata, ComponentType

logger = logging.getLogger(__name__)

class ComponentRegistry:
    """Registry centralisé thread-safe pour tous les composants"""
    
    def __init__(self):
        self._components: Dict[str, Type[IComponent]] = {}
        self._metadata: Dict[str, ComponentMetadata] = {}
        self._categories: Dict[str, List[str]] = {}
        self._types: Dict[ComponentType, List[str]] = {}
        self._lock = threading.Lock()
    
    def register(self, component_class: Type[IComponent]) -> bool:
        """Enregistre un composant de façon thread-safe"""
        try:
            with self._lock:
                # Instancier pour récupérer métadonnées
                instance = component_class()
                metadata = instance.get_metadata()
                
                # Validation basique
                if not self._validate_component(component_class, metadata):
                    return False
                
                # Enregistrement
                self._components[metadata.id] = component_class
                self._metadata[metadata.id] = metadata
                
                # Indexation pour recherches rapides
                self._index_component(metadata)
                
                logger.info(f"Registered component: {metadata.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register component: {e}")
            return False
    
    def get(self, component_id: str) -> Optional[Type[IComponent]]:
        """Récupère un composant par ID"""
        return self._components.get(component_id)
    
    def get_metadata(self, component_id: str) -> Optional[ComponentMetadata]:
        """Récupère les métadonnées d'un composant"""
        return self._metadata.get(component_id)
    
    def list_all(self) -> List[str]:
        """Liste tous les composants enregistrés"""
        return list(self._components.keys())
    
    def list_by_category(self, category: str) -> List[str]:
        """Liste les composants d'une catégorie"""
        return self._categories.get(category, [])
    
    def list_by_type(self, component_type: ComponentType) -> List[str]:
        """Liste les composants d'un type"""
        return self._types.get(component_type, [])
    
    def search(self, query: str) -> List[str]:
        """Recherche de composants par mots-clés"""
        query = query.lower()
        results = []
        
        for comp_id, metadata in self._metadata.items():
            if self._matches_query(metadata, query):
                results.append(comp_id)
        
        return results
    
    def _validate_component(self, component_class: Type[IComponent], metadata: ComponentMetadata) -> bool:
        """Valide un composant avant enregistrement"""
        # Vérifier que l'ID est unique
        if metadata.id in self._components:
            logger.warning(f"Component ID already exists: {metadata.id}")
            return False
        
        # Vérifier les méthodes requises
        required_methods = ['get_metadata', 'get_parameters', 'validate_inputs', 'execute', 'get_ui_widget']
        for method in required_methods:
            if not hasattr(component_class, method):
                logger.error(f"Component missing required method: {method}")
                return False
        
        return True
    
    def _index_component(self, metadata: ComponentMetadata):
        """Index un composant pour recherches rapides"""
        # Index par catégorie
        category = metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(metadata.id)
        
        # Index par type
        comp_type = metadata.type
        if comp_type not in self._types:
            self._types[comp_type] = []
        self._types[comp_type].append(metadata.id)
    
    def _matches_query(self, metadata: ComponentMetadata, query: str) -> bool:
        """Vérifie si un composant correspond à une requête"""
        return (query in metadata.name.lower() or 
                query in metadata.description.lower() or
                any(query in tag.lower() for tag in (metadata.tags or [])))
    
    def clear(self):
        """Vide complètement le registry (pour tests)"""
        with self._lock:
            self._components.clear()
            self._metadata.clear()
            self._categories.clear()
            self._types.clear()

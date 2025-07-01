"""
Plugin discovery & loading system
🔒 CORE STABLE
"""

import importlib
import importlib.util
import json
import logging
from pathlib import Path
from typing import Set
from .registry import ComponentRegistry

logger = logging.getLogger(__name__)

class PluginLoader:
    """Charge dynamiquement tous les plugins et composants"""
    
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.loaded_plugins: Set[str] = set()
        self.root_path = Path(__file__).parent.parent
    
    def load_all(self):
        """Charge tous les composants et plugins disponibles"""
        logger.info("Starting plugin discovery and loading...")
        
        self._load_core_components()
        self._load_official_plugins()
        self._load_community_plugins()
        self._load_qgis_wrappers()
        
        logger.info(f"Loaded {len(self.loaded_plugins)} plugins total")
    
    def _load_core_components(self):
        """Charge les composants officiels du core"""
        components_dir = self.root_path / "components"
        if components_dir.exists():
            self._load_from_directory(components_dir, "core_components")
    
    def _load_official_plugins(self):
        """Charge les plugins officiels validés"""
        plugins_dir = self.root_path / "plugins" / "official"
        if plugins_dir.exists():
            self._load_from_directory(plugins_dir, "official_plugins")
    
    def _load_community_plugins(self):
        """Charge les plugins communauté"""
        plugins_dir = self.root_path / "plugins" / "community"
        if plugins_dir.exists():
            self._load_from_directory(plugins_dir, "community_plugins")
    
    def _load_qgis_wrappers(self):
        """Charge les wrappers automatiques QGIS"""
        try:
            from ..wrappers.qgis_wrapper import load_qgis_algorithms
            count = load_qgis_algorithms(self.registry)
            logger.info(f"Loaded {count} QGIS algorithm wrappers")
        except Exception as e:
            logger.warning(f"Failed to load QGIS wrappers: {e}")
    
    def _load_from_directory(self, directory: Path, source: str):
        """Charge tous les composants d'un répertoire"""
        if not directory.exists():
            return
        
        loaded_count = 0
        for plugin_dir in directory.iterdir():
            if plugin_dir.is_dir() and plugin_dir.name not in self.loaded_plugins:
                if self._load_plugin(plugin_dir, source):
                    loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} plugins from {source}")
    
    def _load_plugin(self, plugin_dir: Path, source: str) -> bool:
        """Charge un plugin spécifique"""
        try:
            plugin_name = plugin_dir.name
            
            # Vérifier la présence d'un fichier __init__.py
            init_file = plugin_dir / "__init__.py"
            if not init_file.exists():
                logger.debug(f"Skipping {plugin_name}: no __init__.py found")
                return False
            
            # Charger le module Python
            module_name = f"{source}.{plugin_name}"
            spec = importlib.util.spec_from_file_location(module_name, init_file)
            
            if spec is None or spec.loader is None:
                logger.warning(f"Failed to create spec for {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Auto-registration si le module l'implémente
            if hasattr(module, 'register_components'):
                module.register_components(self.registry)
                self.loaded_plugins.add(plugin_name)
                logger.debug(f"Successfully loaded plugin: {plugin_name}")
                return True
            else:
                logger.debug(f"Plugin {plugin_name} has no register_components function")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Recharge un plugin spécifique (pour développement)"""
        # TODO: Implémenter le rechargement à chaud
        logger.info(f"Hot reload not yet implemented for {plugin_name}")
        return False
    
    def get_loaded_plugins(self) -> Set[str]:
        """Retourne la liste des plugins chargés"""
        return self.loaded_plugins.copy()

"""
Workflow execution engine
🔒 CORE STABLE
"""

import logging
from typing import Dict, List, Any
from .interfaces import ExecutionContext
from .registry import ComponentRegistry
from .exceptions import GISEngineException

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """Engine d'exécution pour les workflows GISENGINE"""
    
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
    
    def execute_workflow(self, workflow_definition: Dict) -> Dict[str, Any]:
        """
        Exécute un workflow défini par un graphe
        
        Args:
            workflow_definition: Dict contenant nodes et connections
            
        Returns:
            Dict avec résultats d'exécution
        """
        try:
            # Validation du workflow
            self._validate_workflow(workflow_definition)
            
            # Calcul de l'ordre d'exécution
            execution_order = self._calculate_execution_order(workflow_definition)
            
            # Contexte d'exécution
            context = ExecutionContext()
            results = {}
            
            # Exécution séquentielle des nœuds
            for node_id in execution_order:
                node = workflow_definition["nodes"][node_id]
                
                logger.info(f"Executing node: {node_id}")
                result = self._execute_node(node, workflow_definition, results, context)
                results[node_id] = result
            
            return {
                "success": True,
                "results": results,
                "execution_order": execution_order
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": {}
            }
    
    def _validate_workflow(self, workflow_definition: Dict):
        """Valide la définition du workflow"""
        if "nodes" not in workflow_definition:
            raise GISEngineException("Workflow missing 'nodes' definition")
        
        if "connections" not in workflow_definition:
            raise GISEngineException("Workflow missing 'connections' definition")
        
        # Vérifier que tous les composants existent
        for node_id, node in workflow_definition["nodes"].items():
            component_id = node.get("component_id")
            if not component_id:
                raise GISEngineException(f"Node {node_id} missing component_id")
            
            if not self.registry.get(component_id):
                raise GISEngineException(f"Component not found: {component_id}")
    
    def _calculate_execution_order(self, workflow_definition: Dict) -> List[str]:
        """
        Calcule l'ordre d'exécution via tri topologique
        TODO: Implémentation complète avec détection de cycles
        """
        # Implémentation simplifiée pour le moment
        nodes = list(workflow_definition["nodes"].keys())
        
        # Pour l'instant, ordre simple
        # TODO: Vrai tri topologique basé sur les connexions
        return nodes
    
    def _execute_node(self, node: Dict, workflow_definition: Dict, 
                     previous_results: Dict, context: ExecutionContext) -> Any:
        """Exécute un nœud individuel"""
        
        component_id = node["component_id"]
        component_class = self.registry.get(component_id)
        
        if not component_class:
            raise GISEngineException(f"Component not found: {component_id}")
        
        # Instancier le composant
        component = component_class()
        
        # Préparer les inputs
        inputs = self._prepare_node_inputs(node, workflow_definition, previous_results)
        
        # Valider les inputs
        if not component.validate_inputs(inputs):
            raise GISEngineException(f"Invalid inputs for component: {component_id}")
        
        # Exécuter
        result = component.execute(inputs, context)
        
        return result
    
    def _prepare_node_inputs(self, node: Dict, workflow_definition: Dict, 
                           previous_results: Dict) -> Dict[str, Any]:
        """Prépare les inputs d'un nœud depuis les paramètres et connexions"""
        
        # Commencer avec les paramètres du nœud
        inputs = node.get("parameters", {}).copy()
        
        # Ajouter les données des connexions précédentes
        node_id = node.get("id")
        connections = workflow_definition.get("connections", [])
        
        for connection in connections:
            if connection.get("to_node") == node_id:
                source_node_id = connection.get("from_node")
                source_output = connection.get("from_output", "default")
                target_input = connection.get("to_input", source_output)
                
                if source_node_id in previous_results:
                    source_result = previous_results[source_node_id]
                    
                    # Extraire la sortie spécifique ou toute la sortie
                    if isinstance(source_result, dict) and source_output in source_result:
                        inputs[target_input] = source_result[source_output]
                    else:
                        inputs[target_input] = source_result
        
        return inputs

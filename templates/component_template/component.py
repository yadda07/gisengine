"""
Template pour créer un nouveau composant GISENGINE
Copiez ce fichier et adaptez-le à votre composant
"""

from typing import Dict, Any, List, Optional
from qgis.core import QgsProcessingParameterDefinition, QgsProcessingOutputDefinition

from ...core.interfaces import ITransformer, ComponentMetadata
from ...core.exceptions import GISEngineException


class MyComponentTemplate(ITransformer):
    """
    Template de composant - Remplacez par votre logique
    
    INSTRUCTIONS:
    1. Renommez cette classe avec le nom de votre composant
    2. Implémentez les méthodes requises
    3. Définissez vos paramètres d'entrée/sortie
    4. Ajoutez votre logique métier dans execute()
    5. Créez les tests correspondants
    """
    
    def __init__(self):
        super().__init__()
        self._metadata = None
    
    @property
    def metadata(self) -> ComponentMetadata:
        """Métadonnées du composant - chargées depuis metadata.json"""
        if self._metadata is None:
            # Les métadonnées sont automatiquement chargées depuis metadata.json
            # par le système de registry
            pass
        return self._metadata
    
    def get_input_parameters(self) -> List[QgsProcessingParameterDefinition]:
        """
        Définit les paramètres d'entrée du composant
        
        Returns:
            Liste des paramètres d'entrée QGIS Processing
        """
        # Exemple de paramètres - adaptez selon vos besoins
        from qgis.core import (
            QgsProcessingParameterVectorLayer,
            QgsProcessingParameterNumber,
            QgsProcessingParameterString
        )
        
        return [
            QgsProcessingParameterVectorLayer(
                'input_layer',
                'Couche d\'entrée',
                optional=False
            ),
            QgsProcessingParameterNumber(
                'buffer_distance',
                'Distance du tampon',
                defaultValue=100.0,
                optional=False
            ),
            QgsProcessingParameterString(
                'output_name',
                'Nom de la couche de sortie',
                defaultValue='result',
                optional=True
            )
        ]
    
    def get_output_definitions(self) -> List[QgsProcessingOutputDefinition]:
        """
        Définit les sorties du composant
        
        Returns:
            Liste des définitions de sortie QGIS Processing
        """
        from qgis.core import QgsProcessingOutputVectorLayer
        
        return [
            QgsProcessingOutputVectorLayer(
                'output_layer',
                'Couche résultat'
            )
        ]
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """
        Valide les paramètres avant exécution
        
        Args:
            parameters: Dictionnaire des paramètres
            
        Returns:
            Liste des erreurs de validation (vide si OK)
        """
        errors = []
        
        # Exemple de validation - adaptez selon vos besoins
        if 'input_layer' not in parameters:
            errors.append("Couche d'entrée requise")
        
        if 'buffer_distance' in parameters:
            distance = parameters['buffer_distance']
            if distance <= 0:
                errors.append("La distance doit être positive")
        
        return errors
    
    def execute(self, parameters: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """
        Exécute le composant avec les paramètres donnés
        
        Args:
            parameters: Paramètres d'entrée
            context: Contexte d'exécution QGIS
            
        Returns:
            Dictionnaire des résultats
            
        Raises:
            GISEngineException: En cas d'erreur d'exécution
        """
        try:
            # 1. Validation des paramètres
            validation_errors = self.validate_parameters(parameters)
            if validation_errors:
                raise GISEngineException(f"Erreurs de validation: {', '.join(validation_errors)}")
            
            # 2. Récupération des paramètres
            input_layer = parameters['input_layer']
            buffer_distance = parameters.get('buffer_distance', 100.0)
            output_name = parameters.get('output_name', 'result')
            
            # 3. VOTRE LOGIQUE MÉTIER ICI
            # Remplacez cette section par votre traitement
            
            # Exemple simple : créer un tampon
            from qgis.core import QgsVectorLayer
            
            if isinstance(input_layer, str):
                # Si c'est un chemin, charger la couche
                layer = QgsVectorLayer(input_layer, "input", "ogr")
            else:
                layer = input_layer
            
            if not layer.isValid():
                raise GISEngineException("Couche d'entrée invalide")
            
            # Ici vous implémenteriez votre logique spécifique
            # Par exemple : buffer, clip, reproject, etc.
            
            # 4. Retourner les résultats
            return {
                'output_layer': layer,  # Remplacez par votre résultat
                'status': 'success',
                'message': f'Traitement terminé pour {output_name}'
            }
            
        except Exception as e:
            raise GISEngineException(f"Erreur lors de l'exécution: {str(e)}")
    
    def get_help_text(self) -> str:
        """
        Retourne le texte d'aide du composant
        
        Returns:
            Texte d'aide formaté
        """
        return """
        <h3>Mon Composant Template</h3>
        <p>Description de ce que fait votre composant.</p>
        
        <h4>Paramètres:</h4>
        <ul>
            <li><b>Couche d'entrée</b>: La couche vectorielle à traiter</li>
            <li><b>Distance du tampon</b>: Distance en unités de la couche</li>
            <li><b>Nom de sortie</b>: Nom de la couche résultat</li>
        </ul>
        
        <h4>Sorties:</h4>
        <ul>
            <li><b>Couche résultat</b>: Couche traitée</li>
        </ul>
        
        <h4>Exemple d'utilisation:</h4>
        <p>Utilisez ce composant pour...</p>
        """
    
    def get_icon_path(self) -> Optional[str]:
        """
        Retourne le chemin vers l'icône du composant
        
        Returns:
            Chemin vers l'icône ou None
        """
        # Retournez le chemin vers votre icône
        # Par exemple: return ":/plugins/gisengine/icons/my_component.svg"
        return None

"""
Template de tests pour composant GISENGINE
Adaptez ces tests à votre composant spécifique
"""

import unittest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsProject, QgsApplication
)

from .component import MyComponentTemplate
from ...core.exceptions import GISEngineException


class TestMyComponentTemplate(unittest.TestCase):
    """Tests unitaires pour MyComponentTemplate"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration une seule fois pour tous les tests"""
        # Initialiser QGIS si nécessaire
        if not QgsApplication.instance():
            QgsApplication.setPrefixPath("/usr", True)
            QgsApplication.initQgis()
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.component = MyComponentTemplate()
        self.temp_dir = tempfile.mkdtemp()
        
        # Créer une couche de test simple
        self.test_layer = self._create_test_layer()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        # Nettoyer les fichiers temporaires
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_layer(self) -> QgsVectorLayer:
        """Crée une couche vectorielle de test"""
        # Créer une couche en mémoire
        layer = QgsVectorLayer(
            "Point?crs=EPSG:4326&field=id:integer&field=name:string",
            "test_layer",
            "memory"
        )
        
        # Ajouter quelques features de test
        features = []
        for i in range(5):
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(i, i)))
            feature.setAttributes([i, f"point_{i}"])
            features.append(feature)
        
        layer.dataProvider().addFeatures(features)
        layer.updateExtents()
        
        return layer
    
    def test_metadata_loading(self):
        """Test du chargement des métadonnées"""
        # Les métadonnées devraient être chargées automatiquement
        # Ce test vérifie que le composant a des métadonnées valides
        self.assertIsNotNone(self.component.metadata)
    
    def test_input_parameters_definition(self):
        """Test de la définition des paramètres d'entrée"""
        params = self.component.get_input_parameters()
        
        # Vérifier qu'on a les paramètres attendus
        self.assertGreater(len(params), 0)
        
        # Vérifier les noms des paramètres
        param_names = [p.name() for p in params]
        self.assertIn('input_layer', param_names)
        self.assertIn('buffer_distance', param_names)
    
    def test_output_definitions(self):
        """Test de la définition des sorties"""
        outputs = self.component.get_output_definitions()
        
        # Vérifier qu'on a des sorties définies
        self.assertGreater(len(outputs), 0)
        
        # Vérifier les noms des sorties
        output_names = [o.name() for o in outputs]
        self.assertIn('output_layer', output_names)
    
    def test_parameter_validation_success(self):
        """Test de validation avec des paramètres valides"""
        valid_params = {
            'input_layer': self.test_layer,
            'buffer_distance': 100.0,
            'output_name': 'test_result'
        }
        
        errors = self.component.validate_parameters(valid_params)
        self.assertEqual(len(errors), 0, f"Validation échouée: {errors}")
    
    def test_parameter_validation_missing_required(self):
        """Test de validation avec paramètres manquants"""
        invalid_params = {
            'buffer_distance': 100.0
            # input_layer manquant
        }
        
        errors = self.component.validate_parameters(invalid_params)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("entrée" in error.lower() for error in errors))
    
    def test_parameter_validation_invalid_values(self):
        """Test de validation avec valeurs invalides"""
        invalid_params = {
            'input_layer': self.test_layer,
            'buffer_distance': -10.0  # Valeur négative invalide
        }
        
        errors = self.component.validate_parameters(invalid_params)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("positive" in error.lower() for error in errors))
    
    def test_execute_success(self):
        """Test d'exécution réussie"""
        parameters = {
            'input_layer': self.test_layer,
            'buffer_distance': 50.0,
            'output_name': 'test_buffer'
        }
        
        try:
            result = self.component.execute(parameters)
            
            # Vérifier que l'exécution s'est bien passée
            self.assertIsInstance(result, dict)
            self.assertIn('output_layer', result)
            self.assertIn('status', result)
            self.assertEqual(result['status'], 'success')
            
        except GISEngineException as e:
            self.fail(f"L'exécution a échoué: {str(e)}")
    
    def test_execute_with_invalid_parameters(self):
        """Test d'exécution avec paramètres invalides"""
        invalid_parameters = {
            'input_layer': None,  # Couche invalide
            'buffer_distance': 50.0
        }
        
        with self.assertRaises(GISEngineException):
            self.component.execute(invalid_parameters)
    
    def test_help_text_available(self):
        """Test de disponibilité du texte d'aide"""
        help_text = self.component.get_help_text()
        
        self.assertIsInstance(help_text, str)
        self.assertGreater(len(help_text), 0)
        # Vérifier que le texte contient des éléments HTML basiques
        self.assertIn('<h3>', help_text)
        self.assertIn('<p>', help_text)
    
    def test_icon_path(self):
        """Test du chemin d'icône"""
        icon_path = self.component.get_icon_path()
        
        # L'icône peut être None ou un chemin valide
        if icon_path is not None:
            self.assertIsInstance(icon_path, str)
            self.assertGreater(len(icon_path), 0)
    
    def test_component_type_consistency(self):
        """Test de cohérence du type de composant"""
        # Vérifier que le composant implémente bien ITransformer
        from ...core.interfaces import ITransformer
        self.assertIsInstance(self.component, ITransformer)
    
    def test_performance_benchmark(self):
        """Test de performance basique"""
        import time
        
        parameters = {
            'input_layer': self.test_layer,
            'buffer_distance': 10.0,
            'output_name': 'perf_test'
        }
        
        start_time = time.time()
        result = self.component.execute(parameters)
        execution_time = time.time() - start_time
        
        # Pour une couche de test simple, l'exécution devrait être rapide
        self.assertLess(execution_time, 5.0, 
                       f"Exécution trop lente: {execution_time:.2f}s")
        
        # Vérifier que le résultat est valide
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'success')


class TestComponentIntegration(unittest.TestCase):
    """Tests d'intégration avec le système GISENGINE"""
    
    def setUp(self):
        """Configuration pour les tests d'intégration"""
        self.component = MyComponentTemplate()
    
    def test_registry_compatibility(self):
        """Test de compatibilité avec le registry"""
        # Vérifier que le composant peut être enregistré
        from ...core.registry import ComponentRegistry
        
        registry = ComponentRegistry()
        
        # Le composant devrait pouvoir être enregistré
        try:
            registry.register_component('test_template', self.component)
            registered = registry.get_component('test_template')
            self.assertEqual(registered, self.component)
        except Exception as e:
            self.fail(f"Échec d'enregistrement dans le registry: {str(e)}")
    
    def test_workflow_engine_compatibility(self):
        """Test de compatibilité avec le moteur de workflow"""
        # Ce test vérifie que le composant peut être utilisé
        # dans un workflow (test basique)
        
        parameters = {
            'input_layer': QgsVectorLayer(
                "Point?crs=EPSG:4326&field=id:integer",
                "test",
                "memory"
            ),
            'buffer_distance': 25.0
        }
        
        # Le composant devrait pouvoir s'exécuter sans erreur
        try:
            result = self.component.execute(parameters)
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.fail(f"Incompatibilité avec le workflow engine: {str(e)}")


if __name__ == '__main__':
    # Exécuter les tests
    unittest.main()

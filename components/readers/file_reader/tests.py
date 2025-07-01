"""
Tests for File Reader Component
"""

import unittest
import tempfile
from pathlib import Path
from ..component import FileReaderComponent

class TestFileReaderComponent(unittest.TestCase):
    """Tests pour le File Reader"""
    
    def setUp(self):
        self.component = FileReaderComponent()
    
    def test_metadata(self):
        """Test des métadonnées"""
        metadata = self.component.get_metadata()
        self.assertEqual(metadata.id, "core.file_reader")
        self.assertEqual(metadata.name, "File Reader")
    
    def test_parameters(self):
        """Test des paramètres"""
        params = self.component.get_parameters()
        self.assertTrue(len(params) > 0)
        
        # Vérifier le paramètre file_path
        file_param = next((p for p in params if p["name"] == "file_path"), None)
        self.assertIsNotNone(file_param)
        self.assertTrue(file_param["required"])
    
    def test_validate_inputs_missing_file(self):
        """Test validation avec fichier manquant"""
        inputs = {"file_path": "/non/existent/file.shp"}
        self.assertFalse(self.component.validate_inputs(inputs))
    
    def test_validate_inputs_no_path(self):
        """Test validation sans chemin"""
        inputs = {}
        self.assertFalse(self.component.validate_inputs(inputs))

if __name__ == '__main__':
    unittest.main()

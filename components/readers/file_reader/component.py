"""
File Reader Component Implementation
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog

from ....core.interfaces import IReader, ComponentMetadata, ComponentType, ExecutionContext

class FileReaderComponent(IReader):
    """Lit des fichiers vecteur et raster depuis le disque"""
    
    def get_metadata(self) -> ComponentMetadata:
        # Charger depuis metadata.json
        metadata_file = Path(__file__).parent / "metadata.json"
        with open(metadata_file) as f:
            data = json.load(f)
        
        return ComponentMetadata(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            type=ComponentType(data["type"]),
            version=data["version"],
            author=data["author"],
            license=data["license"],
            tags=data.get("tags", [])
        )
    
    def get_parameters(self) -> List[Dict]:
        return [
            {
                "name": "file_path",
                "type": "file",
                "required": True,
                "description": "Path to input file",
                "filters": "Vector files (*.shp *.geojson);;Raster files (*.tif *.jpg)"
            },
            {
                "name": "encoding",
                "type": "string",
                "required": False,
                "default": "utf-8",
                "description": "File encoding"
            }
        ]
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Valide que le fichier existe"""
        file_path = inputs.get("file_path")
        if not file_path:
            return False
        
        return Path(file_path).exists()
    
    def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Exécute la lecture du fichier"""
        file_path = inputs["file_path"]
        encoding = inputs.get("encoding", "utf-8")
        
        try:
            # Utiliser QGIS pour charger le fichier
            from qgis.core import QgsVectorLayer, QgsRasterLayer
            
            # Déterminer le type de fichier
            path = Path(file_path)
            if path.suffix.lower() in ['.shp', '.geojson', '.gpkg']:
                layer = QgsVectorLayer(file_path, path.stem, "ogr")
            elif path.suffix.lower() in ['.tif', '.tiff', '.jpg', '.png']:
                layer = QgsRasterLayer(file_path, path.stem)
            else:
                raise Exception(f"Unsupported file format: {path.suffix}")
            
            if not layer.isValid():
                raise Exception(f"Failed to load file: {file_path}")
            
            return {
                "layer": layer,
                "file_path": file_path,
                "layer_type": "vector" if hasattr(layer, 'featureCount') else "raster"
            }
            
        except Exception as e:
            raise Exception(f"File reading failed: {str(e)}")
    
    def get_ui_widget(self) -> QWidget:
        """Widget de configuration avec sélecteur de fichier"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File selector
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select input file...")
        
        file_button = QPushButton("Browse...")
        file_button.clicked.connect(self._browse_file)
        
        layout.addWidget(self.file_input)
        layout.addWidget(file_button)
        
        return widget
    
    def _browse_file(self):
        """Ouvre le dialogue de sélection de fichier"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Input File",
            "",
            "All Supported (*.shp *.geojson *.tif *.jpg);;Vector files (*.shp *.geojson);;Raster files (*.tif *.jpg)"
        )
        
        if file_path:
            self.file_input.setText(file_path)

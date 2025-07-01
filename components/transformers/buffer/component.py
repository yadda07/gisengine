"""
Buffer Transformer Implementation
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDoubleSpinBox, QLabel, QComboBox

from ....core.interfaces import ITransformer, ComponentMetadata, ComponentType, ExecutionContext

class BufferTransformerComponent(ITransformer):
    """Crée des zones tampon autour des features"""
    
    def get_metadata(self) -> ComponentMetadata:
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
                "name": "distance",
                "type": "float",
                "required": True,
                "default": 100.0,
                "description": "Buffer distance in layer units"
            },
            {
                "name": "segments",
                "type": "int",
                "required": False,
                "default": 8,
                "description": "Number of segments in buffer curves"
            },
            {
                "name": "end_cap_style",
                "type": "choice",
                "required": False,
                "default": "round",
                "choices": ["round", "flat", "square"],
                "description": "End cap style for line buffers"
            }
        ]
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Valide les entrées"""
        # Vérifier qu'on a une layer
        if "layer" not in inputs:
            return False
        
        # Vérifier que la distance est positive
        distance = inputs.get("distance", 0)
        return distance > 0
    
    def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Exécute le buffer"""
        try:
            from qgis.core import QgsProcessingAlgorithm
            import processing
            
            layer = inputs["layer"]
            distance = inputs.get("distance", 100.0)
            segments = inputs.get("segments", 8)
            end_cap_style = inputs.get("end_cap_style", "round")
            
            # Mapper le style vers les valeurs QGIS
            cap_style_map = {"round": 1, "flat": 2, "square": 3}
            cap_style = cap_style_map.get(end_cap_style, 1)
            
            # Utiliser l'algorithme QGIS de buffer
            result = processing.run("native:buffer", {
                'INPUT': layer,
                'DISTANCE': distance,
                'SEGMENTS': segments,
                'END_CAP_STYLE': cap_style,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            
            buffered_layer = result['OUTPUT']
            
            return {
                "layer": buffered_layer,
                "buffer_distance": distance,
                "feature_count": buffered_layer.featureCount()
            }
            
        except Exception as e:
            raise Exception(f"Buffer operation failed: {str(e)}")
    
    def get_ui_widget(self) -> QWidget:
        """Widget de configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Distance
        layout.addWidget(QLabel("Buffer Distance:"))
        self.distance_spin = QDoubleSpinBox()
        self.distance_spin.setRange(0.01, 999999.99)
        self.distance_spin.setValue(100.0)
        self.distance_spin.setSuffix(" units")
        layout.addWidget(self.distance_spin)
        
        # Segments
        layout.addWidget(QLabel("Segments:"))
        self.segments_spin = QDoubleSpinBox()
        self.segments_spin.setRange(1, 99)
        self.segments_spin.setValue(8)
        layout.addWidget(self.segments_spin)
        
        # End cap style
        layout.addWidget(QLabel("End Cap Style:"))
        self.cap_combo = QComboBox()
        self.cap_combo.addItems(["round", "flat", "square"])
        layout.addWidget(self.cap_combo)
        
        return widget

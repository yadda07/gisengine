"""
UI Components for File Reader
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QPushButton, QLabel, QComboBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal

class FileReaderWidget(QWidget):
    """Widget de configuration avancé pour File Reader"""
    
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        layout = QVBoxLayout(self)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File:"))
        
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select input file...")
        self.file_input.textChanged.connect(self._on_parameters_changed)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_file)
        
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)
        
        # Encoding selection
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel("Encoding:"))
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "latin-1", "cp1252"])
        self.encoding_combo.currentTextChanged.connect(self._on_parameters_changed)
        
        encoding_layout.addWidget(self.encoding_combo)
        layout.addLayout(encoding_layout)
    
    def _browse_file(self):
        """Ouvre le dialogue de sélection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input File",
            "",
            "All Supported (*.shp *.geojson *.gpkg *.tif *.jpg);;Vector files (*.shp *.geojson *.gpkg);;Raster files (*.tif *.jpg *.png)"
        )
        
        if file_path:
            self.file_input.setText(file_path)
    
    def _on_parameters_changed(self):
        """Émet les nouveaux paramètres"""
        params = {
            "file_path": self.file_input.text(),
            "encoding": self.encoding_combo.currentText()
        }
        self.parameters_changed.emit(params)
    
    def get_parameters(self) -> dict:
        """Retourne les paramètres actuels"""
        return {
            "file_path": self.file_input.text(),
            "encoding": self.encoding_combo.currentText()
        }
    
    def set_parameters(self, params: dict):
        """Définit les paramètres"""
        if "file_path" in params:
            self.file_input.setText(params["file_path"])
        if "encoding" in params:
            self.encoding_combo.setCurrentText(params["encoding"])

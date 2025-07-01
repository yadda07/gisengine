"""
Interface principale GISENGINE
"""

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    """Fenêtre principale unifiée GISENGINE"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GISENGINE - Modern Workflow Designer")
        self.setGeometry(100, 100, 1400, 900)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Tabs principales
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # TODO: Intégrer les composants workflow existants
        # self.add_workflow_tab()
        # self.add_components_tab()
        # self.add_processing_tab()
    
    def add_workflow_tab(self):
        """Ajoute l'onglet workflow designer"""
        # TODO: Importer le workflow designer existant
        pass
    
    def add_components_tab(self):
        """Ajoute l'onglet browsing de composants"""
        pass
    
    def add_processing_tab(self):
        """Ajoute l'onglet processing QGIS"""
        pass

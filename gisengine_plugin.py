"""
GISENGINE Plugin Entry Point
Point d'entrée minimal pour QGIS
"""

import os
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication

class GISENGINEPlugin:
    """Plugin principal GISENGINE avec architecture modulaire"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = 'GISENGINE'
        
        # Initialiser le registry au chargement
        self.registry = None

    def initGui(self):
        """Initialise l'interface QGIS"""
        
        # Action principale
        action = QAction("Open GISENGINE", self.iface.mainWindow())
        action.triggered.connect(self.run)
        action.setStatusTip("Open GISENGINE Workflow Designer")
        
        # Ajouter au menu
        self.iface.addPluginToMenu(self.menu, action)
        self.iface.addToolBarIcon(action)
        self.actions.append(action)

    def unload(self):
        """Nettoie lors du déchargement"""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Lance l'interface principale"""
        try:
            # Initialiser GISENGINE si pas encore fait
            if self.registry is None:
                from . import initialize
                self.registry = initialize()
            
            # Lancer l'interface principale
            from .ui.main_window import MainWindow
            
            self.main_window = MainWindow()
            self.main_window.show()
            
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "GISENGINE Error",
                f"Failed to start GISENGINE:\n{str(e)}"
            )

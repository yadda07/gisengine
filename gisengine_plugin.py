# -*- coding: utf-8 -*-
"""
GISENGINE Plugin for QGIS - Version Unifiée
Plugin principal avec interface unifiée intégrant tous les composants
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QMessageBox
from qgis.core import QgsProject, QgsApplication

# Import de l'interface unifiée
try:
    from .ui.unified_interface import UnifiedGISENGINEInterface
    print("✅ Interface unifiée importée avec succès")
except ImportError as e:
    print(f"❌ Erreur import interface unifiée: {e}")
    UnifiedGISENGINEInterface = None

class GISENGINEPlugin:
    """Plugin principal GISENGINE - Version Unifiée"""

    def __init__(self, iface):
        """Constructeur du plugin"""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Interface elements
        self.actions = []
        self.menu = '🛠️ GISENGINE'
        self.unified_window = None
        self.dock_widget = None
        
        # Check if plugin was started the first time in current QGIS session
        self.first_start = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API"""
        return QCoreApplication.translate('GISENGINEPlugin', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar"""

        if icon_path:
            icon = QIcon(icon_path)
        else:
            icon = QIcon()
            
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI"""
        
        # Pas d'icône pour l'instant
        icon_path = ""
        
        # Action principale UNIQUE - Interface Unifiée
        self.add_action(
            icon_path,
            text=self.tr('🚀 Ouvrir GISENGINE'),
            callback=self.show_unified_interface,
            parent=self.iface.mainWindow(),
            status_tip=self.tr('Ouvre l\'interface unifiée GISENGINE'),
            whats_this=self.tr('Interface complète avec transformers, workflow designer et scanner processing')
        )
        
        # Séparateur
        self.iface.addPluginToMenu(self.menu, None)
        
        # Actions secondaires pour accès rapide
        self.add_action(
            icon_path,
            text=self.tr('📊 Designer de Workflow'),
            callback=self.show_workflow_tab,
            parent=self.iface.mainWindow(),
            status_tip=self.tr('Accès direct au designer de workflow'),
            add_to_toolbar=False
        )
        
        self.add_action(
            icon_path,
            text=self.tr('🛠️ Bibliothèque Transformers'),
            callback=self.show_transformers_tab,
            parent=self.iface.mainWindow(),
            status_tip=self.tr('Accès direct à la bibliothèque de transformers'),
            add_to_toolbar=False
        )
        
        self.add_action(
            icon_path,
            text=self.tr('⚙️ Scanner Processing'),
            callback=self.show_processing_tab,
            parent=self.iface.mainWindow(),
            status_tip=self.tr('Accès direct au scanner processing QGIS'),
            add_to_toolbar=False
        )
        
        # Séparateur
        self.iface.addPluginToMenu(self.menu, None)
        
        # Action About
        self.add_action(
            icon_path,
            text=self.tr('ℹ️ À propos'),
            callback=self.show_about,
            parent=self.iface.mainWindow(),
            add_to_toolbar=False
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI"""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)
        
        # Fermer l'interface unifiée
        if self.unified_window:
            self.unified_window.close()
        if self.dock_widget:
            self.dock_widget.close()

    def show_unified_interface(self):
        """Affiche l'interface unifiée principale"""
        try:
            if UnifiedGISENGINEInterface is None:
                QMessageBox.critical(
                    self.iface.mainWindow(),
                    "Import Error",
                    "❌ Module interface unifiée non trouvé.\n\n"
                    "Vérifiez que le fichier ui/unified_interface.py existe."
                )
                return
            
            # Option 1: Fenêtre indépendante (recommandé)
            if self.unified_window is None or not self.unified_window.isVisible():
                self.unified_window = UnifiedGISENGINEInterface(self.iface)
                self.unified_window.show()
                
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Erreur",
                f"❌ Erreur lors de l'ouverture de l'interface unifiée:\n\n{str(e)}"
            )

    def show_workflow_tab(self):
        """Accès direct à l'onglet workflow"""
        self.show_unified_interface()
        if self.unified_window and hasattr(self.unified_window, 'tabs'):
            self.unified_window.tabs.setCurrentIndex(1)  # Onglet workflow

    def show_transformers_tab(self):
        """Accès direct à l'onglet transformers"""
        self.show_unified_interface()
        if self.unified_window and hasattr(self.unified_window, 'tabs'):
            self.unified_window.tabs.setCurrentIndex(0)  # Onglet transformers

    def show_processing_tab(self):
        """Accès direct à l'onglet processing"""
        self.show_unified_interface()
        if self.unified_window and hasattr(self.unified_window, 'tabs'):
            self.unified_window.tabs.setCurrentIndex(2)  # Onglet processing

    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        about_text = """
        <h2>🛠️ GISENGINE pour QGIS</h2>
        <p><b>Version:</b> 1.0.0 - Interface Unifiée</p>
        <p><b>Description:</b> Plugin offrant une interface moderne et unifiée pour 
        chaîner des traitements géomatiques dans QGIS avec une interface moderne.</p>
        
        <h3>🎯 Interface Unifiée:</h3>
        <ul>
        <li>🛠️ <b>Bibliothèque Transformers</b> - Catalogue de transformations disponibles</li>
        <li>📊 <b>Workflow Designer</b> - Création graphique de workflows avec connexions</li>
        <li>⚙️ <b>Scanner Processing</b> - Intégration complète avec QGIS Processing Framework</li>
        </ul>
        
        <h3>🚀 Avantages:</h3>
        <ul>
        <li>✅ <b>Une seule fenêtre</b> pour tous les composants</li>
        <li>✅ <b>Navigation par onglets</b> fluide et intuitive</li>
        <li>✅ <b>Interface moderne</b> avec style professionnel</li>
        <li>✅ <b>Intégration QGIS</b> native et optimisée</li>
        </ul>
        
        <h3>📖 Utilisation:</h3>
        <p>Cliquez sur <b>"🚀 Ouvrir GISENGINE"</b> dans le menu Extensions 
        pour accéder à l'interface complète.</p>
        
        <p><i>🔧 Plugin en développement actif - Version prototype avancée</i></p>
        """
        
        QMessageBox.about(self.iface.mainWindow(), "À propos - GISENGINE", about_text)

    def run(self):
        """Run method that performs all the real work"""
        # Méthode appelée lors du premier lancement
        if self.first_start:
            self.first_start = False
            # Optionnel: ouvrir automatiquement l'interface au premier lancement
            # self.show_unified_interface()
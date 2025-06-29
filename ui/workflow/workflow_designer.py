# -*- coding: utf-8 -*-
"""
FME Workflow Designer
Main professional workflow designer window
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import os

from .workflow_scene import FMEStyleScene
from .search_panel import ProfessionalSearchPanel

class FMEWorkflowDesigner(QMainWindow):
    """Professional FME-style workflow designer with modern interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GIS Engine - Workflow Designer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Professional styling
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
            QMenuBar {
                background: white;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
                font-family: 'Segoe UI';
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #e3f2fd;
            }
            QToolBar {
                background: white;
                border-bottom: 1px solid #dee2e6;
                spacing: 8px;
                padding: 4px;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }
            QToolButton:hover {
                background: #e3f2fd;
                border-color: #2196f3;
            }
            QStatusBar {
                background: white;
                border-top: 1px solid #dee2e6;
                color: #495057;
            }
        """)
        
        # Initialize components
        self.setup_scene_and_view()
        self.setup_panels()
        self.setup_layout()
        self.create_menus()
        self.create_toolbar()
        self.setup_connections()
        
        # Status bar
        self.statusBar().showMessage("Ready - Use search panel or keyboard shortcuts to add components")
    
    def setup_scene_and_view(self):
        """Configuration de la scène et de la vue"""
        self.scene = FMEStyleScene()
        
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Style de la vue
        self.view.setStyleSheet("""
            QGraphicsView {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: white;
            }
        """)
    
    def setup_panels(self):
        """Configuration des panneaux"""
        # Panneau de recherche
        self.search_panel = ProfessionalSearchPanel()
        
        # Panneau de propriétés
        self.properties_panel = self.create_properties_panel()
    
    def create_properties_panel(self):
        """Créer le panneau de propriétés professionnel"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("Properties")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Properties content
        self.properties_content = QLabel("Select a component to view properties")
        self.properties_content.setStyleSheet("""
            color: #6c757d;
            font-style: italic;
            padding: 20px;
        """)
        self.properties_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.properties_content)
        
        layout.addStretch()
        
        panel.setFixedWidth(280)
        panel.hide()  # Initially hidden
        
        return panel
    
    def setup_layout(self):
        """Configuration du layout principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Panneau de recherche à gauche
        main_layout.addWidget(self.search_panel)
        
        # Vue centrale
        main_layout.addWidget(self.view, 1)
        
        # Panneau de propriétés à droite (caché par défaut)
        main_layout.addWidget(self.properties_panel)
    
    def create_menus(self):
        """Create professional menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('New Workflow', self.new_workflow, 'Ctrl+N')
        file_menu.addAction('Open Workflow', self.open_workflow, 'Ctrl+O')
        file_menu.addSeparator()
        file_menu.addAction('Save Workflow', self.save_workflow, 'Ctrl+S')
        file_menu.addAction('Save As...', self.save_workflow_as, 'Ctrl+Shift+S')
        file_menu.addSeparator()
        file_menu.addAction('Export', self.export_workflow)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('Undo', self.undo_action, 'Ctrl+Z')
        edit_menu.addAction('Redo', self.redo_action, 'Ctrl+Y')
        edit_menu.addSeparator()
        edit_menu.addAction('Cut', self.cut_action, 'Ctrl+X')
        edit_menu.addAction('Copy', self.copy_action, 'Ctrl+C')
        edit_menu.addAction('Paste', self.paste_action, 'Ctrl+V')
        edit_menu.addSeparator()
        edit_menu.addAction('Delete', self.delete_action, 'Del')
        edit_menu.addAction('Select All', self.select_all_action, 'Ctrl+A')
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        grid_action = QAction('Show Grid', self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self.toggle_grid)
        
        zoom_fit_action = QAction('Zoom to Fit', self)
        zoom_fit_action.triggered.connect(self.zoom_to_fit)
        zoom_fit_action.setShortcut('Ctrl+0')
        
        properties_action = QAction('Properties Panel', self)
        properties_action.setCheckable(True)
        properties_action.triggered.connect(self.toggle_properties_panel)
        
        view_menu.addAction(grid_action)
        view_menu.addAction(zoom_fit_action)
        view_menu.addSeparator()
        view_menu.addAction(properties_action)
        
        # Workflow menu
        workflow_menu = menubar.addMenu('Workflow')
        workflow_menu.addAction('Validate', self.validate_workflow, 'F5')
        workflow_menu.addAction('Run', self.run_workflow, 'F6')
        workflow_menu.addSeparator()
        workflow_menu.addAction('Clear All', self.clear_workflow)
    
    def create_toolbar(self):
        """Créer la barre d'outils professionnelle"""
        toolbar = self.addToolBar('Main')
        toolbar.setMovable(False)
        
        # Actions principales
        toolbar.addAction('New', self.new_workflow).setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        toolbar.addAction('Open', self.open_workflow).setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        toolbar.addAction('Save', self.save_workflow).setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        
        toolbar.addSeparator()
        
        toolbar.addAction('Zoom Fit', self.zoom_to_fit).setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        
        toolbar.addSeparator()
        
        toolbar.addAction('Run', self.run_workflow).setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        toolbar.addAction('Validate', self.validate_workflow).setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
    
    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.search_panel.node_requested.connect(self.add_node_to_scene)
    
    def add_node_to_scene(self, node_data):
        """Ajouter un nœud à la scène"""
        center = self.view.mapToScene(self.view.rect().center())
        
        # Ajout de la position aléatoire pour éviter chevauchement
        import random
        center.setX(center.x() + random.randint(-50, 50))
        center.setY(center.y() + random.randint(-50, 50))
        
        node = self.scene.add_node_from_data(node_data, center)
        self.statusBar().showMessage(f"Added {node_data['name']} to workflow")
        
        return node
    
    # === Actions du menu ===
    
    def new_workflow(self):
        """Nouveau workflow"""
        reply = QMessageBox.question(self, 'New Workflow', 
                                   'Create a new workflow? Unsaved changes will be lost.',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.scene.clear_scene()
            self.statusBar().showMessage("New workflow created")
    
    def open_workflow(self):
        """Ouvrir un workflow"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Workflow', '', 'Workflow Files (*.json);;All Files (*)')
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.scene.load_scene_data(data)
                self.statusBar().showMessage(f"Workflow loaded from {os.path.basename(file_path)}")
            
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load workflow:\n{str(e)}')
    
    def save_workflow(self):
        """Sauvegarder le workflow"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Workflow', 'workflow.json', 'Workflow Files (*.json);;All Files (*)')
        
        if file_path:
            try:
                data = self.scene.get_scene_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.statusBar().showMessage(f"Workflow saved to {os.path.basename(file_path)}")
            
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save workflow:\n{str(e)}')
    
    def save_workflow_as(self):
        """Sauvegarder sous"""
        self.save_workflow()
    
    def export_workflow(self):
        """Exporter le workflow"""
        self.statusBar().showMessage("Export functionality not implemented yet")
    
    def undo_action(self):
        """Annuler"""
        self.statusBar().showMessage("Undo functionality not implemented yet")
    
    def redo_action(self):
        """Refaire"""
        self.statusBar().showMessage("Redo functionality not implemented yet")
    
    def cut_action(self):
        """Couper"""
        self.statusBar().showMessage("Cut functionality not implemented yet")
    
    def copy_action(self):
        """Copier"""
        self.statusBar().showMessage("Copy functionality not implemented yet")
    
    def paste_action(self):
        """Coller"""
        self.statusBar().showMessage("Paste functionality not implemented yet")
    
    def delete_action(self):
        """Supprimer"""
        self.scene.delete_selected_items()
        self.statusBar().showMessage("Selected items deleted")
    
    def select_all_action(self):
        """Sélectionner tout"""
        for item in self.scene.items():
            if hasattr(item, 'setSelected'):
                item.setSelected(True)
        self.statusBar().showMessage("All items selected")
    
    def toggle_grid(self):
        """Basculer la grille"""
        self.scene.toggle_grid()
        self.statusBar().showMessage("Grid toggled")
    
    def zoom_to_fit(self):
        """Zoom pour ajuster"""
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.statusBar().showMessage("Zoomed to fit")
    
    def toggle_properties_panel(self):
        """Basculer le panneau de propriétés"""
        if self.properties_panel.isVisible():
            self.properties_panel.hide()
        else:
            self.properties_panel.show()
    
    def validate_workflow(self):
        """Valider le workflow"""
        # TODO: Implémenter la validation
        self.statusBar().showMessage("Workflow validation not implemented yet")
    
    def run_workflow(self):
        """Exécuter le workflow"""
        # TODO: Implémenter l'exécution
        self.statusBar().showMessage("Workflow execution not implemented yet")
    
    def clear_workflow(self):
        """Vider le workflow"""
        reply = QMessageBox.question(self, 'Clear Workflow', 
                                   'Clear all components from workflow?',
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.scene.clear_scene()
            self.statusBar().showMessage("Workflow cleared")
    
    def keyPressEvent(self, event):
        """Gestion des raccourcis clavier globaux"""
        if event.key() == Qt.Key_Space:
            # Focus sur la recherche avec Espace
            self.search_panel.search_box.setFocus()
            self.search_panel.search_box.selectAll()
        
        super().keyPressEvent(event)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script pour vérifier le système de connexions du workflow designer
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# Ajouter le chemin du plugin
plugin_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_path)

from ui.workflow import FMEWorkflowDesigner

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Workflow Connections")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Workflow designer
        self.workflow_designer = FMEWorkflowDesigner()
        layout.addWidget(self.workflow_designer)
        
        # Ajouter quelques nœuds de test
        self.add_test_nodes()
    
    def add_test_nodes(self):
        """Ajouter des nœuds de test pour tester les connexions"""
        scene = self.workflow_designer.scene
        
        # Nœud reader
        reader_data = {
            'name': 'CSV Reader',
            'type': 'reader',
            'inputs': 0,
            'outputs': 1
        }
        scene.add_node_from_data(reader_data, scene.views()[0].mapToScene(100, 100))
        
        # Nœud transformer
        transformer_data = {
            'name': 'AttributeFilter',
            'type': 'transformer',
            'inputs': 1,
            'outputs': 2
        }
        scene.add_node_from_data(transformer_data, scene.views()[0].mapToScene(400, 100))
        
        # Nœud writer
        writer_data = {
            'name': 'Shapefile Writer',
            'type': 'writer',
            'inputs': 1,
            'outputs': 0
        }
        scene.add_node_from_data(writer_data, scene.views()[0].mapToScene(700, 100))

def main():
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("Instructions de test:")
    print("1. Cliquez sur un port de sortie (bleu, à droite) pour commencer une connexion")
    print("2. Déplacez la souris pour voir la connexion temporaire curviligne")
    print("3. Cliquez sur un port d'entrée (vert, à gauche) pour finaliser la connexion")
    print("4. Utilisez le clic droit ou Échap pour annuler une connexion en cours")
    print("5. Sélectionnez une connexion et appuyez sur Suppr pour la supprimer")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

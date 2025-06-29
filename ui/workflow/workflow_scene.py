# -*- coding: utf-8 -*-
"""
Professional Workflow Scene
FME-style scene with grid and interactions
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .workflow_nodes import ProfessionalWorkflowNode, Connection

class FMEStyleScene(QGraphicsScene):
    """Scène graphique professionnelle style FME"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuration de base
        self.setSceneRect(-2000, -2000, 4000, 4000)
        self.setBackgroundBrush(QBrush(QColor("#f8f9fa")))
        
        # État de connexion
        self.temp_connection = None
        self.connection_start_port = None
        
        # Grille
        self.grid_size = 20
        self.show_grid = True
        
        # Interactions
        self.setItemIndexMethod(QGraphicsScene.NoIndex)
    
    def drawBackground(self, painter, rect):
        """Dessiner la grille de fond professionnelle"""
        if not self.show_grid:
            super().drawBackground(painter, rect)
            return
        
        painter.fillRect(rect, QBrush(QColor("#f8f9fa")))
        
        # Configuration du pinceau pour la grille
        pen = QPen(QColor("#e9ecef"), 1)
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        
        # Lignes verticales
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        lines = []
        
        x = left
        while x < rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += self.grid_size
        
        # Lignes horizontales
        y = top
        while y < rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += self.grid_size
        
        painter.drawLines(lines)
    
    def add_node_from_data(self, node_data, position):
        """Ajouter un nœud à partir des données"""
        # Ajuster la position à la grille
        grid_x = round(position.x() / self.grid_size) * self.grid_size
        grid_y = round(position.y() / self.grid_size) * self.grid_size
        
        # Créer le nœud
        node = ProfessionalWorkflowNode(node_data, grid_x, grid_y)
        self.addItem(node)
        
        # Sélectionner le nouveau nœud
        self.clearSelection()
        node.setSelected(True)
        
        return node
    
    def start_connection(self, start_port):
        """Commencer une nouvelle connexion"""
        self.connection_start_port = start_port
        
        # Créer une connexion temporaire
        self.temp_connection = QGraphicsLineItem()
        self.temp_connection.setPen(QPen(QColor("#007bff"), 2, Qt.DashLine))
        self.addItem(self.temp_connection)
        
        # Position de départ
        start_pos = start_port.scenePos() + start_port.boundingRect().center()
        self.temp_connection.setLine(start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y())
    
    def mouseMoveEvent(self, event):
        """Gestion du mouvement de souris pour les connexions temporaires"""
        if self.temp_connection and self.connection_start_port:
            start_pos = self.connection_start_port.scenePos() + self.connection_start_port.boundingRect().center()
            end_pos = event.scenePos()
            self.temp_connection.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """Gestion des clics pour finaliser les connexions"""
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos(), QTransform())
            
            # Vérifier si on clique sur un port d'entrée
            if hasattr(item, 'port_type') and item.port_type == "input" and self.connection_start_port:
                if self.can_connect(self.connection_start_port, item):
                    # Créer la connexion finale
                    connection = Connection(self.connection_start_port, item)
                    self.addItem(connection)
                
                # Nettoyer la connexion temporaire
                self.cleanup_temp_connection()
            
            elif event.button() == Qt.RightButton or not item:
                # Annuler la connexion temporaire
                self.cleanup_temp_connection()
        
        super().mousePressEvent(event)
    
    def can_connect(self, start_port, end_port):
        """Vérifier si deux ports peuvent être connectés"""
        if not start_port or not end_port:
            return False
        
        # Vérifier les types de ports
        if start_port.port_type == end_port.port_type:
            return False
        
        # Vérifier qu'ils ne sont pas sur le même nœud
        if start_port.parent_node == end_port.parent_node:
            return False
        
        # Vérifier qu'il n'y a pas déjà une connexion
        for connection in end_port.connections:
            if connection.start_port == start_port:
                return False
        
        return True
    
    def cleanup_temp_connection(self):
        """Nettoyer la connexion temporaire"""
        if self.temp_connection:
            self.removeItem(self.temp_connection)
            self.temp_connection = None
        self.connection_start_port = None
    
    def keyPressEvent(self, event):
        """Gestion des raccourcis clavier"""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key_Escape:
            self.cleanup_temp_connection()
            self.clearSelection()
        elif event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
            # Sélectionner tout
            for item in self.items():
                if isinstance(item, ProfessionalWorkflowNode):
                    item.setSelected(True)
        
        super().keyPressEvent(event)
    
    def delete_selected_items(self):
        """Supprimer les éléments sélectionnés"""
        selected_items = self.selectedItems()
        
        for item in selected_items:
            if isinstance(item, ProfessionalWorkflowNode):
                # Supprimer toutes les connexions du nœud
                all_ports = item.input_ports + item.output_ports
                for port in all_ports:
                    for connection in port.connections.copy():
                        connection.remove_from_scene()
                
                # Supprimer le nœud
                self.removeItem(item)
            
            elif isinstance(item, Connection):
                item.remove_from_scene()
    
    def toggle_grid(self):
        """Basculer l'affichage de la grille"""
        self.show_grid = not self.show_grid
        self.update()
    
    def clear_scene(self):
        """Vider la scène"""
        self.cleanup_temp_connection()
        self.clear()
    
    def get_scene_data(self):
        """Obtenir les données de la scène pour sauvegarde"""
        nodes_data = []
        connections_data = []
        
        for item in self.items():
            if isinstance(item, ProfessionalWorkflowNode):
                node_info = {
                    'id': id(item),
                    'data': item.node_data,
                    'position': {'x': item.pos().x(), 'y': item.pos().y()}
                }
                nodes_data.append(node_info)
            
            elif isinstance(item, Connection):
                connection_info = {
                    'start_node_id': id(item.start_port.parent_node),
                    'start_port': item.start_port.port_name,
                    'end_node_id': id(item.end_port.parent_node),
                    'end_port': item.end_port.port_name
                }
                connections_data.append(connection_info)
        
        return {
            'nodes': nodes_data,
            'connections': connections_data
        }
    
    def load_scene_data(self, scene_data):
        """Charger les données dans la scène"""
        self.clear_scene()
        
        # Créer les nœuds d'abord
        node_map = {}
        for node_info in scene_data.get('nodes', []):
            position = QPointF(node_info['position']['x'], node_info['position']['y'])
            node = self.add_node_from_data(node_info['data'], position)
            node_map[node_info['id']] = node
        
        # Créer les connexions
        for conn_info in scene_data.get('connections', []):
            start_node = node_map.get(conn_info['start_node_id'])
            end_node = node_map.get(conn_info['end_node_id'])
            
            if start_node and end_node:
                # Trouver les ports correspondants
                start_port = None
                for port in start_node.output_ports:
                    if port.port_name == conn_info['start_port']:
                        start_port = port
                        break
                
                end_port = None
                for port in end_node.input_ports:
                    if port.port_name == conn_info['end_port']:
                        end_port = port
                        break
                
                if start_port and end_port:
                    connection = Connection(start_port, end_port)
                    self.addItem(connection)

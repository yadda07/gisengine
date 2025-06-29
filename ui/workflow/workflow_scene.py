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
        self.is_connecting = False
        
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
    
    def handle_port_click(self, port):
        """Gérer le clic sur un port"""
        print(f"Port clicked: {port.port_type}, is_connecting: {self.is_connecting}")
        
        if not self.is_connecting:
            # Commencer une nouvelle connexion depuis un port de sortie
            if port.port_type == "output":
                print(f"Starting connection from output port")
                self.start_connection(port)
        else:
            # Terminer la connexion sur un port d'entrée
            if port.port_type == "input" and self.connection_start_port:
                print(f"Finishing connection to input port")
                self.finish_connection(port)
            else:
                # Annuler si on clique sur un mauvais type de port
                print(f"Canceling connection - wrong port type")
                self.cleanup_temp_connection()
    
    def start_connection(self, start_port):
        """Commencer une nouvelle connexion"""
        self.connection_start_port = start_port
        self.is_connecting = True
        
        # Créer une connexion temporaire curviligne
        self.temp_connection = QGraphicsPathItem()
        pen = QPen(QColor("#007bff"), 2, Qt.DashLine)
        pen.setCapStyle(Qt.RoundCap)
        self.temp_connection.setPen(pen)
        self.addItem(self.temp_connection)
        
        # Mettre à jour le curseur
        self.views()[0].setCursor(Qt.CrossCursor) if self.views() else None
    
    def finish_connection(self, end_port):
        """Terminer la connexion"""
        print(f"Attempting to finish connection from {self.connection_start_port.port_type} to {end_port.port_type}")
        
        if self.can_connect(self.connection_start_port, end_port):
            print("Connection allowed - creating final connection")
            # Créer la connexion finale
            connection = Connection(self.connection_start_port, end_port)
            self.addItem(connection)
            print("Connection created and added to scene")
        else:
            print("Connection not allowed")
        
        self.cleanup_temp_connection()
    
    def mouseMoveEvent(self, event):
        """Gestion du mouvement de souris pour les connexions temporaires"""
        if self.temp_connection and self.connection_start_port and self.is_connecting:
            self.update_temp_connection(event.scenePos())
        
        super().mouseMoveEvent(event)
    
    def update_temp_connection(self, end_pos):
        """Mettre à jour la connexion temporaire avec une courbe"""
        if not self.temp_connection or not self.connection_start_port:
            return
            
        start_pos = self.connection_start_port.scenePos() + self.connection_start_port.boundingRect().center()
        
        # Créer un chemin courbe temporaire
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calcul des points de contrôle
        dx = end_pos.x() - start_pos.x()
        distance = abs(dx)
        control_offset = max(50, min(distance * 0.6, 200))
        
        ctrl1 = QPointF(start_pos.x() + control_offset, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - control_offset, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        self.temp_connection.setPath(path)
    
    def mousePressEvent(self, event):
        """Gestion des clics pour finaliser les connexions"""
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos(), QTransform())
            
            # Si on est en train de connecter et qu'on clique dans le vide
            if self.is_connecting and not hasattr(item, 'port_type'):
                self.cleanup_temp_connection()
                return
        
        elif event.button() == Qt.RightButton:
            # Annuler la connexion temporaire avec clic droit
            self.cleanup_temp_connection()
        
        super().mousePressEvent(event)
    
    def can_connect(self, start_port, end_port):
        """Vérifier si deux ports peuvent être connectés"""
        if not start_port or not end_port:
            print("Cannot connect: missing port")
            return False
        
        # Vérifier les types de ports (output vers input)
        if start_port.port_type == end_port.port_type:
            print(f"Cannot connect: same port types ({start_port.port_type})")
            return False
            
        # S'assurer que c'est output vers input
        if start_port.port_type != "output" or end_port.port_type != "input":
            print(f"Cannot connect: wrong direction ({start_port.port_type} -> {end_port.port_type})")
            return False
        
        # Vérifier qu'ils ne sont pas sur le même nœud
        if start_port.parent_node == end_port.parent_node:
            print("Cannot connect: same node")
            return False
        
        # Vérifier qu'il n'y a pas déjà une connexion
        for connection in end_port.connections:
            if connection.start_port == start_port:
                print("Cannot connect: connection already exists")
                return False
        
        print("Connection allowed")
        return True
    
    def cleanup_temp_connection(self):
        """Nettoyer la connexion temporaire"""
        if self.temp_connection:
            self.removeItem(self.temp_connection)
            self.temp_connection = None
        self.connection_start_port = None
        self.is_connecting = False
        
        # Restaurer le curseur normal
        if self.views():
            self.views()[0].setCursor(Qt.ArrowCursor)
    
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

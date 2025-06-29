# -*- coding: utf-8 -*-
"""
Professional Workflow Nodes
FME-style nodes with modern design
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

class ConnectionPort(QGraphicsEllipseItem):
    """Port de connexion professionnel pour les nœuds"""
    
    def __init__(self, parent_node, port_type="input", port_name="", x=0, y=0):
        super().__init__(-6, -6, 12, 12)
        self.parent_node = parent_node
        self.port_type = port_type  # "input" ou "output"
        self.port_name = port_name
        self.connections = []
        
        # Position relative au nœud parent
        self.setPos(x, y)
        self.setParentItem(parent_node)
        
        # Style professionnel
        self.setup_appearance()
        
        # Interaction
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
    
    def setup_appearance(self):
        """Configuration de l'apparence professionnelle"""
        if self.port_type == "input":
            color = QColor("#28a745")  # Vert pour input
        else:
            color = QColor("#007bff")  # Bleu pour output
            
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("white"), 2))
    
    def hoverEnterEvent(self, event):
        """Survol du port"""
        self.setScale(1.3)
        self.update()
    
    def hoverLeaveEvent(self, event):
        """Fin de survol"""
        self.setScale(1.0)
        self.update()
    
    def add_connection(self, connection):
        """Ajouter une connexion à ce port"""
        if connection not in self.connections:
            self.connections.append(connection)
    
    def remove_connection(self, connection):
        """Supprimer une connexion de ce port"""
        if connection in self.connections:
            self.connections.remove(connection)
    
    def mousePressEvent(self, event):
        """Début de création de connexion"""
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            if hasattr(scene, 'handle_port_click'):
                scene.handle_port_click(self)
                event.accept()
                return
        super().mousePressEvent(event)
    
    def add_connection(self, connection):
        """Ajouter une connexion"""
        if connection not in self.connections:
            self.connections.append(connection)
    
    def remove_connection(self, connection):
        """Supprimer une connexion"""
        if connection in self.connections:
            self.connections.remove(connection)

class Connection(QGraphicsPathItem):
    """Connexion courbe professionnelle entre ports"""
    
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        
        # Configuration
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(1)  # Au-dessus des nœuds
        
        # Style professionnel
        self.pen_normal = QPen(QColor("#4A90E2"), 2)
        self.pen_normal.setCapStyle(Qt.RoundCap)
        self.pen_selected = QPen(QColor("#ffc107"), 3)
        self.pen_selected.setCapStyle(Qt.RoundCap)
        
        # Appliquer le style par défaut
        self.setPen(self.pen_normal)
        
        # Enregistrer la connexion dans les ports
        self.start_port.add_connection(self)
        self.end_port.add_connection(self)
        
        # Créer le chemin
        self.update_path()
    
    def update_path(self):
        """Met à jour le chemin de la connexion courbe"""
        if not self.start_port or not self.end_port:
            return
            
        # Positions absolues des centres des ports
        start_pos = self.start_port.scenePos() + self.start_port.boundingRect().center()
        end_pos = self.end_port.scenePos() + self.end_port.boundingRect().center()
        
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calcul des points de contrôle pour une courbe de Bézier fluide
        dx = end_pos.x() - start_pos.x()
        distance = abs(dx)
        
        # Contrôle adaptatif de la courbure selon la distance
        control_offset = max(50, min(distance * 0.6, 200))
        
        ctrl1 = QPointF(start_pos.x() + control_offset, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - control_offset, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        self.setPath(path)
        
        # Mettre à jour la zone de collision
        self.prepareGeometryChange()
    
    def paint(self, painter, option, widget):
        """Rendu personnalisé de la connexion"""
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Ombre portée pour plus de profondeur
        shadow_pen = QPen(QColor(0, 0, 0, 30), 4)
        painter.setPen(shadow_pen)
        shadow_path = self.path()
        shadow_path.translate(2, 2)
        painter.drawPath(shadow_path)
        
        # Connexion principale
        if self.isSelected():
            painter.setPen(self.pen_selected)
        else:
            painter.setPen(self.pen_normal)
        
        painter.drawPath(self.path())
        
        # Flèche directionnelle au milieu
        self.draw_arrow(painter)
    
    def draw_arrow(self, painter):
        """Dessiner une flèche directionnelle sur la connexion"""
        if not self.path().elementCount():
            return
            
        # Point au milieu de la courbe (approximatif)
        percent = 0.5
        point = self.path().pointAtPercent(percent)
        
        # Direction de la tangente
        angle_percent = 0.51  # Légèrement après le milieu pour la direction
        next_point = self.path().pointAtPercent(angle_percent)
        
        # Calculer l'angle
        dx = next_point.x() - point.x()
        dy = next_point.y() - point.y()
        angle = math.atan2(dy, dx)
        
        # Dessiner la flèche
        arrow_size = 8
        arrow_head = QPainterPath()
        arrow_head.moveTo(point.x(), point.y())
        arrow_head.lineTo(
            point.x() - arrow_size * math.cos(angle - math.pi/6),
            point.y() - arrow_size * math.sin(angle - math.pi/6)
        )
        arrow_head.moveTo(point.x(), point.y())
        arrow_head.lineTo(
            point.x() - arrow_size * math.cos(angle + math.pi/6),
            point.y() - arrow_size * math.sin(angle + math.pi/6)
        )
        
        painter.drawPath(arrow_head)
    
    def remove_from_scene(self):
        """Suppression propre de la connexion"""
        if self.start_port:
            self.start_port.remove_connection(self)
        if self.end_port:
            self.end_port.remove_connection(self)
        if self.scene():
            self.scene().removeItem(self)

class ProfessionalWorkflowNode(QGraphicsRectItem):
    """Nœud de workflow professionnel style FME"""
    
    def __init__(self, node_data, x=0, y=0):
        super().__init__(0, 0, 160, 80)
        
        self.node_data = node_data
        self.input_ports = []
        self.output_ports = []
        
        # Position
        self.setPos(x, y)
        
        # Configuration
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        
        # Style professionnel
        self.setup_appearance()
        self.create_ports()
        self.create_label()
    
    def setup_appearance(self):
        """Configuration de l'apparence professionnelle"""
        # Couleur selon le type
        node_type = self.node_data.get('type', 'transformer')
        if node_type == 'reader':
            color = QColor("#28a745")  # Vert
        elif node_type == 'writer':
            color = QColor("#dc3545")  # Rouge
        else:
            color = QColor("#007bff")  # Bleu
        
        # Gradient professionnel
        gradient = QLinearGradient(0, 0, 0, 80)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color)
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(QColor("#dee2e6"), 2))
        
        # Coins arrondis
        self.setRect(0, 0, 160, 80)
    
    def create_ports(self):
        """Créer les ports d'entrée et de sortie"""
        # Ports d'entrée (gauche)
        input_count = self.node_data.get('inputs', 1)
        for i in range(input_count):
            y_pos = 20 + (i * 40) if input_count > 1 else 40
            port = ConnectionPort(self, "input", f"input_{i}", -6, y_pos)
            self.input_ports.append(port)
        
        # Ports de sortie (droite)
        output_count = self.node_data.get('outputs', 1)
        for i in range(output_count):
            y_pos = 20 + (i * 40) if output_count > 1 else 40
            port = ConnectionPort(self, "output", f"output_{i}", 166, y_pos)
            self.output_ports.append(port)
    
    def create_label(self):
        """Créer le label du nœud"""
        self.label = QGraphicsTextItem(self.node_data.get('name', 'Node'))
        self.label.setParentItem(self)
        self.label.setPos(10, 25)
        
        # Style du texte
        font = QFont("Segoe UI", 9, QFont.Bold)
        self.label.setFont(font)
        self.label.setDefaultTextColor(QColor("white"))
    
    def itemChange(self, change, value):
        """Gestion des changements (pour mettre à jour les connexions)"""
        if change == QGraphicsItem.ItemPositionChange:
            # Mettre à jour toutes les connexions
            for port in self.input_ports + self.output_ports:
                for connection in port.connections:
                    connection.update_path()
        
        return super().itemChange(change, value)
    
    def hoverEnterEvent(self, event):
        """Survol du nœud"""
        self.setScale(1.05)
        self.update()
    
    def hoverLeaveEvent(self, event):
        """Fin de survol"""
        self.setScale(1.0)
        self.update()
    
    def paint(self, painter, option, widget):
        """Rendu personnalisé avec coins arrondis"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Rectangle avec coins arrondis
        rect = self.rect()
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffc107"), 3))
        else:
            painter.setPen(self.pen())
        
        painter.setBrush(self.brush())
        painter.drawRoundedRect(rect, 8, 8)

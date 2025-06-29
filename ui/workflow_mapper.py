#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GISEngine Workflow Mapper - Modern FME-Style Interface
Interface de création de workflows visuels moderne avec drag & drop fluide
"""

from PyQt5.QtCore import (
    Qt, QTimer, QPointF, pyqtSignal, QRectF, QPropertyAnimation, QEasingCurve,
    QObject, QEvent, QMimeData, QSizeF, QRect, QSize, QStringListModel
)
from PyQt5.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QLinearGradient, QPainterPath,
    QPixmap, QIcon, QDrag, QPalette, QFontMetrics, QKeySequence
)
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem,
    QGraphicsEllipseItem, QGraphicsTextItem, QDialog, QVBoxLayout,
    QHBoxLayout, QFormLayout, QTabWidget, QWidget, QLineEdit, QTextEdit,
    QTableWidget, QTableWidgetItem, QDialogButtonBox, QLabel, QTransform,
    QCompleter, QListWidget, QListWidgetItem, QFrame, QPushButton,
    QScrollArea, QSplitter, QGroupBox, QCheckBox, QSlider, QSpinBox,
    QApplication, QGraphicsDropShadowEffect, QGraphicsProxyWidget,
    QMainWindow, QShortcut, QMenu, QAction
)
import random
import json
from typing import List, Dict, Optional, Any

# === DONNÉES DES NŒUDS STYLE FME ===

WORKFLOW_NODES = {
    "readers": [
        {"name": "Shapefile Reader", "category": "Spatial Readers", "icon": "📁", "color": "#28a745", "keywords": ["shp", "shapefile", "esri"]},
        {"name": "GeoJSON Reader", "category": "Spatial Readers", "icon": "🗺️", "color": "#28a745", "keywords": ["geojson", "json", "web"]},
        {"name": "CSV Reader", "category": "Table Readers", "icon": "📊", "color": "#28a745", "keywords": ["csv", "table", "data"]},
        {"name": "PostGIS Reader", "category": "Database Readers", "icon": "🗄️", "color": "#28a745", "keywords": ["postgis", "postgresql", "db"]},
        {"name": "WFS Reader", "category": "Web Readers", "icon": "🌐", "color": "#28a745", "keywords": ["wfs", "web", "service"]},
    ],
    "transformers": [
        {"name": "Buffer", "category": "Vector Geometry", "icon": "⭕", "color": "#FF9800", "keywords": ["buffer", "zone", "distance"]},
        {"name": "Clip", "category": "Vector Overlay", "icon": "✂️", "color": "#FF9800", "keywords": ["clip", "cut", "overlay"]},
        {"name": "Dissolve", "category": "Vector Geometry", "icon": "🔗", "color": "#FF9800", "keywords": ["dissolve", "merge", "combine"]},
        {"name": "Reproject", "category": "Coordinate System", "icon": "🌍", "color": "#FF9800", "keywords": ["reproject", "crs", "transform"]},
        {"name": "Intersect", "category": "Vector Overlay", "icon": "⚡", "color": "#FF9800", "keywords": ["intersect", "overlap", "spatial"]},
        {"name": "Join", "category": "Vector Table", "icon": "🔗", "color": "#FF9800", "keywords": ["join", "merge", "attribute"]},
        {"name": "Filter", "category": "Data Processing", "icon": "🔍", "color": "#FF9800", "keywords": ["filter", "select", "where"]},
        {"name": "Calculate Field", "category": "Attributes", "icon": "🧮", "color": "#FF9800", "keywords": ["calculate", "field", "expression"]},
    ],
    "writers": [
        {"name": "Shapefile Writer", "category": "Spatial Writers", "icon": "💾", "color": "#2196F3", "keywords": ["shp", "shapefile", "esri"]},
        {"name": "GeoJSON Writer", "category": "Spatial Writers", "icon": "📤", "color": "#2196F3", "keywords": ["geojson", "json", "web"]},
        {"name": "CSV Writer", "category": "Table Writers", "icon": "📋", "color": "#2196F3", "keywords": ["csv", "table", "export"]},
        {"name": "PostGIS Writer", "category": "Database Writers", "icon": "🗃️", "color": "#2196F3", "keywords": ["postgis", "postgresql", "db"]},
    ]
}

# === CLASSES MODERNES STYLE FME ===

class ModernWorkflowNode(QGraphicsRectItem):
    """Nœud de workflow moderne style FME"""
    
    def __init__(self, node_data, x=0, y=0):
        super().__init__(0, 0, 200, 80)
        self.setPos(x, y)
        self.node_data = node_data
        self.input_ports = []
        self.output_ports = []
        self.is_selected = False
        
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        self.setup_appearance()
        self.create_content()
        self.create_ports()
        
    def setup_appearance(self):
        """Style moderne avec dégradés"""
        color = QColor(self.node_data["color"])
        
        # Dégradé moderne
        gradient = QLinearGradient(0, 0, 0, 80)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(110))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(color.darker(150), 2))
        
    def create_content(self):
        """Contenu visuel du nœud"""
        # Icône
        self.icon_item = QGraphicsTextItem(self.node_data["icon"], self)
        self.icon_item.setPos(8, 8)
        self.icon_item.setFont(QFont("Arial", 14))
        
        # Nom
        self.name_item = QGraphicsTextItem(self.node_data["name"], self)
        self.name_item.setPos(35, 5)
        font = QFont("Arial", 10, QFont.Bold)
        self.name_item.setFont(font)
        self.name_item.setDefaultTextColor(QColor("white"))
        
        # Catégorie
        self.category_item = QGraphicsTextItem(self.node_data["category"], self)
        self.category_item.setPos(8, 45)
        self.category_item.setFont(QFont("Arial", 8))
        self.category_item.setDefaultTextColor(QColor("#f8f9fa"))
        
    def create_ports(self):
        """Créer les ports selon le type de nœud"""
        node_name = self.node_data["name"].lower()
        
        # Readers : sortie seulement
        if "reader" in node_name:
            port = ConnectionPort(-7, 40, "output", "vector", self)
            port.setParentItem(self)
            self.output_ports.append(port)
            
        # Writers : entrée seulement
        elif "writer" in node_name:
            port = ConnectionPort(-7, 40, "input", "vector", self)
            port.setParentItem(self)
            self.input_ports.append(port)
            
        # Transformers : entrée et sortie
        else:
            in_port = ConnectionPort(-7, 40, "input", "vector", self)
            in_port.setParentItem(self)
            self.input_ports.append(in_port)
            
            out_port = ConnectionPort(193, 40, "output", "vector", self)
            out_port.setParentItem(self)
            self.output_ports.append(out_port)
    
    def mousePressEvent(self, event):
        """Gestion de la sélection"""
        if event.button() == Qt.LeftButton:
            self.is_selected = True
            self.update()
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        """Double-clic pour configurer"""
        if event.button() == Qt.LeftButton:
            self.configure_node()
            
    def configure_node(self):
        """Ouvre la configuration du nœud"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        
        dialog = QDialog()
        dialog.setWindowTitle(f"Configuration - {self.node_data['name']}")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Nœud: {self.node_data['name']}"))
        layout.addWidget(QLabel(f"Catégorie: {self.node_data['category']}"))
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

class ModernWorkflowScene(QGraphicsScene):
    """Scène moderne avec grille et interactions fluides"""
    
    node_added = pyqtSignal(object)
    connection_created = pyqtSignal(object, object)
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 3000)
        self.grid_size = 20
        self.show_grid = True
        self.temp_connection = None
        self.connection_start_port = None
        
    def drawBackground(self, painter, rect):
        """Dessine la grille de fond"""
        if not self.show_grid:
            painter.fillRect(rect, QBrush(QColor("#2b2b2b")))
            return
            
        # Fond sombre
        painter.fillRect(rect, QBrush(QColor("#2b2b2b")))
        
        # Grille
        painter.setPen(QPen(QColor("#404040"), 1))
        
        # Lignes verticales
        start_x = int(rect.left() // self.grid_size) * self.grid_size
        while start_x < rect.right():
            painter.drawLine(start_x, rect.top(), start_x, rect.bottom())
            start_x += self.grid_size
            
        # Lignes horizontales  
        start_y = int(rect.top() // self.grid_size) * self.grid_size
        while start_y < rect.bottom():
            painter.drawLine(rect.left(), start_y, rect.right(), start_y)
            start_y += self.grid_size
            
    def add_node_from_data(self, node_data, position):
        """Ajoute un nœud à partir des données"""
        node = ModernWorkflowNode(node_data, position.x(), position.y())
        self.addItem(node)
        self.node_added.emit(node)
        return node
        
    def start_connection(self, port):
        """Démarre la création d'une connexion"""
        self.connection_start_port = port
        
    def mouseMoveEvent(self, event):
        """Gestion du drag & drop et connexions temporaires"""
        if self.connection_start_port:
            # Dessiner ligne temporaire
            if self.temp_connection:
                self.removeItem(self.temp_connection)
                
            start_pos = self.connection_start_port.scenePos() + QPointF(7, 7)
            end_pos = event.scenePos()
            
            self.temp_connection = QGraphicsLineItem(start_pos.x(), start_pos.y(), 
                                                   end_pos.x(), end_pos.y())
            self.temp_connection.setPen(QPen(QColor("#ffc107"), 2, Qt.DashLine))
            self.addItem(self.temp_connection)
            
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Fin de création de connexion"""
        if self.temp_connection:
            self.removeItem(self.temp_connection)
            self.temp_connection = None
            
        if self.connection_start_port:
            # Chercher un port de destination
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, ConnectionPort) and item != self.connection_start_port:
                if self.connection_start_port.can_connect_to(item):
                    connection = Connection(self.connection_start_port, item)
                    self.addItem(connection)
                    self.connection_created.emit(self.connection_start_port, item)
                    
            self.connection_start_port = None
            
        super().mouseReleaseEvent(event)
        
    def toggle_grid(self):
        """Active/désactive la grille"""
        self.show_grid = not self.show_grid
        self.update()

class NodeSearchPanel(QWidget):
    """Panneau de recherche et sélection de nœuds avec auto-complétion"""
    
    node_requested = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_search()
        
    def init_ui(self):
        """Interface du panneau"""
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("📚 Node Library")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: white; padding: 10px;")
        layout.addWidget(title)
        
        # Barre de recherche
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search nodes...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #404040;
                border-radius: 6px;
                background: #3b3b3b;
                color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #ffc107;
            }
        """)
        layout.addWidget(self.search_box)
        
        # Liste des nœuds
        self.node_list = QListWidget()
        self.node_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #404040;
                background: #3b3b3b;
                color: white;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:hover {
                background: #4b4b4b;
            }
            QListWidget::item:selected {
                background: #ffc107;
                color: black;
            }
        """)
        layout.addWidget(self.node_list)
        
        self.setLayout(layout)
        self.setFixedWidth(280)
        self.setStyleSheet("background: #2b2b2b;")
        
    def setup_search(self):
        """Configure la recherche et l'auto-complétion"""
        # Créer la liste de tous les nœuds
        self.all_nodes = []
        for category, nodes in WORKFLOW_NODES.items():
            self.all_nodes.extend(nodes)
            
        # Remplir la liste initiale
        self.populate_list(self.all_nodes)
        
        # Connecter la recherche
        self.search_box.textChanged.connect(self.filter_nodes)
        self.node_list.itemDoubleClicked.connect(self.on_node_selected)
        
        # Drag & Drop
        self.node_list.setDragDropMode(QListWidget.DragOnly)
        
    def populate_list(self, nodes):
        """Remplit la liste avec les nœuds"""
        self.node_list.clear()
        
        for node in nodes:
            item = QListWidgetItem(f"{node['icon']} {node['name']}")
            item.setData(Qt.UserRole, node)
            
            # Couleur selon le type
            color = QColor(node['color'])
            item.setBackground(QBrush(color.darker(300)))
            
            self.node_list.addItem(item)
            
    def filter_nodes(self, text):
        """Filtre les nœuds selon la recherche"""
        if not text:
            self.populate_list(self.all_nodes)
            return
            
        text = text.lower()
        filtered = []
        
        for node in self.all_nodes:
            # Recherche dans nom, catégorie et mots-clés
            searchable = [
                node['name'].lower(),
                node['category'].lower(),
            ] + [kw.lower() for kw in node.get('keywords', [])]
            
            if any(text in field for field in searchable):
                filtered.append(node)
                
        self.populate_list(filtered)
        
    def on_node_selected(self, item):
        """Nœud sélectionné pour ajout"""
        node_data = item.data(Qt.UserRole)
        self.node_requested.emit(node_data)

class ConnectionPort(QGraphicsEllipseItem):
    """Port de connexion amélioré pour les transformers"""
    
    def __init__(self, x, y, port_type="input", data_type="vector", parent_node=None):
        super().__init__(0, 0, 14, 14)
        self.setPos(x, y)
        self.port_type = port_type  # "input" ou "output"
        self.data_type = data_type  # "vector", "raster", "table", "any"
        self.parent_node = parent_node
        self.connections = []
        self.is_connected = False
        
        # Couleurs selon le type de données
        self.colors = {
            "vector": QColor("#28a745"),
            "raster": QColor("#dc3545"), 
            "table": QColor("#ffc107"),
            "any": QColor("#6c757d"),
            "geometry": QColor("#17a2b8"),
            "attribute": QColor("#6f42c1")
        }
        
        self.setup_appearance()
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)
        
    def setup_appearance(self):
        """Configure l'apparence du port"""
        color = self.colors.get(self.data_type, QColor("#6c757d"))
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#ffffff"), 2))
        
        # Effet de brillance
        if self.port_type == "output":
            gradient = QLinearGradient(0, 0, 14, 14)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color.darker(120))
            self.setBrush(QBrush(gradient))
        
    def hoverEnterEvent(self, event):
        """Effet de survol"""
        self.setScale(1.2)
        color = self.colors.get(self.data_type, QColor("#6c757d"))
        self.setBrush(QBrush(color.lighter(150)))
        self.update()
        
    def hoverLeaveEvent(self, event):
        """Fin de survol"""
        self.setScale(1.0)
        self.setup_appearance()
        self.update()
    
    def mousePressEvent(self, event):
        """Début de création de connexion"""
        if event.button() == Qt.LeftButton and self.port_type == "output":
            scene = self.scene()
            if hasattr(scene, 'start_connection'):
                scene.start_connection(self)
        super().mousePressEvent(event)
    
    def can_connect_to(self, other_port):
        """Vérifie si une connexion est possible"""
        if not isinstance(other_port, ConnectionPort):
            return False
        if self.port_type == other_port.port_type:
            return False
        if self.parent_node == other_port.parent_node:
            return False
        
        # Vérification des types de données
        if self.data_type == "any" or other_port.data_type == "any":
            return True
        return self.data_type == other_port.data_type
    
    def add_connection(self, connection):
        """Ajoute une connexion"""
        self.connections.append(connection)
        self.is_connected = True
        self.update_appearance()
    
    def remove_connection(self, connection):
        """Supprime une connexion"""
        if connection in self.connections:
            self.connections.remove(connection)
        self.is_connected = len(self.connections) > 0
        self.update_appearance()
    
    def update_appearance(self):
        """Met à jour l'apparence selon l'état"""
        if self.is_connected:
            self.setPen(QPen(QColor("#28a745"), 3))
        else:
            self.setPen(QPen(QColor("#ffffff"), 2))

class Connection(QGraphicsItem):
    """Connexion améliorée entre deux ports"""
    
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.setZValue(-1)
        self.is_selected = False
        self.animation_offset = 0
        
        # Animation de flux de données
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_flow)
        self.animation_timer.start(50)  # 20 FPS
        
        # Ajouter la connexion aux ports
        start_port.add_connection(self)
        end_port.add_connection(self)
        
    def boundingRect(self):
        start_pos = self.start_port.scenePos() + QPointF(7, 7)  # Centre du port
        end_pos = self.end_port.scenePos() + QPointF(7, 7)
        return QRectF(start_pos, end_pos).normalized().adjusted(-20, -20, 20, 20)
    
    def paint(self, painter, option, widget):
        start_pos = self.start_port.scenePos() + QPointF(7, 7)
        end_pos = self.end_port.scenePos() + QPointF(7, 7)
        
        # Calcul de la courbe Bézier
        distance = abs(end_pos.x() - start_pos.x())
        ctrl_offset = max(50, distance * 0.4)
        
        ctrl1 = QPointF(start_pos.x() + ctrl_offset, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - ctrl_offset, end_pos.y())
        
        # Création du chemin
        path = QPainterPath()
        path.moveTo(start_pos)
        path.cubicTo(ctrl1, ctrl2, end_pos)
        
        # Style de base
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Couleur selon le type de données
        data_type = self.start_port.data_type
        colors = {
            "vector": QColor("#28a745"),
            "raster": QColor("#dc3545"),
            "table": QColor("#ffc107"),
            "any": QColor("#6c757d")
        }
        base_color = colors.get(data_type, QColor("#4A90E2"))
        
        # Ligne principale
        pen = QPen(base_color, 3 if self.is_selected else 2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Animation de flux (points mobiles)
        if hasattr(self, 'animation_offset'):
            flow_pen = QPen(base_color.lighter(150), 6)
            flow_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(flow_pen)
            
            # Dessiner des points le long du chemin
            for i in range(3):
                t = (self.animation_offset + i * 0.3) % 1.0
                point = path.pointAtPercent(t)
                painter.drawPoint(point)
        
        # Flèche à la fin
        self.draw_arrow(painter, path, base_color)
    
    def draw_arrow(self, painter, path, color):
        """Dessine une flèche à la fin de la connexion"""
        if path.length() < 10:
            return
            
        # Position et angle de la flèche
        arrow_pos = path.pointAtPercent(0.95)
        angle = path.angleAtPercent(0.95)
        
        # Créer la flèche - VERSION CORRIGÉE
        arrow_size = 8
        arrow_points = QPolygonF()
        arrow_points.append(QPointF(0, 0))
        arrow_points.append(QPointF(-arrow_size, -arrow_size/2))
        arrow_points.append(QPointF(-arrow_size * 0.6, 0))
        arrow_points.append(QPointF(-arrow_size, arrow_size/2))
        
        # Transformer et dessiner - VERSION CORRIGÉE
        transform = QTransform()
        transform.translate(arrow_pos.x(), arrow_pos.y())
        transform.rotate(-angle)
        
        # S'assurer que c'est un QPolygonF
        transformed_arrow = QPolygonF(transform.map(arrow_points))
        
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(transformed_arrow)
    
    def animate_flow(self):
        """Animation du flux de données"""
        self.animation_offset += 0.05
        if self.animation_offset > 1.0:
            self.animation_offset = 0.0
        self.update()
    
    def mousePressEvent(self, event):
        """Sélection de la connexion"""
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.update()
        elif event.button() == Qt.RightButton:
            # Menu contextuel pour supprimer
            self.show_context_menu(event.screenPos())
    
    def show_context_menu(self, pos):
        """Menu contextuel de la connexion"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        delete_action = menu.addAction("🗑️ Supprimer connexion")
        
        action = menu.exec_(pos.toPoint())
        if action == delete_action:
            self.delete_connection()
    
    def delete_connection(self):
        """Supprime la connexion"""
        self.start_port.remove_connection(self)
        self.end_port.remove_connection(self)
        self.scene().removeItem(self)
        self.animation_timer.stop()

class BaseWorkflowNode(QGraphicsRectItem):
    """Classe de base pour tous les nœuds du workflow"""
    
    def __init__(self, config, x=0, y=0, node_type="transformer"):
        super().__init__(0, 0, 200, 120)
        self.setPos(x, y)
        self.config = config
        self.node_type = node_type
        self.input_ports = []
        self.output_ports = []
        self.is_selected = False
        self.is_running = False
        self.progress = 0
        
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        self.setup_appearance()
        self.create_content()
        self.create_ports()
        
    def setup_appearance(self):
        """Configure l'apparence du nœud"""
        color = QColor(self.config.color)
        
        # Gradient de fond
        gradient = QLinearGradient(0, 0, 0, 100)
        gradient.setColorAt(0, color.lighter(110))
        gradient.setColorAt(1, color.darker(110))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(color.darker(120), 2))
        
        # Coins arrondis
        self.setRect(0, 0, 180, 100)
    
    def create_content(self):
        """Crée le contenu visuel du nœud"""
        # Icône
        self.icon_label = QGraphicsTextItem(self.config.icon, self)
        self.icon_label.setPos(10, 10)
        self.icon_label.setFont(QFont("Arial", 16))
        
        # Titre
        self.title = QGraphicsTextItem(self.config.name, self)
        self.title.setPos(40, 8)
        font = QFont("Arial", 11, QFont.Bold)
        self.title.setFont(font)
        self.title.setDefaultTextColor(QColor("#ffffff"))
        
        # Catégorie
        self.category_label = QGraphicsTextItem(f"📁 {self.config.category}", self)
        self.category_label.setPos(40, 28)
        self.category_label.setFont(QFont("Arial", 9))
        self.category_label.setDefaultTextColor(QColor("#e9ecef"))
        
        # Description
        if len(self.config.description) > 30:
            desc_text = self.config.description[:27] + "..."
        else:
            desc_text = self.config.description
            
        self.desc_label = QGraphicsTextItem(desc_text, self)
        self.desc_label.setPos(10, 50)
        self.desc_label.setFont(QFont("Arial", 8))
        self.desc_label.setDefaultTextColor(QColor("#dee2e6"))
        
        # Barre de progression (initialement cachée)
        self.progress_bar = QGraphicsRectItem(10, 75, 160, 6, self)
        self.progress_bar.setBrush(QBrush(QColor("#e9ecef")))
        self.progress_bar.setPen(QPen(QColor("#dee2e6"), 1))
        self.progress_bar.setVisible(False)
        
        self.progress_fill = QGraphicsRectItem(10, 75, 0, 6, self)
        self.progress_fill.setBrush(QBrush(QColor("#28a745")))
        self.progress_fill.setPen(QPen(Qt.NoPen))
        self.progress_fill.setVisible(False)
    
    def create_ports(self):
        """Crée les ports d'entrée et de sortie"""
        # Ports d'entrée (gauche)
        input_count = len(self.config.input_types) if self.config.input_types else 1
        for i, input_type in enumerate(self.config.input_types or ["vector"]):
            y_pos = 30 + (i * 25)
            port = ConnectionPort(-7, y_pos, "input", input_type, self)
            port.setParentItem(self)
            self.input_ports.append(port)
        
        # Ports de sortie (droite)
        output_count = len(self.config.output_types) if self.config.output_types else 1
        for i, output_type in enumerate(self.config.output_types or ["vector"]):
            y_pos = 30 + (i * 25)
            port = ConnectionPort(173, y_pos, "output", output_type, self)
            port.setParentItem(self)
            self.output_ports.append(port)
    
    def mousePressEvent(self, event):
        """Gestion du clic sur le nœud"""
        if event.button() == Qt.LeftButton:
            self.is_selected = True
            self.update_selection()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.screenPos())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Double-clic pour configuration"""
        if event.button() == Qt.LeftButton:
            self.show_properties_dialog()
    
    def show_context_menu(self, pos):
        """Menu contextuel du nœud"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        config_action = menu.addAction("⚙️ Configurer")
        duplicate_action = menu.addAction("📋 Dupliquer")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(pos.toPoint())
        
        if action == config_action:
            self.show_properties_dialog()
        elif action == duplicate_action:
            self.duplicate_node()
        elif action == delete_action:
            self.delete_node()
    
    def show_properties_dialog(self):
        """Dialogue de configuration du nœud"""
        dialog = TransformerPropertiesDialog(self.config, self.scene().views()[0])
        if dialog.exec_() == QDialog.Accepted:
            # Mettre à jour la configuration
            pass
    
    def duplicate_node(self):
        """Duplique le nœud selon son type"""
        if self.node_type == "reader":
            new_node = ReaderNode(self.config, self.x() + 50, self.y() + 50)
        elif self.node_type == "writer":
            new_node = WriterNode(self.config, self.x() + 50, self.y() + 50)
        else:
            new_node = TransformerNode(self.config, self.x() + 50, self.y() + 50)
        self.scene().addItem(new_node)
    
    def delete_node(self):
        """Supprime le nœud et ses connexions"""
        # Supprimer toutes les connexions
        all_ports = self.input_ports + self.output_ports
        for port in all_ports:
            for connection in port.connections[:]:  # Copie pour éviter modification pendant itération
                connection.delete_connection()
        
        # Supprimer le nœud
        self.scene().removeItem(self)
    
    def update_selection(self):
        """Met à jour l'apparence de sélection"""
        if self.is_selected:
            self.setPen(QPen(QColor("#ffc107"), 3))
        else:
            color = QColor(self.config.color)
            self.setPen(QPen(color.darker(120), 2))
    
    def start_execution(self):
        """Démarre l'animation d'exécution"""
        self.is_running = True
        self.progress = 0
        self.progress_bar.setVisible(True)
        self.progress_fill.setVisible(True)
        
        # Animation de progression
        self.execution_timer = QTimer()
        self.execution_timer.timeout.connect(self.update_progress)
        self.execution_timer.start(100)
    
    def update_progress(self):
        """Met à jour la barre de progression"""
        self.progress += random.randint(1, 10)
        if self.progress >= 100:
            self.progress = 100
            self.execution_timer.stop()
            self.is_running = False
            QTimer.singleShot(1000, self.hide_progress)
        
        width = (self.progress / 100) * 160
        self.progress_fill.setRect(10, 75, width, 6)
    
    def hide_progress(self):
        """Cache la barre de progression"""
        self.progress_bar.setVisible(False)
        self.progress_fill.setVisible(False)
    
    def itemChange(self, change, value):
        """Gestion des changements du nœud"""
        if change == QGraphicsItem.ItemPositionChange:
            # Mettre à jour les connexions
            scene = self.scene()
            if scene:
                scene.update()
        return super().itemChange(change, value)

class TransformerPropertiesDialog(QDialog):
    """Dialogue de propriétés d'un transformer"""
    
    def __init__(self, config: TransformerConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle(f"Propriétés - {config.name}")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout()
        
        # En-tête
        header = QLabel(f"⚙️ Configuration - {self.config.name}")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #495057; margin: 10px 0;")
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Général
        general_tab = QWidget()
        general_layout = QFormLayout()
        
        self.name_edit = QLineEdit(self.config.name)
        self.desc_edit = QTextEdit(self.config.description)
        self.desc_edit.setMaximumHeight(80)
        
        general_layout.addRow("Nom:", self.name_edit)
        general_layout.addRow("Description:", self.desc_edit)
        general_tab.setLayout(general_layout)
        
        # Onglet Paramètres
        params_tab = QWidget()
        params_layout = QVBoxLayout()
        
        self.params_table = QTableWidget()
        self.params_table.setColumnCount(3)
        self.params_table.setHorizontalHeaderLabels(["Paramètre", "Valeur", "Type"])
        self.populate_parameters()
        
        params_layout.addWidget(self.params_table)
        params_tab.setLayout(params_layout)
        
        # Onglet Connexions
        connections_tab = QWidget()
        connections_layout = QVBoxLayout()
        
        # Informations sur les types d'entrée/sortie
        input_types = QLabel(f"Entrées: {', '.join(self.config.input_types) or 'Aucune'}")
        output_types = QLabel(f"Sorties: {', '.join(self.config.output_types) or 'Aucune'}")
        
        connections_layout.addWidget(input_types)
        connections_layout.addWidget(output_types)
        connections_layout.addStretch()
        connections_tab.setLayout(connections_layout)
        
        tabs.addTab(general_tab, "Général")
        tabs.addTab(params_tab, "Paramètres")
        tabs.addTab(connections_tab, "Connexions")
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        
        layout.addWidget(header)
        layout.addWidget(tabs)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def populate_parameters(self):
        """Remplit la table des paramètres"""
        params = self.config.parameters
        self.params_table.setRowCount(len(params))
        
        for i, (key, value) in enumerate(params.items()):
            self.params_table.setItem(i, 0, QTableWidgetItem(key))
            self.params_table.setItem(i, 1, QTableWidgetItem(str(value)))
            self.params_table.setItem(i, 2, QTableWidgetItem(type(value).__name__))
    
    def apply_changes(self):
        """Applique les modifications"""
        self.config.name = self.name_edit.text()
        self.config.description = self.desc_edit.toPlainText()
        # Mettre à jour les paramètres
        for i in range(self.params_table.rowCount()):
            key = self.params_table.item(i, 0).text()
            value = self.params_table.item(i, 1).text()
            self.config.parameters[key] = value

class ReaderNode(BaseWorkflowNode):
    """Nœud Reader professionnel - Lecture de données"""
    
    def __init__(self, config: ReaderConfig, x=0, y=0):
        super().__init__(config, x, y, "reader")
        self.source_path = ""
        self.layer_name = ""
        
    def create_ports(self):
        """Crée uniquement des ports de sortie pour les readers"""
        output_types = self.config.output_types or ["vector", "raster"]
        for i, output_type in enumerate(output_types):
            y_pos = 40 + (i * 30)
            port = ConnectionPort(193, y_pos, "output", output_type, self)
            port.setParentItem(self)
            self.output_ports.append(port)
    
    def create_content(self):
        """Interface spécialisée pour les readers"""
        # Badge Reader
        self.badge = QGraphicsRectItem(10, 10, 80, 25, self)
        self.badge.setBrush(QBrush(QColor("#28a745")))
        self.badge.setPen(QPen(QColor("#ffffff"), 1))
        
        badge_text = QGraphicsTextItem("📁 READER", self)
        badge_text.setPos(12, 12)
        badge_text.setFont(QFont("Arial", 8, QFont.Bold))
        badge_text.setDefaultTextColor(QColor("#ffffff"))
        
        # Titre
        self.title = QGraphicsTextItem(self.config.name, self)
        self.title.setPos(10, 40)
        self.title.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Source type
        source_text = QGraphicsTextItem(f"Source: {self.config.source_type}", self)
        source_text.setPos(10, 65)
        source_text.setFont(QFont("Arial", 9))
        source_text.setDefaultTextColor(QColor("#666"))
        
        # Extensions supportées
        ext_text = ', '.join(self.config.file_extensions[:3])  # Limite à 3
        if len(self.config.file_extensions) > 3:
            ext_text += "..."
        extensions = QGraphicsTextItem(f"Formats: {ext_text}", self)
        extensions.setPos(10, 85)
        extensions.setFont(QFont("Arial", 8))
        extensions.setDefaultTextColor(QColor("#888"))

class TransformerNode(BaseWorkflowNode):
    """Nœud Transformer professionnel - Traitement QGIS"""
    
    def __init__(self, config: TransformerConfig, x=0, y=0):
        super().__init__(config, x, y, "transformer")
        self.algorithm_id = ""
        self.qgis_parameters = {}
        
    def create_content(self):
        """Interface spécialisée pour les transformers"""
        # Badge Transformer
        self.badge = QGraphicsRectItem(10, 10, 100, 25, self)
        self.badge.setBrush(QBrush(QColor("#FF9800")))
        self.badge.setPen(QPen(QColor("#ffffff"), 1))
        
        badge_text = QGraphicsTextItem("⚙️ TRANSFORMER", self)
        badge_text.setPos(12, 12)
        badge_text.setFont(QFont("Arial", 8, QFont.Bold))
        badge_text.setDefaultTextColor(QColor("#ffffff"))
        
        # Titre avec icône
        title_text = f"{self.config.icon} {self.config.name}"
        self.title = QGraphicsTextItem(title_text, self)
        self.title.setPos(10, 40)
        self.title.setFont(QFont("Arial", 11, QFont.Bold))
        
        # Catégorie QGIS
        category = QGraphicsTextItem(f"Catégorie: {self.config.category}", self)
        category.setPos(10, 65)
        category.setFont(QFont("Arial", 9))
        category.setDefaultTextColor(QColor("#666"))
        
        # Description courte
        desc = self.config.description[:40] + "..." if len(self.config.description) > 40 else self.config.description
        description = QGraphicsTextItem(desc, self)
        description.setPos(10, 85)
        description.setFont(QFont("Arial", 8))
        description.setDefaultTextColor(QColor("#888"))
        
        # Barre de progression animée
        self.progress_bg = QGraphicsRectItem(10, 105, 180, 4, self)
        self.progress_bg.setBrush(QBrush(QColor("#e0e0e0")))
        self.progress_bg.setVisible(False)
        
        self.progress_bar = QGraphicsRectItem(10, 105, 0, 4, self)
        self.progress_bar.setBrush(QBrush(QColor("#FF9800")))
        self.progress_bar.setVisible(False)

class WriterNode(BaseWorkflowNode):
    """Nœud Writer professionnel - Écriture de données"""
    
    def __init__(self, config: WriterConfig, x=0, y=0):
        super().__init__(config, x, y, "writer")
        self.output_path = ""
        self.output_format = "shp"
        
    def create_ports(self):
        """Crée uniquement des ports d'entrée pour les writers"""
        input_types = self.config.input_types or ["vector", "raster", "table"]
        for i, input_type in enumerate(input_types):
            y_pos = 40 + (i * 30)
            port = ConnectionPort(-7, y_pos, "input", input_type, self)
            port.setParentItem(self)
            self.input_ports.append(port)
    
    def create_content(self):
        """Interface spécialisée pour les writers"""
        # Badge Writer
        self.badge = QGraphicsRectItem(10, 10, 80, 25, self)
        self.badge.setBrush(QBrush(QColor("#2196F3")))
        self.badge.setPen(QPen(QColor("#ffffff"), 1))
        
        badge_text = QGraphicsTextItem("💾 WRITER", self)
        badge_text.setPos(12, 12)
        badge_text.setFont(QFont("Arial", 8, QFont.Bold))
        badge_text.setDefaultTextColor(QColor("#ffffff"))
        
        # Titre
        self.title = QGraphicsTextItem(self.config.name, self)
        self.title.setPos(10, 40)
        self.title.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Formats de sortie
        formats_text = ', '.join(self.config.output_formats[:3])  # Limite à 3
        if len(self.config.output_formats) > 3:
            formats_text += "..."
        formats = QGraphicsTextItem(f"Formats: {formats_text}", self)
        formats.setPos(10, 65)
        formats.setFont(QFont("Arial", 9))
        formats.setDefaultTextColor(QColor("#666"))
        
        # Status de sauvegarde
        status = QGraphicsTextItem("Prêt à écrire", self)
        status.setPos(10, 85)
        status.setFont(QFont("Arial", 8))
        status.setDefaultTextColor(QColor("#28a745"))

class WorkflowScene(QGraphicsScene):
    """Scène de workflow avancée"""
    
    connection_created = pyqtSignal(object)
    node_selected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 2000, 1500)
        self.connection_start = None
        self.temp_connection_line = None
        self.grid_visible = True
        self.snap_to_grid = True
        self.grid_size = 20
        
    def drawBackground(self, painter, rect):
        """Dessine le fond avec grille"""
        super().drawBackground(painter, rect)
        
        if not self.grid_visible:
            return
        
        # Grille
        painter.setPen(QPen(QColor("#f1f3f4"), 1))
        
        # Lignes verticales
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        for x in range(left, int(rect.right()), self.grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        
        for y in range(top, int(rect.bottom()), self.grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
    
    def start_connection(self, port):
        """Démarre la création d'une connexion"""
        self.connection_start = port
        
        # Ligne temporaire
        start_pos = port.scenePos() + QPointF(7, 7)
        self.temp_connection_line = self.addLine(
            start_pos.x(), start_pos.y(), start_pos.x(), start_pos.y(),
            QPen(QColor("#4A90E2"), 2, Qt.DashLine)
        )
    
    def mouseMoveEvent(self, event):
        """Mise à jour de la ligne temporaire"""
        if self.temp_connection_line and self.connection_start:
            start_pos = self.connection_start.scenePos() + QPointF(7, 7)
            self.temp_connection_line.setLine(
                start_pos.x(), start_pos.y(),
                event.scenePos().x(), event.scenePos().y()
            )
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Finalisation de la connexion"""
        if self.temp_connection_line and self.connection_start:
            # Nettoyer la ligne temporaire
            self.removeItem(self.temp_connection_line)
            self.temp_connection_line = None
            
            # Chercher un port de destination
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, ConnectionPort) and item.port_type == "input":
                if self.connection_start.can_connect_to(item):
                    # Créer la connexion
                    connection = Connection(self.connection_start, item)
                    self.addItem(connection)
                    self.connection_created.emit(connection)
            
            self.connection_start = None
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        """Gestion des raccourcis clavier"""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key_G:
            self.toggle_grid()
        super().keyPressEvent(event)
    
    def delete_selected_items(self):
        """Supprime les éléments sélectionnés"""
        for item in self.selectedItems():
            if isinstance(item, TransformerNode):
                item.delete_node()
            elif isinstance(item, Connection):
                item.delete_connection()
    
    def toggle_grid(self):
        """Active/désactive la grille"""
        self.grid_visible = not self.grid_visible
        self.update()

class WorkflowTestWindow(QMainWindow):
    """Fenêtre principale du Workflow Mapper avancé"""
    
    def __init__(self):
        super().__init__()
        self.transformer_configs = self.load_transformer_configs()
        self.current_file = None
        self.is_modified = False
        
        self.init_ui()
        self.create_sample_workflow()
        self.setup_connections()
        
    def init_ui(self):
        """Interface utilisateur complète"""
        self.setWindowTitle("🔧 Workflow Mapper Avancé - GISENGINE Interface")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Menu principal
        self.create_menu_bar()
        
        # Barre d'outils
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === PANNEAU GAUCHE: Bibliothèque de transformers ===
        self.create_transformer_library()
        
        # === PANNEAU CENTRAL: Canvas de workflow ===
        self.create_workflow_canvas()
        
        # === PANNEAU DROIT: Propriétés et contrôles ===
        self.create_properties_panel()
        
        # Assemblage des panneaux
        main_splitter.addWidget(self.library_panel)
        main_splitter.addWidget(self.canvas_panel)
        main_splitter.addWidget(self.properties_panel)
        main_splitter.setSizes([300, 900, 400])
        
        main_layout.addWidget(main_splitter)
        
        # Barre de statut
        self.create_status_bar()
        
        # Style global amélioré
        self.apply_modern_style()
    
    def create_menu_bar(self):
        """Barre de menu complète"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu('📁 Fichier')
        
        new_action = QAction('🆕 Nouveau', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_workflow)
        
        open_action = QAction('📂 Ouvrir', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_workflow)
        
        save_action = QAction('💾 Enregistrer', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_workflow)
        
        save_as_action = QAction('💾 Enregistrer sous...', self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_workflow_as)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        
        # Menu Édition
        edit_menu = menubar.addMenu('✏️ Édition')
        
        undo_action = QAction('↶ Annuler', self)
        undo_action.setShortcut(QKeySequence.Undo)
        
        redo_action = QAction('↷ Refaire', self)
        redo_action.setShortcut(QKeySequence.Redo)
        
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        
        # Menu Vue
        view_menu = menubar.addMenu('👁️ Vue')
        
        grid_action = QAction('⊞ Grille', self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self.toggle_grid)
        
        zoom_fit_action = QAction('🔍 Ajuster à la fenêtre', self)
        zoom_fit_action.triggered.connect(self.zoom_fit)
        
        view_menu.addAction(grid_action)
        view_menu.addAction(zoom_fit_action)
        
        # Menu Workflow
        workflow_menu = menubar.addMenu('⚙️ Workflow')
        
        validate_action = QAction('✅ Valider', self)
        validate_action.triggered.connect(self.validate_workflow)
        
        execute_action = QAction('▶️ Exécuter', self)
        execute_action.triggered.connect(self.execute_workflow)
        
        workflow_menu.addAction(validate_action)
        workflow_menu.addAction(execute_action)
    
    def create_toolbar(self):
        """Barre d'outils moderne"""
        toolbar = self.addToolBar('Outils')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # Actions principales - SYNTAXE CORRIGÉE
        new_action = QAction('🆕 Nouveau', self)
        new_action.triggered.connect(self.new_workflow)
        
        open_action = QAction('📂 Ouvrir', self)
        open_action.triggered.connect(self.open_workflow)
        
        save_action = QAction('💾 Enregistrer', self)
        save_action.triggered.connect(self.save_workflow)
        
        zoom_in_action = QAction('🔍+ Zoom +', self)
        zoom_in_action.triggered.connect(self.zoom_in)
        
        zoom_out_action = QAction('🔍- Zoom -', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        
        zoom_fit_action = QAction('📐 Ajuster', self)
        zoom_fit_action.triggered.connect(self.zoom_fit)
        
        validate_action = QAction('✅ Valider', self)
        validate_action.triggered.connect(self.validate_workflow)
        
        execute_action = QAction('▶️ Exécuter', self)
        execute_action.triggered.connect(self.execute_workflow)
        
        # Ajouter les actions
        toolbar.addAction(new_action)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(zoom_in_action)
        toolbar.addAction(zoom_out_action)
        toolbar.addAction(zoom_fit_action)
        toolbar.addSeparator()
        toolbar.addAction(validate_action)
        toolbar.addAction(execute_action)
    
    def create_transformer_library(self):
        """Bibliothèque de transformers organisée"""
        self.library_panel = QWidget()
        self.library_panel.setMaximumWidth(350)
        layout = QVBoxLayout()
        
        # En-tête
        header = QLabel("🛠️ Bibliothèque de Transformers")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setStyleSheet("color: #495057; margin: 10px 0;")
        
        # Recherche
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher un transformer...")
        self.search_box.textChanged.connect(self.filter_transformers)
        
        # Arbre des catégories
        self.transformer_tree = QTreeWidget()
        self.transformer_tree.setHeaderLabels(["Transformers"])
        self.populate_transformer_tree()
        self.transformer_tree.itemDoubleClicked.connect(self.add_transformer_from_tree)
        
        # Informations sur le transformer sélectionné
        info_group = QGroupBox("ℹ️ Informations")
        info_layout = QVBoxLayout()
        
        self.transformer_info = QTextEdit()
        self.transformer_info.setMaximumHeight(120)
        self.transformer_info.setReadOnly(True)
        self.transformer_info.setPlainText("Sélectionnez un transformer pour voir ses informations.")
        
        info_layout.addWidget(self.transformer_info)
        info_group.setLayout(info_layout)
        
        layout.addWidget(header)
        layout.addWidget(self.search_box)
        layout.addWidget(self.transformer_tree)
        layout.addWidget(info_group)
        
        self.library_panel.setLayout(layout)
    
    def create_workflow_canvas(self):
        """Zone de canvas principal"""
        self.canvas_panel = QWidget()
        layout = QVBoxLayout()
        
        # En-tête du canvas
        canvas_header = QHBoxLayout()
        
        canvas_title = QLabel("📊 Canvas de Workflow")
        canvas_title.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Contrôles de zoom
        zoom_layout = QHBoxLayout()
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(25, 300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        
        zoom_layout.addWidget(QLabel("Zoom:"))
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(self.zoom_label)
        
        canvas_header.addWidget(canvas_title)
        canvas_header.addStretch()
        canvas_header.addLayout(zoom_layout)
        
        # Scène et vue
        self.scene = WorkflowScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        
        layout.addLayout(canvas_header)
        layout.addWidget(self.view)
        
        self.canvas_panel.setLayout(layout)
    
    def create_properties_panel(self):
        """Panneau de propriétés et contrôles"""
        self.properties_panel = QWidget()
        self.properties_panel.setMaximumWidth(450)
        layout = QVBoxLayout()
        
        # Onglets
        tabs = QTabWidget()
        
        # === Onglet Workflow ===
        workflow_tab = QWidget()
        workflow_layout = QVBoxLayout()
        
        # Statistiques
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QVBoxLayout()
        
        self.node_count_label = QLabel("Nœuds: 0")
        self.connection_count_label = QLabel("Connexions: 0")
        self.status_label = QLabel("Status: ⚠️ Non validé")
        
        stats_layout.addWidget(self.node_count_label)
        stats_layout.addWidget(self.connection_count_label)
        stats_layout.addWidget(self.status_label)
        stats_group.setLayout(stats_layout)
        
        # Actions rapides
        actions_group = QGroupBox("⚡ Actions Rapides")
        actions_layout = QVBoxLayout()
        
        validate_btn = QPushButton("✅ Valider Workflow")
        execute_btn = QPushButton("▶️ Exécuter Workflow")
        clear_btn = QPushButton("🗑️ Vider Canvas")
        
        validate_btn.clicked.connect(self.validate_workflow)
        execute_btn.clicked.connect(self.execute_workflow)
        clear_btn.clicked.connect(self.clear_canvas)
        
        actions_layout.addWidget(validate_btn)
        actions_layout.addWidget(execute_btn)
        actions_layout.addWidget(clear_btn)
        actions_group.setLayout(actions_layout)
        
        workflow_layout.addWidget(stats_group)
        workflow_layout.addWidget(actions_group)
        workflow_layout.addStretch()
        workflow_tab.setLayout(workflow_layout)
        
        # === Onglet Propriétés ===
        properties_tab = QWidget()
        properties_layout = QVBoxLayout()
        
        self.selected_item_info = QTextEdit()
        self.selected_item_info.setReadOnly(True)
        self.selected_item_info.setPlainText("Aucun élément sélectionné.")
        
        properties_layout.addWidget(self.selected_item_info)
        properties_tab.setLayout(properties_layout)
        
        # === Onglet Log ===
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        
        log_header = QHBoxLayout()
        log_title = QLabel("📝 Journal d'Activité")
        clear_log_btn = QPushButton("🗑️ Effacer")
        clear_log_btn.clicked.connect(self.clear_log)
        
        log_header.addWidget(log_title)
        log_header.addStretch()
        log_header.addWidget(clear_log_btn)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        
        log_layout.addLayout(log_header)
        log_layout.addWidget(self.log_text)
        log_tab.setLayout(log_layout)
        
        tabs.addTab(workflow_tab, "Workflow")
        tabs.addTab(properties_tab, "Propriétés")
        tabs.addTab(log_tab, "Log")
        
        layout.addWidget(tabs)
        self.properties_panel.setLayout(layout)
    
    def create_status_bar(self):
        """Barre de statut informative"""
        status_bar = self.statusBar()
        
        # Messages temporaires
        self.status_message = QLabel("Prêt")
        status_bar.addWidget(self.status_message)
        
        # Informations permanentes
        status_bar.addPermanentWidget(QLabel("GISENGINE Workflow Mapper v1.0"))
    
    def apply_modern_style(self):
        """Style moderne pour l'interface"""
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 8px 0;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
                background: white;
            }
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                font-weight: bold;
                color: #495057;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dee2e6, stop:1 #ced4da);
            }
            QTreeWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                selection-background-color: #4A90E2;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                padding: 8px;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-bottom: none;
                border-radius: 6px 6px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid white;
            }
            QGraphicsView {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
            }
        """)
    
    def load_transformer_configs(self):
        """Charge la configuration des transformers"""
        configs = [
            # Transformers Vector
            TransformerConfig(
                "buffer", "Buffer", "Vector Geometry", 
                "Crée une zone tampon autour des géométries",
                "🔲", ["vector"], ["vector"],
                {"distance": 10.0, "segments": 5, "dissolve": False}
            ),
            TransformerConfig(
                "clip", "Clip", "Vector Overlay",
                "Découpe les entités avec un masque",
                "✂️", ["vector", "vector"], ["vector"]
            ),
            TransformerConfig(
                "intersection", "Intersection", "Vector Overlay",
                "Calcule l'intersection entre deux couches",
                "∩", ["vector", "vector"], ["vector"]
            ),
            TransformerConfig(
                "dissolve", "Dissolve", "Vector Geometry",
                "Dissout les géométries adjacentes",
                "🫧", ["vector"], ["vector"]
            ),
            TransformerConfig(
                "merge", "Merge", "Vector General",
                "Fusionne plusieurs couches vectorielles",
                "🔗", ["vector", "vector"], ["vector"]
            ),
            
            # Transformers Raster
            TransformerConfig(
                "raster_calc", "Raster Calculator", "Raster Analysis",
                "Effectue des calculs sur les rasters",
                "🧮", ["raster"], ["raster"],
                {"formula": "A * 2", "no_data": -9999}
            ),
            TransformerConfig(
                "warp", "Warp", "Raster Projections",
                "Reprojette un raster",
                "🔄", ["raster"], ["raster"]
            ),
            TransformerConfig(
                "polygonize", "Polygonize", "Raster Conversion",
                "Convertit un raster en polygones",
                "🔷", ["raster"], ["vector"]
            ),
            
            # Transformers Table
            TransformerConfig(
                "join", "Join Attributes", "Vector Table",
                "Joint des attributs par clé",
                "🔗", ["vector", "table"], ["vector"]
            ),
            TransformerConfig(
                "field_calc", "Field Calculator", "Vector Table",
                "Calcule de nouveaux champs",
                "🧮", ["vector"], ["vector"],
                {"field_name": "new_field", "expression": "area($geometry)"}
            ),
            
            # I/O
            TransformerConfig(
                "input", "Input", "Input/Output",
                "Couche d'entrée",
                "📥", [], ["any"],
                {"source": "", "encoding": "UTF-8"}
            ),
            TransformerConfig(
                "output", "Output", "Input/Output",
                "Couche de sortie",
                "📤", ["any"], [],
                {"destination": "", "format": "GeoJSON"}
            )
        ]
        
        return {config.id: config for config in configs}
    
    def populate_transformer_tree(self):
        """Remplit l'arbre des transformers par catégorie"""
        categories = {}
        
        for config in self.transformer_configs.values():
            if config.category not in categories:
                categories[config.category] = QTreeWidgetItem([config.category])
                self.transformer_tree.addTopLevelItem(categories[config.category])
            
            item = QTreeWidgetItem([f"{config.icon} {config.name}"])
            item.setData(0, Qt.UserRole, config.id)
            item.setToolTip(0, config.description)
            categories[config.category].addChild(item)
        
        # Développer toutes les catégories
        self.transformer_tree.expandAll()
    
    def filter_transformers(self, text):
        """Filtre les transformers selon le texte"""
        for i in range(self.transformer_tree.topLevelItemCount()):
            category = self.transformer_tree.topLevelItem(i)
            category_visible = False
            
            for j in range(category.childCount()):
                child = category.child(j)
                child_text = child.text(0).lower()
                visible = text.lower() in child_text
                child.setHidden(not visible)
                if visible:
                    category_visible = True
            
            category.setHidden(not category_visible)
    
    def add_transformer_from_tree(self, item, column):
        """Ajoute un transformer depuis l'arbre"""
        config_id = item.data(0, Qt.UserRole)
        if config_id and config_id in self.transformer_configs:
            self.add_transformer(config_id)
    
    def add_transformer(self, config_id, x=None, y=None):
        """Ajoute un transformer au canvas"""
        if config_id not in self.transformer_configs:
            return
        
        config = self.transformer_configs[config_id]
        
        # Position aléatoire si non spécifiée
        if x is None:
            x = random.randint(100, 800)
        if y is None:
            y = random.randint(100, 600)
        
        # Créer le nœud
        node = TransformerNode(config, x, y)
        self.scene.addItem(node)
        
        self.update_statistics()
        self.log_action(f"Transformer '{config.name}' ajouté à ({x}, {y})")
        self.set_modified(True)
    
    def setup_connections(self):
        """Configure les connexions de signaux"""
        self.scene.connection_created.connect(self.on_connection_created)
        self.scene.selectionChanged.connect(self.on_selection_changed)
    
    def on_connection_created(self, connection):
        """Appelé lors de la création d'une connexion"""
        self.update_statistics()
        self.log_action("Nouvelle connexion créée")
        self.set_modified(True)
    
    def on_selection_changed(self):
        """Appelé lors du changement de sélection"""
        selected_items = self.scene.selectedItems()
        if len(selected_items) == 1:
            item = selected_items[0]
            if isinstance(item, TransformerNode):
                self.show_node_properties(item)
            elif isinstance(item, Connection):
                self.show_connection_properties(item)
        else:
            self.selected_item_info.setPlainText(
                f"{len(selected_items)} éléments sélectionnés."
            )
    
    def show_node_properties(self, node):
        """Affiche les propriétés d'un nœud"""
        config = node.config
        info = f"""
Transformer: {config.name}
Catégorie: {config.category}
Description: {config.description}

Entrées: {', '.join(config.input_types) or 'Aucune'}
Sorties: {', '.join(config.output_types) or 'Aucune'}

Paramètres:
"""
        for key, value in config.parameters.items():
            info += f"  • {key}: {value}\n"
        
        self.selected_item_info.setPlainText(info.strip())
    
    def show_connection_properties(self, connection):
        """Affiche les propriétés d'une connexion"""
        start_node = connection.start_port.parent_node
        end_node = connection.end_port.parent_node
        data_type = connection.start_port.data_type
        
        info = f"""
Connexion
Type de données: {data_type}

Source: {start_node.config.name}
Destination: {end_node.config.name}
"""
        self.selected_item_info.setPlainText(info.strip())
    
    def create_sample_workflow(self):
        """Crée un workflow d'exemple"""
        # Nœud d'entrée
        input_node = TransformerNode(self.transformer_configs["input"], 100, 200)
        self.scene.addItem(input_node)
        
        # Buffer
        buffer_node = TransformerNode(self.transformer_configs["buffer"], 350, 200)
        self.scene.addItem(buffer_node)
        
        # Dissolve
        dissolve_node = TransformerNode(self.transformer_configs["dissolve"], 600, 200)
        self.scene.addItem(dissolve_node)
        
        # Sortie
        output_node = TransformerNode(self.transformer_configs["output"], 850, 200)
        self.scene.addItem(output_node)
        
        # Connexions
        connection1 = Connection(input_node.output_ports[0], buffer_node.input_ports[0])
        self.scene.addItem(connection1)
        
        connection2 = Connection(buffer_node.output_ports[0], dissolve_node.input_ports[0])
        self.scene.addItem(connection2)
        
        connection3 = Connection(dissolve_node.output_ports[0], output_node.input_ports[0])
        self.scene.addItem(connection3)
        
        self.update_statistics()
        self.log_action("Workflow d'exemple créé")
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        nodes = [item for item in self.scene.items() if isinstance(item, TransformerNode)]
        connections = [item for item in self.scene.items() if isinstance(item, Connection)]
        
        self.node_count_label.setText(f"Nœuds: {len(nodes)}")
        self.connection_count_label.setText(f"Connexions: {len(connections)}")
        
        # Validation simple
        if len(nodes) > 0 and len(connections) > 0:
            self.status_label.setText("Status: ✅ Workflow valide")
        elif len(nodes) > 0:
            self.status_label.setText("Status: ⚠️ Nœuds sans connexions")
        else:
            self.status_label.setText("Status: ❌ Workflow vide")
    
    def log_action(self, action):
        """Ajoute une action au journal"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {action}")
    
    def clear_log(self):
        """Efface le journal"""
        self.log_text.clear()
    
    def set_modified(self, modified):
        """Marque le workflow comme modifié"""
        self.is_modified = modified
        title = "🔧 Workflow Mapper Avancé"
        if self.current_file:
            title += f" - {self.current_file}"
        if modified:
            title += " *"
        self.setWindowTitle(title)
    
    # === Méthodes d'interface ===
    
    def new_workflow(self):
        """Nouveau workflow"""
        if self.is_modified:
            # Demander sauvegarde
            pass
        
        self.scene.clear()
        self.current_file = None
        self.set_modified(False)
        self.log_action("Nouveau workflow créé")
    
    def open_workflow(self):
        """Ouvre un workflow"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un workflow", "", "Workflow Files (*.json)"
        )
        if filename:
            self.load_workflow(filename)
    
    def save_workflow(self):
        """Enregistre le workflow"""
        if self.current_file:
            self.save_workflow_to_file(self.current_file)
        else:
            self.save_workflow_as()
    
    def save_workflow_as(self):
        """Enregistre le workflow sous un nouveau nom"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le workflow", "", "Workflow Files (*.json)"
        )
        if filename:
            self.save_workflow_to_file(filename)
    
    def load_workflow(self, filename):
        """Charge un workflow depuis un fichier"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Charger les nœuds et connexions
            # TODO: Implémenter le chargement
            
            self.current_file = filename
            self.set_modified(False)
            self.log_action(f"Workflow chargé: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger le workflow:\n{e}")
    
    def save_workflow_to_file(self, filename):
        """Sauvegarde le workflow dans un fichier"""
        try:
            # Serialiser les nœuds et connexions
            # TODO: Implémenter la sauvegarde
            
            workflow_data = {
                "version": "1.0",
                "nodes": [],
                "connections": []
            }
            
            with open(filename, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            self.current_file = filename
            self.set_modified(False)
            self.log_action(f"Workflow sauvegardé: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder:\n{e}")
    
    def validate_workflow(self):
        """Valide le workflow"""
        nodes = [item for item in self.scene.items() if isinstance(item, TransformerNode)]
        connections = [item for item in self.scene.items() if isinstance(item, Connection)]
        
        errors = []
        warnings = []
        
        # Vérifications de base
        if not nodes:
            errors.append("Aucun transformer dans le workflow")
        
        # Nœuds sans connexions
        isolated_nodes = []
        for node in nodes:
            has_connections = False
            for port in node.input_ports + node.output_ports:
                if port.connections:
                    has_connections = True
                    break
            if not has_connections:
                isolated_nodes.append(node.config.name)
        
        if isolated_nodes:
            warnings.append(f"Nœuds isolés: {', '.join(isolated_nodes)}")
        
        # Affichage des résultats
        if errors:
            QMessageBox.critical(self, "Erreurs de validation", "\n".join(errors))
        elif warnings:
            QMessageBox.warning(self, "Avertissements", "\n".join(warnings))
        else:
            QMessageBox.information(self, "Validation", "✅ Workflow valide !")
        
        self.log_action("Validation du workflow effectuée")
    
    def execute_workflow(self):
        """Exécute le workflow"""
        # Animation d'exécution
        nodes = [item for item in self.scene.items() if isinstance(item, TransformerNode)]
        
        if not nodes:
            QMessageBox.information(self, "Exécution", "Aucun transformer à exécuter")
            return
        
        # Lancer l'animation sur tous les nœuds
        for node in nodes:
            node.start_execution()
        
        self.log_action("Exécution du workflow démarrée")
        
        # Simulation de fin d'exécution
        QTimer.singleShot(5000, lambda: self.log_action("Exécution terminée"))
    
    def clear_canvas(self):
        """Vide le canvas"""
        reply = QMessageBox.question(
            self, "Vider le canvas", 
            "Êtes-vous sûr de vouloir supprimer tous les éléments ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.scene.clear()
            self.update_statistics()
            self.log_action("Canvas vidé")
            self.set_modified(True)
    
    def toggle_grid(self):
        """Active/désactive la grille"""
        self.scene.toggle_grid()
        self.log_action(f"Grille {'activée' if self.scene.grid_visible else 'désactivée'}")
    
    def zoom_in(self):
        """Zoom avant"""
        self.view.scale(1.25, 1.25)
        self.update_zoom_display()
    
    def zoom_out(self):
        """Zoom arrière"""
        self.view.scale(0.8, 0.8)
        self.update_zoom_display()
    
    def zoom_fit(self):
        """Ajuste le zoom pour voir tout le contenu"""
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.update_zoom_display()
    
    def on_zoom_changed(self, value):
        """Appelé lors du changement de zoom via le slider"""
        factor = value / 100.0
        transform = QTransform()
        transform.scale(factor, factor)
        self.view.setTransform(transform)
        self.zoom_label.setText(f"{value}%")
    
    def update_zoom_display(self):
        """Met à jour l'affichage du zoom"""
        transform = self.view.transform()
        zoom_percent = int(transform.m11() * 100)
        self.zoom_slider.setValue(zoom_percent)
        self.zoom_label.setText(f"{zoom_percent}%")

def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Palette sombre optionnelle
    app.setApplicationName("Workflow Mapper")
    app.setApplicationVersion("1.0")
    
    window = WorkflowTestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
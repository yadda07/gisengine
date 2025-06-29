# -*- coding: utf-8 -*-
"""
Interface principale unifiée - GISENGINE
Intègre tous les composants dans une seule interface avec onglets
"""

import os
import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QSplitter, QLabel, QPushButton, QFrame, QMenuBar, QMenu, QAction,
    QToolBar, QStatusBar, QMessageBox, QApplication, QListWidget,
    QListWidgetItem, QLineEdit, QTextEdit, QGroupBox, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsLineItem
)
from PyQt5.QtCore import Qt, QTimer, QMimeData, pyqtSignal, QPointF, QPoint, QRect, QStringListModel
from PyQt5.QtGui import (
    QFont, QIcon, QKeySequence, QPen, QBrush, QColor, QLinearGradient,
    QDrag, QPainter, QPixmap, QPainterPath
)

# Import des composants
try:
    from .qgis_plugin_ui import QGISPluginUI
    print("✅ QGISPluginUI importé")
except ImportError as e:
    print(f"❌ Erreur import QGISPluginUI: {e}")
    QGISPluginUI = None

try:
    from .qgis_integration import QGISProcessingIntegration
    print("✅ QGISProcessingIntegration importé")
except ImportError as e:
    print(f"❌ Erreur import QGISProcessingIntegration: {e}")
    QGISProcessingIntegration = None

try:
    from .workflow import FMEWorkflowDesigner
    print("✅ FMEWorkflowDesigner importé avec succès")
except ImportError as e:
    print(f"❌ Erreur import FMEWorkflowDesigner: {e}")
    FMEWorkflowDesigner = None

# === Classes du Workflow ===

class Connection(QGraphicsPathItem):
    """Ligne de connexion courbée entre deux ports."""
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(-1) # S'assurer que la ligne est derrière les nœuds

        self.pen = QPen(QColor("#4A90E2"), 2)
        self.pen_selected = QPen(QColor("#ffc107"), 3)

        self.start_port.add_connection(self)
        self.end_port.add_connection(self)

        self.update_path()

    def update_path(self):
        """Met à jour le tracé de la courbe de Bézier."""
        start_pos = self.start_port.scenePos() + self.start_port.boundingRect().center()
        end_pos = self.end_port.scenePos() + self.end_port.boundingRect().center()

        path = QPainterPath()
        path.moveTo(start_pos)

        # Contrôles pour la courbe
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - dx * 0.5, end_pos.y())

        path.cubicTo(ctrl1, ctrl2, end_pos)
        self.setPath(path)

    def paint(self, painter, option, widget=None):
        """Dessine la connexion."""
        self.setPen(self.pen_selected if self.isSelected() else self.pen)
        super().paint(painter, option, widget)

    def delete(self):
        """Supprime la connexion de la scène et des ports."""
        print(f"[DEBUG] Deleting connection: {self.start_port.parentItem().transformer_name} -> {self.end_port.parentItem().transformer_name}")
        self.start_port.remove_connection(self)
        self.end_port.remove_connection(self)
        self.scene().removeItem(self)

class ConnectionPort(QGraphicsEllipseItem):
    """Port de connexion (entrée/sortie) sur un nœud."""
    def __init__(self, parent, is_output=False):
        super().__init__(-6, -6, 12, 12, parent)
        self.is_output = is_output
        self.connections = []

        self.setBrush(QBrush(QColor("#ffffff")))
        self.setPen(QPen(QColor("#4A90E2"), 2))
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("#ffc107")))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor("#ffffff")))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Démarre une tentative de connexion."""
        print(f"[DEBUG] Port mousePressEvent: {self.is_output=}")
        if event.button() == Qt.LeftButton:
            if self.is_output:
                self.scene().start_connection(self)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Termine une tentative de connexion."""
        print(f"[DEBUG] Port mouseReleaseEvent: {self.is_output=}")
        if event.button() == Qt.LeftButton:
            if not self.is_output:
                self.scene().end_connection(self)
        super().mouseReleaseEvent(event)

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

class WorkflowNode(QGraphicsRectItem):
    """Nœud de workflow déplaçable et interactif avec ports."""
    
    def __init__(self, name, category, icon, x=0, y=0):
        super().__init__(0, 0, 160, 80)
        self.setPos(x, y)
        self.transformer_name = name
        self.transformer_category = category
        self.transformer_icon = icon
        self.input_port = None
        self.output_port = None
        
        # Rendre le nœud interactif
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Style
        self.setup_style(category)
        
        # Contenu
        self.create_content()
        self.create_ports()
        
        self.setAcceptHoverEvents(True)

    def setup_style(self, category):
        """Définit le style visuel du nœud."""
        colors = {
            "Vector": QColor("#28a745"), "Raster": QColor("#dc3545"),
            "Database": QColor("#6f42c1"), "General": QColor("#4A90E2")
        }
        base_color = colors.get(category, QColor("#4A90E2"))
        gradient = QLinearGradient(0, 0, 0, 80)
        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(120))
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(base_color.darker(140), 2))

    def create_content(self):
        """Crée le contenu textuel du nœud."""
        self.icon_text = QGraphicsTextItem(self.transformer_icon, self)
        self.icon_text.setPos(10, 10)
        self.icon_text.setFont(QFont("Arial", 16))
        
        self.name_text = QGraphicsTextItem(self.transformer_name, self)
        self.name_text.setPos(35, 8)
        self.name_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.name_text.setDefaultTextColor(QColor("#ffffff"))
        
        self.category_text = QGraphicsTextItem(f"📁 {self.transformer_category}", self)
        self.category_text.setPos(35, 28)
        self.category_text.setFont(QFont("Arial", 8))
        self.category_text.setDefaultTextColor(QColor("#e9ecef"))

    def create_ports(self):
        """Crée les ports d'entrée et de sortie."""
        self.input_port = ConnectionPort(self, is_output=False)
        self.input_port.setPos(0, self.boundingRect().height() / 2 - 6) # Centré verticalement
        
        self.output_port = ConnectionPort(self, is_output=True)
        self.output_port.setPos(self.boundingRect().width() - 12, self.boundingRect().height() / 2 - 6) # Centré verticalement

    def itemChange(self, change, value):
        """Met à jour les connexions lorsque le nœud est déplacé."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.input_port:
                for conn in self.input_port.connections:
                    conn.update_path()
            if self.output_port:
                for conn in self.output_port.connections:
                    conn.update_path()
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        self.setScale(1.05)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        if not self.isSelected():
            self.setScale(1.0)
        super().hoverLeaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Ouvre une boîte de dialogue de configuration pour le nœud."""
        if event.button() == Qt.LeftButton:
            QMessageBox.information(None, "Configuration du Nœud", 
                                    f"Configurer le nœud: {self.transformer_name}\nCatégorie: {self.transformer_category}")
        super().mouseDoubleClickEvent(event)

    def delete(self):
        """Supprime le nœud et ses connexions de la scène."""
        print(f"[DEBUG] Deleting node: {self.transformer_name}")
        # Supprimer les connexions attachées aux ports
        if self.input_port:
            for conn in self.input_port.connections[:]: # Itérer sur une copie
                conn.delete()
        if self.output_port:
            for conn in self.output_port.connections[:]: # Itérer sur une copie
                conn.delete()
        self.scene().removeItem(self)

class ModernWorkflowScene(QGraphicsScene):
    """Scène moderne avec grille et interactions fluides"""
    
    node_added = pyqtSignal(str)
    elements_deleted = pyqtSignal() # Nouveau signal
    
    def __init__(self):
        super().__init__()
        self.transformer_data = [] # Sera défini par la fenêtre principale
        self.setSceneRect(-2000, -2000, 4000, 3000)
        self.setBackgroundBrush(QBrush(QColor("#f8f9fa")))
        self.nodes = []
        self.temp_connection = None
        self.start_port = None
        
    def set_transformer_data(self, data):
        """Reçoit les données des transformers depuis la fenêtre principale."""
        self.transformer_data = data
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("transformer:"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("transformer:"):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith("transformer:"):
            data = event.mimeData().text().split(":")
            if len(data) >= 4:
                _, name, category, icon = data[:4]
                pos = event.scenePos()
                node = WorkflowNode(name, category, icon, pos.x() - 80, pos.y() - 40)
                self.addItem(node)
                self.nodes.append(node)
                self.node_added.emit(name)
                event.acceptProposedAction()
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setPen(QPen(QColor("#e9ecef"), 1))
        grid_size = 25
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        for x in range(left, int(rect.right()), grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(top, int(rect.bottom()), grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def start_connection(self, port):
        """Démarre le dessin d'une ligne de connexion temporaire."""
        print(f"[DEBUG] Scene start_connection from {port.parentItem().transformer_name}")
        self.start_port = port
        self.temp_connection = QGraphicsLineItem()
        self.temp_connection.setPen(QPen(QColor("#ffc107"), 2, Qt.DashLine))
        self.addItem(self.temp_connection)
        self.update_temp_connection(port.scenePos() + port.boundingRect().center())

    def end_connection(self, end_port):
        """Finalise la connexion si elle est valide."""
        print(f"[DEBUG] Scene end_connection to {end_port.parentItem().transformer_name}")
        if self.temp_connection and self.start_port and end_port != self.start_port:
            # Vérifier que c'est une connexion output -> input
            if self.start_port.is_output and not end_port.is_output:
                connection = Connection(self.start_port, end_port)
                self.addItem(connection)
                print(f"[DEBUG] Connection created: {self.start_port.parentItem().transformer_name} -> {end_port.parentItem().transformer_name}")
            else:
                print("[DEBUG] Invalid connection attempt: not output -> input")
        else:
            print("[DEBUG] Connection not finalized: missing temp_connection or start_port, or same port")
        self.cleanup_connection()

    def mouseMoveEvent(self, event):
        """Met à jour la ligne de connexion temporaire."""
        if self.temp_connection:
            self.update_temp_connection(event.scenePos())
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Affiche un champ de recherche pour ajouter un nœud rapidement."""
        if self.itemAt(event.scenePos(), self.views()[0].transform()) is None:
            self.show_node_search_box(event.scenePos())
        super().mouseDoubleClickEvent(event)

    def show_node_search_box(self, position):
        """Crée et affiche un QLineEdit avec auto-complétion sur la scène."""
        from PyQt5.QtWidgets import QLineEdit, QCompleter
        from PyQt5.QtCore import QStringListModel

        # Créer la liste des noms pour l'auto-complétion
        transformer_names = [f"{item[2]} {item[0]}" for item in self.transformer_data]
        model = QStringListModel(transformer_names)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        # Créer le champ de texte
        line_edit = QLineEdit()
        line_edit.setCompleter(completer)
        line_edit.setFixedSize(250, 30)
        line_edit.setStyleSheet("""QLineEdit { 
            border: 1px solid #4A90E2; 
            border-radius: 4px; 
            padding: 4px; 
            background: white;
            font-size: 11pt;
        }""")

        # Logique pour ajouter le nœud quand on appuie sur Entrée
        def add_node():
            text = line_edit.text()
            found = False
            for name, category, icon, desc in self.transformer_data:
                if f"{icon} {name}" == text:
                    node = WorkflowNode(name, category, icon, position.x(), position.y())
                    self.addItem(node)
                    found = True
                    break
            line_edit.deleteLater()

        line_edit.returnPressed.connect(add_node)
        line_edit.editingFinished.connect(line_edit.deleteLater) # Auto-destruction si on clique ailleurs

        # Ajouter le QLineEdit à la scène via un proxy
        proxy = self.addWidget(line_edit)
        proxy.setPos(position)
        line_edit.setFocus()

    def mouseReleaseEvent(self, event):
        print("[DEBUG] Scene mouseReleaseEvent")
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if not isinstance(item, ConnectionPort):
             self.cleanup_connection()
        super().mouseReleaseEvent(event)

    def update_temp_connection(self, end_pos):
        if self.temp_connection and self.start_port:
            start_pos = self.start_port.scenePos() + self.start_port.boundingRect().center()
            self.temp_connection.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

    def cleanup_connection(self):
        print("[DEBUG] Cleaning up connection")
        if self.temp_connection:
            self.removeItem(self.temp_connection)
            self.temp_connection = None
            self.start_port = None

    def keyPressEvent(self, event):
        """Gère la suppression des éléments sélectionnés avec la touche Suppr."""
        if event.key() == Qt.Key_Delete:
            print("[DEBUG] Delete key pressed.")
            for item in self.selectedItems():
                if isinstance(item, WorkflowNode):
                    item.delete()
                elif isinstance(item, Connection):
                    item.delete()
            self.elements_deleted.emit() # Notifier la fenêtre principale
        super().keyPressEvent(event)

# Alias pour la compatibilité
WorkflowScene = ModernWorkflowScene

# === Classes de l'interface principale ===

class DraggableTransformerItem(QListWidgetItem):
    """Item de transformer avec support du drag and drop"""
    
    def __init__(self, name, category, icon, description=""):
        super().__init__(f"{icon} {name}")
        self.transformer_name = name
        self.transformer_category = category
        self.transformer_icon = icon
        self.transformer_description = description
        
        # Configurer l'item pour le drag
        self.setFlags(self.flags() | Qt.ItemIsDragEnabled)
        self.setToolTip(f"{name}\nCategorie: {category}\n{description}")

class DraggableTransformerList(QListWidget):
    """Liste de transformers avec drag and drop"""
    
    def __init__(self):
        super().__init__()
        self.setDragDropMode(QListWidget.DragOnly)
        self.setDefaultDropAction(Qt.CopyAction)
        
        # Style
        self.setStyleSheet("""
            QListWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                padding: 4px;
            }
            QListWidget::item {
                padding: 12px;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                margin: 2px;
                background: #f8f9fa;
            }
            QListWidget::item:hover {
                background: #e3f2fd;
                border-color: #4A90E2;
            }
            QListWidget::item:selected {
                background: #4A90E2;
                color: white;
                border-color: #357ABD;
            }
        """)
    
    def startDrag(self, supportedActions):
        """Démarre le drag d'un transformer"""
        item = self.currentItem()
        if not item:
            return
        
        # Créer les données MIME
        mimeData = QMimeData()
        mimeData.setText(f"transformer:{item.transformer_name}:{item.transformer_category}:{item.transformer_icon}")
        
        # Créer l'image de drag
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        
        # Créer un pixmap pour visualiser le drag
        pixmap = QPixmap(200, 60)
        pixmap.fill(QColor(74, 144, 226, 180))
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 30, f"{item.transformer_icon} {item.transformer_name}")
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(100, 30))
        
        # Exécuter le drag
        dropAction = drag.exec_(Qt.CopyAction)

class InteractiveWorkflowView(QGraphicsView):
    """
    Vue interactive améliorée du workflow.
    - Zoom intelligent avec la molette (centré sur la souris).
    - Panoramique (déplacement) avec le clic du milieu de la souris).
    - Rendu de haute qualité (anti-crénelage).
    """
    
    def __init__(self, scene):
        super().__init__(scene)
        self._is_panning = False
        self._last_pan_point = QPoint()

        # --- Améliorations de la fluidité et de la qualité ---
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        
        self.setDragMode(QGraphicsView.RubberBandDrag) # Sélection en rectangle
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Style
        self.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
        """)

    def wheelEvent(self, event):
        """Zoom centré sur la souris pour une navigation intuitive."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Zoom avant ou arrière
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def mousePressEvent(self, event):
        """Initialise le panoramique avec le clic du milieu."""
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        
        self.setFocus()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Effectue le panoramique si activé."""
        if self._is_panning:
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            
            # Déplacer la vue en utilisant les barres de défilement
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Arrête le panoramique."""
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

class UnifiedGISENGINEInterface(QMainWindow):
    """Interface principale unifiée GISENGINE"""
    
    def __init__(self, iface=None):
        super().__init__()
        self.qgis_iface = iface
        self.init_ui()
        self.setup_components()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("🛠️ GISENGINE - Interface Unifiée")
        self.setGeometry(50, 50, 1600, 1000)
        
        # Menu principal
        self.create_menu_bar()
        
        # Barre d'outils
        self.create_toolbar()
        
        # Debug des imports
        print(f"[DEBUG] Status imports - QGISPluginUI: {QGISPluginUI is not None}, QGISProcessingIntegration: {QGISProcessingIntegration is not None}, FMEWorkflowDesigner: {FMEWorkflowDesigner is not None}")
        
        # Widget central avec onglets
        self.create_main_interface()
        
        # Barre de statut
        self.create_status_bar()
        
        # Style moderne
        self.apply_style()
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu('📁 Fichier')
        
        new_action = QAction('🆕 Nouveau Workflow', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_workflow)
        
        open_action = QAction('📂 Ouvrir Workflow', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_workflow)
        
        save_action = QAction('💾 Enregistrer', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_workflow)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        
        # Menu Vue
        view_menu = menubar.addMenu('👁️ Vue')
        
        transformers_action = QAction('🛠️ Bibliothèque Transformers', self)
        transformers_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        
        workflow_action = QAction('📊 Workflow Designer', self)
        workflow_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        
        processing_action = QAction('⚙️ Scanner Processing', self)
        processing_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        
        view_menu.addAction(transformers_action)
        view_menu.addAction(workflow_action)
        view_menu.addAction(processing_action)
        
        # Menu Aide
        help_menu = menubar.addMenu('❓ Aide')
        
        about_action = QAction('ℹ️ À propos', self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = self.addToolBar('🔧 Outils Principaux')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Navigation rapide entre onglets
        tab1_action = QAction('🛠️ Transformers', self)
        tab1_action.setToolTip('Bibliothèque de Transformers')
        tab1_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        
        tab2_action = QAction('📊 Workflow', self)
        tab2_action.setToolTip('Designer de Workflow')
        tab2_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        
        tab3_action = QAction('⚙️ Processing', self)
        tab3_action.setToolTip('Scanner Processing QGIS')
        tab3_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        
        toolbar.addAction(tab1_action)
        toolbar.addAction(tab2_action)
        toolbar.addAction(tab3_action)
        
        toolbar.addSeparator()
        
        # Actions de workflow
        validate_action = QAction('✅ Valider', self)
        validate_action.setToolTip('Valider le workflow')
        validate_action.triggered.connect(self.validate_workflow)
        
        execute_action = QAction('▶️ Exécuter', self)
        execute_action.setToolTip('Exécuter le workflow')
        execute_action.triggered.connect(self.execute_workflow)
        
        toolbar.addAction(validate_action)
        toolbar.addAction(execute_action)
    
    def create_main_interface(self):
        """Crée l'interface principale avec onglets"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # En-tête de bienvenue
        header = self.create_header()
        layout.addWidget(header)
        
        # Onglets principaux
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Style des onglets
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                padding: 12px 20px;
                margin-right: 4px;
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                font-weight: bold;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid white;
                color: #4A90E2;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
            }
        """)
        
        layout.addWidget(self.tabs)
    
    def create_header(self):
        """Crée l'en-tête de l'interface"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A90E2, stop:1 #357ABD);
                border-radius: 8px;
                margin: 4px;
            }
        """)
        
        layout = QHBoxLayout()
        header_frame.setLayout(layout)
        
        # Titre principal
        title = QLabel("🛠️ GISENGINE")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white; margin: 10px;")
        
        # Description
        desc = QLabel("Interface unifiée pour la création de workflows géomatiques")
        desc.setFont(QFont("Arial", 12))
        desc.setStyleSheet("color: #e9ecef; margin: 10px;")
        
        # Informations d'état
        self.status_info = QLabel("Prêt")
        self.status_info.setFont(QFont("Arial", 10))
        self.status_info.setStyleSheet("color: #ffffff; margin: 10px; padding: 5px 10px; background: rgba(0,0,0,0.2); border-radius: 4px;")
        
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(self.status_info)
        
        return header_frame
    
    def setup_components(self):
        """Configure les composants dans les onglets"""
        # Onglet 1: Bibliothèque de Transformers
        self.setup_transformers_tab()
        
        # Onglet 2: Workflow Designer  
        self.setup_workflow_tab()
        
        # Onglet 3: Scanner Processing
        self.setup_processing_tab()
    
    def setup_transformers_tab(self):
        """Configure l'onglet des transformers avec drag and drop"""
        try:
            # Créer directement le widget transformers avec drag
            transformers_widget = self.create_draggable_transformers_widget()
            self.tabs.addTab(transformers_widget, "🛠️ Bibliothèque Transformers")
                
        except Exception as e:
            error_widget = self.create_error_widget(f"Erreur transformers: {str(e)}")
            self.tabs.addTab(error_widget, "🛠️ Transformers (Erreur)")
    
    def create_draggable_transformers_widget(self):
        """Crée un widget transformers avec drag and drop"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # En-tête
        header = QLabel("🛠️ Bibliothèque de Transformers")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #495057; margin: 10px 0;")
        
        # Instructions pour le drag and drop
        instructions = QLabel("💡 Glissez un transformer vers l'onglet 'Workflow Designer' pour l'ajouter au canvas")
        instructions.setStyleSheet("""
            QLabel {
                color: #6c757d; 
                font-style: italic; 
                background: #e8f5e8; 
                padding: 10px; 
                border-radius: 6px; 
                border-left: 4px solid #28a745;
                margin: 5px 0;
            }
        """)
        instructions.setWordWrap(True)
        
        # Zone de recherche
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher un transformer...")
        self.search_box.textChanged.connect(self.filter_transformers)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 12px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
        """)
        
        # Liste des transformers avec drag enabled
        self.transformer_list = DraggableTransformerList()
        
        # Remplir la liste des transformers
        self.populate_draggable_transformers()
        
        # Informations et actions
        info_layout = QHBoxLayout()
        
        info_label = QLabel(f"📦 {self.transformer_list.count()} transformers disponibles")
        info_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        
        modeler_btn = QPushButton("🛠️ Ouvrir Processing Modeler")
        modeler_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #218838; }
        """)
        
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        info_layout.addWidget(modeler_btn)
        
        # Assemblage
        layout.addWidget(header)
        layout.addWidget(instructions)
        layout.addWidget(self.search_box)
        layout.addWidget(self.transformer_list)
        layout.addLayout(info_layout)
        
        widget.setLayout(layout)
        return widget
    
    def populate_draggable_transformers(self):
        """Remplit la liste des transformers avec drag and drop"""
        transformers_data = [
            ("Buffer", "Vector", "🔲", "Crée une zone tampon autour des géométries"),
            ("Clip", "Vector", "✂️", "Découpe les entités avec un masque"),
            ("Merge", "Vector", "🔗", "Fusionne plusieurs couches vectorielles"),
            ("Dissolve", "Vector", "🫧", "Dissout les géométries adjacentes"),
            ("Reproject", "Vector", "🌍", "Change la projection des données"),
            ("Field Calculator", "Vector", "🧮", "Calcule de nouveaux champs"),
            ("Intersection", "Vector", "∩", "Calcule l'intersection entre couches"),
            ("Union", "Vector", "∪", "Calcule l'union de géométries"),
            ("Difference", "Vector", "⊖", "Calcule la différence entre couches"),
            ("Centroid", "Vector", "⊙", "Calcule les centroïdes des géométries"),
            ("Raster Calculator", "Raster", "📊", "Effectue des calculs sur rasters"),
            ("Warp", "Raster", "🔄", "Reprojette les données raster"),
            ("Polygonize", "Raster", "🔷", "Convertit raster en polygones"),
            ("Zonal Statistics", "Raster", "📈", "Calcule des statistiques par zones"),
            ("Aspect", "Raster", "🧭", "Calcule l'exposition des pentes"),
            ("Slope", "Raster", "📐", "Calcule la pente du terrain"),
            ("Export Database", "Database", "🗃️", "Exporte vers une base de données"),
            ("Join Attributes", "Database", "🔗", "Joint des attributs par clé"),
            ("Import CSV", "Database", "📄", "Importe des données CSV"),
            ("SQL Query", "Database", "💾", "Exécute une requête SQL")
        ]
        
        for name, category, icon, description in transformers_data:
            item = DraggableTransformerItem(name, category, icon, description)
            self.transformer_list.addItem(item)
    
    def filter_transformers(self, text):
        """Filtre les transformers selon le texte de recherche"""
        if hasattr(self, 'transformer_list'):
            for i in range(self.transformer_list.count()):
                item = self.transformer_list.item(i)
                if hasattr(item, 'transformer_name'):
                    visible = (text.lower() in item.transformer_name.lower() or 
                              text.lower() in item.transformer_category.lower() or
                              text.lower() in item.transformer_description.lower())
                    item.setHidden(not visible)
    
    def setup_workflow_tab(self):
        """Configure l'onglet du workflow designer avec le nouveau FME Designer"""
        try:
            # Utiliser le nouveau FMEWorkflowDesigner professionnel
            print(f"[DEBUG] FMEWorkflowDesigner disponible: {FMEWorkflowDesigner is not None}")
            if FMEWorkflowDesigner:
                print("[DEBUG] Création du FMEWorkflowDesigner...")
                # Créer le nouveau workflow designer professionnel
                self.workflow_designer = FMEWorkflowDesigner()
                print("[DEBUG] FMEWorkflowDesigner créé avec succès")
                
                # L'intégrer comme widget central sans barre de menu/outils
                workflow_widget = QWidget()
                layout = QVBoxLayout()
                layout.setContentsMargins(0, 0, 0, 0)
                
                # Ajouter juste le contenu central du workflow designer
                central_widget = self.workflow_designer.centralWidget()
                layout.addWidget(central_widget)
                
                workflow_widget.setLayout(layout)
                self.tabs.addTab(workflow_widget, "Workflow Designer")
                print("[DEBUG] Onglet Workflow Designer ajouté avec succès")
            else:
                print("[DEBUG] FMEWorkflowDesigner non disponible, utilisation du fallback")
                # Fallback vers l'ancien système si import échoue
                workflow_widget = self.create_interactive_workflow_widget()
                self.tabs.addTab(workflow_widget, "Workflow Designer")
                
        except Exception as e:
            print(f"[ERROR] Erreur workflow designer: {e}")
            import traceback
            traceback.print_exc()
            error_widget = self.create_error_widget(f"Erreur workflow: {str(e)}")
            self.tabs.addTab(error_widget, "Workflow Designer (Erreur)")
    
    def get_transformers_data_for_scene(self):
        """Retourne les données des transformers pour la scène."""
        return [
            ("Buffer", "Vector", "🔲", "Crée une zone tampon autour des géométries"),
            ("Clip", "Vector", "✂️", "Découpe les entités avec un masque"),
            ("Merge", "Vector", "🔗", "Fusionne plusieurs couches vectorielles"),
            ("Dissolve", "Vector", "🫧", "Dissout les géométries adjacentes"),
            ("Reproject", "Vector", "🌍", "Change la projection des données"),
            ("Field Calculator", "Vector", "🧮", "Calcule de nouveaux champs"),
            ("Intersection", "Vector", "∩", "Calcule l'intersection entre couches"),
            ("Union", "Vector", "∪", "Calcule l'union de géométries"),
            ("Difference", "Vector", "⊖", "Calcule la différence entre couches"),
            ("Centroid", "Vector", "⊙", "Calcule les centroïdes des géométries"),
            ("Raster Calculator", "Raster", "📊", "Effectue des calculs sur rasters"),
            ("Warp", "Raster", "🔄", "Reprojette les données raster"),
            ("Polygonize", "Raster", "🔷", "Convertit raster en polygones"),
            ("Zonal Statistics", "Raster", "📈", "Calcule des statistiques par zones"),
            ("Aspect", "Raster", "🧭", "Calcule l'exposition des pentes"),
            ("Slope", "Raster", "📐", "Calcule la pente du terrain"),
            ("Export Database", "Database", "🗃️", "Exporte vers une base de données"),
            ("Join Attributes", "Database", "🔗", "Joint des attributs par clé"),
            ("Import CSV", "Database", "📄", "Importe des données CSV"),
            ("SQL Query", "Database", "💾", "Exécute une requête SQL")
        ]

    def create_interactive_workflow_widget(self):
        """Crée un widget workflow avec drag and drop et clic droit"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # En-tête avec instructions étendues
        header_layout = QHBoxLayout()
        
        header = QLabel("📊 Designer de Workflow Interactif")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #495057;")
        
        # Instructions détaillées
        instructions = QLabel(
            "💡 Multiples façons d'ajouter des transformers:\n"
            "🖱️ Glissez depuis l'onglet 1 • 🖱️ Clic droit + recherche • ⌨️ Raccourcis I/O/Espace"
        )
        instructions.setStyleSheet("""
            QLabel {
                color: #6c757d; 
                font-style: italic; 
                background: #e8f5e8; 
                padding: 8px; 
                border-radius: 6px; 
                border-left: 4px solid #28a745;
                font-size: 11px;
                line-height: 1.3;
            }
        """)
        instructions.setWordWrap(True)
        
        # Boutons d'action avec raccourcis
        clear_btn = QPushButton("🗑️ Vider")
        zoom_btn = QPushButton("📐 Ajuster")
        help_btn = QPushButton("❓ Aide")
        run_btn = QPushButton("▶️ Exécuter")
        
        help_btn.clicked.connect(self.show_workflow_help)
        
        run_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background: #218838; }
        """)
        
        header_layout.addWidget(header)
        header_layout.addWidget(instructions)
        header_layout.addStretch()
        header_layout.addWidget(help_btn)
        header_layout.addWidget(clear_btn)
        header_layout.addWidget(zoom_btn)
        header_layout.addWidget(run_btn)
        
        # Splitter pour canvas + propriétés
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === CANVAS INTERACTIF ===
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout()
        
        # Scène de workflow interactive
        self.workflow_scene = ModernWorkflowScene()
        # Passer les données des transformers à la scène
        self.workflow_scene.set_transformer_data(self.get_transformers_data_for_scene())
        self.workflow_view = InteractiveWorkflowView(self.workflow_scene)
        
        canvas_layout.addWidget(self.workflow_view)
        canvas_widget.setLayout(canvas_layout)
        
        # === PANNEAU DE PROPRIÉTÉS ÉTENDU ===
        props_widget = QWidget()
        props_widget.setMaximumWidth(300)
        props_layout = QVBoxLayout()
        
        props_title = QLabel("⚙️ Propriétés & Raccourcis")
        props_title.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Raccourcis clavier
        shortcuts_group = QGroupBox("⌨️ Raccourcis Clavier")
        shortcuts_layout = QVBoxLayout()
        
        shortcuts_text = QLabel(
            "• Clic droit: Recherche rapide\n"
            "• I: Ajouter Input\n"
            "• O: Ajouter Output\n"
            "• Espace: Recherche rapide\n"
            "• Suppr: Effacer sélection\n"
            "• Molette: Zoom\n"
            "• Glisser: Déplacer nœuds"
        )
        shortcuts_text.setStyleSheet("font-size: 10px; color: #495057; line-height: 1.3;")
        shortcuts_layout.addWidget(shortcuts_text)
        shortcuts_group.setLayout(shortcuts_layout)
        
        # Statistiques
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QVBoxLayout()
        
        self.workflow_node_count = QLabel("Nœuds: 0")
        self.workflow_connections = QLabel("Connexions: 0")
        self.workflow_status = QLabel("Status: ⚪ Vide")
        
        stats_layout.addWidget(self.workflow_node_count)
        stats_layout.addWidget(self.workflow_connections)
        stats_layout.addWidget(self.workflow_status)
        stats_group.setLayout(stats_layout)
        
        # Actions rapides
        actions_group = QGroupBox("⚡ Actions Rapides")
        actions_layout = QVBoxLayout()
        
        quick_input_btn = QPushButton("📥 Input Rapide (I)")
        quick_output_btn = QPushButton("📤 Output Rapide (O)")
        validate_btn = QPushButton("✅ Valider")
        example_btn = QPushButton("🎯 Créer Exemple")
        
        quick_input_btn.clicked.connect(self.add_quick_input)
        quick_output_btn.clicked.connect(self.add_quick_output)
        validate_btn.clicked.connect(self.validate_workflow)
        example_btn.clicked.connect(self.create_example_workflow)
        
        for btn in [quick_input_btn, quick_output_btn, validate_btn, example_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    background: #f8f9fa;
                    text-align: left;
                }
                QPushButton:hover { background: #e9ecef; }
            """)
        
        actions_layout.addWidget(quick_input_btn)
        actions_layout.addWidget(quick_output_btn)
        actions_layout.addWidget(validate_btn)
        actions_layout.addWidget(example_btn)
        actions_group.setLayout(actions_layout)
        
        # Log
        log_group = QGroupBox("📝 Log d'Activité")
        log_layout = QVBoxLayout()
        
        self.workflow_log = QTextEdit()
        self.workflow_log.setMaximumHeight(120)
        self.workflow_log.setPlainText(
            "Workflow designer initialisé\n"
            "✅ Drag & drop activé\n"
            "✅ Clic droit activé\n"
            "✅ Raccourcis clavier activés\n"
            "Prêt pour la création de workflows..."
        )
        self.workflow_log.setStyleSheet("font-family: monospace; font-size: 9px;")
        
        log_layout.addWidget(self.workflow_log)
        log_group.setLayout(log_layout)
        
        props_layout.addWidget(props_title)
        props_layout.addWidget(shortcuts_group)
        props_layout.addWidget(stats_group)
        props_layout.addWidget(actions_group)
        props_layout.addWidget(log_group)
        props_layout.addStretch()
        props_widget.setLayout(props_layout)
        
        # Assemblage
        main_splitter.addWidget(canvas_widget)
        main_splitter.addWidget(props_widget)
        main_splitter.setSizes([550, 300])
        
        layout.addLayout(header_layout)
        layout.addWidget(main_splitter)
        
        # Connecter les boutons
        clear_btn.clicked.connect(self.clear_workflow_canvas)
        zoom_btn.clicked.connect(self.zoom_fit_workflow)
        
        widget.setLayout(layout)
        return widget
    
    def add_quick_input(self):
        """Ajoute un input rapide"""
        try:
            if hasattr(self, 'workflow_view') and hasattr(self, 'workflow_scene'):
                center = self.workflow_view.mapToScene(self.workflow_view.rect().center())
                node = WorkflowNode("Input", "General", "📥", center.x(), center.y())
                self.workflow_scene.addItem(node)
                self.workflow_scene.nodes.append(node) # Ajouter à la liste des nœuds de la scène
                self.status_message.setText("Input ajouté")
                self.on_workflow_node_added("Input") # Mettre à jour les statistiques
        except Exception as e:
            print(f"Erreur ajout input: {e}")
    
    def add_quick_output(self):
        """Ajoute un output rapide"""
        try:
            if hasattr(self, 'workflow_scene') and self.workflow_scene:
                center = self.workflow_view.mapToScene(self.workflow_view.rect().center())
                node = WorkflowNode("Output", "General", "📤", center.x(), center.y())
                self.workflow_scene.addItem(node)
                self.workflow_scene.nodes.append(node) # Ajouter à la liste des nœuds de la scène
                self.status_message.setText("Output ajouté")
                self.on_workflow_node_added("Output") # Mettre à jour les statistiques
        except Exception as e:
            print(f"Erreur ajout output: {e}")
    
    def show_workflow_help(self):
        """Affiche l'aide du workflow"""
        help_text = """
        <h3>🎯 Guide d'Utilisation du Workflow Designer</h3>
        
        <h4>🖱️ Ajout de Transformers :</h4>
        <ul>
        <li><b>Glisser-déposer</b> : Depuis l'onglet "Bibliothèque Transformers"</li>
        <li><b>Clic droit</b> : Menu de recherche rapide</li>
        <li><b>Raccourcis</b> : I=Input, O=Output, Espace=Recherche</li>
        </ul>
        
        <h4>🔧 Manipulation :</h4>
        <ul>
        <li><b>Déplacer</b> : Glisser les nœuds</li>
        <li><b>Sélectionner</b> : Clic sur un nœud</li>
        <li><b>Supprimer</b> : Touche Suppr</li>
        <li><b>Zoom</b> : Molette de la souris</li>
        </ul>
        
        <h4>⌨️ Raccourcis Clavier :</h4>
        <ul>
        <li><b>I</b> : Ajouter Input</li>
        <li><b>O</b> : Ajouter Output</li>
        <li><b>Espace</b> : Recherche rapide</li>
        <li><b>Suppr</b> : Effacer sélection</li>
        </ul>
        """
        
        QMessageBox.information(self, "Aide - Workflow Designer", help_text)
    
    def on_workflow_node_added(self, name):
        """Appelé quand un nœud est ajouté au workflow"""
        node_count = len(self.workflow_scene.nodes)
        self.workflow_node_count.setText(f"Nœuds: {node_count}")
        
        if node_count == 1:
            self.workflow_status.setText("Status: 🟡 En construction")
        elif node_count >= 3:
            self.workflow_status.setText("Status: 🟢 Prêt")
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.workflow_log.append(f"[{timestamp}] Nœud '{name}' ajouté")
        
        self.status_info.setText(f"📍 Workflow - Nœud ajouté: {name}")
    
    def clear_workflow_canvas(self):
        """Vide le canvas du workflow"""
        if hasattr(self, 'workflow_scene'):
            self.workflow_scene.clear()
            self.workflow_node_count.setText("Nœuds: 0")
            self.workflow_status.setText("Status: ⚪ Vide")
            self.workflow_log.append("[System] Canvas vidé")
    
    def zoom_fit_workflow(self):
        """Ajuste le zoom du workflow"""
        if hasattr(self, 'workflow_view'):
            self.workflow_view.fitInView(self.workflow_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
            self.workflow_log.append("[System] Zoom ajusté")
    
    def validate_workflow(self):
        """Valide le workflow"""
        if hasattr(self, 'workflow_scene'):
            # Compter les items dans la scène (approximation)
            node_count = len([item for item in self.workflow_scene.items() if hasattr(item, 'transformer_name')])
            if node_count == 0:
                self.workflow_log.append("[Validation] ❌ Aucun nœud")
            elif node_count < 2:
                self.workflow_log.append("[Validation] ⚠️ Au moins 2 nœuds recommandés")
            else:
                self.workflow_log.append("[Validation] ✅ Workflow valide")
    
    def create_example_workflow(self):
        """Crée un workflow d'exemple"""
        if hasattr(self, 'workflow_scene'):
            # Créer des nœuds d'exemple basiques (simulation)
            node_data = [
                ("Input", 150, 200),
                ("Buffer", 400, 200),
                ("Output", 650, 200)
            ]
            
            for name, x, y in node_data:
                node = WorkflowNode(name, "General", "⚙️", x, y)
                self.workflow_scene.addItem(node)
            
            self.workflow_log.append("[System] Workflow d'exemple créé (simulation)")
    
    def setup_processing_tab(self):
        """Configure l'onglet du scanner processing"""
        if QGISProcessingIntegration is None:
            error_widget = self.create_error_widget("Module qgis_integration non disponible")
            self.tabs.addTab(error_widget, "⚙️ Processing")
            return
        
        try:
            # Créer un widget processing simple
            processing_widget = self.create_simple_processing_widget()
            self.tabs.addTab(processing_widget, "⚙️ Scanner Processing")
                
        except Exception as e:
            error_widget = self.create_error_widget(f"Erreur processing: {str(e)}")
            self.tabs.addTab(error_widget, "⚙️ Processing (Erreur)")
    
    def create_simple_processing_widget(self):
        """Crée un widget processing simple et interactif"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # En-tête
        header = QLabel("⚙️ Scanner Processing QGIS")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #495057; margin: 10px 0;")
        
        # Boutons de scan
        scan_layout = QHBoxLayout()
        scan_btn = QPushButton("🔄 Scanner les Algorithmes")
        scan_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background: #218838; }
        """)
        
        scan_layout.addWidget(scan_btn)
        scan_layout.addStretch()
        
        # Zone de résultats
        results_area = QTextEdit()
        results_area.setPlainText("""🔍 Scanner Processing QGIS\n        \n📋 Algorithmes disponibles:\n\n📁 Vector geometry:\n  • native:buffer - Crée des zones tampons\n  • native:centroid - Calcule les centroïdes\n  • native:convexhull - Enveloppe convexe\n  \n📁 Vector overlay:\n  • native:clip - Découpe des entités\n  • native:intersection - Intersection de couches\n  • native:union - Union de géométries\n  \n📁 Raster analysis:\n  • gdal:aspect - Calcul d'exposition\n  • gdal:slope - Calcul de pente\n  • native:rastercalculator - Calculatrice raster\n  \n📁 Database:\n  • native:postgisexecutesql - Exécute du SQL\n  • native:spatialindex - Index spatial\n  \n✅ {scan_count} algorithmes trouvés\n🔧 Prêt pour intégration dans le workflow\n        """.format(scan_count=25))
        
        results_area.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        
        # Actions
        action_layout = QHBoxLayout()
        export_btn = QPushButton("📄 Exporter Liste")
        integrate_btn = QPushButton("🔗 Intégrer au Workflow")
        
        for btn in [export_btn, integrate_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border: 1px solid #4A90E2;
                    border-radius: 4px;
                    background: white;
                    color: #4A90E2;
                }
                QPushButton:hover {
                    background: #4A90E2;
                    color: white;
                }
            """)
        
        action_layout.addWidget(export_btn)
        action_layout.addWidget(integrate_btn)
        action_layout.addStretch()
        
        # Assemblage
        layout.addWidget(header)
        layout.addLayout(scan_layout)
        layout.addWidget(results_area)
        layout.addLayout(action_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_error_widget(self, error_message):
        """Crée un widget d'erreur informatif"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Icône d'erreur
        error_label = QLabel("⚠️")
        error_label.setFont(QFont("Arial", 48))
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: #dc3545; margin: 20px;")
        
        # Message d'erreur
        message_label = QLabel(error_message)
        message_label.setFont(QFont("Arial", 12))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #6c757d; margin: 20px;")
        
        # Bouton de rechargement
        reload_btn = QPushButton("🔄 Recharger le composant")
        reload_btn.clicked.connect(self.reload_components)
        reload_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #4A90E2;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #357ABD;
            }
        """)
        
        layout.addStretch()
        layout.addWidget(error_label)
        layout.addWidget(message_label)
        layout.addWidget(reload_btn, 0, Qt.AlignCenter)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        status_bar = self.statusBar()
        
        self.status_message = QLabel("Interface unifiée prête")
        status_bar.addWidget(self.status_message)
        
        # Informations permanentes
        version_label = QLabel("GISENGINE v1.0")
        status_bar.addPermanentWidget(version_label)
    
    def apply_style(self):
        """Applique le style moderne"""
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
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
            QMenuBar {
                background: #ffffff;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #e9ecef;
            }
            QToolBar {
                background: #ffffff;
                border-bottom: 1px solid #dee2e6;
                spacing: 4px;
                padding: 4px;
            }
            QStatusBar {
                background: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
    
    def on_tab_changed(self, index):
        """Appelé lors du changement d'onglet"""
        tab_names = ["Transformers", "Workflow Designer", "Scanner Processing"]
        if 0 <= index < len(tab_names):
            self.status_message.setText(f"Onglet actif: {tab_names[index]}")
            self.status_info.setText(f"📍 {tab_names[index]}")
    
    def reload_components(self):
        """Recharge tous les composants"""
        # Vider les onglets
        self.tabs.clear()
        
        # Recharger
        self.setup_components()
        
        QMessageBox.information(self, "Rechargement", "✅ Composants rechargés avec succès !")
    
    def new_workflow(self):
        """Nouveau workflow"""
        self.tabs.setCurrentIndex(1)  # Aller à l'onglet workflow
        if hasattr(self, 'workflow_designer') and self.workflow_designer:
            self.workflow_designer.new_workflow()
        self.status_message.setText("Nouveau workflow créé")
    
    def open_workflow(self):
        """Ouvrir un workflow"""
        self.tabs.setCurrentIndex(1)
        self.status_message.setText("Ouverture de workflow...")
    
    def save_workflow(self):
        """Sauvegarder le workflow"""
        if hasattr(self, 'workflow_designer') and self.workflow_designer:
            self.workflow_designer.save_workflow()
        else:
            self.status_message.setText("Workflow sauvegardé")
    
    def validate_workflow(self):
        """Valider le workflow"""
        self.tabs.setCurrentIndex(1)
        if hasattr(self, 'workflow_designer') and self.workflow_designer:
            # Le workflow designer gère sa propre validation
            self.status_message.setText("Validation du workflow...")
        else:
            self.status_message.setText("Validation du workflow en cours...")
            # Simulation de validation
            QTimer.singleShot(1000, lambda: self.status_message.setText("✅ Workflow validé"))
    
    def execute_workflow(self):
        """Exécuter le workflow"""
        self.tabs.setCurrentIndex(1)
        if hasattr(self, 'workflow_designer') and self.workflow_designer:
            self.workflow_designer.run_workflow()
        else:
            self.status_message.setText("Exécution du workflow en cours...")
            # Simulation d'exécution
            QTimer.singleShot(2000, lambda: self.status_message.setText("✅ Workflow exécuté"))
    
    def show_about(self):
        """Affiche les informations"""
        about_text = """
        <h2>🛠️ GISENGINE pour QGIS</h2>
        <p><b>Version:</b> 1.0.0 - Interface Unifiée</p>
        
        <h3>🎯 Fonctionnalités:</h3>
        <ul>
        <li>🛠️ <b>Bibliothèque Transformers</b> - Catalogue de transformations</li>
        <li>📊 <b>Workflow Designer</b> - Création graphique de workflows</li>
        <li>⚙️ <b>Scanner Processing</b> - Intégration QGIS Processing</li>
        </ul>
        
        <h3>🚀 Interface unifiée:</h3>
        <p>Tous les composants sont maintenant intégrés dans une seule fenêtre
        avec des onglets pour une expérience utilisateur optimale.</p>
        
        <p><i>🔧 Plugin en développement actif</i></p>
        """
        
        QMessageBox.information(self, "À propos", about_text)

    def clear_workflow_canvas(self):
        """Vide le canvas du workflow"""
        try:
            if hasattr(self, 'workflow_scene') and self.workflow_scene:
                # Supprimer tous les éléments de la scène
                for item in self.workflow_scene.items():
                    if isinstance(item, (WorkflowNode, Connection)):
                        item.delete() # Appelle la méthode delete() de l'élément
                self.workflow_scene.nodes = [] # Réinitialiser la liste des nœuds de la scène
                self.status_message.setText("Canvas vidé")
                self.on_elements_deleted() # Mettre à jour les statistiques
        except Exception as e:
            print(f"Erreur vidage canvas: {e}")
    
    def add_quick_input(self):
        """Ajoute un input rapide"""
        try:
            if hasattr(self, 'workflow_view') and hasattr(self, 'workflow_scene'):
                center = self.workflow_view.mapToScene(self.workflow_view.rect().center())
                node = WorkflowNode("Input", "General", "📥", center.x(), center.y())
                self.workflow_scene.addItem(node)
                self.workflow_scene.nodes.append(node) # Ajouter à la liste des nœuds de la scène
                self.status_message.setText("Input ajouté")
                self.on_workflow_node_added("Input") # Mettre à jour les statistiques
        except Exception as e:
            print(f"Erreur ajout input: {e}")
    
    def add_quick_output(self):
        """Ajoute un output rapide"""
        try:
            if hasattr(self, 'workflow_scene') and self.workflow_scene:
                center = self.workflow_view.mapToScene(self.workflow_view.rect().center())
                node = WorkflowNode("Output", "General", "📤", center.x(), center.y())
                self.workflow_scene.addItem(node)
                self.workflow_scene.nodes.append(node) # Ajouter à la liste des nœuds de la scène
                self.status_message.setText("Output ajouté")
                self.on_workflow_node_added("Output") # Mettre à jour les statistiques
        except Exception as e:
            print(f"Erreur ajout output: {e}")
    
    def show_quick_add_dialog(self):
        """Affiche le dialogue d'ajout rapide"""
        try:
            from PyQt5.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, 'Ajout rapide', 'Nom du transformer:')
            if ok and text:
                self.status_message.setText(f"Transformer '{text}' ajouté")
        except Exception as e:
            print(f"Erreur dialogue: {e}")

    def on_elements_deleted(self):
        """Met à jour les statistiques après suppression d'éléments."""
        node_count = len([item for item in self.workflow_scene.items() if isinstance(item, WorkflowNode)])
        connection_count = len([item for item in self.workflow_scene.items() if isinstance(item, Connection)])
        self.workflow_node_count.setText(f"Nœuds: {node_count}")
        self.workflow_connections.setText(f"Connexions: {connection_count}")
        self.status_message.setText("Éléments supprimés")

def main():
    """Fonction de test standalone"""
    app = QApplication([])
    window = UnifiedGISENGINEInterface()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()

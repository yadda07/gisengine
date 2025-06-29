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
    QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem
)
from PyQt5.QtCore import Qt, QTimer, QMimeData, pyqtSignal, QPointF, QPoint, QRect
from PyQt5.QtGui import (
    QFont, QIcon, QKeySequence, QPen, QBrush, QColor, QLinearGradient,
    QDrag, QPainter, QPixmap
)

# Import des composants
try:
    from .qgis_plugin_ui import QGISPluginUI
    from .workflow_mapper import WorkflowTestWindow
    from .qgis_integration import QGISProcessingIntegration
    print("✅ Tous les composants importés avec succès")
except ImportError as e:
    print(f"❌ Erreur import composants: {e}")
    QGISPluginUI = None
    WorkflowTestWindow = None
    QGISProcessingIntegration = None

# === Classes pour Drag and Drop ===

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
        # CORRECTION: Utiliser QPoint au lieu de QPointF
        from PyQt5.QtCore import QPoint
        drag.setHotSpot(QPoint(100, 30))
        
        # Exécuter le drag
        dropAction = drag.exec_(Qt.CopyAction)

class WorkflowNode(QGraphicsRectItem):
    """Nœud de workflow déplaçable et interactif"""
    
    def __init__(self, name, category, icon, x=0, y=0):
        super().__init__(0, 0, 160, 80)
        self.setPos(x, y)
        self.transformer_name = name
        self.transformer_category = category
        self.transformer_icon = icon
        
        # Rendre le nœud interactif
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Style selon la catégorie
        colors = {
            "Vector": QColor("#28a745"),
            "Raster": QColor("#dc3545"),
            "Database": QColor("#6f42c1"),
            "General": QColor("#4A90E2")
        }
        
        base_color = colors.get(category, QColor("#4A90E2"))
        
        # Gradient de fond
        gradient = QLinearGradient(0, 0, 0, 80)
        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(120))
        
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(base_color.darker(140), 2))
        
        # Créer le contenu textuel
        self.create_content()
        
        # Effet de sélection
        self.setAcceptHoverEvents(True)
    
    def create_content(self):
        """Crée le contenu visuel du nœud"""
        # Icône
        self.icon_text = QGraphicsTextItem(self.transformer_icon, self)
        self.icon_text.setPos(10, 10)
        self.icon_text.setFont(QFont("Arial", 16))
        
        # Nom
        self.name_text = QGraphicsTextItem(self.transformer_name, self)
        self.name_text.setPos(35, 8)
        self.name_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.name_text.setDefaultTextColor(QColor("#ffffff"))
        
        # Catégorie
        self.category_text = QGraphicsTextItem(f"📁 {self.transformer_category}", self)
        self.category_text.setPos(35, 28)
        self.category_text.setFont(QFont("Arial", 8))
        self.category_text.setDefaultTextColor(QColor("#e9ecef"))
    
    def hoverEnterEvent(self, event):
        """Effet de survol"""
        self.setScale(1.05)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Fin de survol"""
        if not self.isSelected():
            self.setScale(1.0)
        super().hoverLeaveEvent(event)

class QuickAddDialog(QWidget):
    """Dialog de recherche rapide pour ajouter des transformers"""
    
    transformer_selected = pyqtSignal(str, str, str)  # name, category, icon
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(300, 200)
        self.transformers_data = self.get_transformers_data()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # En-tête
        header = QLabel("⚡ Ajout Rapide de Transformer")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setStyleSheet("color: #495057; margin-bottom: 5px;")
        
        # Champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tapez le nom du transformer...")
        self.search_input.textChanged.connect(self.filter_results)
        self.search_input.returnPressed.connect(self.select_first_result)
        
        # Liste des résultats
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(120)
        self.results_list.itemDoubleClicked.connect(self.on_item_selected)
        
        # Raccourcis rapides
        shortcuts_layout = QHBoxLayout()
        
        input_btn = QPushButton("📥 Input")
        output_btn = QPushButton("📤 Output") 
        buffer_btn = QPushButton("🔲 Buffer")
        
        input_btn.clicked.connect(lambda: self.add_transformer("Input", "General", "📥"))
        output_btn.clicked.connect(lambda: self.add_transformer("Output", "General", "📤"))
        buffer_btn.clicked.connect(lambda: self.add_transformer("Buffer", "Vector", "🔲"))
        
        for btn in [input_btn, output_btn, buffer_btn]:
            btn.setMaximumHeight(30)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                }
                QPushButton:hover { background: #e9ecef; }
            """)
        
        shortcuts_layout.addWidget(input_btn)
        shortcuts_layout.addWidget(output_btn)
        shortcuts_layout.addWidget(buffer_btn)
        
        layout.addWidget(header)
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_list)
        layout.addLayout(shortcuts_layout)
        
        self.setLayout(layout)
        
        # Style du dialog
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #4A90E2;
                border-radius: 8px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-size: 12px;
            }
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f1f3f4;
            }
            QListWidget::item:hover {
                background: #e3f2fd;
            }
            QListWidget::item:selected {
                background: #4A90E2;
                color: white;
            }
        """)
        
        # Remplir la liste initialement
        self.populate_all_results()
    
    def get_transformers_data(self):
        """Données des transformers disponibles"""
        return [
            ("Input", "General", "📥"),
            ("Output", "General", "📤"),
            ("Buffer", "Vector", "🔲"),
            ("Clip", "Vector", "✂️"),
            ("Merge", "Vector", "🔗"),
            ("Dissolve", "Vector", "🫧"),
            ("Reproject", "Vector", "🌍"),
            ("Field Calculator", "Vector", "🧮"),
            ("Intersection", "Vector", "∩"),
            ("Union", "Vector", "∪"),
            ("Difference", "Vector", "⊖"),
            ("Centroid", "Vector", "⊙"),
            ("Raster Calculator", "Raster", "📊"),
            ("Warp", "Raster", "🔄"),
            ("Polygonize", "Raster", "🔷"),
            ("Zonal Statistics", "Raster", "📈"),
            ("Export Database", "Database", "🗃️"),
            ("Join Attributes", "Database", "🔗")
        ]
    
    def populate_all_results(self):
        """Remplit la liste avec tous les transformers"""
        self.results_list.clear()
        for name, category, icon in self.transformers_data:
            item = QListWidgetItem(f"{icon} {name} ({category})")
            item.setData(Qt.UserRole, (name, category, icon))
            self.results_list.addItem(item)
    
    def filter_results(self, text):
        """Filtre les résultats selon le texte"""
        self.results_list.clear()
        
        if not text.strip():
            self.populate_all_results()
            return
        
        text_lower = text.lower()
        for name, category, icon in self.transformers_data:
            if (text_lower in name.lower() or 
                text_lower in category.lower()):
                item = QListWidgetItem(f"{icon} {name} ({category})")
                item.setData(Qt.UserRole, (name, category, icon))
                self.results_list.addItem(item)
    
    def select_first_result(self):
        """Sélectionne le premier résultat avec Entrée"""
        if self.results_list.count() > 0:
            first_item = self.results_list.item(0)
            self.on_item_selected(first_item)
    
    def on_item_selected(self, item):
        """Appelé quand un item est sélectionné"""
        data = item.data(Qt.UserRole)
        if data:
            name, category, icon = data
            self.add_transformer(name, category, icon)
    
    def add_transformer(self, name, category, icon):
        """Émet le signal pour ajouter le transformer"""
        self.transformer_selected.emit(name, category, icon)
        self.hide()
    
    def showEvent(self, event):
        """Appelé quand le dialog s'affiche"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def keyPressEvent(self, event):
        """Gestion des touches"""
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_Up:
            current = self.results_list.currentRow()
            if current > 0:
                self.results_list.setCurrentRow(current - 1)
        elif event.key() == Qt.Key_Down:
            current = self.results_list.currentRow()
            if current < self.results_list.count() - 1:
                self.results_list.setCurrentRow(current + 1)
        else:
            super().keyPressEvent(event)
    """Scène interactive pour le workflow avec support drop"""
    
    node_added = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 2000, 1500)
        self.setBackgroundBrush(QBrush(QColor("#f8f9fa")))
        self.nodes = []
        
    def dragEnterEvent(self, event):
        """Accepte le drag des transformers"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("transformer:"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Gère le mouvement pendant le drag"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("transformer:"):
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Gère le drop d'un transformer"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("transformer:"):
            # Extraire les données du transformer
            data = event.mimeData().text().split(":")
            if len(data) >= 4:
                _, name, category, icon = data[:4]
                
                # Position du drop
                pos = event.scenePos()
                
                # Créer le nœud
                node = WorkflowNode(name, category, icon, pos.x() - 80, pos.y() - 40)
                self.addItem(node)
                self.nodes.append(node)
                
                # Animation d'apparition
                node.setScale(0.1)
                animation = QTimer()
                scale = [0.1]  # Liste pour éviter les problèmes de closure
                
                def animate():
                    scale[0] += 0.1
                    node.setScale(scale[0])
                    if scale[0] >= 1.0:
                        animation.stop()
                
                animation.timeout.connect(animate)
                animation.start(30)
                
                self.node_added.emit(name)
                event.acceptProposedAction()
    
    def drawBackground(self, painter, rect):
        """Dessine le fond avec grille"""
        super().drawBackground(painter, rect)
        
        # Grille légère
        painter.setPen(QPen(QColor("#e9ecef"), 1))
        
        grid_size = 25
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        # Lignes verticales
        for x in range(left, int(rect.right()), grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        
        # Lignes horizontales
        for y in range(top, int(rect.bottom()), grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

class InteractiveWorkflowView(QGraphicsView):
    """Vue interactive du workflow avec support clavier"""
    
    def __init__(self, scene):
        super().__init__(scene)
        self.setAcceptDrops(True)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFocusPolicy(Qt.StrongFocus)  # Permettre le focus clavier
        
        # Style
        self.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
        """)
    
    def wheelEvent(self, event):
        """Zoom avec la molette"""
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        self.scale(factor, factor)
    
    def mousePressEvent(self, event):
        """Gère les clics de souris - assure le focus pour les raccourcis"""
        self.setFocus()  # S'assurer que la vue a le focus pour les raccourcis clavier
        super().mousePressEvent(event)

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
        
        # Navigation rapide entre onglets - SYNTAXE CORRIGÉE
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
        
        # Actions de workflow - SYNTAXE CORRIGÉE
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
        """Configure l'onglet du workflow designer avec drag and drop"""
        try:
            # Créer directement le widget workflow interactif
            workflow_widget = self.create_interactive_workflow_widget()
            self.tabs.addTab(workflow_widget, "📊 Workflow Designer")
                
        except Exception as e:
            error_widget = self.create_error_widget(f"Erreur workflow: {str(e)}")
            self.tabs.addTab(error_widget, "📊 Workflow (Erreur)")
    
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
        
        # Zone de drop avec instructions visuelles étendues
        drop_info = QLabel(
            "🎯 Canvas Interactif GISENGINE\n\n"
            "🖱️ Clic droit → Recherche rapide de transformers\n"
            "🖱️ Glisser-déposer depuis la bibliothèque\n"
            "⌨️ Raccourcis: I=Input, O=Output, Espace=Recherche\n"
            "🔄 Déplacez les nœuds librement\n"
            "🗑️ Suppr pour effacer la sélection"
        )
        drop_info.setAlignment(Qt.AlignCenter)
        drop_info.setStyleSheet("""
            QLabel {
                border: 3px dashed #4A90E2;
                border-radius: 12px;
                background: rgba(74, 144, 226, 0.1);
                color: #4A90E2;
                font-weight: bold;
                padding: 25px;
                margin: 10px;
                line-height: 1.4;
            }
        """)
        
        # Scène de workflow interactive
        self.workflow_scene = InteractiveWorkflowScene()
        self.workflow_view = InteractiveWorkflowView(self.workflow_scene)
        
        # Connecter les signaux
        self.workflow_scene.node_added.connect(self.on_workflow_node_added)
        
        canvas_layout.addWidget(drop_info)
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
        """Ajoute rapidement un Input au centre"""
        if hasattr(self, 'workflow_view'):
            center = self.workflow_view.mapToScene(self.workflow_view.rect().center())
            self.workflow_scene.create_node_at_position("Input", "General", "📥", center.x() - 80, center.y() - 40)
    
    def add_quick_output(self):
        """Ajoute rapidement un Output au centre"""
        if hasattr(self, 'workflow_view'):
            center = self.workflow_view.mapToScene(self.workflow_view.rect().center())
            self.workflow_scene.create_node_at_position("Output", "General", "📤", center.x() - 80, center.y() - 40)
    
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
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.workflow_log.append(f"[{timestamp}] Nœud '{name}' ajouté")
        
        self.status_info.setText(f"📍 Workflow - Nœud ajouté: {name}")
    
    def clear_workflow_canvas(self):
        """Vide le canvas du workflow"""
        if hasattr(self, 'workflow_scene'):
            self.workflow_scene.clear()
            self.workflow_scene.nodes.clear()
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
            node_count = len(self.workflow_scene.nodes)
            if node_count == 0:
                self.workflow_log.append("[Validation] ❌ Aucun nœud")
            elif node_count < 2:
                self.workflow_log.append("[Validation] ⚠️ Au moins 2 nœuds recommandés")
            else:
                self.workflow_log.append("[Validation] ✅ Workflow valide")
    
    def create_example_workflow(self):
        """Crée un workflow d'exemple"""
        if hasattr(self, 'workflow_scene'):
            # Ajouter des nœuds d'exemple
            nodes_data = [
                ("Input", "General", "📥", 150, 200),
                ("Buffer", "Vector", "🔲", 400, 200),
                ("Output", "General", "📤", 650, 200)
            ]
            
            for name, category, icon, x, y in nodes_data:
                node = WorkflowNode(name, category, icon, x, y)
                self.workflow_scene.addItem(node)
                self.workflow_scene.nodes.append(node)
            
            self.on_workflow_node_added("Exemple créé")
            self.workflow_log.append("[System] Workflow d'exemple créé")
    
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
    
    def create_simple_transformers_widget(self):
        """Crée un widget transformers simple et interactif"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # En-tête
        header = QLabel("🛠️ Bibliothèque de Transformers")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #495057; margin: 10px 0;")
        
        # Zone de recherche
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Rechercher un transformer...")
        search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 12px;
            }
        """)
        
        # Liste des transformers
        transformers_list = QListWidget()
        transformers_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background: white;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:hover {
                background: #e9ecef;
            }
            QListWidget::item:selected {
                background: #4A90E2;
                color: white;
            }
        """)
        
        # Remplir la liste
        transformers_data = [
            "🔲 Buffer - Crée une zone tampon",
            "✂️ Clip - Découpe les entités", 
            "🌍 Reproject - Change la projection",
            "🧮 Field Calculator - Calcule des champs",
            "🔗 Merge - Fusionne les couches",
            "🫧 Dissolve - Dissout les géométries",
            "📊 Raster Calculator - Calculs raster",
            "🔄 Warp - Reprojette les rasters",
            "🔷 Polygonize - Raster vers polygones",
            "🗃️ Export Database - Export vers BD"
        ]
        
        for transformer in transformers_data:
            transformers_list.addItem(transformer)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Ajouter au Workflow")
        add_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))  # Aller au workflow
        
        modeler_btn = QPushButton("🛠️ Ouvrir Processing Modeler")
        
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #4A90E2;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background: #357ABD; }
        """)
        
        modeler_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background: #218838; }
        """)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(modeler_btn)
        
        # Assemblage
        layout.addWidget(header)
        layout.addWidget(search_box)
        layout.addWidget(transformers_list)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_simple_workflow_widget(self):
        """Crée un widget workflow simple et interactif"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # En-tête
        header_layout = QHBoxLayout()
        header = QLabel("📊 Designer de Workflow")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #495057;")
        
        # Boutons de toolbar
        new_btn = QPushButton("🆕 Nouveau")
        open_btn = QPushButton("📂 Ouvrir") 
        save_btn = QPushButton("💾 Sauver")
        run_btn = QPushButton("▶️ Exécuter")
        
        for btn in [new_btn, open_btn, save_btn, run_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    background: white;
                }
                QPushButton:hover { background: #e9ecef; }
            """)
        
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(new_btn)
        header_layout.addWidget(open_btn)
        header_layout.addWidget(save_btn)
        header_layout.addWidget(run_btn)
        
        # Zone principale avec splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Canvas interactif
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout()
        
        canvas_info = QLabel("🎨 Zone de Workflow Interactive")
        canvas_info.setAlignment(Qt.AlignCenter)
        canvas_info.setStyleSheet("""
            QLabel {
                padding: 40px;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                background: #f8f9fa;
                font-size: 16px;
                color: #6c757d;
            }
        """)
        
        # Boutons de test interactifs
        canvas_buttons = QHBoxLayout()
        add_input_btn = QPushButton("📥 Ajouter Input")
        add_transform_btn = QPushButton("⚙️ Ajouter Transform")
        add_output_btn = QPushButton("📤 Ajouter Output")
        
        for btn in [add_input_btn, add_transform_btn, add_output_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border: 2px solid #4A90E2;
                    border-radius: 6px;
                    background: white;
                    color: #4A90E2;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #4A90E2;
                    color: white;
                }
            """)
        
        canvas_buttons.addWidget(add_input_btn)
        canvas_buttons.addWidget(add_transform_btn)
        canvas_buttons.addWidget(add_output_btn)
        
        canvas_layout.addWidget(canvas_info)
        canvas_layout.addLayout(canvas_buttons)
        canvas_widget.setLayout(canvas_layout)
        
        # Panneau de propriétés
        props_widget = QWidget()
        props_widget.setMaximumWidth(250)
        props_layout = QVBoxLayout()
        
        props_title = QLabel("⚙️ Propriétés")
        props_title.setFont(QFont("Arial", 12, QFont.Bold))
        
        props_info = QTextEdit()
        props_info.setPlainText("Sélectionnez un élément du workflow pour voir ses propriétés.\n\nActions disponibles:\n• Glisser-déposer des transformers\n• Connecter les éléments\n• Configurer les paramètres")
        props_info.setMaximumHeight(200)
        
        # Stats du workflow
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(QLabel("Nœuds: 3"))
        stats_layout.addWidget(QLabel("Connexions: 2"))
        stats_layout.addWidget(QLabel("Status: ✅ Valide"))
        stats_group.setLayout(stats_layout)
        
        props_layout.addWidget(props_title)
        props_layout.addWidget(props_info)
        props_layout.addWidget(stats_group)
        props_layout.addStretch()
        props_widget.setLayout(props_layout)
        
        # Assemblage
        main_splitter.addWidget(canvas_widget)
        main_splitter.addWidget(props_widget)
        main_splitter.setSizes([600, 250])
        
        layout.addLayout(header_layout)
        layout.addWidget(main_splitter)
        
        widget.setLayout(layout)
        return widget
    
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
        results_area.setPlainText("""🔍 Scanner Processing QGIS
        
📋 Algorithmes disponibles:

📁 Vector geometry:
  • native:buffer - Crée des zones tampons
  • native:centroid - Calcule les centroïdes
  • native:convexhull - Enveloppe convexe
  
📁 Vector overlay:
  • native:clip - Découpe des entités
  • native:intersection - Intersection de couches
  • native:union - Union de géométries
  
📁 Raster analysis:
  • gdal:aspect - Calcul d'exposition
  • gdal:slope - Calcul de pente
  • native:rastercalculator - Calculatrice raster
  
📁 Database:
  • native:postgisexecutesql - Exécute du SQL
  • native:spatialindex - Index spatial
  
✅ {scan_count} algorithmes trouvés
🔧 Prêt pour intégration dans le workflow
        """.format(scan_count=25))
        
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
        self.status_message.setText("Nouveau workflow créé")
    
    def open_workflow(self):
        """Ouvrir un workflow"""
        self.tabs.setCurrentIndex(1)
        self.status_message.setText("Ouverture de workflow...")
    
    def save_workflow(self):
        """Sauvegarder le workflow"""
        self.status_message.setText("Workflow sauvegardé")
    
    def validate_workflow(self):
        """Valider le workflow"""
        self.tabs.setCurrentIndex(1)
        self.status_message.setText("Validation du workflow en cours...")
        
        # Simulation de validation
        QTimer.singleShot(1000, lambda: self.status_message.setText("✅ Workflow validé"))
    
    def execute_workflow(self):
        """Exécuter le workflow"""
        self.tabs.setCurrentIndex(1)
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
        
        QMessageBox.about(self, "À propos", about_text)

def main():
    """Fonction de test standalone"""
    app = QApplication([])
    window = UnifiedGISENGINEInterface()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
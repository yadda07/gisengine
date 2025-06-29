#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin QGIS - Interface Prototype pour GISENGINE
Version corrigée sans erreurs de polygones
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QListWidgetItem, QPushButton, QLineEdit, QLabel,
    QSplitter, QFrame, QScrollArea, QGroupBox, QComboBox, QTextEdit,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QGraphicsView, 
    QGraphicsScene, QGraphicsProxyWidget, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsLineItem, QGraphicsTextItem
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QPen, QBrush, QPainter,
    QLinearGradient, QPixmap
)

class ModernButton(QPushButton):
    """Bouton avec style moderne"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setStyleSheet(self.get_style())
        
    def get_style(self):
        if self.primary:
            return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A90E2, stop:1 #357ABD);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5BA0F2, stop:1 #4A90E2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #357ABD, stop:1 #2E6AA3);
            }
            """
        else:
            return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                color: #495057;
                border: 1px solid #dee2e6;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border-color: #adb5bd;
            }
            """

class SearchBox(QLineEdit):
    """Boîte de recherche moderne"""
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("🔍 Rechercher un transformer...")
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
                outline: none;
            }
        """)

class TransformerItem(QWidget):
    """Widget personnalisé pour afficher un transformer"""
    def __init__(self, name, category, description, icon="⚙️"):
        super().__init__()
        self.name = name
        self.category = category
        self.description = description
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 16px; margin-right: 8px;")
        
        # Informations
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        category_label = QLabel(f"📁 {category}")
        category_label.setStyleSheet("color: #6c757d; font-size: 9px;")
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #495057; font-size: 9px;")
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(category_label)
        info_layout.addWidget(desc_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                margin: 2px;
            }
            QWidget:hover {
                background: #f8f9fa;
                border-color: #4A90E2;
            }
        """)

class WorkflowCanvas(QGraphicsView):
    """Zone de canvas pour créer le workflow graphique - VERSION CORRIGÉE"""
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Style du canvas
        self.setStyleSheet("""
            QGraphicsView {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #ffffff);
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)
        
        # Ajout d'éléments de démonstration
        self.add_demo_nodes()
        
    def add_demo_nodes(self):
        """Ajoute des nœuds de démonstration - VERSION SANS ERREUR"""
        # Nœud Input
        input_rect = self.scene.addRect(50, 50, 120, 60, 
                                       QPen(QColor("#28a745")), 
                                       QBrush(QColor("#d4edda")))
        input_text = self.scene.addText("📥 Input Layer", QFont("Arial", 10))
        input_text.setPos(60, 70)
        
        # Nœud Transform
        transform_rect = self.scene.addRect(250, 50, 120, 60, 
                                          QPen(QColor("#4A90E2")), 
                                          QBrush(QColor("#d1ecf1")))
        transform_text = self.scene.addText("⚙️ Buffer", QFont("Arial", 10))
        transform_text.setPos(280, 70)
        
        # Nœud Output
        output_rect = self.scene.addRect(450, 50, 120, 60, 
                                        QPen(QColor("#dc3545")), 
                                        QBrush(QColor("#f8d7da")))
        output_text = self.scene.addText("📤 Output", QFont("Arial", 10))
        output_text.setPos(480, 70)
        
        # Connexions (lignes simples)
        line1 = self.scene.addLine(170, 80, 250, 80, QPen(QColor("#6c757d"), 2))
        line2 = self.scene.addLine(370, 80, 450, 80, QPen(QColor("#6c757d"), 2))
        
        # Flèches simples avec des ellipses au lieu de polygones
        arrow1 = self.scene.addEllipse(240, 76, 8, 8, 
                                      QPen(QColor("#6c757d")), 
                                      QBrush(QColor("#6c757d")))
        
        arrow2 = self.scene.addEllipse(440, 76, 8, 8, 
                                      QPen(QColor("#6c757d")), 
                                      QBrush(QColor("#6c757d")))

class PropertiesPanel(QWidget):
    """Panneau des propriétés pour configurer les transformers"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Propriétés du Transformer")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        
        # Exemple de propriétés pour un transformer Buffer
        form_layout = QVBoxLayout()
        
        # Distance
        distance_group = QGroupBox("Distance de Buffer")
        distance_layout = QVBoxLayout()
        distance_input = QLineEdit("10")
        distance_input.setStyleSheet("padding: 4px; border: 1px solid #dee2e6; border-radius: 3px;")
        distance_layout.addWidget(distance_input)
        distance_group.setLayout(distance_layout)
        
        # Unité
        unit_group = QGroupBox("Unité")
        unit_layout = QVBoxLayout()
        unit_combo = QComboBox()
        unit_combo.addItems(["Mètres", "Kilomètres", "Degrés"])
        unit_combo.setStyleSheet("padding: 4px; border: 1px solid #dee2e6;")
        unit_layout.addWidget(unit_combo)
        unit_group.setLayout(unit_layout)
        
        # Options avancées
        advanced_group = QGroupBox("Options Avancées")
        advanced_layout = QVBoxLayout()
        advanced_text = QTextEdit()
        advanced_text.setMaximumHeight(80)
        advanced_text.setPlaceholderText("Paramètres additionnels...")
        advanced_text.setStyleSheet("border: 1px solid #dee2e6; border-radius: 3px;")
        advanced_layout.addWidget(advanced_text)
        advanced_group.setLayout(advanced_layout)
        
        layout.addWidget(title)
        layout.addWidget(distance_group)
        layout.addWidget(unit_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        apply_btn = ModernButton("Appliquer", primary=True)
        reset_btn = ModernButton("Reset")
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

class QGISPluginUI(QMainWindow):
    """Interface principale du plugin QGIS"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.populate_transformers()
        
    def init_ui(self):
        self.setWindowTitle("QGIS GISENGINE - Version Test")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === PANNEAU GAUCHE: Liste des Transformers ===
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout()
        
        # Header avec titre et recherche
        header_layout = QVBoxLayout()
        title_label = QLabel("🛠️ Transformers QGIS")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #495057; margin: 10px 0;")
        
        self.search_box = SearchBox()
        self.search_box.textChanged.connect(self.filter_transformers)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.search_box)
        
        # Liste des transformers
        self.transformer_list = QListWidget()
        self.transformer_list.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                margin: 1px;
            }
        """)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        modeler_btn = ModernButton("Ouvrir Modeler", primary=True)
        favorites_btn = ModernButton("⭐ Favoris")
        action_layout.addWidget(modeler_btn)
        action_layout.addWidget(favorites_btn)
        
        left_layout.addLayout(header_layout)
        left_layout.addWidget(self.transformer_list)
        left_layout.addLayout(action_layout)
        left_panel.setLayout(left_layout)
        
        # === PANNEAU CENTRAL: Canvas de Workflow ===
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        
        canvas_title = QLabel("📊 Workflow Canvas")
        canvas_title.setFont(QFont("Arial", 12, QFont.Bold))
        canvas_title.setStyleSheet("color: #495057; margin: 5px 0;")
        
        self.workflow_canvas = WorkflowCanvas()
        
        # Toolbar du canvas
        canvas_toolbar = QHBoxLayout()
        zoom_in_btn = ModernButton("🔍+")
        zoom_out_btn = ModernButton("🔍-")
        fit_btn = ModernButton("📐 Ajuster")
        run_btn = ModernButton("▶️ Exécuter", primary=True)
        
        canvas_toolbar.addWidget(zoom_in_btn)
        canvas_toolbar.addWidget(zoom_out_btn)
        canvas_toolbar.addWidget(fit_btn)
        canvas_toolbar.addStretch()
        canvas_toolbar.addWidget(run_btn)
        
        center_layout.addWidget(canvas_title)
        center_layout.addWidget(self.workflow_canvas)
        center_layout.addLayout(canvas_toolbar)
        center_panel.setLayout(center_layout)
        
        # === PANNEAU DROIT: Propriétés ===
        right_panel = QWidget()
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout()
        
        props_title = QLabel("⚙️ Propriétés")
        props_title.setFont(QFont("Arial", 12, QFont.Bold))
        props_title.setStyleSheet("color: #495057; margin: 5px 0;")
        
        self.properties_panel = PropertiesPanel()
        
        right_layout.addWidget(props_title)
        right_layout.addWidget(self.properties_panel)
        right_panel.setLayout(right_layout)
        
        # Assemblage des panneaux
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([350, 700, 300])
        
        main_layout.addWidget(main_splitter)
        
        # Style global
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin: 4px 0;
                padding-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
                color: #495057;
            }
        """)
    
    def populate_transformers(self):
        """Remplit la liste avec des transformers d'exemple"""
        transformers_data = [
            ("Buffer", "Vector", "Crée une zone tampon autour des géométries", "🔲"),
            ("Clip", "Vector", "Découpe les entités avec un masque", "✂️"),
            ("Reproject", "Vector", "Change la projection des données", "🌍"),
            ("Field Calculator", "Vector", "Calcule de nouveaux champs", "🧮"),
            ("Merge", "Vector", "Fusionne plusieurs couches", "🔗"),
            ("Dissolve", "Vector", "Dissout les géométries adjacentes", "🫧"),
            ("Raster Calculator", "Raster", "Effectue des calculs sur rasters", "📊"),
            ("Warp", "Raster", "Reprojette les données raster", "🔄"),
            ("Polygonize", "Raster", "Convertit raster en polygones", "🔷"),
            ("Zonal Statistics", "Raster", "Statistiques par zones", "📈"),
            ("Join by Attributes", "Table", "Joint par attributs", "🔗"),
            ("Export to PostgreSQL", "Database", "Export vers base de données", "🗃️"),
        ]
        
        for name, category, description, icon in transformers_data:
            item = QListWidgetItem()
            widget = TransformerItem(name, category, description, icon)
            item.setSizeHint(widget.sizeHint())
            self.transformer_list.addItem(item)
            self.transformer_list.setItemWidget(item, widget)
    
    def filter_transformers(self, text):
        """Filtre les transformers selon le texte de recherche"""
        for i in range(self.transformer_list.count()):
            item = self.transformer_list.item(i)
            widget = self.transformer_list.itemWidget(item)
            if widget:
                visible = (text.lower() in widget.name.lower() or 
                          text.lower() in widget.category.lower() or
                          text.lower() in widget.description.lower())
                item.setHidden(not visible)

def main():
    app = QApplication(sys.argv)
    
    # Style global de l'application
    app.setStyle('Fusion')
    
    window = QGISPluginUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
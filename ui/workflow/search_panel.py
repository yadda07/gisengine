# -*- coding: utf-8 -*-
"""
Professional Search Panel
FME-style search with autocompletion
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ProfessionalSearchPanel(QWidget):
    """Panneau de recherche professionnel avec autocomplétion"""
    
    node_requested = pyqtSignal(dict)  # Signal émis quand un nœud est demandé
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setup_ui()
        self.setup_data()
        self.setup_connections()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        self.setStyleSheet("""
            QWidget {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: white;
                alternate-background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f1f3f4;
            }
            QListWidget::item:hover {
                background: #e3f2fd;
            }
            QListWidget::item:selected {
                background: #2196f3;
                color: white;
            }
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("Add Components")
        header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.setStyleSheet("color: #495057; margin-bottom: 5px; border: none;")
        layout.addWidget(header)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search transformers, readers, writers...")
        layout.addWidget(self.search_box)
        
        # Filter buttons
        filter_layout = QHBoxLayout()
        self.filter_all = QPushButton("All")
        self.filter_readers = QPushButton("Readers")
        self.filter_transformers = QPushButton("Transformers")
        self.filter_writers = QPushButton("Writers")
        
        for btn in [self.filter_all, self.filter_readers, self.filter_transformers, self.filter_writers]:
            btn.setCheckable(True)
            filter_layout.addWidget(btn)
        
        self.filter_all.setChecked(True)
        layout.addLayout(filter_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        layout.addWidget(self.results_list)
        
        # Quick add section
        quick_label = QLabel("Quick Add")
        quick_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        quick_label.setStyleSheet("color: #6c757d; margin-top: 10px; border: none;")
        layout.addWidget(quick_label)
        
        quick_layout = QVBoxLayout()
        quick_layout.setSpacing(4)
        
        quick_buttons = [
            ("📁 File Reader", {"type": "reader", "name": "File Reader", "category": "Input"}),
            ("🔄 Transformer", {"type": "transformer", "name": "AttributeManager", "category": "Attributes"}),
            ("💾 File Writer", {"type": "writer", "name": "File Writer", "category": "Output"})
        ]
        
        for text, data in quick_buttons:
            btn = QPushButton(text.replace("📁 ", "").replace("🔄 ", "").replace("💾 ", ""))
            btn.clicked.connect(lambda checked, d=data: self.node_requested.emit(d))
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8f9fa;
                    color: #495057;
                    text-align: left;
                    padding: 8px 12px;
                    border: 1px solid #dee2e6;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            quick_layout.addWidget(btn)
        
        layout.addLayout(quick_layout)
        layout.addStretch()
    
    def setup_data(self):
        """Configuration des données de recherche"""
        self.components_data = [
            # Readers
            {"type": "reader", "name": "File Reader", "category": "Input", "description": "Read files from disk"},
            {"type": "reader", "name": "Database Reader", "category": "Input", "description": "Read from database"},
            {"type": "reader", "name": "Web Reader", "category": "Input", "description": "Read from web services"},
            {"type": "reader", "name": "CSV Reader", "category": "Input", "description": "Read CSV files"},
            {"type": "reader", "name": "JSON Reader", "category": "Input", "description": "Read JSON files"},
            
            # Transformers
            {"type": "transformer", "name": "AttributeManager", "category": "Attributes", "description": "Manage feature attributes"},
            {"type": "transformer", "name": "Bufferer", "category": "Geometry", "description": "Create buffers around features"},
            {"type": "transformer", "name": "Clipper", "category": "Geometry", "description": "Clip features by boundary"},
            {"type": "transformer", "name": "Reprojector", "category": "Geometry", "description": "Reproject coordinates"},
            {"type": "transformer", "name": "Filter", "category": "Conditional", "description": "Filter features by condition"},
            {"type": "transformer", "name": "Sorter", "category": "Workflow", "description": "Sort features by attributes"},
            {"type": "transformer", "name": "Counter", "category": "Workflow", "description": "Count features"},
            {"type": "transformer", "name": "Inspector", "category": "Debug", "description": "Inspect feature data"},
            
            # Writers
            {"type": "writer", "name": "File Writer", "category": "Output", "description": "Write files to disk"},
            {"type": "writer", "name": "Database Writer", "category": "Output", "description": "Write to database"},
            {"type": "writer", "name": "Web Writer", "category": "Output", "description": "Write to web services"},
            {"type": "writer", "name": "CSV Writer", "category": "Output", "description": "Write CSV files"},
            {"type": "writer", "name": "JSON Writer", "category": "Output", "description": "Write JSON files"},
        ]
        
        self.filtered_data = self.components_data.copy()
        self.update_results_list()
    
    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.search_box.textChanged.connect(self.filter_components)
        self.results_list.itemDoubleClicked.connect(self.add_selected_component)
        
        # Filter buttons
        self.filter_all.clicked.connect(lambda: self.set_filter("all"))
        self.filter_readers.clicked.connect(lambda: self.set_filter("reader"))
        self.filter_transformers.clicked.connect(lambda: self.set_filter("transformer"))
        self.filter_writers.clicked.connect(lambda: self.set_filter("writer"))
        
        # Keyboard shortcuts
        self.search_box.returnPressed.connect(self.add_first_result)
    
    def filter_components(self, text):
        """Filtrer les composants selon le texte de recherche"""
        text = text.lower()
        self.filtered_data = [
            comp for comp in self.components_data
            if text in comp['name'].lower() or 
               text in comp['category'].lower() or
               text in comp['description'].lower()
        ]
        self.update_results_list()
    
    def set_filter(self, filter_type):
        """Définir le filtre par type"""
        # Reset all buttons
        for btn in [self.filter_all, self.filter_readers, self.filter_transformers, self.filter_writers]:
            btn.setChecked(False)
        
        # Set active button
        if filter_type == "all":
            self.filter_all.setChecked(True)
            self.filtered_data = self.components_data.copy()
        elif filter_type == "reader":
            self.filter_readers.setChecked(True)
            self.filtered_data = [c for c in self.components_data if c['type'] == 'reader']
        elif filter_type == "transformer":
            self.filter_transformers.setChecked(True)
            self.filtered_data = [c for c in self.components_data if c['type'] == 'transformer']
        elif filter_type == "writer":
            self.filter_writers.setChecked(True)
            self.filtered_data = [c for c in self.components_data if c['type'] == 'writer']
        
        # Apply search filter if active
        search_text = self.search_box.text()
        if search_text:
            self.filter_components(search_text)
        else:
            self.update_results_list()
    
    def update_results_list(self):
        """Mettre à jour la liste des résultats"""
        self.results_list.clear()
        
        for comp in self.filtered_data:
            item = QListWidgetItem()
            
            # Icon selon le type
            if comp['type'] == 'reader':
                icon = "📁"
            elif comp['type'] == 'writer':
                icon = "💾"
            else:
                icon = "🔄"
            
            # Texte sans emoji pour design professionnel
            text = f"{comp['name']}\n{comp['category']} - {comp['description']}"
            item.setText(text)
            item.setData(Qt.UserRole, comp)
            
            self.results_list.addItem(item)
    
    def add_selected_component(self, item):
        """Ajouter le composant sélectionné"""
        comp_data = item.data(Qt.UserRole)
        if comp_data:
            self.node_requested.emit(comp_data)
    
    def add_first_result(self):
        """Ajouter le premier résultat (Enter dans search box)"""
        if self.results_list.count() > 0:
            first_item = self.results_list.item(0)
            self.add_selected_component(first_item)
    
    def keyPressEvent(self, event):
        """Gestion des raccourcis clavier"""
        if event.key() == Qt.Key_Escape:
            self.search_box.clear()
        elif event.key() == Qt.Key_Down and self.search_box.hasFocus():
            if self.results_list.count() > 0:
                self.results_list.setFocus()
                self.results_list.setCurrentRow(0)
        
        super().keyPressEvent(event)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'intégration avec QGIS Processing Framework
Scanner et utiliser les algorithmes existants de QGIS
"""

import sys
import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QComboBox, QTextEdit,
    QTabWidget, QSplitter, QGroupBox, QLineEdit, QCheckBox,
    QProgressBar, QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

@dataclass
class AlgorithmParameter:
    """Représente un paramètre d'algorithme QGIS"""
    name: str
    description: str
    param_type: str
    default_value: Any = None
    optional: bool = False
    values: List[str] = field(default_factory=list)

@dataclass
class QGISAlgorithm:
    """Représente un algorithme QGIS Processing"""
    id: str
    name: str
    group: str
    provider: str
    description: str
    parameters: List[AlgorithmParameter] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

class AlgorithmScanner(QThread):
    """Thread pour scanner les algorithmes QGIS en arrière-plan"""
    
    algorithm_found = pyqtSignal(QGISAlgorithm)
    scan_finished = pyqtSignal(int)
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.algorithms = []
        
    def run(self):
        """Scanner simulé des algorithmes QGIS"""
        # En réalité, ici on utiliserait :
        # from qgis.core import QgsApplication, QgsProcessingRegistry
        # registry = QgsApplication.processingRegistry()
        
        # Simulation d'algorithmes QGIS réels
        sample_algorithms = [
            # Algorithmes Vector
            {
                "id": "native:buffer",
                "name": "Buffer",
                "group": "Vector geometry",
                "provider": "QGIS (native c++)",
                "description": "Compute buffer zones around input features",
                "parameters": [
                    ("INPUT", "Input layer", "vector", None, False),
                    ("DISTANCE", "Distance", "number", 10.0, False),
                    ("SEGMENTS", "Segments", "number", 5, True),
                    ("END_CAP_STYLE", "End cap style", "enum", 0, True, ["Round", "Flat", "Square"]),
                    ("JOIN_STYLE", "Join style", "enum", 0, True, ["Round", "Miter", "Bevel"]),
                    ("MITER_LIMIT", "Miter limit", "number", 2.0, True),
                    ("DISSOLVE", "Dissolve result", "boolean", False, True),
                    ("OUTPUT", "Buffered", "sink", None, False)
                ],
                "outputs": ["OUTPUT"],
                "tags": ["buffer", "geometry", "zone"]
            },
            {
                "id": "native:clip",
                "name": "Clip",
                "group": "Vector overlay",
                "provider": "QGIS (native c++)",
                "description": "Clip features using another layer",
                "parameters": [
                    ("INPUT", "Input layer", "vector", None, False),
                    ("OVERLAY", "Overlay layer", "vector", None, False),
                    ("OUTPUT", "Clipped", "sink", None, False)
                ],
                "outputs": ["OUTPUT"],
                "tags": ["clip", "overlay", "cut"]
            },
            {
                "id": "native:reprojectlayer",
                "name": "Reproject layer",
                "group": "Vector general",
                "provider": "QGIS (native c++)",
                "description": "Reproject a vector layer to a different CRS",
                "parameters": [
                    ("INPUT", "Input layer", "vector", None, False),
                    ("TARGET_CRS", "Target CRS", "crs", "EPSG:4326", False),
                    ("OUTPUT", "Reprojected", "sink", None, False)
                ],
                "outputs": ["OUTPUT"],
                "tags": ["reproject", "crs", "coordinate"]
            },
            {
                "id": "native:fieldcalculator",
                "name": "Field calculator",
                "group": "Vector table",
                "provider": "QGIS (native c++)",
                "description": "Calculate field values using expressions",
                "parameters": [
                    ("INPUT", "Input layer", "vector", None, False),
                    ("FIELD_NAME", "Field name", "string", "new_field", False),
                    ("FIELD_TYPE", "Field type", "enum", 0, False, ["Integer", "Float", "String"]),
                    ("FIELD_LENGTH", "Field length", "number", 10, True),
                    ("FIELD_PRECISION", "Field precision", "number", 3, True),
                    ("FORMULA", "Formula", "expression", "", False),
                    ("OUTPUT", "Calculated", "sink", None, False)
                ],
                "outputs": ["OUTPUT"],
                "tags": ["field", "calculate", "expression"]
            },
            # Algorithmes Raster
            {
                "id": "gdal:warpreproject",
                "name": "Warp (reproject)",
                "group": "Raster projections",
                "provider": "GDAL",
                "description": "Reproject raster to different coordinate system",
                "parameters": [
                    ("INPUT", "Input layer", "raster", None, False),
                    ("TARGET_CRS", "Target CRS", "crs", "EPSG:4326", False),
                    ("RESAMPLING", "Resampling method", "enum", 0, True, ["Nearest", "Bilinear", "Cubic"]),
                    ("OUTPUT", "Reprojected", "rasterDestination", None, False)
                ],
                "outputs": ["OUTPUT"],
                "tags": ["reproject", "warp", "raster"]
            },
            {
                "id": "gdal:rastercalculator",
                "name": "Raster calculator",
                "group": "Raster analysis",
                "provider": "GDAL",
                "description": "Perform mathematical operations on raster bands",
                "parameters": [
                    ("INPUT_A", "Input layer A", "raster", None, False),
                    ("BAND_A", "Band A", "band", 1, False),
                    ("INPUT_B", "Input layer B", "raster", None, True),
                    ("BAND_B", "Band B", "band", 1, True),
                    ("FORMULA", "Formula", "string", "A", False),
                    ("OUTPUT", "Calculated", "rasterDestination", None, False)
                ],
                "outputs": ["OUTPUT"],
                "tags": ["calculator", "math", "bands"]
            },
            # Algorithmes de base de données
            {
                "id": "native:importintospatialite",
                "name": "Import into SpatiaLite",
                "group": "Database",
                "provider": "QGIS (native c++)",
                "description": "Import vector layer into SpatiaLite database",
                "parameters": [
                    ("INPUT", "Input layer", "vector", None, False),
                    ("DATABASE", "Database file", "fileDestination", None, False),
                    ("TABLENAME", "Table name", "string", "", False),
                    ("PRIMARY_KEY", "Primary key field", "string", "id", True),
                    ("GEOMETRY_COLUMN", "Geometry column name", "string", "geom", True),
                    ("ENCODING", "Encoding", "string", "UTF-8", True)
                ],
                "outputs": [],
                "tags": ["database", "spatialite", "import"]
            }
        ]
        
        total = len(sample_algorithms)
        
        for i, alg_data in enumerate(sample_algorithms):
            # Simulation du temps de traitement
            self.msleep(100)
            
            # Création de l'objet Algorithm
            parameters = []
            for param_data in alg_data["parameters"]:
                param = AlgorithmParameter(
                    name=param_data[0],
                    description=param_data[1],
                    param_type=param_data[2],
                    default_value=param_data[3] if len(param_data) > 3 else None,
                    optional=param_data[4] if len(param_data) > 4 else False,
                    values=param_data[5] if len(param_data) > 5 else []
                )
                parameters.append(param)
            
            algorithm = QGISAlgorithm(
                id=alg_data["id"],
                name=alg_data["name"],
                group=alg_data["group"],
                provider=alg_data["provider"],
                description=alg_data["description"],
                parameters=parameters,
                outputs=alg_data["outputs"],
                tags=alg_data["tags"]
            )
            
            self.algorithms.append(algorithm)
            self.algorithm_found.emit(algorithm)
            self.progress_updated.emit(int((i + 1) / total * 100), f"Scanning {algorithm.name}...")
        
        self.scan_finished.emit(len(self.algorithms))

class ParameterWidget(QWidget):
    """Widget pour configurer un paramètre d'algorithme"""
    
    def __init__(self, parameter: AlgorithmParameter):
        super().__init__()
        self.parameter = parameter
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        
        # Label du paramètre
        label = QLabel(self.parameter.description)
        label.setMinimumWidth(150)
        if not self.parameter.optional:
            label.setStyleSheet("font-weight: bold; color: #dc3545;")
        
        # Widget de saisie selon le type
        if self.parameter.param_type == "vector":
            self.widget = QComboBox()
            self.widget.addItems(["<Sélectionner une couche>", "Couche 1", "Couche 2"])
        elif self.parameter.param_type == "raster":
            self.widget = QComboBox()
            self.widget.addItems(["<Sélectionner un raster>", "Raster 1", "Raster 2"])
        elif self.parameter.param_type == "number":
            self.widget = QDoubleSpinBox()
            self.widget.setRange(-999999, 999999)
            if self.parameter.default_value is not None:
                self.widget.setValue(float(self.parameter.default_value))
        elif self.parameter.param_type == "string":
            self.widget = QLineEdit()
            if self.parameter.default_value:
                self.widget.setText(str(self.parameter.default_value))
        elif self.parameter.param_type == "boolean":
            self.widget = QCheckBox()
            if self.parameter.default_value:
                self.widget.setChecked(bool(self.parameter.default_value))
        elif self.parameter.param_type == "enum":
            self.widget = QComboBox()
            self.widget.addItems(self.parameter.values)
            if self.parameter.default_value is not None:
                self.widget.setCurrentIndex(int(self.parameter.default_value))
        elif self.parameter.param_type in ["sink", "fileDestination", "rasterDestination"]:
            file_layout = QHBoxLayout()
            self.widget = QLineEdit()
            browse_btn = QPushButton("📁")
            browse_btn.setMaximumWidth(30)
            browse_btn.clicked.connect(self.browse_file)
            file_layout.addWidget(self.widget)
            file_layout.addWidget(browse_btn)
            file_widget = QWidget()
            file_widget.setLayout(file_layout)
            self.widget = file_widget
        else:
            self.widget = QLineEdit()
            self.widget.setPlaceholderText(f"Type: {self.parameter.param_type}")
        
        layout.addWidget(label)
        layout.addWidget(self.widget)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """Ouvre un dialog de sélection de fichier"""
        filename, _ = QFileDialog.getSaveFileName(
            self, f"Sélectionner le fichier de sortie", "", 
            "Tous les fichiers (*.*)"
        )
        if filename:
            if hasattr(self.widget, 'layout'):
                line_edit = self.widget.layout().itemAt(0).widget()
                line_edit.setText(filename)
    
    def get_value(self):
        """Récupère la valeur du paramètre"""
        if isinstance(self.widget, QComboBox):
            return self.widget.currentText()
        elif isinstance(self.widget, (QSpinBox, QDoubleSpinBox)):
            return self.widget.value()
        elif isinstance(self.widget, QLineEdit):
            return self.widget.text()
        elif isinstance(self.widget, QCheckBox):
            return self.widget.isChecked()
        elif hasattr(self.widget, 'layout'):
            # Pour les widgets de fichier
            line_edit = self.widget.layout().itemAt(0).widget()
            return line_edit.text()
        return None

class AlgorithmConfigWidget(QWidget):
    """Widget pour configurer un algorithme"""
    
    def __init__(self, algorithm: QGISAlgorithm):
        super().__init__()
        self.algorithm = algorithm
        self.parameter_widgets = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel(f"⚙️ {self.algorithm.name}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        
        description = QLabel(self.algorithm.description)
        description.setWordWrap(True)
        description.setStyleSheet("color: #6c757d; font-style: italic;")
        
        provider = QLabel(f"Provider: {self.algorithm.provider}")
        provider.setStyleSheet("color: #495057; font-size: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(description)
        header_layout.addWidget(provider)
        
        # Paramètres
        params_group = QGroupBox("Paramètres")
        params_layout = QVBoxLayout()
        
        for param in self.algorithm.parameters:
            param_widget = ParameterWidget(param)
            self.parameter_widgets[param.name] = param_widget
            params_layout.addWidget(param_widget)
        
        params_group.setLayout(params_layout)
        
        # Boutons
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("🔄 Reset")
        test_btn = QPushButton("🧪 Test")
        run_btn = QPushButton("▶️ Exécuter")
        
        reset_btn.clicked.connect(self.reset_parameters)
        test_btn.clicked.connect(self.test_algorithm)
        run_btn.clicked.connect(self.run_algorithm)
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        button_layout.addWidget(run_btn)
        
        layout.addLayout(header_layout)
        layout.addWidget(params_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def reset_parameters(self):
        """Remet les paramètres à leurs valeurs par défaut"""
        # Implementation du reset
        pass
    
    def test_algorithm(self):
        """Teste la configuration de l'algorithme"""
        QMessageBox.information(self, "Test", f"Test de {self.algorithm.name}")
    
    def run_algorithm(self):
        """Exécute l'algorithme avec les paramètres configurés"""
        params = {}
        for name, widget in self.parameter_widgets.items():
            params[name] = widget.get_value()
        
        QMessageBox.information(
            self, "Exécution", 
            f"Exécution de {self.algorithm.name}\nParamètres: {params}"
        )

class QGISProcessingIntegration(QMainWindow):
    """Interface principale pour l'intégration Processing"""
    
    def __init__(self):
        super().__init__()
        self.algorithms = {}
        self.current_algorithm = None
        self.init_ui()
        self.start_scanning()
    
    def init_ui(self):
        self.setWindowTitle("QGIS Processing Integration - Scanner d'Algorithmes")
        self.setGeometry(100, 100, 1400, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton("🔄 Re-scanner")
        self.scan_btn.clicked.connect(self.start_scanning)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher un algorithme...")
        self.search_box.textChanged.connect(self.filter_algorithms)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("Prêt")
        
        toolbar_layout.addWidget(self.scan_btn)
        toolbar_layout.addWidget(self.search_box)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.progress_bar)
        toolbar_layout.addWidget(self.status_label)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        
        # === PANNEAU GAUCHE: Liste des algorithmes ===
        left_widget = QWidget()
        left_widget.setMaximumWidth(400)
        left_layout = QVBoxLayout()
        
        # Arbre des algorithmes
        self.algorithm_tree = QTreeWidget()
        self.algorithm_tree.setHeaderLabels(["Algorithmes", "Provider"])
        self.algorithm_tree.itemClicked.connect(self.on_algorithm_selected)
        
        left_layout.addWidget(QLabel("📋 Algorithmes Disponibles"))
        left_layout.addWidget(self.algorithm_tree)
        left_widget.setLayout(left_layout)
        
        # === PANNEAU DROIT: Configuration ===
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Tabs
        self.tab_widget = QTabWidget()
        
        # Tab Configuration
        self.config_scroll = QScrollArea()
        self.config_scroll.setWidgetResizable(True)
        self.tab_widget.addTab(self.config_scroll, "⚙️ Configuration")
        
        # Tab JSON Export
        self.json_text = QTextEdit()
        self.json_text.setFont(QFont("Courier", 10))
        self.tab_widget.addTab(self.json_text, "📄 JSON Export")
        
        # Tab Documentation
        self.doc_text = QTextEdit()
        self.doc_text.setReadOnly(True)
        self.tab_widget.addTab(self.doc_text, "📖 Documentation")
        
        right_layout.addWidget(self.tab_widget)
        right_widget.setLayout(right_layout)
        
        # Assemblage
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([400, 1000])
        
        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(main_splitter)
        
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background: #ffffff;
            }
            QTreeWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: #f8f9fa;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTreeWidget::item:selected {
                background: #4A90E2;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: #f8f9fa;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin: 4px 0;
                padding-top: 6px;
            }
        """)
    
    def start_scanning(self):
        """Démarre le scan des algorithmes"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Scanning algorithms...")
        self.scan_btn.setEnabled(False)
        
        # Clear existing data
        self.algorithm_tree.clear()
        self.algorithms.clear()
        
        # Start scanner thread
        self.scanner = AlgorithmScanner()
        self.scanner.algorithm_found.connect(self.on_algorithm_found)
        self.scanner.progress_updated.connect(self.on_progress_updated)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.start()
    
    def on_algorithm_found(self, algorithm: QGISAlgorithm):
        """Appelé quand un algorithme est trouvé"""
        self.algorithms[algorithm.id] = algorithm
        
        # Ajouter à l'arbre
        # Trouver ou créer le groupe
        group_items = self.algorithm_tree.findItems(algorithm.group, Qt.MatchExactly, 0)
        if group_items:
            group_item = group_items[0]
        else:
            group_item = QTreeWidgetItem([algorithm.group, ""])
            group_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            self.algorithm_tree.addTopLevelItem(group_item)
        
        # Ajouter l'algorithme
        alg_item = QTreeWidgetItem([algorithm.name, algorithm.provider])
        alg_item.setData(0, Qt.UserRole, algorithm.id)
        group_item.addChild(alg_item)
        
        # Expand group
        group_item.setExpanded(True)
    
    def on_progress_updated(self, progress: int, message: str):
        """Met à jour la barre de progression"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def on_scan_finished(self, count: int):
        """Appelé quand le scan est terminé"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Scan terminé - {count} algorithmes trouvés")
        self.scan_btn.setEnabled(True)
        
        # Sort tree
        self.algorithm_tree.sortItems(0, Qt.AscendingOrder)
    
    def on_algorithm_selected(self, item: QTreeWidgetItem, column: int):
        """Appelé quand un algorithme est sélectionné"""
        algorithm_id = item.data(0, Qt.UserRole)
        if not algorithm_id:
            return
        
        algorithm = self.algorithms.get(algorithm_id)
        if not algorithm:
            return
        
        self.current_algorithm = algorithm
        
        # Mise à jour de l'interface de configuration
        config_widget = AlgorithmConfigWidget(algorithm)
        self.config_scroll.setWidget(config_widget)
        
        # Mise à jour du JSON
        self.update_json_export(algorithm)
        
        # Mise à jour de la documentation
        self.update_documentation(algorithm)
    
    def update_json_export(self, algorithm: QGISAlgorithm):
        """Met à jour l'export JSON de l'algorithme"""
        data = {
            "id": algorithm.id,
            "name": algorithm.name,
            "group": algorithm.group,
            "provider": algorithm.provider,
            "description": algorithm.description,
            "parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "type": p.param_type,
                    "default": p.default_value,
                    "optional": p.optional,
                    "values": p.values
                }
                for p in algorithm.parameters
            ],
            "outputs": algorithm.outputs,
            "tags": algorithm.tags
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.json_text.setPlainText(json_str)
    
    def update_documentation(self, algorithm: QGISAlgorithm):
        """Met à jour la documentation de l'algorithme"""
        doc = f"""
<h2>📖 {algorithm.name}</h2>
<p><strong>ID:</strong> {algorithm.id}</p>
<p><strong>Groupe:</strong> {algorithm.group}</p>
<p><strong>Provider:</strong> {algorithm.provider}</p>

<h3>Description</h3>
<p>{algorithm.description}</p>

<h3>Paramètres</h3>
<table border="1" cellpadding="5" cellspacing="0">
<tr><th>Nom</th><th>Description</th><th>Type</th><th>Optionnel</th></tr>
"""
        
        for param in algorithm.parameters:
            optional_text = "✅" if param.optional else "❌"
            doc += f"""
<tr>
    <td><strong>{param.name}</strong></td>
    <td>{param.description}</td>
    <td>{param.param_type}</td>
    <td>{optional_text}</td>
</tr>
"""
        
        doc += "</table>"
        
        if algorithm.outputs:
            doc += "<h3>Sorties</h3><ul>"
            for output in algorithm.outputs:
                doc += f"<li>{output}</li>"
            doc += "</ul>"
        
        if algorithm.tags:
            doc += "<h3>Tags</h3><p>" + ", ".join(algorithm.tags) + "</p>"
        
        self.doc_text.setHtml(doc)
    
    def filter_algorithms(self, text: str):
        """Filtre les algorithmes selon le texte de recherche"""
        def filter_item(item):
            text_lower = text.lower()
            item_text = item.text(0).lower()
            
            # Vérifier si l'item correspond
            matches = text_lower in item_text
            
            # Pour les groupes, vérifier aussi les enfants
            if item.childCount() > 0:
                child_matches = False
                for i in range(item.childCount()):
                    child = item.child(i)
                    if filter_item(child):
                        child_matches = True
                
                # Un groupe est visible si lui-même ou ses enfants correspondent
                item.setHidden(not (matches or child_matches))
                return matches or child_matches
            else:
                item.setHidden(not matches)
                return matches
        
        # Appliquer le filtre à tous les items de niveau supérieur
        for i in range(self.algorithm_tree.topLevelItemCount()):
            item = self.algorithm_tree.topLevelItem(i)
            filter_item(item)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = QGISProcessingIntegration()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
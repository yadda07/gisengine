"""
Template d'interface utilisateur pour composant GISENGINE
Interface de configuration des paramètres du composant
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QSpinBox,
    QComboBox, QCheckBox, QPushButton, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon

from qgis.core import QgsVectorLayer, QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox, QgsFileWidget

from ...core.interfaces import ComponentMetadata


class MyComponentTemplateUI(QWidget):
    """
    Interface utilisateur pour MyComponentTemplate
    
    Cette classe crée l'interface de configuration des paramètres
    du composant dans le workflow designer.
    """
    
    # Signaux émis quand les paramètres changent
    parameters_changed = pyqtSignal(dict)
    validation_changed = pyqtSignal(bool)  # True si valide, False sinon
    
    def __init__(self, metadata: ComponentMetadata, parent=None):
        super().__init__(parent)
        self.metadata = metadata
        self.parameters = {}
        self._setup_ui()
        self._connect_signals()
        self._load_default_values()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # En-tête avec icône et titre
        self._create_header(layout)
        
        # Paramètres principaux
        self._create_main_parameters(layout)
        
        # Paramètres avancés (repliables)
        self._create_advanced_parameters(layout)
        
        # Boutons d'action
        self._create_action_buttons(layout)
        
        # Barre de progression (cachée par défaut)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Étirer l'espace restant
        layout.addStretch()
    
    def _create_header(self, parent_layout):
        """Crée l'en-tête avec icône et titre"""
        header_layout = QHBoxLayout()
        
        # Icône du composant
        icon_label = QLabel()
        icon_path = self.metadata.get('ui_config', {}).get('icon')
        if icon_path:
            pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🔧")  # Icône par défaut
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Titre et description
        title_layout = QVBoxLayout()
        title_label = QLabel(f"<h3>{self.metadata.get('display_name', 'Composant')}</h3>")
        description_label = QLabel(self.metadata.get('description', ''))
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #666; font-size: 11px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(description_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def _create_main_parameters(self, parent_layout):
        """Crée les paramètres principaux"""
        main_group = QGroupBox("Paramètres")
        main_layout = QFormLayout(main_group)
        
        # Couche d'entrée
        self.input_layer_combo = QgsMapLayerComboBox()
        self.input_layer_combo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.input_layer_combo.setAllowEmptyLayer(False)
        main_layout.addRow("Couche d'entrée:", self.input_layer_combo)
        
        # Distance du tampon
        self.buffer_distance_spin = QDoubleSpinBox()
        self.buffer_distance_spin.setRange(0.1, 999999.0)
        self.buffer_distance_spin.setValue(100.0)
        self.buffer_distance_spin.setSuffix(" unités")
        self.buffer_distance_spin.setDecimals(2)
        main_layout.addRow("Distance du tampon:", self.buffer_distance_spin)
        
        parent_layout.addWidget(main_group)
    
    def _create_advanced_parameters(self, parent_layout):
        """Crée les paramètres avancés (repliables)"""
        advanced_group = QGroupBox("Paramètres avancés")
        advanced_group.setCheckable(True)
        advanced_group.setChecked(False)  # Replié par défaut
        
        advanced_layout = QFormLayout(advanced_group)
        
        # Nom de la couche de sortie
        self.output_name_edit = QLineEdit("result")
        self.output_name_edit.setPlaceholderText("Nom de la couche résultat")
        advanced_layout.addRow("Nom de sortie:", self.output_name_edit)
        
        # Options supplémentaires (exemple)
        self.preserve_attributes_check = QCheckBox("Conserver les attributs")
        self.preserve_attributes_check.setChecked(True)
        advanced_layout.addRow("", self.preserve_attributes_check)
        
        parent_layout.addWidget(advanced_group)
    
    def _create_action_buttons(self, parent_layout):
        """Crée les boutons d'action"""
        button_layout = QHBoxLayout()
        
        # Bouton de validation
        self.validate_button = QPushButton("Valider les paramètres")
        self.validate_button.clicked.connect(self._validate_parameters)
        
        # Bouton de réinitialisation
        self.reset_button = QPushButton("Réinitialiser")
        self.reset_button.clicked.connect(self._reset_parameters)
        
        # Bouton d'aide
        self.help_button = QPushButton("Aide")
        self.help_button.clicked.connect(self._show_help)
        
        button_layout.addWidget(self.validate_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.help_button)
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connecte les signaux des widgets"""
        # Connecter tous les widgets aux changements de paramètres
        self.input_layer_combo.layerChanged.connect(self._on_parameters_changed)
        self.buffer_distance_spin.valueChanged.connect(self._on_parameters_changed)
        self.output_name_edit.textChanged.connect(self._on_parameters_changed)
        self.preserve_attributes_check.toggled.connect(self._on_parameters_changed)
    
    def _load_default_values(self):
        """Charge les valeurs par défaut depuis les métadonnées"""
        params_meta = self.metadata.get('parameters', {})
        
        # Distance du tampon
        if 'buffer_distance' in params_meta:
            default_distance = params_meta['buffer_distance'].get('default', 100.0)
            self.buffer_distance_spin.setValue(default_distance)
        
        # Nom de sortie
        if 'output_name' in params_meta:
            default_name = params_meta['output_name'].get('default', 'result')
            self.output_name_edit.setText(default_name)
        
        # Mettre à jour les paramètres
        self._on_parameters_changed()
    
    def _on_parameters_changed(self):
        """Appelé quand les paramètres changent"""
        # Collecter tous les paramètres
        self.parameters = self.get_parameters()
        
        # Valider les paramètres
        is_valid = self._validate_current_parameters()
        
        # Émettre les signaux
        self.parameters_changed.emit(self.parameters)
        self.validation_changed.emit(is_valid)
        
        # Mettre à jour l'état du bouton de validation
        self.validate_button.setEnabled(is_valid)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Récupère les paramètres actuels de l'interface
        
        Returns:
            Dictionnaire des paramètres
        """
        return {
            'input_layer': self.input_layer_combo.currentLayer(),
            'buffer_distance': self.buffer_distance_spin.value(),
            'output_name': self.output_name_edit.text().strip() or 'result',
            'preserve_attributes': self.preserve_attributes_check.isChecked()
        }
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """
        Définit les paramètres dans l'interface
        
        Args:
            parameters: Dictionnaire des paramètres à définir
        """
        # Bloquer les signaux temporairement
        self.blockSignals(True)
        
        try:
            if 'input_layer' in parameters:
                layer = parameters['input_layer']
                if isinstance(layer, QgsVectorLayer):
                    self.input_layer_combo.setLayer(layer)
            
            if 'buffer_distance' in parameters:
                self.buffer_distance_spin.setValue(parameters['buffer_distance'])
            
            if 'output_name' in parameters:
                self.output_name_edit.setText(str(parameters['output_name']))
            
            if 'preserve_attributes' in parameters:
                self.preserve_attributes_check.setChecked(parameters['preserve_attributes'])
        
        finally:
            # Réactiver les signaux
            self.blockSignals(False)
            self._on_parameters_changed()
    
    def _validate_current_parameters(self) -> bool:
        """
        Valide les paramètres actuels
        
        Returns:
            True si les paramètres sont valides
        """
        # Vérifier la couche d'entrée
        if not self.input_layer_combo.currentLayer():
            return False
        
        # Vérifier la distance
        if self.buffer_distance_spin.value() <= 0:
            return False
        
        # Vérifier le nom de sortie
        if not self.output_name_edit.text().strip():
            return False
        
        return True
    
    def _validate_parameters(self):
        """Action du bouton de validation"""
        if self._validate_current_parameters():
            QMessageBox.information(
                self,
                "Validation",
                "Les paramètres sont valides ✓"
            )
        else:
            QMessageBox.warning(
                self,
                "Validation",
                "Certains paramètres sont invalides. Veuillez les corriger."
            )
    
    def _reset_parameters(self):
        """Réinitialise les paramètres aux valeurs par défaut"""
        reply = QMessageBox.question(
            self,
            "Réinitialisation",
            "Voulez-vous vraiment réinitialiser tous les paramètres ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._load_default_values()
    
    def _show_help(self):
        """Affiche l'aide du composant"""
        from PyQt5.QtWidgets import QDialog, QTextBrowser, QVBoxLayout, QPushButton
        
        # Créer une fenêtre d'aide
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle(f"Aide - {self.metadata.get('display_name', 'Composant')}")
        help_dialog.resize(600, 400)
        
        layout = QVBoxLayout(help_dialog)
        
        # Navigateur de texte pour afficher l'aide HTML
        help_browser = QTextBrowser()
        
        # Charger le texte d'aide depuis les métadonnées ou le composant
        help_text = self.metadata.get('help_text', '<p>Aucune aide disponible.</p>')
        help_browser.setHtml(help_text)
        
        layout.addWidget(help_browser)
        
        # Bouton fermer
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(help_dialog.accept)
        layout.addWidget(close_button)
        
        help_dialog.exec_()
    
    def show_progress(self, value: int, maximum: int = 100, text: str = ""):
        """
        Affiche la progression d'une opération
        
        Args:
            value: Valeur actuelle
            maximum: Valeur maximum
            text: Texte descriptif
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{text} (%p%)" if text else "%p%")
        self.progress_bar.setVisible(True)
    
    def hide_progress(self):
        """Cache la barre de progression"""
        self.progress_bar.setVisible(False)
    
    def get_validation_errors(self) -> list:
        """
        Retourne la liste des erreurs de validation
        
        Returns:
            Liste des messages d'erreur
        """
        errors = []
        
        if not self.input_layer_combo.currentLayer():
            errors.append("Aucune couche d'entrée sélectionnée")
        
        if self.buffer_distance_spin.value() <= 0:
            errors.append("La distance doit être positive")
        
        if not self.output_name_edit.text().strip():
            errors.append("Le nom de sortie ne peut pas être vide")
        
        return errors

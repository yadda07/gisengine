# GISENGINE - Changelog

## Version 1.0.0 - Renommage FME vers GISENGINE

### Changements majeurs
- **Renommage complet du plugin** : De "FME-like Workbench" vers "GISENGINE"
- **Suppression de toutes les références FME** dans le code, l'interface utilisateur et la documentation
- **Nouveau nom de dossier** : `gisengine` (au lieu de `qgis_fme_plugin`)
- **Nouveau fichier principal** : `gisengine_plugin.py` (au lieu de `fme_workbench_plugin.py`)

### Fichiers modifiés
- `metadata.txt` : Mise à jour des métadonnées du plugin
- `gisengine_plugin.py` : Renommage et mise à jour de la classe principale
- `__init__.py` : Mise à jour du point d'entrée
- `ui/unified_interface.py` : Renommage de la classe d'interface principale
- `ui/workflow_mapper.py` : Mise à jour des références d'interface
- `ui/qgis_plugin_ui.py` : Mise à jour des titres et références

### Fonctionnalités conservées
- Interface moderne et intuitive pour chaîner des traitements géomatiques
- Scanner dynamique de la Processing Toolbox QGIS
- Recherche par mots-clés et filtrage par catégories
- Intégration avec le Processing Modeler QGIS
- Architecture modulaire

### Stack technique
- Python >= 3.9
- QGIS >= 3.28
- PyQt5/PyQt6

### Prochaines étapes
- Tests d'intégration dans QGIS
- Correction des warnings de lint PyQt
- Documentation utilisateur
- Exemples de workflows

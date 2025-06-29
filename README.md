# GISENGINE - Plugin QGIS

**GISENGINE** est un plugin QGIS moderne qui reproduit le principe des workbenches de traitement géomatique en s'appuyant sur les algorithmes existants du Processing Framework de QGIS.

## Fonctionnalités

### Interface Moderne

- **Interface unifiée** avec onglets pour une navigation fluide
- **Canvas interactif** pour la création visuelle de workflows
- **Recherche intelligente** avec filtrage par catégories
- **Bibliothèque de transformers** organisée et accessible

### Fonctionnalités Avancées

- **Scanner dynamique** de la Processing Toolbox QGIS
- **Glisser-déposer** pour créer des workflows
- **Connexions visuelles** entre les transformers
- **Exécution pas-à-pas** avec logs détaillés
- **Sauvegarde/chargement** des workflows

### Intégration QGIS

- **Compatibilité totale** avec les algorithmes QGIS
- **Intégration Processing Modeler** pour les workflows complexes
- **Gestion des projets** QGIS intégrée

## 🔧 Installation

1. Copiez le dossier `gisengine` dans votre répertoire de plugins QGIS
2. Activez le plugin dans QGIS : **Extensions > Gestionnaire d'extensions**
3. Lancez GISENGINE depuis le menu **Extensions > GISENGINE**

## Utilisation

### Démarrage rapide

1. **Ouvrez GISENGINE** depuis le menu Extensions
2. **Explorez la bibliothèque** de transformers dans le panneau de gauche
3. **Glissez-déposez** des transformers sur le canvas
4. **Connectez les transformers** en cliquant sur les ports d'entrée/sortie
5. **Exécutez votre workflow** avec le bouton Play

### Raccourcis clavier

- **Espace** : Recherche rapide de transformers
- **I** : Ajouter un transformer d'entrée
- **O** : Ajouter un transformer de sortie
- **Ctrl+S** : Sauvegarder le workflow
- **Ctrl+O** : Ouvrir un workflow

## Architecture

### Structure modulaire

```
gisengine/
├── gisengine_plugin.py     # Plugin principal
├── metadata.txt            # Métadonnées QGIS
├── ui/                     # Interfaces utilisateur
│   ├── unified_interface.py
│   ├── workflow_mapper.py
│   └── qgis_plugin_ui.py
├── core/                   # Logique métier
│   ├── algorithm_scanner.py
│   ├── workflow_engine.py
│   └── mapping_engine.py
└── tests/                  # Tests unitaires
```

### Classes principales

- `GISENGINEPlugin` : Classe principale du plugin
- `UnifiedGISENGINEInterface` : Interface utilisateur unifiée
- `WorkflowTestWindow` : Fenêtre de test des workflows

## 🛠️ Développement

### Prérequis

- Python >= 3.9
- QGIS >= 3.28
- PyQt5 ou PyQt6

### Configuration de développement

```bash
# Cloner le projet
git clone <repository-url>

# Lien symbolique vers le répertoire QGIS
ln -s /path/to/gisengine ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Tests

```bash
# Exécuter les tests unitaires
python -m pytest tests/

# Tests d'intégration
python tests/test_integration.py
```

## Roadmap

### Version 1.1

- [ ] Amélioration de l'interface utilisateur
- [ ] Nouveaux transformers personnalisés
- [ ] Export vers Processing Modeler
- [ ] Historique des exécutions

### Version 1.2

- [ ] Support multilingue (FR/EN)
- [ ] Templates de workflows
- [ ] Intégration avec des services web
- [ ] Mode batch pour traitement en lot

## Contribution

Les contributions sont les bienvenues ! Consultez le fichier `CONTRIBUTING.md` pour plus d'informations.

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Support

- **Issues** : [GitHub Issues](https://github.com/your-repo/gisengine/issues)
- **Documentation** : [Wiki](https://github.com/your-repo/gisengine/wiki)
- **Email** : youcef.geodesien@gmail.com

---

*GISENGINE - Simplifiez vos workflows géomatiques avec QGIS*

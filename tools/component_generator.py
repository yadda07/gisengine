#!/usr/bin/env python3
"""
GISENGINE Component Generator
Outil CLI pour créer rapidement de nouveaux composants
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ComponentGenerator:
    """Générateur de composants GISENGINE"""
    
    def __init__(self, gisengine_root: str):
        self.gisengine_root = Path(gisengine_root)
        self.template_dir = self.gisengine_root / "templates" / "component_template"
        self.components_dir = self.gisengine_root / "components"
        
    def create_component(self, 
                        name: str,
                        component_type: str,
                        category: str,
                        author: str,
                        email: str,
                        description: str = "",
                        advanced: bool = False) -> bool:
        """
        Crée un nouveau composant basé sur le template
        
        Args:
            name: Nom du composant (ex: "BufferTransformer")
            component_type: Type (reader, transformer, writer)
            category: Catégorie du composant
            author: Nom de l'auteur
            email: Email de l'auteur
            description: Description du composant
            advanced: Créer avec options avancées
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Validation des paramètres
            if not self._validate_inputs(name, component_type, category):
                return False
            
            # Créer le dossier de destination
            component_dir = self._get_component_directory(component_type, name)
            if component_dir.exists():
                print(f"❌ Le composant {name} existe déjà dans {component_dir}")
                return False
            
            component_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Création du dossier: {component_dir}")
            
            # Copier et adapter les fichiers template
            self._copy_template_files(component_dir, name, component_type, 
                                    category, author, email, description, advanced)
            
            # Créer les fichiers spécifiques au type
            self._create_type_specific_files(component_dir, component_type, name)
            
            # Mettre à jour les registres
            self._update_registries(component_type, name)
            
            print(f"✅ Composant {name} créé avec succès!")
            print(f"📍 Emplacement: {component_dir}")
            print(f"🔧 Prochaines étapes:")
            print(f"   1. Éditez {component_dir}/component.py pour implémenter votre logique")
            print(f"   2. Adaptez {component_dir}/metadata.json selon vos besoins")
            print(f"   3. Complétez {component_dir}/tests.py avec vos tests")
            print(f"   4. Personnalisez {component_dir}/ui.py pour l'interface")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
            return False
    
    def _validate_inputs(self, name: str, component_type: str, category: str) -> bool:
        """Valide les paramètres d'entrée"""
        # Vérifier le nom
        if not name or not name.replace('_', '').replace('-', '').isalnum():
            print("❌ Le nom du composant doit être alphanumérique (avec _ ou - autorisés)")
            return False
        
        # Vérifier le type
        valid_types = ['reader', 'transformer', 'writer']
        if component_type not in valid_types:
            print(f"❌ Type invalide. Types valides: {', '.join(valid_types)}")
            return False
        
        # Vérifier que le template existe
        if not self.template_dir.exists():
            print(f"❌ Template non trouvé: {self.template_dir}")
            return False
        
        return True
    
    def _get_component_directory(self, component_type: str, name: str) -> Path:
        """Retourne le répertoire de destination du composant"""
        type_dir = self.components_dir / f"{component_type}s"  # readers, transformers, writers
        return type_dir / name.lower().replace('-', '_')
    
    def _copy_template_files(self, dest_dir: Path, name: str, component_type: str,
                           category: str, author: str, email: str, 
                           description: str, advanced: bool):
        """Copie et adapte les fichiers template"""
        
        # Mapping des fichiers à copier
        files_to_copy = {
            'component.py': 'component.py',
            'metadata.json': 'metadata.json',
            'tests.py': 'tests.py',
            'ui.py': 'ui.py',
            '__init__.py': '__init__.py'
        }
        
        for src_file, dest_file in files_to_copy.items():
            src_path = self.template_dir / src_file
            dest_path = dest_dir / dest_file
            
            if src_path.exists():
                # Lire le contenu du template
                content = src_path.read_text(encoding='utf-8')
                
                # Remplacer les placeholders
                content = self._replace_placeholders(
                    content, name, component_type, category, 
                    author, email, description, advanced
                )
                
                # Écrire le fichier adapté
                dest_path.write_text(content, encoding='utf-8')
                print(f"📄 Créé: {dest_file}")
    
    def _replace_placeholders(self, content: str, name: str, component_type: str,
                            category: str, author: str, email: str,
                            description: str, advanced: bool) -> str:
        """Remplace les placeholders dans le contenu"""
        
        # Générer les noms de classe
        class_name = self._to_class_name(name)
        ui_class_name = f"{class_name}UI"
        
        # Interface selon le type
        interface_map = {
            'reader': 'IReader',
            'transformer': 'ITransformer', 
            'writer': 'IWriter'
        }
        interface = interface_map.get(component_type, 'ITransformer')
        
        # Remplacements
        replacements = {
            'MyComponentTemplate': class_name,
            'MyComponentTemplateUI': ui_class_name,
            'ITransformer': interface,
            'Template pour créer un nouveau composant GISENGINE': description or f"Composant {name}",
            'Votre Nom': author,
            'votre.email@example.com': email,
            'template': category,
            'transformer': component_type,
            '2024-01-01': datetime.now().strftime('%Y-%m-%d'),
            'Version initiale du template': f'Version initiale de {name}'
        }
        
        # Appliquer les remplacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        return content
    
    def _to_class_name(self, name: str) -> str:
        """Convertit un nom en nom de classe Python"""
        # Supprimer les caractères non alphanumériques
        clean_name = ''.join(c for c in name if c.isalnum() or c in '_-')
        
        # Convertir en PascalCase
        parts = clean_name.replace('-', '_').split('_')
        return ''.join(part.capitalize() for part in parts if part)
    
    def _create_type_specific_files(self, component_dir: Path, component_type: str, name: str):
        """Crée des fichiers spécifiques au type de composant"""
        
        if component_type == 'reader':
            # Créer un exemple de fichier de configuration pour les readers
            config_content = {
                "supported_formats": ["shp", "geojson", "gpkg"],
                "default_crs": "EPSG:4326",
                "encoding": "utf-8"
            }
            config_path = component_dir / "reader_config.json"
            config_path.write_text(json.dumps(config_content, indent=2))
            print(f"📄 Créé: reader_config.json")
            
        elif component_type == 'writer':
            # Créer un exemple de fichier de configuration pour les writers
            config_content = {
                "output_formats": ["shp", "geojson", "gpkg"],
                "compression": False,
                "overwrite": True
            }
            config_path = component_dir / "writer_config.json"
            config_path.write_text(json.dumps(config_content, indent=2))
            print(f"📄 Créé: writer_config.json")
    
    def _update_registries(self, component_type: str, name: str):
        """Met à jour les fichiers __init__.py des registres"""
        
        type_dir = self.components_dir / f"{component_type}s"
        init_file = type_dir / "__init__.py"
        
        # Créer le __init__.py s'il n'existe pas
        if not init_file.exists():
            init_content = f'"""\n{component_type.capitalize()}s GISENGINE\n"""\n\n__all__ = []\n'
            init_file.write_text(init_content)
        
        # Ajouter l'import du nouveau composant
        class_name = self._to_class_name(name)
        folder_name = name.lower().replace('-', '_')
        
        import_line = f"from .{folder_name} import {class_name}"
        export_line = f"    '{class_name}'"
        
        content = init_file.read_text()
        
        # Ajouter l'import si pas déjà présent
        if import_line not in content:
            # Trouver où insérer l'import
            lines = content.split('\n')
            insert_pos = len(lines)
            
            # Chercher la fin des imports existants
            for i, line in enumerate(lines):
                if line.startswith('__all__'):
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, import_line)
            
            # Ajouter à __all__
            for i, line in enumerate(lines):
                if '__all__ = [' in line and export_line not in content:
                    if line.strip() == '__all__ = []':
                        lines[i] = f'__all__ = [\n{export_line}\n]'
                    else:
                        # Trouver la fin de __all__
                        for j in range(i, len(lines)):
                            if ']' in lines[j]:
                                lines[j] = lines[j].replace(']', f',\n{export_line}\n]')
                                break
                    break
            
            init_file.write_text('\n'.join(lines))
            print(f"📄 Mis à jour: {init_file}")
    
    def list_components(self) -> Dict[str, list]:
        """Liste tous les composants existants"""
        components = {
            'readers': [],
            'transformers': [],
            'writers': []
        }
        
        for component_type in components.keys():
            type_dir = self.components_dir / component_type
            if type_dir.exists():
                for item in type_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('_'):
                        # Lire les métadonnées si disponibles
                        metadata_file = item / 'metadata.json'
                        if metadata_file.exists():
                            try:
                                metadata = json.loads(metadata_file.read_text())
                                components[component_type].append({
                                    'name': item.name,
                                    'display_name': metadata.get('display_name', item.name),
                                    'version': metadata.get('version', '?'),
                                    'author': metadata.get('author', '?'),
                                    'description': metadata.get('description', '')
                                })
                            except:
                                components[component_type].append({
                                    'name': item.name,
                                    'display_name': item.name,
                                    'version': '?',
                                    'author': '?',
                                    'description': 'Métadonnées non disponibles'
                                })
        
        return components
    
    def validate_component(self, component_path: str) -> Dict[str, Any]:
        """Valide un composant existant"""
        component_dir = Path(component_path)
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Vérifier les fichiers requis
        required_files = ['component.py', 'metadata.json', '__init__.py']
        for file_name in required_files:
            file_path = component_dir / file_name
            if not file_path.exists():
                validation_result['errors'].append(f"Fichier manquant: {file_name}")
                validation_result['valid'] = False
        
        # Vérifier les fichiers optionnels
        optional_files = ['tests.py', 'ui.py']
        for file_name in optional_files:
            file_path = component_dir / file_name
            if not file_path.exists():
                validation_result['warnings'].append(f"Fichier optionnel manquant: {file_name}")
        
        # Valider metadata.json
        metadata_file = component_dir / 'metadata.json'
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
                
                required_fields = ['name', 'display_name', 'version', 'component_type']
                for field in required_fields:
                    if field not in metadata:
                        validation_result['errors'].append(f"Champ manquant dans metadata.json: {field}")
                        validation_result['valid'] = False
                
                validation_result['info'].append(f"Métadonnées valides pour {metadata.get('display_name', 'composant')}")
                
            except json.JSONDecodeError as e:
                validation_result['errors'].append(f"metadata.json invalide: {str(e)}")
                validation_result['valid'] = False
        
        return validation_result


def main():
    """Point d'entrée CLI"""
    parser = argparse.ArgumentParser(
        description="Générateur de composants GISENGINE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Créer un transformer simple
  python component_generator.py create BufferTransformer transformer spatial "John Doe" john@example.com

  # Créer un reader avec description
  python component_generator.py create ShapefileReader reader file "Jane Smith" jane@example.com --description "Lecteur de fichiers Shapefile"

  # Lister tous les composants
  python component_generator.py list

  # Valider un composant
  python component_generator.py validate ../components/transformers/buffer
        """
    )
    
    # Sous-commandes
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande create
    create_parser = subparsers.add_parser('create', help='Créer un nouveau composant')
    create_parser.add_argument('name', help='Nom du composant (ex: BufferTransformer)')
    create_parser.add_argument('type', choices=['reader', 'transformer', 'writer'], 
                              help='Type de composant')
    create_parser.add_argument('category', help='Catégorie du composant (ex: spatial, file, database)')
    create_parser.add_argument('author', help='Nom de l\'auteur')
    create_parser.add_argument('email', help='Email de l\'auteur')
    create_parser.add_argument('--description', '-d', default='', 
                              help='Description du composant')
    create_parser.add_argument('--advanced', '-a', action='store_true',
                              help='Créer avec options avancées')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Lister les composants existants')
    list_parser.add_argument('--type', '-t', choices=['reader', 'transformer', 'writer'],
                            help='Filtrer par type de composant')
    
    # Commande validate
    validate_parser = subparsers.add_parser('validate', help='Valider un composant')
    validate_parser.add_argument('path', help='Chemin vers le composant à valider')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Déterminer le répertoire racine de GISENGINE
    script_dir = Path(__file__).parent
    gisengine_root = script_dir.parent
    
    generator = ComponentGenerator(str(gisengine_root))
    
    if args.command == 'create':
        success = generator.create_component(
            args.name, args.type, args.category,
            args.author, args.email, args.description, args.advanced
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'list':
        components = generator.list_components()
        
        for component_type, items in components.items():
            if args.type and component_type != f"{args.type}s":
                continue
                
            print(f"\n📦 {component_type.upper()}")
            print("=" * 50)
            
            if not items:
                print("  Aucun composant trouvé")
                continue
            
            for item in items:
                print(f"  🔧 {item['display_name']} (v{item['version']})")
                print(f"     Auteur: {item['author']}")
                print(f"     Dossier: {item['name']}")
                if item['description']:
                    print(f"     Description: {item['description']}")
                print()
    
    elif args.command == 'validate':
        result = generator.validate_component(args.path)
        
        print(f"🔍 Validation de: {args.path}")
        print("=" * 50)
        
        if result['valid']:
            print("✅ Composant valide!")
        else:
            print("❌ Composant invalide!")
        
        if result['errors']:
            print("\n🚨 Erreurs:")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['warnings']:
            print("\n⚠️  Avertissements:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['info']:
            print("\n💡 Informations:")
            for info in result['info']:
                print(f"  - {info}")
        
        sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()

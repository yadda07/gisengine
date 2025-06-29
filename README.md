![GitHub release](https://img.shields.io/github/v/release/yadda07/gisengine)
![License](https://img.shields.io/github/license/yadda07/gisengine)
![Issues](https://img.shields.io/github/issues/yadda07/gisengine)
![Stars](https://img.shields.io/github/stars/yadda07/gisengine?style=social)

# GISENGINE - QGIS Plugin

**GISENGINE** is a modern QGIS plugin that replicates the principles of geoprocessing workbenches by leveraging the existing algorithms from the QGIS Processing Framework.

## Features

### Modern Interface

- **Unified interface** with tabs for smooth navigation
- **Interactive canvas** for visual workflow creation
- **Smart search** with category filtering
- **Organized transformer library** easily accessible

### Advanced Features

- **Dynamic scanner** of QGIS Processing Toolbox
- **Drag-and-drop** to create workflows
- **Visual connections** between transformers
- **Step-by-step execution** with detailed logs
- **Save/load** workflow functionality

### QGIS Integration

- **Full compatibility** with QGIS algorithms
- **Processing Modeler integration** for complex workflows
- **Integrated QGIS project management**

## 🔧 Installation

1. Copy the `gisengine` folder to your QGIS plugins directory
2. Enable the plugin in QGIS: **Plugins > Manage and Install Plugins**
3. Launch GISENGINE from the **Plugins > GISENGINE** menu

## Usage

### Quick Start

1. **Open GISENGINE** from the Plugins menu
2. **Explore the transformer library** in the left panel
3. **Drag and drop** transformers onto the canvas
4. **Connect transformers** by clicking on input/output ports
5. **Execute your workflow** with the Play button

### Keyboard Shortcuts

- **Space**: Quick transformer search
- **I**: Add input transformer
- **O**: Add output transformer
- **Ctrl+S**: Save workflow
- **Ctrl+O**: Open workflow

## Architecture

### Modular Structure

```
gisengine/
├── __init__.py             # Package initialization
├── gisengine_plugin.py     # Main plugin file
├── plugin.py               # Plugin entry point
├── metadata.txt            # QGIS metadata
├── ui/                     # User interfaces
│   ├── unified_interface.py
│   ├── workflow_mapper.py
│   ├── qgis_plugin_ui.py
│   └── qgis_integration.py
├── core/                   # Business logic
│   ├── algorithm_scanner.py
│   ├── workflow_engine.py
│   └── mapping_engine.py
├── resources/              # Static resources
│   ├── icons/
│   │   └── icon.svg
│   └── styles/
├── tests/                  # Unit tests
│   ├── test_integration.py
│   ├── test_ui.py
│   └── test_workflow.py
├── CHANGELOG.md            # Version history
├── CODE_OF_CONDUCT.md      # Community guidelines
├── MIT.LICENSE             # License file
├── SECURITY.MD             # Security policy
└── README.md               # This file
```

### Main Classes

- `GISENGINEPlugin`: Main plugin class
- `UnifiedGISENGINEInterface`: Unified user interface
- `WorkflowTestWindow`: Workflow testing window

## 🛠️ Development

### Prerequisites

- Python >= 3.9
- QGIS >= 3.28
- PyQt5 or PyQt6

### Development Setup

```bash
# Clone the project
git clone <repository-url>

# Create symbolic link to QGIS directory
ln -s /path/to/gisengine ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Integration tests
python tests/test_integration.py
```

## Roadmap

### Version 1.1

- [ ] User interface improvements
- [ ] New custom transformers
- [ ] Export to Processing Modeler
- [ ] Execution history

### Version 1.2

- [ ] Multilingual support (FR/EN)
- [ ] Workflow templates
- [ ] Web services integration
- [ ] Batch processing mode

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for more information.

## License

This project is licensed under the [MIT License](https://github.com/yadda07/gisengine/blob/master/MIT.LICENSE).

## Support

- **Issues**: [GitHub Issues](https://github.com/yadda07/gisengine/issues)
- **Documentation**: [Wiki](https://github.com/yadda07/gisengine/wiki)
- **Email**: youcef.geodesien@gmail.com

---

*GISENGINE - Streamline your geospatial workflows with QGIS*

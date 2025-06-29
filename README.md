![GitHub release](https://img.shields.io/github/v/release/yadda07/gisengine)
![License](https://img.shields.io/github/license/yadda07/gisengine)
![Issues](https://img.shields.io/github/issues/yadda07/gisengine)
![Stars](https://img.shields.io/github/stars/yadda07/gisengine?style=social)

# GISENGINE - QGIS Plugin

**GISENGINE** is a modern QGIS plugin that aims to replicate the principles of geoprocessing workbenches (like FME) by leveraging the existing algorithms from the QGIS Processing Framework.

> ⚠️ **Status**: This project is currently in active development. The core workflow designer is functional but the plugin is not yet ready for production use. Contributors are welcome to help complete the implementation.

## Features

### ✅ Implemented Components

#### Professional Workflow Designer
- **Modern FME-style interface** with clean, professional design
- **Interactive canvas** with grid-based node placement
- **Curvilinear connections** with Bézier curves and directional arrows
- **Professional workflow nodes** with input/output ports
- **Smart search panel** with autocompletion and filtering
- **Real-time connection system** with temporary connection preview

#### User Interface
- **Unified interface** with tabbed navigation
- **Workflow Designer tab** - Main visual workflow editor
- **Scanner Processing tab** - QGIS Processing Toolbox integration
- **Professional styling** without emojis, inspired by FME

### 🚧 In Development

#### Core Engine (Placeholder)
- **Algorithm scanner** - Dynamic discovery of QGIS Processing algorithms
- **Workflow engine** - Execution engine for created workflows
- **Mapping engine** - Data transformation and routing

#### Advanced Features (Planned)
- **Drag-and-drop** workflow creation from search panel
- **Step-by-step execution** with detailed logs
- **Save/load** workflow functionality
- **QGIS Processing integration** for algorithm execution

## 🔧 Installation

> ⚠️ **Note**: This plugin is in development and not yet ready for end-user installation.

For **developers and contributors**:

1. Clone or download the repository
2. Copy the `gisengine` folder to your QGIS plugins directory:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Enable the plugin in QGIS: **Plugins > Manage and Install Plugins**
4. Launch GISENGINE from the **Plugins > GISENGINE** menu

## Current Usage

### Workflow Designer Testing

1. **Open GISENGINE** from the Plugins menu
2. **Navigate to Workflow Designer tab**
3. **Test connection creation**:
   - Right-click on canvas to add sample nodes
   - Click on blue output ports to start connections
   - Click on green input ports to complete connections
   - Use right-click or Escape to cancel connections
4. **Use search panel** to filter and find components

### Available Features

- ✅ **Visual workflow canvas** with professional grid
- ✅ **Node creation** and positioning
- ✅ **Connection system** between workflow nodes
- ✅ **Search and filtering** of components
- ⚠️ **Algorithm execution** - Not yet implemented
- ⚠️ **Save/Load workflows** - Not yet implemented

## Architecture

### Current Project Structure

```
gisengine/
├── __init__.py                 # Package initialization
├── gisengine_plugin.py         # Main plugin class (8.6KB)
├── metadata.txt                # QGIS plugin metadata
├── ui/                         # User Interface Layer
│   ├── unified_interface.py    # Main unified interface (59KB)
│   ├── workflow_mapper.py      # Workflow mapping logic (107KB)
│   ├── qgis_plugin_ui.py       # QGIS plugin UI integration (17KB)
│   ├── qgis_integration.py     # QGIS Processing integration (28KB)
│   └── workflow/               # Workflow Designer Components
│       ├── __init__.py         # Module exports
│       ├── fme_workflow_designer.py  # Main workflow designer (14KB)
│       ├── workflow_scene.py   # Graphics scene management (11KB)
│       ├── workflow_nodes.py   # Node and connection classes (11KB)
│       └── search_panel.py     # Search and filtering panel (11KB)
├── core/                       # Business Logic (Placeholder)
│   ├── algorithm_scanner.py    # QGIS algorithm discovery
│   ├── workflow_engine.py      # Workflow execution engine
│   └── mapping_engine.py       # Data transformation engine
├── tests/                      # Unit Tests
│   ├── test_integration.py
│   ├── test_ui.py
│   └── test_workflow.py
├── resources/                  # Static Resources
│   └── icons/
├── CHANGELOG.md               # Version history
├── CODE_OF_CONDUCT.md         # Community guidelines
├── MIT.LICENSE                # License file
├── SECURITY.MD                # Security policy
└── README.md                  # This file
```

### Key Components

#### ✅ Implemented Classes

**Workflow Designer:**
- `FMEWorkflowDesigner`: Main workflow designer interface
- `FMEStyleScene`: Graphics scene with grid and connection management
- `ProfessionalWorkflowNode`: Workflow nodes with ports
- `ConnectionPort`: Input/output ports for connections
- `Connection`: Bézier curve connections with arrows
- `ProfessionalSearchPanel`: Component search and filtering

**Main Interface:**
- `GISENGINEPlugin`: Main QGIS plugin entry point
- `UnifiedGISENGINEInterface`: Tabbed main interface
- `QGISIntegration`: QGIS Processing framework integration

#### 🚧 Placeholder Classes (Core)

- `AlgorithmScanner`: Dynamic QGIS algorithm discovery
- `WorkflowEngine`: Workflow execution and processing
- `MappingEngine`: Data transformation and routing

## 🛠️ Development

### Prerequisites

- **Python** >= 3.9
- **QGIS** >= 3.28
- **PyQt5** (QGIS standard)
- **Git** for version control

### Development Setup

```bash
# Clone the project
git clone https://github.com/yadda07/gisengine.git

# Windows - Create symbolic link
mklink /D "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\gisengine" "C:\path\to\gisengine"

# Linux/macOS - Create symbolic link
ln -s /path/to/gisengine ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Development Status

#### ✅ Completed Components
- **Workflow Designer UI** - Fully functional visual editor
- **Connection System** - Complete with Bézier curves and arrows
- **Search Panel** - Component filtering and autocompletion
- **Professional Styling** - Modern FME-inspired interface
- **QGIS Integration** - Plugin framework and UI integration

#### 🚧 In Progress
- **Core Engine Implementation** - Algorithm execution logic
- **Drag-and-Drop** - From search panel to canvas
- **Workflow Persistence** - Save/load functionality

#### 📋 TODO
- **Algorithm Scanner** - Dynamic QGIS Processing discovery
- **Workflow Execution** - Run created workflows
- **Data Mapping** - Input/output parameter handling
- **Error Handling** - Robust error management
- **Documentation** - User and developer guides

### Testing

```bash
# Manual testing in QGIS
# 1. Load plugin in QGIS
# 2. Open GISENGINE interface
# 3. Test workflow designer functionality

# Unit tests (when implemented)
python -m pytest tests/
```

## Development Roadmap

### Phase 1: Core Implementation (Current)

- [x] **Workflow Designer** - Visual workflow editor
- [x] **Connection System** - Node-to-node connections
- [x] **Search Panel** - Component discovery
- [ ] **Algorithm Scanner** - QGIS Processing integration
- [ ] **Workflow Engine** - Execution framework
- [ ] **Data Mapping** - Parameter handling

### Phase 2: Functionality (Next)

- [ ] **Drag-and-Drop** - Component placement
- [ ] **Workflow Execution** - Run workflows
- [ ] **Save/Load** - Workflow persistence
- [ ] **Error Handling** - Robust error management
- [ ] **Progress Tracking** - Execution monitoring

### Phase 3: Enhancement (Future)

- [ ] **Export to Processing Modeler** - QGIS integration
- [ ] **Workflow Templates** - Predefined workflows
- [ ] **Batch Processing** - Multiple dataset processing
- [ ] **Multilingual Support** - FR/EN localization
- [ ] **Plugin Marketplace** - Custom transformers

### Phase 4: Advanced Features (Long-term)

- [ ] **Web Services Integration** - Remote processing
- [ ] **Collaborative Workflows** - Team sharing
- [ ] **Workflow Versioning** - Change tracking
- [ ] **Performance Optimization** - Large dataset handling

## Contributing

**Contributors are welcome!** This project needs help to complete the implementation.

### How to Contribute

#### 🎯 Priority Areas
1. **Core Engine Implementation** - Algorithm scanner and workflow engine
2. **Drag-and-Drop Functionality** - Component placement from search panel
3. **Workflow Persistence** - Save/load workflows to/from files
4. **QGIS Processing Integration** - Execute QGIS algorithms
5. **Error Handling** - Robust error management and user feedback

#### 🛠️ Technical Skills Needed
- **Python** programming
- **PyQt5** GUI development
- **QGIS Plugin** development experience
- **QGIS Processing Framework** knowledge
- **Git** version control

#### 📋 Getting Started
1. **Fork** the repository
2. **Set up** development environment (see Development section)
3. **Pick an issue** or propose a new feature
4. **Create a branch** for your changes
5. **Submit a pull request** with detailed description

#### 🐛 Bug Reports
- Use GitHub Issues to report bugs
- Include QGIS version, OS, and steps to reproduce
- Attach screenshots if relevant

#### 💡 Feature Requests
- Discuss new features in GitHub Issues first
- Consider implementation complexity
- Align with project goals and architecture

See `CONTRIBUTING.md` for detailed guidelines (when available).

## License

This project is licensed under the [MIT License](https://github.com/yadda07/gisengine/blob/master/MIT.LICENSE).

## Support

- **Issues**: [GitHub Issues](https://github.com/yadda07/gisengine/issues)
- **Documentation**: [Wiki](https://github.com/yadda07/gisengine/wiki)
- **Email**: youcef.geodesien@gmail.com

---

*GISENGINE - Streamline your geospatial workflows with QGIS*

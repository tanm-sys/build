# File Structure Overview

## Project Directory Structure

```
decentralized-ai-simulation/
├── 📁 src/                          # Source code modules
│   ├── 📁 core/                     # Core simulation components
│   │   ├── 📁 agents/              # Agent management system
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 agent_manager.py
│   │   ├── 📁 database/            # Database and ledger management
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 ledger_manager.py
│   │   ├── 📁 simulation/          # Simulation engine
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 simulation_engine.py
│   │   ├── 📄 agents.py            # Main agent implementation
│   │   ├── 📄 database.py          # Database ledger system
│   │   ├── 📄 simulation.py        # Simulation framework
│   │   └── 📄 decentralized_ai_simulation.py
│   ├── 📁 config/                  # Configuration management
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config_loader.py     # Configuration loading utilities
│   │   └── 📄 config_manager.py    # Configuration management system
│   ├── 📁 ui/                      # User interface components
│   │   ├── 📄 __init__.py
│   │   ├── 📄 api_server.py       # REST API server
│   │   └── 📄 streamlit_app.py    # Streamlit dashboard
│   ├── 📁 utils/                   # Utility modules
│   │   ├── 📁 logging/             # Logging system
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 logger.py
│   │   ├── 📁 monitoring/          # Monitoring and health checks
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 monitor.py
│   │   ├── 📄 __init__.py
│   │   ├── 📄 data_manager.py      # Data management utilities
│   │   ├── 📄 exceptions.py        # Custom exception classes
│   │   ├── 📄 file_manager.py      # File management utilities
│   │   ├── 📄 logging_setup.py     # Logging configuration
│   │   ├── 📄 migration_helper.py  # Migration and refactoring tools
│   │   ├── 📄 monitoring.py       # Monitoring system
│   │   ├── 📄 README.md           # Utils documentation
│   │   └── 📄 render_mermaid_diagrams.py
│   └── 📄 __init__.py              # Main package initialization
├── 📁 tests/                       # Test suite
│   ├── 📁 fixtures/                # Test data and fixtures
│   │   └── 📄 __init__.py
│   ├── 📁 integration/             # Integration tests
│   │   └── 📄 __init__.py
│   ├── 📁 unit/                    # Unit tests
│   │   └── 📄 __init__.py
│   ├── 📁 utils/                   # Test utilities
│   │   └── 📄 __init__.py
│   └── 📄 __init__.py              # Test package initialization
├── 📁 docs/                        # Documentation
│   ├── 📁 api/                     # API documentation
│   ├── 📁 guides/                  # User guides and tutorials
│   ├── 📁 project/                 # Project documentation
│   │   ├── 📄 design.md           # System design document
│   │   └── 📄 file-structure-overview.md (this file)
│   ├── 📄 *.md                     # Various documentation files
│   └── 📄 README.md               # Main project documentation
├── 📁 config/                      # Configuration files
│   ├── 📁 environments/            # Environment-specific configs
│   │   ├── 📄 base.yaml           # Base configuration
│   │   ├── 📄 development.env     # Development environment
│   │   └── 📄 production.env      # Production environment
│   ├── 📁 templates/               # Configuration templates
│   │   └── 📄 .env.example        # Environment template
│   ├── 📄 .env.example             # Environment variables template
│   ├── 📄 config.yaml             # Main configuration file
│   └── 📄 requirements.txt        # Python dependencies
├── 📁 scripts/                     # Automation scripts
│   ├── 📁 maintenance/             # Maintenance scripts
│   │   ├── 📄 cleanup.sh          # Cleanup utilities
│   │   └── 📄 render_mermaid_diagrams.py
│   ├── 📁 runtime/                 # Runtime scripts
│   │   ├── 📄 decentralized_ai_simulation.py
│   │   ├── 📄 deploy.sh           # Deployment script
│   │   ├── 📄 run.sh              # Main execution script
│   │   └── 📄 streamlit_app.py    # Dashboard launcher
│   ├── 📁 setup/                   # Setup and installation
│   │   ├── 📄 setup.sh            # Main setup script
│   │   └── 📄 setup.py            # Python package setup
│   ├── 📁 testing/                 # Testing automation
│   │   ├── 📄 benchmark_performance.py
│   │   └── 📄 test.sh             # Test runner
│   └── 📄 utils.py                 # Script utilities
├── 📁 data/                        # Data and runtime files
│   ├── 📁 blacklists/              # Blacklist data
│   │   └── 📁 nodes/              # Node-specific blacklists
│   ├── 📁 databases/               # Database files
│   ├── 📁 documents/               # Document storage
│   └── 📄 README.md               # Data directory documentation
└── 📄 __init__.py                  # Root package initialization
```

## Directory Purpose and Contents

### 📁 `src/` - Source Code Modules

**Purpose**: Contains all source code organized by functional responsibility.

**Key Components**:
- **`core/`**: Core simulation logic and business rules
  - `agents.py` - Main agent implementation with anomaly detection
  - `database.py` - Thread-safe ledger system with connection pooling
  - `simulation.py` - Mesa-based simulation framework
  - `decentralized_ai_simulation.py` - Main application entry point

- **`config/`**: Configuration management system
  - `config_loader.py` - YAML configuration loading with environment overrides
  - `config_manager.py` - Advanced configuration management with validation

- **`ui/`**: User interface components
  - `api_server.py` - REST API for external integrations
  - `streamlit_app.py` - Interactive web dashboard

- **`utils/`**: Shared utility functions and helpers
  - `file_manager.py` - Robust file operations with atomic writes
  - `data_manager.py` - JSON/YAML data management and validation
  - `migration_helper.py` - Automated refactoring and file reorganization
  - `exceptions.py` - Custom exception hierarchy
  - `logging_setup.py` - Structured logging configuration
  - `monitoring.py` - Health checks and metrics collection

### 📁 `tests/` - Test Suite

**Purpose**: Comprehensive testing framework organized by test type and scope.

**Structure**:
- **`unit/`**: Unit tests for individual components
- **`integration/`**: Integration tests for component interactions
- **`fixtures/`**: Test data and mock objects
- **`utils/`**: Testing utilities and helpers

### 📁 `docs/` - Documentation

**Purpose**: Complete project documentation and user guides.

**Content Types**:
- API documentation (`api/`)
- User guides and tutorials (`guides/`)
- Project documentation (`project/`)
- Technical design documents

### 📁 `config/` - Configuration Files

**Purpose**: Centralized configuration management with environment support.

**Key Files**:
- `config.yaml` - Main configuration file
- `requirements.txt` - Python dependencies
- `environments/` - Environment-specific configurations
- `templates/` - Configuration templates for new deployments

### 📁 `scripts/` - Automation Scripts

**Purpose**: Executable scripts for common operations and maintenance.

**Categories**:
- **`setup/`**: Installation and initialization scripts
- **`runtime/`**: Application execution and deployment scripts
- **`testing/`**: Test execution and performance benchmarking
- **`maintenance/`**: Cleanup and maintenance utilities

### 📁 `data/` - Runtime Data

**Purpose**: Persistent data storage and runtime-generated files.

**Data Types**:
- **`databases/`**: SQLite database files and ledger data
- **`blacklists/`**: Security blacklist data organized by date/node
- **`documents/`**: Document storage and processing data

## File Naming Conventions

### Python Files
- **Modules**: `snake_case.py` (e.g., `file_manager.py`, `data_manager.py`)
- **Classes**: `PascalCase` (e.g., `FileManager`, `DataManager`)
- **Functions/Methods**: `snake_case` (e.g., `safe_write_file()`, `load_json_data()`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `ALLOWED_EXTENSIONS`)

### Configuration Files
- **YAML files**: `kebab-case.yaml` or `snake_case.yaml`
- **Environment files**: `environment.env` or `.env.development`
- **Templates**: `filename.example` or `filename.template`

### Documentation Files
- **README files**: `README.md` (always capitalized)
- **Guides**: `feature-guide.md` or `how-to-topic.md`
- **API docs**: `API_COMPONENT.md` or `api-component-reference.md`
- **Design docs**: `design.md` or `architecture.md`

### Data Files
- **Database files**: `descriptive_name.db`
- **JSON data**: `data_type_date.json` (e.g., `blacklist_2024-01-15.json`)
- **Backups**: `backup_timestamp/` directories

## Relationships Between Directories

### Import Structure
```python
# Core modules import utilities
from decentralized_ai_simulation.src.utils.file_manager import FileManager
from decentralized_ai_simulation.src.utils.data_manager import DataManager
from decentralized_ai_simulation.src.config.config_manager import get_config

# UI modules import core functionality
from decentralized_ai_simulation.src.core.simulation import Simulation
from decentralized_ai_simulation.src.core.agents import AnomalyAgent

# Tests import from all layers
from decentralized_ai_simulation.src.core.database import DatabaseLedger
from decentralized_ai_simulation.src.utils.monitoring import get_monitoring
```

### Data Flow
1. **Configuration** (`config/`) → **Core Logic** (`src/core/`)
2. **Core Logic** → **Data Storage** (`data/`)
3. **Utilities** (`src/utils/`) ↔ **All Components**
4. **UI** (`src/ui/`) → **Core Logic** + **Monitoring** (`src/utils/`)
5. **Tests** (`tests/`) → **All Components**

### Dependency Hierarchy
```
Configuration Layer (config/)
     ↓
Infrastructure Layer (src/utils/)
     ↓
Core Business Logic (src/core/)
     ↓
Interface Layer (src/ui/)
     ↓
Data Persistence (data/)
```

## Module Organization Principles

### 1. **Separation of Concerns**
- Each directory has a single, well-defined responsibility
- Core business logic separated from infrastructure concerns
- Configuration and data management isolated from application logic

### 2. **Dependency Direction**
- Higher-level modules depend on lower-level utilities
- Core modules don't depend on UI components
- Configuration and utilities are dependency-free

### 3. **Cohesive Packaging**
- Related functionality grouped together
- Clear boundaries between different functional areas
- Consistent internal structure within each package

### 4. **Scalability**
- Structure supports adding new components without reorganization
- Clear patterns for extending functionality
- Organized for team development and parallel work

## Examples of Correct File Placement

### Adding a New Utility Module
```
decentralized-ai-simulation/src/utils/
└── 📄 cache_manager.py    # New utility → utils/
```

### Adding a New Agent Type
```
decentralized-ai-simulation/src/core/agents/
├── 📄 __init__.py
├── 📄 agent_manager.py
└── 📄 advanced_agent.py   # New agent type → core/agents/
```

### Adding Configuration for New Feature
```
decentralized-ai-simulation/config/
├── 📄 config.yaml         # Update main config
└── 📁 environments/
    └── 📄 feature.env     # Feature-specific config → environments/
```

### Adding Tests for New Component
```
decentralized-ai-simulation/tests/
└── 📁 unit/
    └── 📄 test_cache_manager.py  # Tests → tests/unit/
```

This structure ensures maintainability, scalability, and clear organization as the project grows.

## Related Documentation

- **[File Management Guidelines](../guides/file-management-guidelines.md)** - Learn how to use the file management utilities effectively
- **[Developer File Guide](../guides/developer-file-guide.md)** - Step-by-step guide for adding and modifying files
- **[Configuration Management Guide](../guides/configuration-management.md)** - How to manage project configuration across environments
- **[Migration Documentation](../guides/migration-documentation.md)** - Details about the file structure reorganization
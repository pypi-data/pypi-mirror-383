# Port Experience

A Python middleware service for managing [Port.io](https://www.getport.io/) resources including blueprints, actions, mappings, and widgets. This tool provides an interactive CLI to create, update, and synchronize Port.io configurations from local JSON files.

## Features

- 🎯 **Multi-Resource Management**: Handle blueprints, actions, mappings, and widgets
- 🔄 **Intelligent Sync**: Compare local resources with existing Port.io resources
- ✅ **Interactive Confirmation**: Review and confirm changes before applying them
- 🛡️ **Safe Merge Strategy**: Update existing resources without losing data
- 📊 **Detailed Reporting**: Clear summary of operations and their outcomes
- 🔧 **Flexible Configuration**: Control which resources to process via environment variables

## Architecture

The project is organized into specialized managers:

- **`BasePortManager`**: Shared authentication and API request handling
- **`PortBlueprintManager`**: Manages Port.io blueprints
- **`PortActionManager`**: Manages Port.io actions
- **`PortMappingManager`**: Manages Port.io integrations and mappings
- **`PortWidgetManager`**: Manages Port.io dashboard widgets
- **`BlueprintTreeManager`**: Handles blueprint dependency resolution

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Port.io account with API credentials (Client ID and Client Secret)

### Installation

**Option 1: Install from PyPI (recommended)**
```bash
pip install port-experience
```

**Option 2: Install from source**
1. **Clone the repository**:
   ```bash
   git clone https://github.com/port-experimental/one-click-port-experience
   cd one-click-port-experience
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install package in development mode**:
   ```bash
   pip install -e .
   ```

5. **Configure environment variables**:
   
   Create a `.env` file in the project root:
   ```bash
   PORT_CLIENT_ID=your_client_id_here
   PORT_CLIENT_SECRET=your_client_secret_here
   
   # Optional: Customize directories
   BLUEPRINTS_DIR=setup/blueprints
   ACTIONS_DIR=setup/actions
   MAPPINGS_DIR=setup/mappings
   WIDGETS_DIR=setup/widgets
   
   # Optional: Specify which resources to process
   ACTION=all  # Options: blueprints, actions, mappings, widgets, all
   
   # Optional: Define which folders are required
   EXPECTED_FOLDERS=blueprints,actions,widgets  # Comma-separated list
   
   # Optional: Set log level
   LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
   ```

   **Getting Port.io Credentials**:
   - Log in to your Port.io account
   - Navigate to Settings → Credentials
   - Create a new API client or use existing credentials
   - Copy the Client ID and Client Secret

### Usage

**Recommended: Install and use the CLI**
```bash
# Install the package
pip install port-experience

# Apply all configurations
experience apply
```

**Alternative: Run from source**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install in development mode
pip install -e .

# Run using the CLI command
experience apply
```

The tool will:
1. 🔍 Scan local JSON files in the `setup/` directories
2. 📋 Compare them with existing resources in Port.io
3. 📊 Display a summary of changes (new vs. updates)
4. ⚠️  Ask for confirmation before proceeding
5. 🚀 Create/update resources based on your confirmation
6. ✅ Report the results

### Programmatic Usage

You can also use the managers programmatically in your Python code:

```python
from port_experience import PortBlueprintManager, PortActionManager

# Initialize managers
blueprint_manager = PortBlueprintManager(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

action_manager = PortActionManager(
    client_id="your_client_id", 
    client_secret="your_client_secret"
)

# Setup blueprints from directory
blueprint_results = blueprint_manager.setup_all_blueprints("setup/blueprints")

# Setup actions from directory
action_results = action_manager.setup_all_actions("setup/actions")

# Check if specific resources exist
if blueprint_manager.blueprint_exists("my_blueprint"):
    print("Blueprint exists!")

if action_manager.action_exists("my_action"):
    print("Action exists!")
```

### Processing Specific Resources

Currently, the CLI processes all resource types by default. For more granular control, you can modify the source code or use environment variables:

```bash
# The CLI will process all resources by default
experience apply

# For development/testing with specific resource types,
# you can modify the source code or use environment variables
```

## Project Structure

```
one-click-port-experience/
├── pyproject.toml              # Python package configuration
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── .env                        # Environment configuration (create this)
├── .gitignore                  # Git ignore patterns
├── port_experience/  # Main package directory
│   ├── __init__.py            # Package initialization and exports
│   ├── main.py                # Main entry point and orchestration
│   └── managers/              # Resource managers
│       ├── __init__.py        # Base manager class
│       ├── action_manager.py  # Action resource manager
│       ├── blueprint_manager.py  # Blueprint resource manager
│       ├── blueprint_tree_manager.py  # Blueprint dependency manager
│       ├── mapping_manager.py # Mapping/integration manager
│       └── widget_manager.py  # Widget/dashboard manager
└── setup/                     # Resource definitions (JSON files)
    ├── blueprints/            # Blueprint JSON files
    ├── actions/               # Action JSON files
    ├── mappings/              # Mapping JSON files
    └── widgets/               # Widget JSON files
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT_CLIENT_ID` | ✅ | - | Port.io API Client ID |
| `PORT_CLIENT_SECRET` | ✅ | - | Port.io API Client Secret |
| `BLUEPRINTS_DIR` | ❌ | `setup/blueprints` | Path to blueprints directory |
| `ACTIONS_DIR` | ❌ | `setup/actions` | Path to actions directory |
| `MAPPINGS_DIR` | ❌ | `setup/mappings` | Path to mappings directory |
| `WIDGETS_DIR` | ❌ | `setup/widgets` | Path to widgets directory |
| `ACTION` | ❌ | `all` | Resource types to process |
| `EXPECTED_FOLDERS` | ❌ | `blueprints,actions,mappings,widgets` | Required directories |
| `LOG_LEVEL` | ❌ | `INFO` | Logging verbosity level |

### Resource JSON Format

Each resource type expects JSON files in a specific format. Here are examples:

**Blueprint** (`setup/blueprints/example.json`):
```json
{
  "identifier": "my_blueprint",
  "title": "My Blueprint",
  "icon": "Microservice",
  "schema": {
    "properties": {
      "name": {
        "type": "string",
        "title": "Name"
      }
    }
  }
}
```

**Action** (`setup/actions/example.json`):
```json
{
  "identifier": "my_action",
  "title": "My Action",
  "icon": "Github",
  "blueprint": "my_blueprint",
  "invocationMethod": {
    "type": "WEBHOOK"
  }
}
```

## How It Works

### 1. Resource Discovery
The tool scans the configured directories for JSON files containing resource definitions.

### 2. Comparison & Analysis
For each local resource, the tool:
- Checks if it already exists in Port.io
- Determines if it needs to be created or updated
- Identifies any additional resources in Port.io not in local files

### 3. User Confirmation
Before making any changes, the tool displays:
- Resources to be created (🆕)
- Resources to be updated (🔄)
- Total operation summary

### 4. Merge Strategy
The tool uses a **merge strategy** when updating resources:
- Existing properties are preserved
- New properties are added
- Changed properties are updated
- No data is deleted

### 5. Execution & Reporting
After confirmation, the tool:
- Processes each resource
- Reports success/failure for each operation
- Provides a final summary

## Manager Classes

### BasePortManager
Located in `managers/__init__.py`, provides:
- Authentication with Port.io API
- Access token management
- Generic API request methods
- JSON file discovery
- Logging configuration

### PortBlueprintManager
Manages Port.io blueprints:
- Create and update blueprints
- Check blueprint existence
- Handle blueprint dependencies

### PortActionManager
Manages Port.io actions:
- Create and update actions
- Validate action configurations
- Link actions to blueprints

### PortMappingManager
Manages Port.io integrations:
- Create and update mappings
- Handle integration configurations

### PortWidgetManager
Manages Port.io dashboard widgets:
- Create and update pages/widgets
- Configure dashboard layouts

### BlueprintTreeManager
Handles blueprint dependencies:
- Parse blueprint relationships
- Resolve dependency order
- Build blueprint hierarchy trees

## Error Handling

The tool includes comprehensive error handling:

- **Missing Credentials**: Clear error if Port.io credentials are not provided
- **API Failures**: Detailed logging of API errors with status codes
- **Invalid JSON**: Reports which files have syntax errors
- **Missing Directories**: Configurable whether to treat as error or skip
- **Failed Operations**: Continues processing other resources, reports failures at the end

## Logging

Configure logging verbosity with the `LOG_LEVEL` environment variable:

```bash
LOG_LEVEL=DEBUG experience apply  # Detailed debug information
LOG_LEVEL=INFO experience apply   # Standard information (default)
LOG_LEVEL=WARNING experience apply  # Only warnings and errors
LOG_LEVEL=ERROR experience apply  # Only errors
```

## Development

### Adding New Resource Types

1. Create a new manager class inheriting from `BasePortManager`
2. Implement resource-specific methods
3. Add the resource type to `main.py`
4. Create corresponding directory in `setup/`

### Running Tests

```bash
# Add your test commands here
pytest tests/
```

## Troubleshooting

### Authentication Failures
```
Error: Authentication failed: 401
```
**Solution**: Verify your `PORT_CLIENT_ID` and `PORT_CLIENT_SECRET` are correct.

### Missing Resources
```
Error: Required blueprints directory 'setup/blueprints' not found
```
**Solution**: Create the directory or update `BLUEPRINTS_DIR` in `.env`.

### API Rate Limits
If you encounter rate limiting, the tool will log the error. Wait a moment and retry.

### JSON Syntax Errors
```
Error: Invalid JSON in example.json: Expecting ',' delimiter
```
**Solution**: Validate your JSON files using a JSON validator.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your license here]

## Support

For issues, questions, or contributions:
- Open an issue in the repository
- Contact the development team
- Check Port.io documentation: https://docs.getport.io/

## Acknowledgments

Built for seamless integration with [Port.io](https://www.getport.io/) - The Internal Developer Portal.

# Port OneClick Middleware

A Python middleware service for managing Port.io guides, blueprints, actions, mappings, and widgets.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export PORT_CLIENT_ID=your_client_id
export PORT_CLIENT_SECRET=your_client_secret

# Run the middleware
python main.py
```

## Configuration

### Required Environment Variables

```bash
PORT_CLIENT_ID=your_client_id
PORT_CLIENT_SECRET=your_client_secret
```

### Optional Environment Variables

```bash
# Directory paths (defaults shown)
BLUEPRINTS_DIR=setup/blueprints
ACTIONS_DIR=setup/actions
MAPPINGS_DIR=setup/mappings
WIDGETS_DIR=setup/widgets

# Action filter - what to process
ACTION=all  # Options: all, blueprints, actions, mappings, widgets

# Required folders - comma-separated list
# Only folders in this list will be required to exist
EXPECTED_FOLDERS=blueprints,actions,mappings,widgets  # Default: all folders
```

## Features

### Flexible Folder Requirements

You can specify which folders are required using the `EXPECTED_FOLDERS` environment variable:

- **Default behavior**: All folders (blueprints, actions, mappings, widgets) are required
- **Custom requirements**: Only folders listed in `EXPECTED_FOLDERS` are required
- **Missing non-required folders**: Will be skipped without causing errors

**Example:**

```bash
# Only require blueprints and widgets folders
EXPECTED_FOLDERS=blueprints,widgets python main.py

# If actions or mappings folders are missing, they will be skipped
```

## Usage Examples

```bash
# Process all resources
python main.py

# Process only blueprints
ACTION=blueprints python main.py

# Process everything, but only require blueprints and actions to exist
EXPECTED_FOLDERS=blueprints,actions python main.py
```

For detailed configuration options, see [CONFIG.md](CONFIG.md).

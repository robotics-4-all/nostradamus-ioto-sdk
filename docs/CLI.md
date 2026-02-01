# Nostradamus IoT Observatory CLI (nioto)

Professional command-line interface for the Nostradamus IoT Observatory platform.

## Installation

```bash
pip install nostradamus-ioto-sdk[cli]
```

Or install from source:

```bash
pip install -e ".[cli]"
```

## Authentication

Set your API key as an environment variable:

```bash
export NOSTRADAMUS_API_KEY="your-api-key-here"
```

Or pass it with each command:

```bash
nioto --api-key="your-key" org get
```

## Quick Start

```bash
# View organization info
nioto org get

# List all projects
nioto projects list

# Create a new project
nioto projects create --name "Smart Home" --description "Home automation"

# List collections in a project
nioto collections list --project PROJECT_ID

# Send data to a collection
nioto data send --project PROJECT_ID --collection COLLECTION_ID --data '[{"value": 25.5}]'
```

## Commands

### Organization Management

```bash
# Get organization information
nioto org get

# Update organization
nioto org update --description "New description" --tags "iot,production"
```

### Project Management

```bash
# List all projects
nioto projects list
nioto projects list --limit 10
nioto projects list --format json

# Get project details
nioto projects get PROJECT_ID

# Create a new project
nioto projects create --name "Factory Sensors" --description "Production monitoring"

# Update project
nioto projects update PROJECT_ID --description "Updated description"

# Delete project
nioto projects delete PROJECT_ID --yes
```

### Collection Management

```bash
# List collections in a project
nioto collections list --project PROJECT_ID

# Get collection details
nioto collections get --project PROJECT_ID COLLECTION_ID

# Create a new collection
nioto collections create \
  --project PROJECT_ID \
  --name "Temperature Sensors" \
  --description "Factory temperature data" \
  --schema '{"type": "timeseries", "fields": ["temperature", "humidity"]}'

# Delete collection
nioto collections delete --project PROJECT_ID COLLECTION_ID
```

### Data Operations

```bash
# Send data to a collection
nioto data send \
  --project PROJECT_ID \
  --collection COLLECTION_ID \
  --data '[{"temperature": 25.5, "humidity": 60}]'

# Query data from a collection
nioto data get --project PROJECT_ID --collection COLLECTION_ID --limit 100
```

### API Key Management

```bash
# List API keys for a project
nioto keys list --project PROJECT_ID

# Create a new API key
nioto keys create --project PROJECT_ID --type read

# Delete an API key
nioto keys delete --project PROJECT_ID API_KEY_STRING
```

## Output Formats

The CLI supports multiple output formats:

```bash
# Table format (default) - human-readable
nioto projects list

# JSON format - for scripting
nioto projects list --format json

# Compact format - minimal output
nioto projects list --format compact
```

## Advanced Usage

### Using Custom API Base URL

```bash
export NOSTRADAMUS_BASE_URL="https://custom-api.example.com"
nioto org get
```

Or:

```bash
nioto --base-url="https://custom-api.example.com" org get
```

### Verbose Mode

```bash
nioto --verbose projects list
```

### Scripting Examples

#### Bash Script - Create Project and Collection

```bash
#!/bin/bash

# Create project
PROJECT_ID=$(nioto projects create --name "My Project" --format json | jq -r '.project_id')

echo "Created project: $PROJECT_ID"

# Create collection
COLLECTION_ID=$(nioto collections create \
  --project "$PROJECT_ID" \
  --name "Sensors" \
  --description "Sensor data" \
  --schema '{"type": "timeseries"}' \
  --format json | jq -r '.collection_id')

echo "Created collection: $COLLECTION_ID"
```

#### Python Script - Send Bulk Data

```python
import subprocess
import json

project_id = "your-project-id"
collection_id = "your-collection-id"

data_points = [
    {"temperature": 25.5, "timestamp": "2024-01-01T12:00:00Z"},
    {"temperature": 26.0, "timestamp": "2024-01-01T13:00:00Z"},
    {"temperature": 24.8, "timestamp": "2024-01-01T14:00:00Z"},
]

subprocess.run([
    "nioto", "data", "send",
    "--project", project_id,
    "--collection", collection_id,
    "--data", json.dumps(data_points)
])
```

## Error Handling

The CLI provides clear error messages:

```bash
$ nioto org get
Error: No API key provided.
Use --api-key option or set NOSTRADAMUS_API_KEY environment variable.

$ nioto projects get invalid-id
Not Found: Project not found

$ nioto projects create --name "Test"
Validation Error: Description is required
```

## Getting Help

```bash
# General help
nioto --help

# Command-specific help
nioto projects --help
nioto projects create --help

# Version
nioto --version
```

## Tips & Best Practices

1. **Store API key securely**: Use environment variables instead of passing keys in command line
2. **Use JSON format for scripting**: Parse output with `jq` or similar tools
3. **Confirm destructive operations**: Add `--yes` flag to skip confirmations in scripts
4. **Use compact format for automation**: Minimal output for parsing in scripts
5. **Check exit codes**: CLI returns non-zero exit codes on errors

## Troubleshooting

### Command not found

Make sure the CLI is installed and your PATH includes the Python bin directory:

```bash
pip install -e ".[cli]"
which nioto
```

### Authentication errors

Verify your API key is set correctly:

```bash
echo $NOSTRADAMUS_API_KEY
nioto org get --verbose
```

### JSON parsing errors

When sending data, ensure JSON is properly formatted:

```bash
# Good
nioto data send -p PID -c CID -d '[{"value": 25.5}]'

# Bad - missing quotes
nioto data send -p PID -c CID -d [{"value": 25.5}]
```

## Support

For issues or questions:
- GitHub: https://github.com/nostradamus/nostradamus-ioto-sdk
- Documentation: https://nostradamus-ioto-sdk.readthedocs.io

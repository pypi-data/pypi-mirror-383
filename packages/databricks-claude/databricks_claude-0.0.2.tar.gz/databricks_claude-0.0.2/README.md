# Databricks Claude CLI

A simple CLI tool that integrates Claude with Databricks authentication.

## Installation

```bash
pip install databricks-claude
```

## Quick Start

### Setup
```bash
# Authenticate with your Databricks workspace
databricks-claude login
```

### Usage
```bash
# Interactive chat with Claude
databricks-claude

# Quick responses
databricks-claude --print "What is Python?"

# Check status
databricks-claude status
```

## How it Works

This tool handles Databricks OAuth authentication and automatically configures Claude CLI to work with your Databricks workspace. You authenticate once, and it manages tokens automatically.

## Configuration

The tool stores configuration in:
- `~/.databricks-claude/config.json` - Main settings
- `~/.claude/settings.json` - Claude CLI config (managed automatically)

### Managing Configuration

```bash
# View current configuration
databricks-claude config

# Update workspace URL
databricks-claude config --host https://your-workspace.databricks.com

# Reset all settings
databricks-claude config --reset

# Use different workspace for one command
databricks-claude --host https://other-workspace.databricks.com login
```

## Commands

- `databricks-claude` - Interactive Claude session
- `databricks-claude login` - Authenticate with Databricks
- `databricks-claude logout` - Clear authentication
- `databricks-claude status` - Check system status
- `databricks-claude config` - Manage configuration

## Requirements

- Python 3.8+
- Claude CLI (will be installed automatically if missing)
- Databricks workspace access

## Development

```bash
git clone https://github.com/ahdbilal/databricks-claude.git
cd databricks-claude

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src tests
isort src tests
```

## Troubleshooting

**Authentication issues:**
```bash
databricks-claude logout
databricks-claude login
```

**Configuration issues:**
```bash
databricks-claude config --reset
```

**Debug mode:**
```bash
databricks-claude --debug status
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.
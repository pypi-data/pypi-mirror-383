# DB Claude Bridge

An unofficial CLI bridge that integrates Claude with Databricks OAuth authentication.

## Installation

```bash
pip install db-claude-bridge
```

## Quick Start

### Setup
```bash
# Authenticate with your Databricks workspace
db-claude-bridge login
```

### Usage
```bash
# Interactive chat with Claude
db-claude-bridge

# Quick responses
db-claude-bridge --print "What is Python?"

# Check status
db-claude-bridge status
```

## How it Works

This tool handles Databricks OAuth authentication and automatically configures Claude CLI to work with your Databricks workspace. You authenticate once, and it manages tokens automatically.

## Configuration

The tool stores configuration in:
- `~/.db-claude-bridge/config.json` - Main settings
- `~/.claude/settings.json` - Claude CLI config (managed automatically)

### Managing Configuration

```bash
# View current configuration
db-claude-bridge config

# Update workspace URL
db-claude-bridge config --host https://your-workspace.databricks.com

# Reset all settings
db-claude-bridge config --reset

# Use different workspace for one command
db-claude-bridge --host https://other-workspace.databricks.com login
```

## Commands

- `db-claude-bridge` - Interactive Claude session
- `db-claude-bridge login` - Authenticate with Databricks
- `db-claude-bridge logout` - Clear authentication
- `db-claude-bridge status` - Check system status
- `db-claude-bridge config` - Manage configuration

## Requirements

- Python 3.8+
- Claude CLI (will be installed automatically if missing)
- Databricks workspace access

## Development

```bash
git clone https://github.com/ahdbilal/db-claude-bridge.git
cd db-claude-bridge

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
db-claude-bridge logout
db-claude-bridge login
```

**Configuration issues:**
```bash
db-claude-bridge config --reset
```

**Debug mode:**
```bash
db-claude-bridge --debug status
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.
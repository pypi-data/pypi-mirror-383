# DB Claude Bridge

**A lightweight bridge that lets the Claude Code CLI authenticate and run through Databricks Foundation Models using Databricks OAuth.**

This lightweight bridge provides seamless integration between Claude Code CLI and Databricks Foundation Models, handling Databricks OAuth authentication automatically so you can focus on using powerful language models.

## Installation

```bash
pip install db-claude-bridge
```

## Quick Start

### Setup
```bash
# Authenticate with Databricks OAuth to enable Claude Code CLI access to Foundation Models
db-claude-bridge login
```

### Usage
```bash
# Run Claude Code CLI through Databricks Foundation Models
db-claude-bridge

# Quick responses through Foundation Models
db-claude-bridge --print "What is Python?"

# Check Claude Code CLI and Databricks OAuth status
db-claude-bridge status
```

## How it Works

This lightweight bridge handles Databricks OAuth authentication and configures Claude Code CLI to run through Databricks Foundation Models. Simply authenticate once with your Databricks workspace, and the bridge automatically manages OAuth tokens, enabling Claude Code CLI to seamlessly access Foundation Models hosted on Databricks.

## Configuration

The bridge stores configuration in:
- `~/.db-claude-bridge/config.json` - Bridge settings and OAuth tokens
- `~/.claude/settings.json` - Claude Code CLI config (managed automatically by the bridge)

### Managing Configuration

```bash
# View current bridge configuration
db-claude-bridge config

# Update Databricks workspace URL
db-claude-bridge config --host https://your-workspace.databricks.com

# Reset bridge settings and OAuth tokens
db-claude-bridge config --reset

# Use different workspace for one session
db-claude-bridge --host https://your-workspace.databricks.com login
```

## Commands

- `db-claude-bridge` - Run Claude Code CLI through Databricks Foundation Models
- `db-claude-bridge login` - Authenticate with Databricks OAuth for Foundation Models access
- `db-claude-bridge logout` - Clear OAuth authentication tokens
- `db-claude-bridge status` - Check Claude Code CLI and Databricks OAuth status
- `db-claude-bridge config` - Manage bridge configuration and OAuth settings

## Requirements

- Python 3.8+
- Claude Code CLI (automatically installed by the bridge if missing)
- Databricks workspace with Foundation Models access

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

**OAuth authentication issues:**
```bash
db-claude-bridge logout
db-claude-bridge login
```

**Bridge configuration issues:**
```bash
db-claude-bridge config --reset
```

**Debug the bridge:**
```bash
db-claude-bridge --debug status
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.
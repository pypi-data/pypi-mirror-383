"""Command-line interface for DB Claude Bridge - lightweight bridge that lets Claude Code CLI authenticate and run through Databricks Foundation Models using Databricks OAuth."""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import click

from .__about__ import __version__
from .core import DatabricksClaudeCore
from .exceptions import AuthenticationError, DatabricksClaudeError


@click.group(
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--host', help='Databricks workspace host URL')
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx: click.Context, debug: bool, host: Optional[str], version: bool) -> None:
    """A lightweight bridge that lets the Claude Code CLI authenticate and run through Databricks Foundation Models using Databricks OAuth."""
    if version:
        click.echo(f"db-claude-bridge {__version__}")
        return

    # Initialize core with options
    core = DatabricksClaudeCore(databricks_host=host, debug=debug)
    ctx.obj = core

    # If no subcommand provided, pass arguments to Claude
    if ctx.invoked_subcommand is None:
        # Get remaining args that weren't processed by our options
        claude_args = ctx.args

        # If no arguments provided, show help
        if not claude_args:
            click.echo(ctx.get_help())
            return

        try:
            # First, set up Claude CLI if needed
            if not core.is_claude_cli_installed():
                if not core.setup_claude_cli():
                    click.echo("❌ Failed to set up Claude CLI", err=True)
                    click.echo(
                        "   Please install manually from: https://claude.ai/download",
                        err=True,
                    )
                    sys.exit(1)

            exit_code = core.refresh_token_and_execute(claude_args)
            sys.exit(exit_code)
        except DatabricksClaudeError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.pass_obj
def login(core: DatabricksClaudeCore) -> None:
    """Set up authentication with Databricks."""
    try:
        click.echo("🔐 Databricks Claude Authentication")
        click.echo("=" * 40)

        # First, set up Claude CLI
        if not core.setup_claude_cli():
            click.echo("❌ Failed to set up Claude CLI", err=True)
            sys.exit(1)

        click.echo("\n🔑 Setting up Databricks authentication...")

        # Check if already authenticated
        is_auth, email = core.is_authenticated()
        if is_auth and email:
            click.echo(f"✅ Already authenticated as: {email}")
            if not click.confirm("Do you want to re-authenticate?"):
                return

        click.echo(f"🌐 Opening browser for Databricks authentication...")
        click.echo(f"   Host: {core.databricks_host}")

        # Perform authentication
        core.authenticate()

        # Verify and complete setup
        is_auth, email = core.is_authenticated()
        if not is_auth:
            raise AuthenticationError("Authentication verification failed")

        click.echo("✅ Authenticated successfully!")
        if email:
            click.echo(f"   User: {email}")
            core.config['user_email'] = email
        click.echo(f"   Host: {core.databricks_host}")

        # Update configuration
        core.config['last_login'] = time.time()
        core.save_config()

        # Get fresh token and update Claude config
        click.echo("\n🔧 Updating Claude configuration...")
        token = core.get_databricks_token()
        if token:
            # Get existing config to preserve user's base_url and model settings
            config_data = {}
            if core.claude_config_path.exists():
                try:
                    with open(core.claude_config_path, 'r') as f:
                        config_data = json.load(f)
                except (json.JSONDecodeError, IOError, OSError):
                    pass

            env = config_data.get('env', {})
            base_url = env.get('ANTHROPIC_BASE_URL')
            model = env.get('ANTHROPIC_MODEL')

            core.update_claude_config(token, base_url, model)
            click.echo("✅ Claude configuration updated with authentication token")

        click.echo("\n🎉 Setup complete!")
        click.echo("\nYou can now use:")
        click.echo("  db-claude-bridge 'your prompt'")
        click.echo("  db-claude-bridge --print 'quick question'")
        click.echo("  db-claude-bridge status")

    except DatabricksClaudeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_obj
def logout(core: DatabricksClaudeCore) -> None:
    """Clear all authentication data."""
    try:
        click.echo("🔓 Logging out from Databricks Claude...")
        core.logout()
        click.echo("✅ Logout complete!")
        click.echo("\nTo re-authenticate, run:")
        click.echo("  db-claude-bridge login")
    except DatabricksClaudeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_obj
def status(core: DatabricksClaudeCore) -> None:
    """Check authentication and system status."""
    try:
        click.echo("📊 Databricks Claude Integration Status")
        click.echo("=" * 45)

        # Check Databricks authentication
        is_auth, email = core.is_authenticated()
        if is_auth:
            click.echo("✅ Databricks: Authenticated")
            if email:
                click.echo(f"   User: {email}")
            click.echo(f"   Host: {core.databricks_host}")

            if core.config.get('last_login'):
                login_time = time.ctime(core.config['last_login'])
                click.echo(f"   Last Login: {login_time}")
        else:
            click.echo("❌ Databricks: Not authenticated")
            click.echo("   Run: db-claude-bridge login")
            sys.exit(1)

        # Check Claude CLI
        try:
            if core.is_claude_cli_installed():
                result = subprocess.run(
                    ['claude', '--version'], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    click.echo(f"✅ Claude CLI: {version}")
                else:
                    click.echo("⚠️  Claude CLI: Version check failed")
            else:
                click.echo("❌ Claude CLI: Not installed")
                if core.auto_install_claude:
                    click.echo("   Will be installed automatically on first use")
                else:
                    click.echo("   Install from: https://claude.ai/download")
                    sys.exit(1)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            click.echo("❌ Claude CLI: Not found")
            sys.exit(1)

        # Check Claude configuration
        claude_config_path = Path(core.claude_config_path).expanduser()
        if claude_config_path.exists():
            try:
                with open(claude_config_path, 'r') as f:
                    config = json.load(f)

                env = config.get('env', {})
                auth_token = env.get('ANTHROPIC_AUTH_TOKEN')
                base_url = env.get('ANTHROPIC_BASE_URL')

                if auth_token and base_url:
                    click.echo("✅ Claude Config: Configured for Databricks")
                    click.echo(f"   Base URL: {base_url}")

                    # Check if token is current
                    current_token = core.get_databricks_token()
                    if current_token and current_token == auth_token:
                        click.echo("   Token: ✅ Current")
                    else:
                        click.echo("   Token: ⚠️  May need refresh")
                else:
                    click.echo("❌ Claude Config: Missing Databricks configuration")
                    sys.exit(1)
            except (json.JSONDecodeError, IOError):
                click.echo("❌ Claude Config: Invalid configuration")
                sys.exit(1)
        else:
            click.echo("❌ Claude Config: Not found")
            sys.exit(1)

        click.echo("\n🎉 All systems operational!")

    except DatabricksClaudeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', help='Update Databricks workspace host URL')
@click.option('--reset', is_flag=True, help='Reset all configuration')
@click.pass_obj
def config(core: DatabricksClaudeCore, host: Optional[str], reset: bool) -> None:
    """Manage configuration settings."""
    try:
        if reset:
            click.echo("🔄 Resetting configuration...")

            # Clear config file
            if core.config_file.exists():
                core.config_file.unlink()

            # Clear Claude config
            if core.claude_config_path.exists():
                core.claude_config_path.unlink()

            click.echo("✅ Configuration reset complete!")
            click.echo("   Next command will prompt for setup again")
            return

        if host:
            click.echo(f"🔧 Updating workspace URL to: {host}")

            if not host.startswith('http'):
                host = f"https://{host}"

            core.databricks_host = host
            core.config['databricks_host'] = host
            core.save_config()

            click.echo("✅ Workspace URL updated!")
            click.echo("   You may need to re-authenticate: db-claude-bridge login")
            return

        # Show current configuration
        click.echo("📋 Current Configuration")
        click.echo("=" * 30)

        if core.databricks_host:
            click.echo(f"🏢 Workspace URL: {core.databricks_host}")
        else:
            click.echo("🏢 Workspace URL: Not configured")

        if core.config.get('user_email'):
            click.echo(f"👤 User: {core.config['user_email']}")

        if core.config.get('last_login'):
            login_time = time.ctime(core.config['last_login'])
            click.echo(f"🕒 Last Login: {login_time}")

        click.echo(f"📁 Config File: {core.config_file}")
        click.echo(f"📁 Claude Config: {core.claude_config_path}")

        click.echo("\n💡 Available options:")
        click.echo("   db-claude-bridge config --host <url>    # Update workspace URL")
        click.echo("   db-claude-bridge config --reset         # Reset all settings")

    except DatabricksClaudeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        # Handle simple version check first
        if '--version' in sys.argv:
            click.echo(f"db-claude-bridge {__version__}")
            return

        # Parse our own arguments
        debug = '--debug' in sys.argv
        host = None

        # Find host value if provided
        for i, arg in enumerate(sys.argv):
            if arg == '--host' and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
                break
            elif arg.startswith('--host='):
                host = arg.split('=', 1)[1]
                break

        # Initialize core
        core = DatabricksClaudeCore(databricks_host=host, debug=debug)

        # Filter out our own arguments to get Claude arguments
        claude_args = []
        skip_next = False

        for i, arg in enumerate(sys.argv[1:], 1):  # Skip script name
            if skip_next:
                skip_next = False
                continue

            if arg in ['--debug', '--version']:
                continue
            elif arg == '--host':
                skip_next = True
                continue
            elif arg.startswith('--host='):
                continue
            else:
                claude_args.append(arg)

        # Check if this is a subcommand
        if claude_args and claude_args[0] in ['login', 'logout', 'status', 'config']:
            # Use Click for subcommands
            cli()
        else:
            # Pass to Claude (including interactive mode when no args)
            try:
                # First, set up Claude CLI if needed
                if not core.is_claude_cli_installed():
                    if not core.setup_claude_cli():
                        click.echo("❌ Failed to set up Claude CLI", err=True)
                        click.echo(
                            "   Please install manually from: https://claude.ai/download",
                            err=True,
                        )
                        sys.exit(1)

                # If no arguments, start interactive Claude session
                if not claude_args:
                    click.echo("🤖 Starting interactive Claude session...")
                    click.echo("   (Ctrl+C to exit)\n")

                exit_code = core.refresh_token_and_execute(claude_args)
                sys.exit(exit_code)
            except DatabricksClaudeError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Command Line Interface module
"""

import click
import sys


from .config import config_manager
from .llm_client import LLMClient
from .executor import executor
from .utils import get_system_info


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """
    ScriptMate - Intelligent Script Companion

    A tool for generating command line instructions through natural language
    """
    if version:
        from . import __version__

        click.echo(f"ScriptMate v{__version__}")
        return

    if ctx.invoked_subcommand is None:
        # If no subcommand, show help information
        click.echo(ctx.get_help())


@cli.group()
def config() -> None:
    """Configuration management"""
    pass


@config.command()
def setup() -> None:
    """Setup configuration"""
    try:
        config_manager.setup_interactive()
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Configuration setup failed: {e}")


@config.command()
def show() -> None:
    """Show current configuration"""
    config_manager.show_config()


@config.command()
def test() -> None:
    """Test configuration"""
    if not config_manager.is_configured():
        click.echo("❌ Not configured yet, please run: scriptmate config setup")
        return

    click.echo("🔄 Testing configuration...")
    success = config_manager.test_config()
    if not success:
        click.echo(
            "💡 Tip: Please check if API Key, model name and Base URL are correct"
        )


@config.command()
def reset() -> None:
    """Reset configuration"""
    config_manager.reset_config()


@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Only generate command, do not execute")
@click.option("--auto-yes", "-y", is_flag=True, help="Automatically confirm execution")
def generate(query: tuple[str, ...], dry_run: bool, auto_yes: bool) -> None:
    """
    Generate and execute commands

    QUERY: Task described in natural language
    """
    # Check configuration
    if not config_manager.is_configured():
        click.echo("❌ Not configured yet, starting configuration wizard...")
        try:
            config_manager.setup_interactive()
        except Exception as e:
            raise click.ClickException(f"Configuration failed: {e}")

    # Merge query parameters
    user_query = " ".join(query)

    if not user_query.strip():
        raise click.ClickException("Please provide query content")

    try:
        # Get configuration
        api_config = config_manager.get_api_config()

        # Create client
        client = LLMClient(
            api_key=api_config["api_key"],
            model_name=api_config["model_name"],
            base_url=api_config["base_url"],
        )

        # Generate command
        click.echo(f"🤖 Generating command for you: {user_query}")
        result = client.generate_command(user_query)

        cmd = result["cmd"]
        reason = result["reason"]

        if dry_run:
            # Only show results, do not execute
            executor._display_result(cmd, reason)
            click.echo(f"\n📋 Generated command: {cmd}")
            return

        # Execute command
        if auto_yes:
            # Auto-confirm mode
            executor._display_result(cmd, reason)
            click.echo("\n🚀 Auto-execution mode")
            executor._execute_command(cmd)
        else:
            # Normal confirmation mode
            executor.execute_with_confirmation(cmd, reason)

    except Exception as e:
        raise click.ClickException(f"Command generation failed: {e}")


@cli.command()
def info() -> None:
    """Show system information"""
    from . import __version__

    click.echo("📊 ScriptMate System Information")
    click.echo(f"Version: {__version__}")

    # System information
    sys_info = get_system_info()
    click.echo(f"Operating System: {sys_info['os']}")
    click.echo(f"Architecture: {sys_info['arch']}")
    click.echo(f"Platform: {sys_info['platform']}")
    click.echo(f"Python Version: {sys_info['python_version']}")

    # Configuration status
    if config_manager.is_configured():
        click.echo("Configuration Status: ✅ Configured")
        config = config_manager.load_config()
        if config:
            click.echo(f"Model: {config.get('model_name', 'N/A')}")
    else:
        click.echo("Configuration Status: ❌ Not configured")

    # Configuration file path
    click.echo(f"Configuration File: {config_manager.config_file}")


@cli.command()
def history() -> None:
    """Show execution history"""
    last_cmd = executor.get_last_command()
    last_result = executor.get_last_result()

    if not last_cmd:
        click.echo("📝 No execution history")
        return

    click.echo("📝 Recently executed command:")
    click.echo(f"Command: {last_cmd}")

    if last_result:
        if last_result.get("success"):
            click.echo("Status: ✅ Success")
        else:
            click.echo("Status: ❌ Failed")
            if "return_code" in last_result:
                click.echo(f"Return Code: {last_result['return_code']}")


def main() -> None:
    """Main entry function"""
    # Handle direct invocation (without subcommands)
    if (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in ["config", "info", "history"]
    ):
        # If the first argument is not a known subcommand, treat it as generate command
        sys.argv.insert(1, "generate")

    try:
        cli()
    except click.ClickException as e:
        click.echo(f"❌ {e.message}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Unknown error occurred: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

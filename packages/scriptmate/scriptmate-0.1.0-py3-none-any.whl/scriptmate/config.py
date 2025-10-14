"""
Configuration management module
"""

import click
from typing import Any

from .utils import get_config_file, save_json, load_json, get_timestamp, validate_url


class ConfigManager:
    """Configuration manager"""

    def __init__(self):
        self.config_file = get_config_file()
        self._config: dict[str, Any] | None = None

    def load_config(self) -> dict[str, Any] | None:
        """Load configuration"""
        if self._config is None:
            self._config = load_json(self.config_file)
        return self._config

    def save_config(self, config: dict[str, Any]) -> None:
        """Save configuration"""
        config["updated_at"] = get_timestamp()
        save_json(config, self.config_file)
        self._config = config

    def is_configured(self) -> bool:
        """Check if configuration is complete"""
        config = self.load_config()
        if not config:
            return False

        required_fields = ["api_key", "model_name", "base_url"]
        return all(field in config and config[field] for field in required_fields)

    def get_api_config(self) -> dict[str, str]:
        """Get API configuration"""
        config = self.load_config()
        if not config:
            raise Exception("Configuration not found, please run setup command first")

        return {
            "api_key": config.get("api_key", ""),
            "model_name": config.get("model_name", ""),
            "base_url": config.get("base_url", ""),
        }

    def setup_interactive(self) -> None:
        """Interactive configuration setup"""
        click.echo("🔧 ScriptMate Initial Configuration")
        click.echo("Please enter LLM service configuration:")

        # API Key
        api_key = click.prompt(
            "API Key", type=str, hide_input=True, confirmation_prompt=False
        ).strip()

        if not api_key:
            raise click.ClickException("API Key cannot be empty")

        # Model Name
        model_name = click.prompt(
            "Model Name", type=str, default="gpt-3.5-turbo", show_default=True
        ).strip()

        # Base URL
        base_url = click.prompt(
            "Base URL", type=str, default="https://api.openai.com/v1", show_default=True
        ).strip()

        # Validate URL format
        if not validate_url(base_url):
            raise click.ClickException("Invalid Base URL format")

        # Save configuration
        config = {
            "api_key": api_key,
            "model_name": model_name,
            "base_url": base_url,
            "created_at": get_timestamp(),
        }

        try:
            self.save_config(config)
            click.echo("✅ Configuration saved successfully!")
        except Exception as e:
            raise click.ClickException(f"Failed to save configuration: {e}")

    def show_config(self) -> None:
        """Display current configuration"""
        config = self.load_config()
        if not config:
            click.echo("❌ Configuration file not found")
            return

        click.echo("📋 Current Configuration:")
        click.echo(f"  API Key: {'*' * 8}...{config.get('api_key', '')[-4:]}")
        click.echo(f"  Model Name: {config.get('model_name', 'N/A')}")
        click.echo(f"  Base URL: {config.get('base_url', 'N/A')}")
        click.echo(f"  Created At: {config.get('created_at', 'N/A')}")
        click.echo(f"  Updated At: {config.get('updated_at', 'N/A')}")
        click.echo(f"  Config File: {self.config_file}")

    def test_config(self) -> bool:
        """Test configuration"""
        try:
            from .llm_client import LLMClient

            config = self.get_api_config()
            client = LLMClient(
                api_key=config["api_key"],
                model_name=config["model_name"],
                base_url=config["base_url"],
            )

            # Send test request
            client.generate_command("test connection")
            click.echo("✅ Configuration test successful!")
            return True

        except Exception as e:
            click.echo(f"❌ Configuration test failed: {e}")
            return False

    def reset_config(self) -> None:
        """Reset configuration"""
        if self.config_file.exists():
            if click.confirm(
                "Are you sure you want to delete the existing configuration?"
            ):
                self.config_file.unlink()
                self._config = None
                click.echo("✅ Configuration reset")
        else:
            click.echo("❌ Configuration file does not exist")


# Global configuration manager instance
config_manager = ConfigManager()

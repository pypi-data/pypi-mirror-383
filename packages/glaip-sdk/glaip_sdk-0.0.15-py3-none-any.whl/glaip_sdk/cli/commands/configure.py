"""Configuration management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import getpass
import os
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.text import Text

from glaip_sdk import Client
from glaip_sdk._version import __version__ as _SDK_VERSION
from glaip_sdk.branding import AIPBranding
from glaip_sdk.rich_components import AIPTable

console = Console()

CONFIG_DIR = Path.home() / ".aip"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Set secure file permissions
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:  # pragma: no cover - platform dependent best effort
        pass


@click.group()
def config_group() -> None:
    """Configuration management operations."""
    pass


@config_group.command("list")
def list_config() -> None:
    """List current configuration."""

    config = load_config()

    if not config:
        console.print(
            "[yellow]No configuration found. Run 'aip config configure' to set up.[/yellow]"
        )
        return

    table = AIPTable(title="🔧 AIP Configuration")
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="green")

    for key, value in config.items():
        if key == "api_key" and value:
            # Mask the API key
            masked_value = "***" + value[-4:] if len(value) > 4 else "***"
            table.add_row(key, masked_value)
        else:
            table.add_row(key, str(value))

    console.print(table)
    console.print(Text(f"\n📁 Config file: {CONFIG_FILE}"))


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key: str, value: str) -> None:
    """Set a configuration value."""

    valid_keys = ["api_url", "api_key"]

    if key not in valid_keys:
        console.print(
            f"[red]Error: Invalid key '{key}'. Valid keys are: {', '.join(valid_keys)}[/red]"
        )
        raise click.ClickException(f"Invalid configuration key: {key}")

    config = load_config()
    config[key] = value
    save_config(config)

    if key == "api_key":
        masked_value = "***" + value[-4:] if len(value) > 4 else "***"
        console.print(Text(f"✅ Set {key} = {masked_value}"))
    else:
        console.print(Text(f"✅ Set {key} = {value}"))


@config_group.command("get")
@click.argument("key")
def get_config(key: str) -> None:
    """Get a configuration value."""

    config = load_config()

    if key not in config:
        console.print(Text(f"[yellow]Configuration key '{key}' not found.[/yellow]"))
        raise click.ClickException(f"Configuration key not found: {key}")

    value = config[key]

    if key == "api_key":
        # Mask the API key for display
        masked_value = "***" + value[-4:] if len(value) > 4 else "***"
        console.print(masked_value)
    else:
        console.print(value)


@config_group.command("unset")
@click.argument("key")
def unset_config(key: str) -> None:
    """Remove a configuration value."""

    config = load_config()

    if key not in config:
        console.print(Text(f"[yellow]Configuration key '{key}' not found.[/yellow]"))
        return

    del config[key]
    save_config(config)

    console.print(Text(f"✅ Removed {key} from configuration"))


@config_group.command("reset")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def reset_config(force: bool) -> None:
    """Reset all configuration to defaults."""

    if not force:
        console.print("[yellow]This will remove all AIP configuration.[/yellow]")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm not in ["y", "yes"]:
            console.print("Cancelled.")
            return

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        console.print(
            "✅ Configuration reset. Run 'aip config configure' to set up again."
        )
    else:
        console.print("[yellow]No configuration found to reset.[/yellow]")


def _configure_interactive() -> None:
    """Shared configuration logic for both configure commands."""
    # Display AIP welcome banner
    branding = AIPBranding.create_from_sdk(
        sdk_version=_SDK_VERSION, package_name="glaip-sdk"
    )
    branding.display_welcome_panel(title="🔧 AIP Configuration")

    # Load existing config
    config = load_config()

    console.print("\n[bold]Enter your AIP configuration:[/bold]")
    console.print("(Leave blank to keep current values)")
    console.print("─" * 50)

    # API URL
    current_url = config.get("api_url", "")
    console.print(
        f"\n[cyan]AIP API URL[/cyan] {f'(current: {current_url})' if current_url else ''}:"
    )
    new_url = input("> ").strip()
    if new_url:
        config["api_url"] = new_url
    elif not current_url:
        config["api_url"] = "https://your-aip-instance.com"

    # API Key
    current_key_masked = (
        "***" + config.get("api_key", "")[-4:] if config.get("api_key") else ""
    )
    console.print(
        f"\n[cyan]AIP API Key[/cyan] {f'(current: {current_key_masked})' if current_key_masked else ''}:"
    )
    new_key = getpass.getpass("> ")
    if new_key:
        config["api_key"] = new_key

    # Save configuration
    save_config(config)

    console.print(Text(f"\n✅ Configuration saved to: {CONFIG_FILE}"))

    # Test the new configuration
    console.print("\n🔌 Testing connection...")
    try:
        # Create client with new config
        client = Client(api_url=config["api_url"], api_key=config["api_key"])

        # Try to list resources to test connection
        try:
            agents = client.list_agents()
            console.print(Text(f"✅ Connection successful! Found {len(agents)} agents"))
        except Exception as e:
            console.print(Text(f"⚠️  Connection established but API call failed: {e}"))
            console.print(
                "   You may need to check your API permissions or network access"
            )

        client.close()

    except Exception as e:
        console.print(Text(f"❌ Connection failed: {e}"))
        console.print("   Please check your API URL and key")
        console.print("   You can run 'aip status' later to test again")

    console.print("\n💡 You can now use AIP CLI commands!")
    console.print("   • Run 'aip status' to check connection")
    console.print("   • Run 'aip agents list' to see your agents")


@config_group.command()
def configure() -> None:
    """Configure AIP CLI credentials and settings interactively."""
    _configure_interactive()


# Alias command for backward compatibility
@click.command()
def configure_command() -> None:
    """Configure AIP CLI credentials and settings interactively.

    This is an alias for 'aip config configure' for backward compatibility.
    """
    # Delegate to the shared function
    _configure_interactive()


# Note: The config command group should be registered in main.py

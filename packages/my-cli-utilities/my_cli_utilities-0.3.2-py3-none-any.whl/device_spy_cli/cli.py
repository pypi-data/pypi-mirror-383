# -*- coding: utf-8 -*-

import logging
from typing import Optional
import typer

from my_cli_utilities_common.config import LoggingUtils
from .commands import CLICommands

# --- Setup ---
logger = LoggingUtils.setup_logger('device_spy_cli')
logging.getLogger("httpx").setLevel(logging.WARNING)

app = typer.Typer(
    name="ds",
    help="📱 Device Spy CLI - Device Management Tools",
    add_completion=False,
    rich_markup_mode="rich"
)

# --- Enhanced CLI Instance ---
# All command logic is now handled by the enhanced, refactored implementation.
cli_commands = CLICommands()


# --- CLI Command Definitions ---
@app.command("udid")
def get_device_info(udid: str = typer.Argument(..., help="Device UDID to lookup")):
    """📱 Display detailed information for a specific device."""
    cli_commands.get_device_info(udid)


@app.command("devices")
def list_available_devices(platform: str = typer.Argument(..., help="Platform: android or ios")):
    """📋 List available devices for a platform."""
    cli_commands.list_available_devices(platform)


@app.command("host")
def find_host_info(
    query: str = typer.Argument(..., help="Host query string (hostname or alias)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed host information")
):
    """🖥️  Find host information by query."""
    cli_commands.find_host_info(query, detailed)


@app.command("ssh")
def ssh_connect(query: str = typer.Argument(..., help="Host query string to connect via SSH")):
    """🔗 Connect to a host via SSH."""
    cli_commands.ssh_connect(query)


@app.command("connect")
def adb_connect(udid: str = typer.Argument(..., help="Android device UDID to connect via ADB")):
    """🤖 Connect to Android device via ADB."""
    cli_commands.adb_connect(udid)


@app.command("android-ip")
def get_android_connection(udid: str = typer.Argument(..., help="Android device UDID")):
    """🤖 Get Android device IP:Port for script usage."""
    cli_commands.get_android_connection(udid)


@app.command("host-ip")
def get_host_ip_for_script(query: str = typer.Argument(..., help="Host query string")):
    """🌐 Get host IP address for script usage."""
    cli_commands.get_host_ip_for_script(query)


@app.command("status")
def show_system_status():
    """📊 Show system status and cache information."""
    cli_commands.show_system_status()


@app.command("refresh")
def refresh_cache():
    """🔄 Refresh cached data from server."""
    cli_commands.refresh_cache()


def main_ds_function():
    """Main entry point for Device Spy CLI."""
    app()


if __name__ == "__main__":
    main_ds_function()

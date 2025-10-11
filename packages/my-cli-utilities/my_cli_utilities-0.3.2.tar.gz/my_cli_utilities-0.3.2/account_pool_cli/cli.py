# -*- coding: utf-8 -*-

import logging
from typing import Optional
import typer
from rich.console import Console

from my_cli_utilities_common.config import LoggingUtils
from .service import AccountService
from .display_manager import DisplayManager

# --- Setup ---
logger = LoggingUtils.setup_logger('account_pool_cli')
logging.getLogger("httpx").setLevel(logging.WARNING)

app = typer.Typer(
    name="ap",
    help="🏦 Account Pool CLI - Account Management Tools",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()

# --- Service and Display Instances ---
# All command logic is now handled by the refactored service-layer implementation.
account_service = AccountService()
display_manager = DisplayManager()


# --- CLI Command Definitions ---
@app.command("get")
def get_random_account(
    account_type: str = typer.Argument(..., help="Account type string or index number from 'ap types'"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """Get a random available account of a specific type."""
    account_service.get_random_account(account_type, env_name)


@app.command("by-id")
def get_account_by_id(
    account_id: str = typer.Argument(..., help="Account ID to lookup"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """Get account details by its specific Account ID."""
    account_service.get_account_by_id(account_id, env_name)


@app.command("info")
def get_info_by_phone(
    main_number: str = typer.Argument(..., help="Phone number to lookup"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """Get account details by its main phone number."""
    account_service.get_account_by_phone(main_number, env_name)


@app.command("types")
def list_account_types(
    filter_keyword: Optional[str] = typer.Argument(None, help="Filter account types by keyword (optional)"),
    brand: str = typer.Option(AccountService.DEFAULT_BRAND, "--brand", "-b", help="Brand ID")
):
    """List all available account types for a given brand."""
    account_service.list_account_types(brand, filter_keyword)


@app.command("cache")
def manage_cache(
    action: Optional[str] = typer.Argument(None, help="Action: 'clear' to clear cache, empty to show status")
):
    """Manage the local cache. Shows status by default."""
    account_service.manage_cache(action)


def main_cli_function():
    """Main entry point for Account Pool CLI."""
    app()


if __name__ == "__main__":
    main_cli_function()

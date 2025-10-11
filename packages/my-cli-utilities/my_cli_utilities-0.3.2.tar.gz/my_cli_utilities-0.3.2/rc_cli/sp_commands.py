# -*- coding: utf-8 -*-

"""Service Parameter (SP) commands for RC CLI."""

import asyncio
from typing import Optional, Dict, Any
import typer
from .sp_service import sp_service
from my_cli_utilities_common.config import DisplayUtils

# Create SP sub-app
sp_app = typer.Typer(
    name="sp",
    help="🔧 Service Parameter (SP) management commands",
    add_completion=False,
    rich_markup_mode="rich"
)


# Common utility functions
async def _get_sp_value_with_description(sp_id: str, account_id: str) -> tuple[Dict[str, Any], Optional[str]]:
    """Get SP value and description information."""
    # Get SP value
    result = await sp_service.get_service_parameter_value(sp_id, account_id)
    
    if not result.success:
        DisplayUtils.format_error(result.error_message)
        raise typer.Exit(1)
    
    sp_data = result.data
    
    # Get SP description for better display
    sp_def_result = await sp_service.get_service_parameter_definition(sp_id)
    sp_description = None
    if sp_def_result.success:
        sp_description = sp_def_result.data.get("description")
    
    return sp_data, sp_description


def _display_sp_value(sp_data: Dict[str, Any], sp_description: Optional[str] = None):
    """Display SP value with optional description."""
    typer.echo(f"\n📊 Service Parameter Value:")
    typer.echo("-" * 60)
    
    formatted_output = sp_service.format_sp_value_display(sp_data, sp_description)
    typer.echo(formatted_output)
    
    typer.echo("-" * 60)
    DisplayUtils.format_success("Successfully retrieved service parameter value")


def async_command(func):
    """Decorator for async commands."""
    def wrapper(*args, **kwargs):
        async def _async_wrapper():
            return await func(*args, **kwargs)
        asyncio.run(_async_wrapper())
    return wrapper


async def _resolve_phone_to_account_id(phone_number: str) -> str:
    """Resolve phone number to account ID using account pool service."""
    try:
        from account_pool_cli.data_manager import DataManager
        from returns.pipeline import is_successful
        
        data_manager = DataManager()
        
        # Get all accounts for the environment
        accounts_result = data_manager.get_all_accounts_for_env("webaqaxmn")
        
        if not is_successful(accounts_result):
            raise ValueError("Could not fetch accounts from account pool")
        
        accounts = accounts_result.unwrap()
        # Find account by phone number (with + prefix normalization)
        normalized_phone = "+" + phone_number if not phone_number.startswith("+") else phone_number
        for account in accounts:
            if account.get("mainNumber") == normalized_phone:
                return account.get("accountId")  # Use camelCase field name
        
        raise ValueError(f"Could not resolve phone number {phone_number} to account ID")
        
    except ImportError:
        raise ImportError("Account pool service not available")
    except Exception as e:
        raise ValueError(f"Error resolving phone number: {e}")


@sp_app.command("list")
def list_service_parameters(
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit the number of results to display"
    )
):
    """📋 List all service parameters
    
    Examples:
    
        rc sp list                    # List all service parameters
        rc sp list --limit 10         # List first 10 service parameters
    """
    DisplayUtils.format_search_info("All Service Parameters")
    
    async def _list_sps():
        result = await sp_service.get_all_service_parameters()
        
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)
        
        service_parameters = result.data
        total_count = result.count
        
        typer.echo(f"\n📊 Found {total_count} service parameters")
        typer.echo("-" * 60)
        
        # Apply limit if specified
        items_to_show = service_parameters
        if limit and limit > 0:
            items_to_show = dict(list(service_parameters.items())[:limit])
            if limit < total_count:
                typer.echo(f"Showing first {limit} of {total_count} parameters:")
        
        # Display service parameters
        for sp_id, description in items_to_show.items():
            formatted_line = sp_service.format_service_parameter_display(sp_id, description)
            typer.echo(formatted_line)
        
        if limit and limit < total_count:
            typer.echo(f"\n... and {total_count - limit} more parameters")
        
        typer.echo("-" * 60)
        DisplayUtils.format_success(f"Successfully retrieved {len(items_to_show)} service parameters")
    
    asyncio.run(_list_sps())


@sp_app.command("search")
def search_service_parameters(
    query: str = typer.Argument(..., help="Search query string"),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit the number of results to display"
    )
):
    """🔍 Search service parameters by description
    
    Examples:
    
        rc sp search "Call Handling"     # Search for Call Handling parameters
        rc sp search "SMS" --limit 5     # Search for SMS parameters, limit to 5 results
    """
    DisplayUtils.format_search_info("Service Parameters", {"Query": query})
    
    async def _search_sps():
        result = await sp_service.search_service_parameters(query)
        
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)
        
        matching_sps = result.data
        total_count = result.count
        
        if total_count == 0:
            typer.echo(f"\n❌ No service parameters found matching '{query}'")
            return
        
        typer.echo(f"\n📊 Found {total_count} matching service parameters")
        typer.echo("-" * 60)
        
        # Apply limit if specified
        items_to_show = matching_sps
        if limit and limit > 0:
            items_to_show = dict(list(matching_sps.items())[:limit])
            if limit < total_count:
                typer.echo(f"Showing first {limit} of {total_count} results:")
        
        # Display matching service parameters
        for sp_id, description in items_to_show.items():
            formatted_line = sp_service.format_service_parameter_display(sp_id, description)
            typer.echo(formatted_line)
        
        if limit and limit < total_count:
            typer.echo(f"\n... and {total_count - limit} more results")
        
        typer.echo("-" * 60)
        DisplayUtils.format_success(f"Found {len(items_to_show)} matching service parameters")
    
    asyncio.run(_search_sps())


@sp_app.command("get")
def get_service_parameter_value(
    sp_id: str = typer.Argument(..., help="Service parameter ID"),
    account_identifier: str = typer.Argument(..., help="Account ID or phone number"),
    auto_resolve: bool = typer.Option(
        True,
        "--auto-resolve/--no-auto-resolve",
        help="Automatically resolve phone number to account ID"
    )
):
    """📊 Get service parameter value for a specific account
    
    Examples:
    
        rc sp get "1157" "8023391076"           # Get SP-1157 value for account 8023391076
        rc sp get "1157" "16789350903"          # Get SP-1157 value for phone 16789350903 (auto-resolve)
        rc sp get "1157" "16789350903" --no-auto-resolve  # Use phone as account ID directly
    """
    DisplayUtils.format_search_info("Service Parameter Value", {
        "SP ID": sp_id,
        "Account Identifier": account_identifier,
        "Auto Resolve": "Enabled" if auto_resolve else "Disabled"
    })
    
    async def _get_sp_value():
        # Determine if we need to resolve phone number to account ID
        account_id = account_identifier
        
        if auto_resolve and len(account_identifier) == 11 and account_identifier.isdigit():
            # Looks like a phone number, try to resolve it
            typer.echo(f"🔍 Detected phone number, attempting to resolve to account ID...")
            
            try:
                account_id = await _resolve_phone_to_account_id(account_identifier)
                typer.echo(f"✅ Resolved phone {account_identifier} to account ID: {account_id}")
            except ValueError as e:
                typer.echo(f"⚠️  {e}, using as account ID")
                account_id = account_identifier
            except ImportError as e:
                typer.echo(f"⚠️  {e}, using as account ID")
                account_id = account_identifier
        
        # Get SP value and description
        sp_data, sp_description = await _get_sp_value_with_description(sp_id, account_id)
        
        # Display the result
        _display_sp_value(sp_data, sp_description)
    
    asyncio.run(_get_sp_value())


@sp_app.command("get-by-phone")
def get_service_parameter_value_by_phone(
    sp_id: str = typer.Argument(..., help="Service parameter ID"),
    phone_number: str = typer.Argument(..., help="Phone number (11 digits)")
):
    """📱 Get service parameter value by phone number
    
    This command automatically resolves the phone number to account ID and then queries the SP value.
    
    Examples:
    
        rc sp get-by-phone "1157" "16789350903"     # Get SP-1157 value for phone 16789350903
    """
    DisplayUtils.format_search_info("Service Parameter Value by Phone", {
        "SP ID": sp_id,
        "Phone Number": phone_number
    })
    
    async def _get_sp_value_by_phone():
        # Validate phone number format
        if len(phone_number) != 11 or not phone_number.isdigit():
            DisplayUtils.format_error("Phone number must be 11 digits")
            raise typer.Exit(1)
        
        typer.echo(f"🔍 Resolving phone number {phone_number} to account ID...")
        
        try:
            account_id = await _resolve_phone_to_account_id(phone_number)
            typer.echo(f"✅ Resolved phone {phone_number} to account ID: {account_id}")
            
            # Get SP value and description
            sp_data, sp_description = await _get_sp_value_with_description(sp_id, account_id)
            
            # Display the result
            _display_sp_value(sp_data, sp_description)
            
        except ValueError as e:
            DisplayUtils.format_error(str(e))
            raise typer.Exit(1)
        except ImportError as e:
            DisplayUtils.format_error("Account pool service not available. Please use 'rc sp get' command instead.")
            raise typer.Exit(1)
    
    asyncio.run(_get_sp_value_by_phone())


@sp_app.command("describe")
def describe_service_parameter(
    sp_id: str = typer.Argument(..., help="Service parameter ID")
):
    """📖 Get detailed description of a service parameter
    
    Examples:
    
        rc sp describe "1157"     # Get description for SP 1157
    """
    DisplayUtils.format_search_info("Service Parameter Description", {
        "SP ID": sp_id
    })
    
    async def _describe_sp():
        result = await sp_service.get_service_parameter_definition(sp_id)
        
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)
        
        sp_data = result.data
        sp_id_from_data = sp_data.get("id")
        description = sp_data.get("description")
        
        typer.echo(f"\n📖 Service Parameter Description:")
        typer.echo("-" * 60)
        typer.echo(f"  📋 SP ID: {sp_id_from_data}")
        typer.echo(f"  📝 Description: {description}")
        typer.echo("-" * 60)
        DisplayUtils.format_success("Successfully retrieved service parameter description")
    
    asyncio.run(_describe_sp())


@sp_app.command("info")
def show_sp_info():
    """ℹ️  Show SP service configuration and usage information"""
    typer.echo("\n🔧 Service Parameter (SP) Management")
    typer.echo("=" * 50)
    
    typer.echo("📋 Available Commands:")
    typer.echo("  rc sp list [--limit N]                    # List all service parameters")
    typer.echo("  rc sp search <query> [--limit N]          # Search service parameters")
    typer.echo("  rc sp get <sp_id> <account_identifier>    # Get SP value for account")
    typer.echo("  rc sp get-by-phone <sp_id> <phone>        # Get SP value by phone number")
    typer.echo("  rc sp describe <sp_id>                    # Get SP description and details")
    typer.echo("  rc sp info                                # Show this help")
    
    typer.echo("\n💡 Examples:")
    typer.echo("  rc sp list                                # Show all SPs")
    typer.echo("  rc sp search 'Call Handling'              # Find Call Handling SPs")
    typer.echo("  rc sp describe '1157'                     # Get SP 1157 description")
    typer.echo("  rc sp get '1157' '8023391076'             # Get SP value for account ID")
    typer.echo("  rc sp get '1157' '16789350903'            # Get SP value for phone (auto-resolve)")
    typer.echo("  rc sp get-by-phone '1157' '16789350903'   # Get SP value by phone number")
    typer.echo("  rc sp get '1157' '16789350903' --no-auto-resolve  # Use phone as account ID")
    
    typer.echo("\n🔍 Smart Account Resolution:")
    typer.echo("  • 11-digit numbers are automatically resolved as phone numbers")
    typer.echo("  • Phone numbers are resolved to account IDs using account pool service")
    typer.echo("  • Use --no-auto-resolve to disable automatic resolution")
    
    typer.echo("\n⚙️  Configuration:")
    typer.echo("  GitLab Token: Set GITLAB_TOKEN environment variable")
    typer.echo("  Internal API: http://intapi-webaqaxmn.int.rclabenv.com:8082")
    
    typer.echo("\n🔗 Related:")
    typer.echo("  For more information, see the mcp-sp project documentation")

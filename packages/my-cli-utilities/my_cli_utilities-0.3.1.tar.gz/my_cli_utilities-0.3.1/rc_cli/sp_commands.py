# -*- coding: utf-8 -*-

"""Service Parameter (SP) commands for RC CLI."""

import asyncio
from typing import Optional
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
    account_id: str = typer.Argument(..., help="Account ID")
):
    """📊 Get service parameter value for a specific account
    
    Examples:
    
        rc sp get "SP-123" "8023391076"     # Get SP-123 value for account 8023391076
    """
    DisplayUtils.format_search_info("Service Parameter Value", {
        "SP ID": sp_id,
        "Account ID": account_id
    })
    
    async def _get_sp_value():
        result = await sp_service.get_service_parameter_value(sp_id, account_id)
        
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)
        
        sp_data = result.data
        
        typer.echo(f"\n📊 Service Parameter Value:")
        typer.echo("-" * 40)
        
        formatted_output = sp_service.format_sp_value_display(sp_data)
        typer.echo(formatted_output)
        
        typer.echo("-" * 40)
        DisplayUtils.format_success("Successfully retrieved service parameter value")
    
    asyncio.run(_get_sp_value())


@sp_app.command("info")
def show_sp_info():
    """ℹ️  Show SP service configuration and usage information"""
    typer.echo("\n🔧 Service Parameter (SP) Management")
    typer.echo("=" * 50)
    
    typer.echo("📋 Available Commands:")
    typer.echo("  rc sp list [--limit N]              # List all service parameters")
    typer.echo("  rc sp search <query> [--limit N]    # Search service parameters")
    typer.echo("  rc sp get <sp_id> <account_id>      # Get SP value for account")
    typer.echo("  rc sp info                          # Show this help")
    
    typer.echo("\n💡 Examples:")
    typer.echo("  rc sp list                          # Show all SPs")
    typer.echo("  rc sp search 'Call Handling'        # Find Call Handling SPs")
    typer.echo("  rc sp get 'SP-123' '8023391076'     # Get SP value")
    
    typer.echo("\n⚙️  Configuration:")
    typer.echo("  GitLab Token: Set GITLAB_TOKEN environment variable")
    typer.echo("  Internal API: http://intapi-webaqaxmn.int.rclabenv.com:8082")
    
    typer.echo("\n🔗 Related:")
    typer.echo("  For more information, see the mcp-sp project documentation")

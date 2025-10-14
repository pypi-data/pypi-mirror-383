"""Command-line interface for MCP ToolBox"""

import click
import sys
import os
from pathlib import Path
from getpass import getpass
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from .config import config
from .client import ToolBoxClient

console = Console()


@click.group()
@click.version_option()
def cli():
    """MCP ToolBox CLI - Upload and manage MCP tools"""
    pass


@cli.command()
@click.option('--email', help='Your email address')
@click.option('--password', help='Your password')
@click.option('--token', help='Personal Access Token (PAT)')
@click.option('--url', 
              help='API URL (overrides current configuration)')
def login(email: Optional[str], password: Optional[str], token: Optional[str], url: Optional[str]):
    """Login to MCP ToolBox and save credentials (use --token for PAT or --email/--password for username/password)"""
    try:
        # Use provided URL or fall back to current configuration
        api_url = url or config.api_url
        
        # Test endpoint first if URL was provided
        if url:
            console.print(f"[yellow]Testing endpoint: {url}[/yellow]")
            try:
                import requests
                test_url = url.rstrip('/') + '/api/system/status'
                response = requests.get(test_url, timeout=10)
                response.raise_for_status()
                config.api_url = url.rstrip('/')
                console.print("[green]✓ Endpoint verified[/green]")
            except Exception as e:
                console.print(f"[red]✗ Endpoint test failed: {e}[/red]")
                if not click.confirm("Continue with login anyway?"):
                    sys.exit(1)

        # PAT authentication (preferred)
        if token:
            config.api_token = token
            # Verify token by getting user info
            client = ToolBoxClient(api_url, token)
            user = client.get_user_info()
            
            console.print(Panel.fit(
                f"[bold green]✓ Successfully authenticated using PAT[/bold green]\n\n"
                f"[cyan]User:[/cyan] {user['email']}\n"
                f"[cyan]Endpoint:[/cyan] {api_url}\n"
                f"[cyan]Config:[/cyan] {config.config_file}",
                title="[bold]Authentication Success",
                border_style="green"
            ))
        # Username/password authentication
        elif email and password:
            client = ToolBoxClient(api_url)
            auth_token = client.login(email, password)
            config.api_token = auth_token

            # Verify login by getting user info
            client = ToolBoxClient(api_url, auth_token)
            user = client.get_user_info()

            console.print(Panel.fit(
                f"[bold green]✓ Successfully logged in[/bold green]\n\n"
                f"[cyan]User:[/cyan] {user['email']}\n"
                f"[cyan]Endpoint:[/cyan] {api_url}\n"
                f"[cyan]Config:[/cyan] {config.config_file}",
                title="[bold]Login Success",
                border_style="green"
            ))
        # Interactive mode
        else:
            click.echo("Choose authentication method:")
            click.echo("1. Personal Access Token (recommended)")
            click.echo("2. Email/Password")
            choice = click.prompt("Enter choice", type=int, default=1)

            if choice == 1:
                pat = click.prompt("Enter your Personal Access Token", hide_input=True)
                config.api_token = pat
                # Verify token
                client = ToolBoxClient(api_url, pat)
                user = client.get_user_info()
                
                console.print(Panel.fit(
                    f"[bold green]✓ Successfully authenticated using PAT[/bold green]\n\n"
                    f"[cyan]User:[/cyan] {user['email']}\n"
                    f"[cyan]Endpoint:[/cyan] {api_url}\n"
                    f"[cyan]Config:[/cyan] {config.config_file}",
                    title="[bold]Authentication Success",
                    border_style="green"
                ))
            else:
                email = click.prompt("Email")
                password = click.prompt("Password", hide_input=True)
                client = ToolBoxClient(api_url)
                auth_token = client.login(email, password)
                config.api_token = auth_token

                # Verify login
                client = ToolBoxClient(api_url, auth_token)
                user = client.get_user_info()
                
                console.print(Panel.fit(
                    f"[bold green]✓ Successfully logged in[/bold green]\n\n"
                    f"[cyan]User:[/cyan] {user['email']}\n"
                    f"[cyan]Endpoint:[/cyan] {api_url}\n"
                    f"[cyan]Config:[/cyan] {config.config_file}",
                    title="[bold]Login Success",
                    border_style="green"
                ))

    except Exception as e:
        click.echo(f"✗ Login failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def logout():
    """Logout and clear saved credentials"""
    config.clear()
    click.echo("✓ Logged out successfully")


@cli.command()
def whoami():
    """Show current logged-in user"""
    if not config.api_token:
        console.print("[red]✗ Not logged in. Run 'mcp-toolbox login' first[/red]")
        sys.exit(1)

    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        user = client.get_user_info()
        
        console.print(Panel.fit(
            f"[bold cyan]Logged in as:[/bold cyan] {user['email']}\n"
            f"[cyan]User ID:[/cyan] {user['id']}\n"
            f"[cyan]Role:[/cyan] {'Admin' if user.get('is_admin') else 'User'}\n"
            f"[cyan]API Endpoint:[/cyan] {config.api_url}",
            title="[bold]User Information",
            border_style="blue"
        ))
    except Exception as e:
        console.print(f"[red]✗ Failed to get user info: {e}[/red]")
        sys.exit(1)


@cli.command()
def status():
    """Show CLI configuration and platform connectivity"""
    # Get configuration with sources
    api_url, url_source = config.get_effective_api_url()
    api_token, token_source = config.get_effective_api_token()
    
    console.print("[bold cyan]MCP ToolBox CLI Status[/bold cyan]\n")
    
    # Configuration table
    config_table = Table(show_header=True, header_style="bold magenta")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="white")
    config_table.add_column("Source", style="yellow")
    
    config_table.add_row("API URL", api_url, url_source)
    config_table.add_row(
        "API Token", 
        "***" if api_token else "(not set)",
        token_source
    )
    
    console.print(config_table)
    
    # Test connectivity
    console.print(f"\n[bold yellow]Testing connectivity to {api_url}...[/bold yellow]")
    
    try:
        client = ToolBoxClient(api_url, api_token)
        
        with console.status("[bold green]Checking system status..."):
            # Use direct API call since we might not have this method in client yet
            response = client.session.get(f'{client.api_url}/api/system/status')
            response.raise_for_status()
            system_status = response.json()
            
        # System status
        status_color = "green" if system_status.get('overall') == 'healthy' else "red"
        console.print(f"[bold {status_color}]System Status: {system_status.get('overall', 'unknown').upper()}[/bold {status_color}]")
        
        # Component status table
        if system_status.get('api') or system_status.get('database') or system_status.get('storage'):
            status_table = Table(show_header=True, header_style="bold magenta")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="white")
            status_table.add_column("Response Time", style="yellow")
            
            for component in ['api', 'database', 'storage']:
                if component in system_status:
                    comp_data = system_status[component]
                    status_color = "green" if comp_data.get('status') == 'healthy' else "red"
                    status_table.add_row(
                        component.upper(),
                        f"[{status_color}]{comp_data.get('status', 'unknown')}[/{status_color}]",
                        f"{comp_data.get('response_time', 'N/A')}ms" if comp_data.get('response_time') else "N/A"
                    )
            
            console.print(status_table)
        
        # User info if authenticated
        if api_token:
            try:
                user = client.get_user_info()
                console.print(f"\n[bold green]✓ Authenticated as: {user['email']}[/bold green]")
            except:
                console.print(f"\n[bold red]✗ Authentication failed - check your token[/bold red]")
        else:
            console.print(f"\n[bold yellow]⚠ Not authenticated - use 'mcp-toolbox login'[/bold yellow]")
            
    except Exception as e:
        console.print(f"[bold red]✗ Connection failed: {e}[/bold red]")
        console.print("\n[yellow]Troubleshooting tips:[/yellow]")
        console.print("• Check your internet connection")
        console.print("• Verify the API URL is correct")
        console.print("• Ensure the endpoint is running")
        console.print("• Try: mcp-toolbox config endpoint <url>")
        sys.exit(1)


@cli.command()
@click.option('--page', default=1, help='Page number')
@click.option('--page-size', default=10, help='Tools per page')
def list(page: int, page_size: int):
    """List available tools"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        data = client.list_tools(page, page_size)

        console.print(f"\n[bold blue]Showing {len(data['tools'])} of {data['total']} tools (page {page})[/bold blue]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="green")
        table.add_column("Downloads", justify="right", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Tags", style="blue")

        for tool in data['tools']:
            tags_str = ', '.join(tool.get('tags', [])) if tool.get('tags') else ""
            description = tool.get('description', '')
            if len(description) > 50:
                description = description[:47] + "..."
                
            table.add_row(
                tool['name'],
                f"v{tool['version']}",
                str(tool.get('downloads', 0)),
                description,
                tags_str
            )

        console.print(table)
    except Exception as e:
        click.echo(f"✗ Failed to list tools: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--name', prompt=True, help='Tool name')
@click.option('--version', prompt=True, help='Tool version')
@click.option('--description', prompt=True, help='Tool description')
@click.option('--tags', help='Comma-separated tags')
@click.option('--thumbnail', type=click.Path(exists=True, path_type=Path), help='Thumbnail image')
def upload(file: Path, name: str, version: str, description: str, tags: Optional[str], thumbnail: Optional[Path]):
    """Upload a new tool to MCP ToolBox"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        tags_list = [t.strip() for t in tags.split(',')] if tags else []

        with console.status(f"[bold green]Uploading {file.name}..."):
            client = ToolBoxClient(config.api_url, config.api_token)
            tool = client.upload_tool(
                name=name,
                version=version,
                description=description,
                file_path=file,
                tags=tags_list,
                thumbnail_path=thumbnail
            )

        console.print(Panel.fit(
            f"[bold green]✓ Tool uploaded successfully![/bold green]\n\n"
            f"[cyan]ID:[/cyan] {tool['id']}\n"
            f"[cyan]Name:[/cyan] {tool['name']}\n"
            f"[cyan]Version:[/cyan] {tool['version']}\n"
            f"[cyan]View at:[/cyan] {config.api_url}/tools/{tool['id']}",
            title="[bold]Upload Success",
            border_style="green"
        ))
    except Exception as e:
        click.echo(f"✗ Upload failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('tool-id')
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--version', prompt=True, help='New version number')
@click.option('--changelog', help='Version changelog')
def new_version(tool_id: str, file: Path, version: str, changelog: Optional[str]):
    """Upload a new version of an existing tool"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        click.echo(f"Uploading new version {version}...")
        client = ToolBoxClient(config.api_url, config.api_token)
        result = client.create_version(
            tool_id=tool_id,
            version=version,
            file_path=file,
            changelog=changelog
        )

        click.echo(f"✓ New version uploaded successfully!")
        click.echo(f"  Version: {result['version']}")
        click.echo(f"  Tool: {result['tool_name']}")
    except Exception as e:
        click.echo(f"✗ Upload failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('tool-id')
@click.argument('thumbnail', type=click.Path(exists=True, path_type=Path))
def update_thumbnail(tool_id: str, thumbnail: Path):
    """Update the thumbnail for a tool"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        click.echo(f"Updating thumbnail...")
        client = ToolBoxClient(config.api_url, config.api_token)
        tool = client.update_thumbnail(tool_id, thumbnail)

        click.echo(f"✓ Thumbnail updated successfully!")
        click.echo(f"  Tool: {tool['name']}")
    except Exception as e:
        click.echo(f"✗ Update failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('github-url')
@click.option('--name', help='Tool name (auto-detected if not provided)')
@click.option('--description', help='Tool description (auto-detected if not provided)')
@click.option('--version', help='Tool version (auto-detected if not provided)')
def upload_github(github_url: str, name: Optional[str], description: Optional[str], version: Optional[str]):
    """Upload a tool from GitHub repository"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        with console.status(f"[bold green]Uploading from GitHub: {github_url}"):
            client = ToolBoxClient(config.api_url, config.api_token)
            tool = client.upload_from_github(
                github_url=github_url,
                name=name,
                description=description,
                version=version
            )

        console.print(Panel.fit(
            f"[bold green]✓ Tool uploaded successfully from GitHub![/bold green]\n\n"
            f"[cyan]ID:[/cyan] {tool['id']}\n"
            f"[cyan]Name:[/cyan] {tool['name']}\n"
            f"[cyan]Version:[/cyan] {tool['version']}\n"
            f"[cyan]View at:[/cyan] {config.api_url}/tools/{tool['id']}",
            title="[bold]GitHub Upload Success",
            border_style="green"
        ))
    except Exception as e:
        click.echo(f"✗ Upload failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('tool-id')
def update_from_github(tool_id: str):
    """Update a tool from its connected GitHub repository"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        click.echo(f"Updating tool from GitHub...")
        client = ToolBoxClient(config.api_url, config.api_token)
        tool = client.update_from_github(tool_id)

        click.echo(f"✓ Tool updated successfully from GitHub!")
        click.echo(f"  Name: {tool['name']}")
        click.echo(f"  Version: {tool['version']}")
    except Exception as e:
        click.echo(f"✗ Update failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('tool-id')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file path')
def download(tool_id: str, output: Optional[Path]):
    """Download a tool"""
    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        file_path = client.download_tool(tool_id, output_path=output)
        
        click.echo(f"✓ Tool downloaded successfully!")
        click.echo(f"  File: {file_path}")
    except Exception as e:
        click.echo(f"✗ Download failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--category', help='Filter by category')
@click.option('--tags', help='Filter by tags (comma-separated)')
@click.option('--page', default=1, help='Page number')
@click.option('--page-size', default=10, help='Results per page')
def search(query: str, category: Optional[str], tags: Optional[str], page: int, page_size: int):
    """Search for tools"""
    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        
        filters = {}
        if category:
            filters['category'] = category
        if tags:
            filters['tags'] = [t.strip() for t in tags.split(',')]
            
        data = client.search_tools(
            query=query,
            filters=filters,
            page=page,
            page_size=page_size
        )
        
        click.echo(f"\nFound {data['total']} tools matching '{query}' (page {page}):\n")
        
        for tool in data['tools']:
            click.echo(f"  {tool['name']} v{tool['version']}")
            click.echo(f"    ID: {tool['id']}")
            if tool.get('description'):
                click.echo(f"    Description: {tool['description']}")
            click.echo(f"    Downloads: {tool.get('downloads', 0)}")
            if tool.get('tags'):
                click.echo(f"    Tags: {', '.join(tool['tags'])}")
            click.echo()
    except Exception as e:
        click.echo(f"✗ Search failed: {e}", err=True)
        sys.exit(1)


# Personal Access Token management commands
@cli.group()
def tokens():
    """Manage Personal Access Tokens"""
    pass


@tokens.command()
@click.option('--name', prompt=True, help='Token name')
@click.option('--expires-days', type=int, help='Token expiration in days (default: no expiration)')
def create(name: str, expires_days: Optional[int]):
    """Create a new Personal Access Token"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        token_data = client.create_personal_token(name, expires_days)
        
        click.echo(f"✓ Personal Access Token created!")
        click.echo(f"  Name: {token_data['name']}")
        click.echo(f"  Token: {token_data['token']}")
        click.echo(f"  ⚠️  Save this token now - it won't be shown again!")
        
        if token_data.get('expires_at'):
            click.echo(f"  Expires: {token_data['expires_at']}")
    except Exception as e:
        click.echo(f"✗ Token creation failed: {e}", err=True)
        sys.exit(1)


@tokens.command('list')
def list_tokens():
    """List your Personal Access Tokens"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        tokens_list = client.list_personal_tokens()
        
        if not tokens_list:
            click.echo("No Personal Access Tokens found")
            return
            
        click.echo(f"\nYour Personal Access Tokens:\n")
        
        for token in tokens_list:
            click.echo(f"  {token['name']}")
            click.echo(f"    ID: {token['id']}")
            click.echo(f"    Created: {token['created_at']}")
            if token.get('expires_at'):
                click.echo(f"    Expires: {token['expires_at']}")
            else:
                click.echo(f"    Expires: Never")
            click.echo()
    except Exception as e:
        click.echo(f"✗ Failed to list tokens: {e}", err=True)
        sys.exit(1)


@tokens.command()
@click.argument('token-id')
def delete(token_id: str):
    """Delete a Personal Access Token"""
    if not config.api_token:
        click.echo("✗ Not logged in. Run 'mcp-toolbox login' first", err=True)
        sys.exit(1)

    try:
        if click.confirm(f"Are you sure you want to delete token {token_id}?"):
            client = ToolBoxClient(config.api_url, config.api_token)
            client.delete_personal_token(token_id)
            
            click.echo(f"✓ Token {token_id} deleted successfully!")
    except Exception as e:
        click.echo(f"✗ Token deletion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('tool-id')
def info(tool_id: str):
    """Show detailed information about a tool"""
    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        tool = client.get_tool_info(tool_id)
        
        click.echo(f"\nTool Information:")
        click.echo(f"  Name: {tool['name']}")
        click.echo(f"  ID: {tool['id']}")
        click.echo(f"  Version: {tool['version']}")
        click.echo(f"  Author: {tool['author']}")
        click.echo(f"  Downloads: {tool.get('downloads', 0)}")
        click.echo(f"  Created: {tool['created_at']}")
        click.echo(f"  Updated: {tool['updated_at']}")
        
        if tool.get('description'):
            click.echo(f"  Description: {tool['description']}")
        if tool.get('tags'):
            click.echo(f"  Tags: {', '.join(tool['tags'])}")
        if tool.get('category'):
            click.echo(f"  Category: {tool['category']}")
        if tool.get('github_url'):
            click.echo(f"  GitHub: {tool['github_url']}")
            
        # Show versions
        versions = client.get_tool_versions(tool_id)
        if len(versions) > 1:
            click.echo(f"\n  Available Versions:")
            for version in versions:
                click.echo(f"    v{version['version']} - {version['created_at']}")
                if version.get('changelog'):
                    click.echo(f"      {version['changelog']}")
        
    except Exception as e:
        click.echo(f"✗ Failed to get tool info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('tool-id')
@click.argument('version-id')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file path')
def download_version(tool_id: str, version_id: str, output: Optional[Path]):
    """Download a specific version of a tool"""
    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        file_path = client.download_tool_version(tool_id, version_id, output_path=output)
        
        click.echo(f"✓ Tool version downloaded successfully!")
        click.echo(f"  File: {file_path}")
    except Exception as e:
        click.echo(f"✗ Download failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def stats():
    """Show platform statistics"""
    try:
        client = ToolBoxClient(config.api_url, config.api_token)
        # Make request to stats endpoint
        response = client.session.get(f'{client.api_url}/api/stats')
        response.raise_for_status()
        stats_data = response.json()
        
        click.echo(f"\nPlatform Statistics:")
        click.echo(f"  Total Tools: {stats_data.get('total_tools', 0)}")
        click.echo(f"  Total Downloads: {stats_data.get('total_downloads', 0)}")
        click.echo(f"  Total Users: {stats_data.get('total_users', 0)}")
        if stats_data.get('popular_tools'):
            click.echo(f"\n  Popular Tools:")
            for tool in stats_data['popular_tools'][:5]:
                click.echo(f"    {tool['name']} - {tool.get('downloads', 0)} downloads")
                
    except Exception as e:
        click.echo(f"✗ Failed to get statistics: {e}", err=True)
        sys.exit(1)


@cli.group()
def config_cmd():
    """Manage CLI configuration"""
    pass


@config_cmd.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key: str, value: str):
    """Set a configuration value"""
    valid_keys = ['api_url', 'api_token']
    
    if key not in valid_keys:
        console.print(f"[red]✗ Invalid configuration key: {key}[/red]")
        console.print(f"[yellow]Valid keys: {', '.join(valid_keys)}[/yellow]")
        sys.exit(1)
    
    if key == 'api_url':
        # Validate URL format
        if not value.startswith(('http://', 'https://')):
            console.print(f"[red]✗ API URL must start with http:// or https://[/red]")
            sys.exit(1)
        config.api_url = value.rstrip('/')
    elif key == 'api_token':
        config.api_token = value
    
    console.print(f"[green]✓ Set {key} = {value}[/green]")


@config_cmd.command('get')
@click.argument('key', required=False)
def config_get(key: Optional[str]):
    """Get configuration value(s)"""
    if key:
        if key == 'api_url':
            console.print(f"api_url = {config.api_url}")
        elif key == 'api_token':
            token = config.api_token
            if token:
                # Mask token for security
                masked = token[:8] + '...' + token[-4:] if len(token) > 12 else '***'
                console.print(f"api_token = {masked}")
            else:
                console.print("api_token = (not set)")
        else:
            console.print(f"[red]✗ Unknown configuration key: {key}[/red]")
    else:
        # Show all configuration
        console.print("[bold cyan]Current Configuration:[/bold cyan]")
        console.print(f"  api_url = {config.api_url}")
        
        token = config.api_token
        if token:
            masked = token[:8] + '...' + token[-4:] if len(token) > 12 else '***'
            console.print(f"  api_token = {masked}")
        else:
            console.print("  api_token = (not set)")
            
        # Show environment variables if set
        env_vars = []
        if os.getenv('MCP_TOOLBOX_API_URL'):
            env_vars.append(f"MCP_TOOLBOX_API_URL = {os.getenv('MCP_TOOLBOX_API_URL')}")
        if os.getenv('TOOLBOX_API_URL'):
            env_vars.append(f"TOOLBOX_API_URL = {os.getenv('TOOLBOX_API_URL')}")
        if os.getenv('MCP_TOOLBOX_API_TOKEN'):
            env_vars.append("MCP_TOOLBOX_API_TOKEN = ***")
        if os.getenv('TOOLBOX_API_TOKEN'):
            env_vars.append("TOOLBOX_API_TOKEN = ***")
            
        if env_vars:
            console.print("\n[bold yellow]Environment Variables:[/bold yellow]")
            for var in env_vars:
                console.print(f"  {var}")


@config_cmd.command('clear')
def config_clear():
    """Clear all configuration"""
    if click.confirm("Are you sure you want to clear all configuration?"):
        config.clear()
        console.print("[green]✓ Configuration cleared[/green]")


@config_cmd.command('endpoint')
@click.argument('url')
def config_endpoint(url: str):
    """Set the API endpoint URL"""
    if not url.startswith(('http://', 'https://')):
        console.print(f"[red]✗ URL must start with http:// or https://[/red]")
        sys.exit(1)
    
    # Test the endpoint
    try:
        import requests
        test_url = url.rstrip('/') + '/api/system/status'
        
        with console.status(f"[bold green]Testing endpoint: {url}"):
            response = requests.get(test_url, timeout=10)
            response.raise_for_status()
            
        config.api_url = url.rstrip('/')
        console.print(Panel.fit(
            f"[bold green]✓ Endpoint set successfully![/bold green]\n\n"
            f"[cyan]URL:[/cyan] {config.api_url}\n"
            f"[cyan]Status:[/cyan] Connected",
            title="[bold]Endpoint Configuration",
            border_style="green"
        ))
        
    except requests.exceptions.ConnectTimeout:
        console.print(f"[red]✗ Connection timeout - endpoint may be unreachable[/red]")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        console.print(f"[red]✗ Connection failed - check URL and network connectivity[/red]")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            console.print(f"[red]✗ Endpoint doesn't appear to be a MCP ToolBox instance[/red]")
        else:
            console.print(f"[red]✗ HTTP error {e.response.status_code}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error testing endpoint: {e}[/red]")
        sys.exit(1)


# Add the config command group to the main CLI
cli.add_command(config_cmd, name='config')


if __name__ == '__main__':
    cli()

"""
Configuration management commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.config import Config
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info
from ..utils.config_schema import build_config_schema

console = get_console()

@click.group()
def config():
    """⚙️ CLI configuration and environment management
    
    Configure IvyBloom CLI settings, endpoints, and preferences for optimal 
    performance in your environment.
    
    CONFIGURATION CATEGORIES:
    
      🌐 Endpoints & URLs:      API and frontend server addresses
      🔐 Authentication:        Default auth methods and tokens
      📊 Output & Display:      Formatting, colors, and verbosity  
      ⚡ Performance:          Timeouts, concurrency, caching
      📁 Project Settings:     Default project IDs and directories
    
    COMMON SETTINGS (with defaults):
    
      • api_url (default: https://www.ivybiosciences.com/api/v1)
          Base API endpoint for all requests.
      • frontend_url (default: https://www.ivybiosciences.com)
          Web app URL used for browser auth and link checks.
      • default_project_id (default: none)
          Project ID used when not specified on commands.
      • output_format (default: json)
          Default output format (json, yaml, table, csv).
      • timeout (default: 30)
          Request timeout in seconds.
      • retries (default: 3)
          Number of retry attempts for failed requests.
      • debug (default: false)
          Enable verbose debug logging.
      • disable_keyring (default: true)
          Disable system keyring; store credentials in config files instead.
    
    CONFIGURATION WORKFLOW:
    
      1. View current settings:    ivybloom config show
      2. Set individual values:    ivybloom config set api_url https://api.example.com
      3. Get specific setting:     ivybloom config get timeout  
      4. Reset to defaults:        ivybloom config reset
      5. Validate configuration:   ivybloom config validate
      6. Interactive editor:       ivybloom config edit
    
    ENVIRONMENT VARIABLES:
    
      Settings can also be configured via environment variables:
      • IVY_API_URL, IVY_FRONTEND_URL
      • IVY_DEFAULT_PROJECT_ID  
      • IVY_DEBUG=true/false
      • IVY_TIMEOUT=30
    
    CONFIGURATION PRIORITY:
    
      1. Command-line arguments (highest)
      2. Environment variables  
      3. Config file settings
      4. Built-in defaults (lowest)
    
    💡 TIP: Use 'ivybloom config validate' to check for configuration issues
    💡 TIP: Environment variables override config file settings
    
    Run 'ivybloom config <command> --help' for detailed help on each command.
    """
    pass


@config.command()
@click.option('--reset', is_flag=True, help='Reset configuration to defaults (batch mode).')
@click.pass_context
def edit(ctx, reset):
    """Interactively edit common configuration values.

    Prompts for frequently used settings with current values as defaults.
    Press Enter to keep the existing value.
    """
    config_obj = ctx.obj['config']

    if reset:
        if click.confirm("Reset configuration to defaults?", default=False):
            config_obj.reset()
            print_success("Configuration reset to defaults.")
        else:
            print_info("Reset cancelled.")
        return

    # Current values
    current = config_obj.show_config()

    staged: dict[str, any] = {}

    def prompt_str(label: str, key: str) -> None:
        default_val = str(current.get(key) or "")
        val = click.prompt(label, default=default_val, show_default=True)
        # Only set when changed to avoid unnecessary writes
        if val != default_val:
            # Minimal validation for URLs
            if key in {"api_url","frontend_url"} and val and not (val.startswith("http://") or val.startswith("https://")):
                raise click.ClickException(f"{key} must start with http:// or https://")
            staged[key] = val

    def prompt_int(label: str, key: str) -> None:
        try:
            default_int = int(current.get(key) if current.get(key) is not None else 0)
        except Exception:
            default_int = 0
        val = click.prompt(label, default=default_int, show_default=True, type=int)
        if val != default_int:
            if val < 0:
                raise click.ClickException(f"{key} must be a non-negative integer")
            staged[key] = int(val)

    def prompt_choice(label: str, key: str, choices: list[str]) -> None:
        default_val = str(current.get(key) or choices[0])
        val = click.prompt(label, default=default_val, show_default=True, type=click.Choice(choices))
        if val != default_val:
            staged[key] = val

    def prompt_bool(label: str, key: str) -> None:
        default_bool = bool(current.get(key, False))
        val = click.confirm(label, default=default_bool, show_default=True)
        if val != default_bool:
            staged[key] = bool(val)

    console.print("[b]Interactive Configuration Editor[/b]")
    console.print("Press Enter to keep the current value shown in brackets.")

    # Endpoints
    prompt_str("API URL", "api_url")
    prompt_str("Frontend URL", "frontend_url")

    # Output & Theme
    prompt_choice("Output Format", "output_format", ["json", "yaml", "table", "csv"])
    prompt_choice("Theme", "theme", ["light", "dark"])

    # Performance
    prompt_int("Timeout (seconds)", "timeout")
    prompt_int("Retries", "retries")
    prompt_int("TUI Refresh Interval (seconds)", "tui_refresh_interval_secs")

    # Flags
    prompt_bool("Enable debug logging?", "debug")
    prompt_bool("Disable system keyring?", "disable_keyring")

    # Show path and confirm write
    console.print(f"Config file: {config_obj.config_path}")
    if not staged:
        print_info("No changes to apply.")
        return
    if click.confirm(f"Apply {len(staged)} changes?", default=True):
        for k, v in staged.items():
            config_obj.set(k, v)
        console.print("[green]✅ Configuration updated[/green]")
    else:
        print_info("No changes applied.")

@config.command()
@click.pass_context
def validate(ctx):
    """Validate configuration, connectivity, and optional dependencies.
    
    Checks:
      • Frontend URL resolves and CLI endpoints respond
      • API connectivity (account endpoint)
      • Optional tools: FlatProt (uvx/flatprot), DSSP (mkdssp)
    """
    import httpx
    import shutil
    config_obj = ctx.obj['config']
    table = Table(title="🔧 Configuration Validation")
    table.add_column("Check", style="cyan")
    table.add_column("Result", style="green")
    table.add_column("Details", style="yellow")
    # Frontend
    fe = config_obj.get_frontend_url()
    try:
        with httpx.Client(follow_redirects=True, timeout=10.0) as client:
            r = client.get(f"{fe.rstrip('/')}/api/cli/link-status/test")
        table.add_row("Frontend URL", "OK", f"{fe} ({r.status_code})")
    except Exception as e:
        table.add_row("Frontend URL", "FAIL", str(e))
    # Account (auth)
    try:
        from ..utils.auth import AuthManager
        from ..client.api_client import IvyBloomAPIClient
        am = AuthManager(config_obj)
        with IvyBloomAPIClient(config_obj, am) as client:
            info = client.get_account_info()
        table.add_row("Account endpoint", "OK", info.get('email', 'Unknown'))
    except Exception as e:
        table.add_row("Account endpoint", "FAIL", str(e))
    # Optional deps
    flatprot = bool(shutil.which("uvx") or shutil.which("flatprot"))
    table.add_row("FlatProt available", "Yes" if flatprot else "No", "uvx flatprot or flatprot on PATH")
    dssp = bool(shutil.which("mkdssp"))
    table.add_row("DSSP (mkdssp)", "Yes" if dssp else "No", "Required for PDB inputs (FlatProt)")
    console.print(table)

@click.argument('key')
@click.argument('value')
@click.option('--type', type=click.Choice(['string', 'int', 'float', 'bool', 'json']), help='Value type (auto-detected if not specified)')
@click.pass_context
def set(ctx, key, value, type):
    """⚙️ Set a configuration value
    
    Update CLI configuration settings. Values are automatically parsed based on
    content, or you can specify the type explicitly.
    
    COMMON SETTINGS:
    
      # Endpoint configuration
      ivybloom config set api_url https://api.ivybiosciences.com
      ivybloom config set frontend_url https://ivybiosciences.com
      
      # Default project and formatting  
      ivybloom config set default_project_id proj_abc123
      ivybloom config set output_format json
      
      # Performance tuning
      ivybloom config set timeout 60
      ivybloom config set max_concurrent_jobs 5
      ivybloom config set debug true
    
    VALUE TYPES:
    
      📄 Strings:     URLs, names, IDs (quoted or unquoted)
      🔢 Numbers:     Integers and floats (timeout: 30, rate: 1.5)
      ✅ Booleans:    true/false, yes/no, 1/0
      📋 JSON:        Complex objects {"key": "value"} or ["item1", "item2"]
    
    EXAMPLES:
    
      ivybloom config set debug true
      ivybloom config set timeout 30  
      ivybloom config set tags '["research", "covid"]' --type json
      ivybloom config set endpoints '{"api": "...", "web": "..."}' --type json
    
    Configuration is stored in ~/.config/ivybloom/config.json and takes effect
    immediately for new commands.
    
    💡 TIP: Use 'ivybloom config show' to see all current settings  
    💡 TIP: Complex JSON values should be quoted and use --type json
    """
    config_obj = ctx.obj['config']

    # Whitelist only safe, user-facing keys
    allowed_top = {"debug", "visualization"}
    if key not in allowed_top:
        raise click.ClickException(
            "Setting this configuration key is restricted. Allowed keys: 'debug', 'visualization'."
        )

    # Parse provided value (may be JSON)
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value

    if key == "debug":
        # Coerce to boolean
        val_str = str(parsed_value).strip().lower()
        if isinstance(parsed_value, bool):
            debug_val = parsed_value
        elif val_str in {"true", "1", "yes", "y"}:
            debug_val = True
        elif val_str in {"false", "0", "no", "n"}:
            debug_val = False
        else:
            raise click.ClickException("Invalid value for debug. Use true/false.")
        config_obj.set("debug", debug_val)
        console.print(f"[green]✅ Set debug = {debug_val}[/green]")
        return

    if key == "visualization":
        # Only allow specific subkeys
        if not isinstance(parsed_value, dict):
            raise click.ClickException("Visualization value must be a JSON object with allowed keys.")
        allowed_sub = {"prefer_flatprot", "flatprot_output_format", "flatprot_auto_open"}
        disallowed = [k for k in parsed_value.keys() if k not in allowed_sub]
        if disallowed:
            raise click.ClickException(
                f"Disallowed visualization keys: {', '.join(disallowed)}. Allowed: {', '.join(sorted(allowed_sub))}."
            )
        current = config_obj.get("visualization") or {}
        if not isinstance(current, dict):
            current = {}
        merged = dict(current)
        merged.update(parsed_value)
        # Normalize format
        if "flatprot_output_format" in merged:
            fmt = str(merged["flatprot_output_format"]).lower()
            if fmt not in {"svg", "png"}:
                fmt = "svg"
            merged["flatprot_output_format"] = fmt
        config_obj.set("visualization", merged)
        console.print(f"[green]✅ Updated visualization = {json.dumps(merged)}[/green]")
        return

@config.command()
@click.argument('key')
@click.option('--default', help='Default value if setting not found')
@click.pass_context
def get(ctx, key, default):
    """📋 Get a specific configuration value
    
    Retrieve the current value of a configuration setting. Useful for 
    scripting and automation.
    
    USAGE EXAMPLES:
    
      # Get individual settings  
      ivybloom config get api_url
      ivybloom config get timeout
      ivybloom config get debug
      
      # Use in scripts with default fallback
      ivybloom config get default_project_id --default proj_fallback
      
      # Check boolean settings
      ivybloom config get debug  # Returns: true or false
    
    RETURN VALUES:
    
      • Found setting: Prints the value and exits with code 0
      • Missing setting: Shows error message and exits with code 1  
      • With --default: Shows default value for missing settings (exit 0)
    
    SCRIPTING EXAMPLES:
    
      ```bash
      # Store setting in variable
      API_URL=$(ivybloom config get api_url)
      
      # Conditional logic based on setting
      if [ "$(ivybloom config get debug)" = "true" ]; then
          echo "Debug mode enabled"  
      fi
      
      # Use default values safely
      PROJECT=$(ivybloom config get default_project_id --default proj_main)
      ```
    
    💡 TIP: Use --default to avoid errors when settings might not exist
    💡 TIP: Perfect for shell scripting and automation workflows
    """
    config_obj = ctx.obj['config']
    
    value = config_obj.get(key)
    if value is None:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")
    else:
        console.print(f"{key} = {value}")

@config.command()
@click.pass_context
def list(ctx):
    """List all configuration values"""
    config_obj = ctx.obj['config']
    
    config_data = config_obj.show_config()
    
    table = Table(title="🔧 Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in config_data.items():
        table.add_row(key, str(value))
    
    console.print(table)

@config.command()
@click.option('--format', 'fmt', default='json', type=click.Choice(['json', 'yaml', 'table']), help='Output format')
@click.pass_context
def schema(ctx, fmt):
    """Output a machine-readable configuration schema.

    Includes all recognized keys with types, defaults, choices, and descriptions.
    """
    config_obj = ctx.obj['config']
    schema = build_config_schema(config_obj.defaults)
    if fmt == 'json':
        console.print(json.dumps(schema, indent=2))
        return
    if fmt == 'yaml':
        import yaml
        console.print(yaml.safe_dump(schema, default_flow_style=False))
        return
    # table output for human readability
    table = Table(title="🔧 Configuration Schema")
    table.add_column("Key", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Default", style="green")
    table.add_column("Description", style="yellow")
    for entry in schema.get('keys', []):
        default_str = json.dumps(entry.get('default'))
        table.add_row(entry.get('key', ''), entry.get('type', ''), default_str, entry.get('description', ''))
    console.print(table)

@config.command()
@click.option('--format', 'fmt', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.pass_context
def keys(ctx, fmt):
    """List supported configuration keys with defaults and descriptions."""
    config_obj = ctx.obj['config']
    schema = build_config_schema(config_obj.defaults)
    keys = schema.get('keys', [])
    if fmt == 'json':
        console.print(json.dumps(keys, indent=2))
        return
    if fmt == 'yaml':
        import yaml
        console.print(yaml.safe_dump(keys, default_flow_style=False))
        return
    table = Table(title="🔑 Supported Configuration Keys")
    table.add_column("Key", style="cyan")
    table.add_column("Default", style="green")
    table.add_column("Description", style="yellow")
    for entry in keys:
        default_str = json.dumps(entry.get('default'))
        table.add_row(entry.get('key', ''), default_str, entry.get('description', ''))
    console.print(table)

@config.command(name="show")
@click.pass_context
def show_config(ctx):
    """Show key runtime values (frontend URL, API URL, client_id)."""
    config_obj = ctx.obj['config']
    table = Table(title="🔧 IvyBloom Runtime Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("IVY_ORCHESTRATOR_URL (resolved)", config_obj.get_api_url())
    table.add_row("IVY_FRONTEND_URL (resolved)", config_obj.get_frontend_url())
    table.add_row("client_id", config_obj.get_or_create_client_id())
    console.print(table)

@config.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset(ctx, confirm):
    """Reset configuration to defaults"""
    config_obj = ctx.obj['config']
    
    if not confirm:
        if not click.confirm("Are you sure you want to reset all configuration to defaults?"):
            console.print("Reset cancelled.")
            return
    
    config_obj.reset()
    console.print("[green]✅ Configuration reset to defaults[/green]")

@config.command()
@click.pass_context
def path(ctx):
    """Show configuration file path"""
    config_obj = ctx.obj['config']
    console.print(f"Configuration file: {config_obj.config_path}")

@config.command()
@click.argument('key')
@click.pass_context
def unset(ctx, key):
    """Remove configuration key"""
    config_obj = ctx.obj['config']
    
    config_data = config_obj.show_config()
    if key not in config_data:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")
        return
    
    # Remove by setting to None and reloading defaults
    config_obj.config.pop(key, None)
    config_obj.save()
    console.print(f"[green]✅ Removed configuration key '{key}'[/green]")

@config.command()
@click.option('--format', default='json', type=click.Choice(['json', 'yaml']), help='Export format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def export(ctx, format, output):
    """Export configuration to file"""
    config_obj = ctx.obj['config']
    config_data = config_obj.show_config()
    
    if format == 'json':
        content = json.dumps(config_data, indent=2)
    elif format == 'yaml':
        import yaml
        content = yaml.dump(config_data, default_flow_style=False)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        console.print(f"[green]✅ Configuration exported to {output}[/green]")
    else:
        console.print(content)

@config.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--merge', is_flag=True, help='Merge with existing config instead of replacing')
@click.pass_context
def import_config(ctx, file_path, merge):
    """Import configuration from file"""
    config_obj = ctx.obj['config']
    
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                import yaml
                imported_config = yaml.safe_load(f)
            else:
                imported_config = json.load(f)
        
        if merge:
            # Merge with existing config
            current_config = config_obj.show_config()
            current_config.update(imported_config)
            config_obj.config = current_config
        else:
            # Replace config
            config_obj.config = imported_config
        
        config_obj.save()
        action = "merged" if merge else "imported"
        console.print(f"[green]✅ Configuration {action} from {file_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to import configuration: {e}[/red]")
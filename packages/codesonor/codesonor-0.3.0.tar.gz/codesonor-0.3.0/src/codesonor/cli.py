"""Command-line interface for CodeSonor."""

import click
import json
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from .analyzer import RepositoryAnalyzer
from .config import Config
from .__init__ import __version__


console = Console()
config_manager = Config()


@click.group()
@click.version_option(version=__version__, prog_name="CodeSonor")
def cli():
    """
    CodeSonor - AI-Powered GitHub Repository Analyzer
    
    Analyze any public GitHub repository and get instant insights including
    language distribution, file statistics, and AI-generated code summaries.
    """
    pass


@cli.command()
@click.argument('repo_url')
@click.option('--no-ai', is_flag=True, help='Skip AI analysis (faster)')
@click.option('--max-files', default=500, help='Maximum files to analyze (default: 500)')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.option('--github-token', help='GitHub Personal Access Token (overrides stored config)')
@click.option('--llm-provider', type=click.Choice(['gemini', 'openai', 'anthropic', 'mistral', 'groq'], case_sensitive=False), help='LLM provider to use')
@click.option('--llm-api-key', help='API key for LLM provider (overrides stored config)')
@click.option('--llm-model', help='Specific model to use (overrides default)')
@click.option('--gemini-key', help='[DEPRECATED] Use --llm-api-key with --llm-provider gemini')
def analyze(repo_url, no_ai, max_files, json_output, github_token, llm_provider, llm_api_key, llm_model, gemini_key):
    """
    Analyze a GitHub repository.
    
    REPO_URL: The URL of the GitHub repository to analyze
    
    Example: codesonor analyze https://github.com/pallets/flask
    
    With specific LLM provider:
      codesonor analyze URL --llm-provider openai --llm-api-key YOUR_KEY
    """
    try:
        # Get GitHub token
        if not github_token:
            github_token = config_manager.get_github_token()
        
        # Get LLM configuration
        if not llm_provider:
            llm_provider = config_manager.get_llm_provider()
        
        if not llm_api_key:
            # Handle legacy gemini-key parameter
            if gemini_key:
                llm_api_key = gemini_key
                llm_provider = 'gemini'
                console.print("[yellow]⚠ --gemini-key is deprecated. Use --llm-api-key with --llm-provider gemini[/yellow]\n")
            else:
                llm_api_key = config_manager.get_llm_api_key()
        
        if not llm_model:
            llm_model = config_manager.get_llm_model()
        
        # Check for required keys
        if not github_token:
            console.print("[yellow]⚠ GitHub token not configured. You may hit rate limits.[/yellow]")
            console.print("[yellow]Run 'codesonor setup' to configure your API keys.[/yellow]\n")
        
        if not no_ai and not llm_api_key:
            console.print(f"[yellow]⚠ LLM API key not configured. AI analysis will be skipped.[/yellow]")
            console.print("[yellow]Run 'codesonor setup' to configure your API keys.[/yellow]\n")
        
        # Create analyzer with LLM provider support
        analyzer = RepositoryAnalyzer(
            github_token, 
            llm_api_key,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        # Analyze with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Analyzing repository...", total=None)
            result = analyzer.analyze(repo_url, include_ai=not no_ai, max_files=max_files)
        
        # Output results
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            display_results(result)
        
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)
    except PermissionError as e:
        console.print(f"[red]Authentication Error:[/red] {e}", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.argument('repo_url')
@click.option('--github-token', help='GitHub Personal Access Token (overrides stored config)')
def summary(repo_url, github_token):
    """
    Get a quick summary of a repository (no AI analysis).
    
    REPO_URL: The URL of the GitHub repository
    
    Example: codesonor summary https://github.com/pallets/flask
    """
    try:
        # Get GitHub token from config if not provided
        if not github_token:
            github_token = config_manager.get_github_token()
        
        if not github_token:
            console.print("[yellow]⚠ GitHub token not configured. You may hit rate limits.[/yellow]")
            console.print("[yellow]Run 'codesonor setup' to configure your API keys.[/yellow]\n")
        
        analyzer = RepositoryAnalyzer(github_token)
        summary_text = analyzer.get_summary(repo_url)
        console.print(summary_text)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        sys.exit(1)


def display_results(result: dict):
    """Display analysis results in a beautiful format."""
    repo = result['repository']
    stats = result['statistics']
    
    # Repository Header
    console.print(f"\n[bold cyan]{'='*70}[/bold cyan]")
    console.print(f"[bold]Repository:[/bold] [green]{repo['name']}[/green] by [blue]{repo['owner']}[/blue]")
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")
    
    # Basic Info
    console.print(f"[bold]Description:[/bold] {repo['description']}")
    console.print(f"[bold]URL:[/bold] {repo['url']}")
    console.print(f"[bold]Stars:[/bold] ⭐ {repo['stars']:,}  [bold]Forks:[/bold] 🔱 {repo['forks']:,}")
    console.print(f"[bold]Created:[/bold] {repo['created_at'][:10]}")
    console.print(f"[bold]Updated:[/bold] {repo['updated_at'][:10]}\n")
    
    # Statistics Table
    stats_table = Table(title="📊 Repository Statistics", show_header=False)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Files", f"{stats['total_files']:,}")
    stats_table.add_row("Primary Language", stats['primary_language'])
    
    console.print(stats_table)
    console.print()
    
    # Language Distribution Table
    if stats['language_distribution']:
        lang_table = Table(title="💻 Language Distribution", show_header=True)
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Percentage", style="green", justify="right")
        lang_table.add_column("Bar", style="yellow")
        
        for lang, pct in stats['language_distribution'].items():
            bar = '█' * int(pct / 2)  # Scale to max 50 chars
            lang_table.add_row(lang, f"{pct:.2f}%", bar)
        
        console.print(lang_table)
        console.print()
    
    # AI Analysis
    if result['ai_analysis']:
        console.print("[bold magenta]🤖 AI-Powered Code Analysis[/bold magenta]\n")
        
        for i, analysis in enumerate(result['ai_analysis'], 1):
            console.print(f"[bold cyan]File {i}:[/bold cyan] [yellow]{analysis['file']}[/yellow]")
            console.print(f"[dim]{analysis['summary']}[/dim]\n")
    
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")


@cli.command()
def setup():
    """
    Interactive setup wizard for API keys.
    
    Configure your GitHub token and choose your preferred LLM provider.
    """
    from .llm_providers import SUPPORTED_PROVIDERS
    
    console.print("[bold cyan]🔧 CodeSonor Setup Wizard[/bold cyan]\n")
    
    # Check current status
    status = config_manager.get_config_status()
    
    console.print("[bold]Current Configuration:[/bold]")
    
    # GitHub Token status
    if status['github_token']['set']:
        source = status['github_token']['source']
        console.print(f"  GitHub Token: ✅ Configured (from {source})")
    else:
        console.print("  GitHub Token: ❌ Not configured")
    
    # LLM status
    if status['llm_api_key']['set']:
        source = status['llm_api_key']['source']
        provider = status['llm_provider']
        model = status['llm_model']
        model_str = f" ({model})" if model else ""
        console.print(f"  LLM Provider: ✅ {provider.capitalize()}{model_str} (from {source})")
    else:
        console.print("  LLM Provider: ❌ Not configured")
    
    console.print(f"\n[dim]Config file: {status['config_file']}[/dim]\n")
    
    # Ask if user wants to configure
    if status['github_token']['set'] and status['llm_api_key']['set']:
        console.print("[green]✓ All API keys are configured![/green]\n")
        reconfigure = click.confirm("Do you want to update your configuration?", default=False)
        if not reconfigure:
            return
    
    console.print("[bold yellow]Let's configure your API keys:[/bold yellow]\n")
    
    # GitHub Token setup
    console.print("[bold]1. GitHub Personal Access Token[/bold] (Optional, but recommended)")
    console.print("   [dim]Without this, you may hit GitHub's rate limits[/dim]")
    console.print("   • Visit: [cyan]https://github.com/settings/tokens[/cyan]")
    console.print("   • Click 'Generate new token (classic)'")
    console.print("   • Select scope: [yellow]public_repo[/yellow]")
    console.print("   • Copy the token\n")
    
    github_token = click.prompt(
        "Enter your GitHub token (or press Enter to skip)",
        default="",
        hide_input=True,
        show_default=False
    )
    
    # LLM Provider selection
    console.print("\n[bold]2. Choose Your LLM Provider[/bold] (Required for AI analysis)")
    console.print("   [dim]Select which AI service you want to use:[/dim]\n")
    
    for idx, (key, info) in enumerate(SUPPORTED_PROVIDERS.items(), 1):
        console.print(f"   {idx}. [cyan]{info['name']}[/cyan] - Default model: {info['default']}")
    
    console.print()
    
    # Get provider choice
    provider_choice = click.prompt(
        "Select provider (1-5)",
        type=click.IntRange(1, len(SUPPORTED_PROVIDERS)),
        default=1
    )
    
    provider_keys = list(SUPPORTED_PROVIDERS.keys())
    selected_provider = provider_keys[provider_choice - 1]
    provider_info = SUPPORTED_PROVIDERS[selected_provider]
    
    console.print(f"\n[bold]Selected: {provider_info['name']}[/bold]")
    
    # API Key instructions per provider
    console.print(f"\n[bold]Get your {provider_info['name']} API Key:[/bold]")
    
    if selected_provider == "gemini":
        console.print("   • Visit: [cyan]https://aistudio.google.com/app/apikey[/cyan]")
        console.print("   • Click 'Create API key'")
    elif selected_provider == "openai":
        console.print("   • Visit: [cyan]https://platform.openai.com/api-keys[/cyan]")
        console.print("   • Click 'Create new secret key'")
    elif selected_provider == "anthropic":
        console.print("   • Visit: [cyan]https://console.anthropic.com/settings/keys[/cyan]")
        console.print("   • Click 'Create Key'")
    elif selected_provider == "mistral":
        console.print("   • Visit: [cyan]https://console.mistral.ai/api-keys/[/cyan]")
        console.print("   • Click 'Create new key'")
    elif selected_provider == "groq":
        console.print("   • Visit: [cyan]https://console.groq.com/keys[/cyan]")
        console.print("   • Click 'Create API Key'")
    
    console.print("   • Copy the key\n")
    
    llm_api_key = click.prompt(
        f"Enter your {provider_info['name']} API key (or press Enter to skip)",
        default="",
        hide_input=True,
        show_default=False
    )
    
    # Optional: Custom model selection
    llm_model = None
    if llm_api_key and len(provider_info['models']) > 1:
        console.print(f"\n[bold]Available models for {provider_info['name']}:[/bold]")
        for idx, model in enumerate(provider_info['models'], 1):
            default_mark = " (default)" if model == provider_info['default'] else ""
            console.print(f"   {idx}. {model}{default_mark}")
        
        use_custom = click.confirm(f"\nUse a different model? (default: {provider_info['default']})", default=False)
        if use_custom:
            model_choice = click.prompt(
                "Select model",
                type=click.IntRange(1, len(provider_info['models'])),
                default=1
            )
            llm_model = provider_info['models'][model_choice - 1]
    
    # Save configuration
    if github_token or llm_api_key:
        config_manager.save_config(
            github_token=github_token if github_token else None,
            llm_provider=selected_provider if llm_api_key else None,
            llm_api_key=llm_api_key if llm_api_key else None,
            llm_model=llm_model
        )
        
        console.print("\n[bold green]✓ Configuration saved successfully![/bold green]")
        console.print(f"[dim]Keys stored in: {status['config_file']}[/dim]\n")
        
        if github_token:
            console.print("  ✓ GitHub token configured")
        if llm_api_key:
            model_str = f" with model {llm_model}" if llm_model else ""
            console.print(f"  ✓ {provider_info['name']} configured{model_str}")
        
        console.print("\n[bold cyan]You're all set![/bold cyan]")
        console.print("Try it out: [yellow]codesonor analyze https://github.com/pallets/flask[/yellow]\n")
        
        # Show installation note for provider package
        console.print(f"[dim]Note: Make sure you have installed: pip install {provider_info['requires']}[/dim]\n")
    else:
        console.print("\n[yellow]No keys entered. Run 'codesonor setup' again when ready.[/yellow]\n")


@cli.command()
def config():
    """
    Show current configuration status.
    """
    status = config_manager.get_config_status()
    
    console.print("[bold cyan]📋 CodeSonor Configuration[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Source/Value", style="yellow")
    
    # GitHub Token
    github_status = "✅ Configured" if status['github_token']['set'] else "❌ Not set"
    github_source = status['github_token']['source'] or "-"
    table.add_row("GitHub Token", github_status, github_source)
    
    # LLM Provider
    llm_status = "✅ Configured" if status['llm_api_key']['set'] else "❌ Not set"
    llm_source = status['llm_api_key']['source'] or "-"
    table.add_row("LLM Provider", status['llm_provider'].capitalize(), llm_source)
    
    # LLM Model
    model_value = status['llm_model'] or "(default)"
    table.add_row("LLM Model", "", model_value)
    
    # LLM API Key
    table.add_row("LLM API Key", llm_status, llm_source)
    
    console.print(table)
    console.print(f"\n[dim]Config file: {status['config_file']}[/dim]")
    
    if not status['github_token']['set'] or not status['llm_api_key']['set']:
        console.print("\n[yellow]💡 Run 'codesonor setup' to configure missing keys[/yellow]\n")


@cli.command()
def reset():
    """
    Clear stored API keys from configuration.
    """
    if click.confirm("Are you sure you want to clear all stored API keys?", default=False):
        config_manager.clear_config()
        console.print("[green]✓ Configuration cleared successfully[/green]")
        console.print("\n[dim]Run 'codesonor setup' to reconfigure[/dim]\n")
    else:
        console.print("[yellow]Cancelled[/yellow]\n")


if __name__ == '__main__':
    cli()


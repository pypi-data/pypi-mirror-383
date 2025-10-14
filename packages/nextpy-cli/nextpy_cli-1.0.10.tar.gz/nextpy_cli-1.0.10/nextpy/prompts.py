"""
Interactive prompts for NextPy CLI
"""
import questionary
from rich.console import Console
from .config import build_config, validate_config, FRONTEND_FRAMEWORKS, DATABASE_TYPES

console = Console()


def collect_user_input(partial_config: dict = None) -> dict:
    """
    Collect user input through interactive prompts
    
    Args:
        partial_config: Partial configuration from CLI arguments
        
    Returns:
        Complete configuration dictionary
    """
    if partial_config is None:
        partial_config = {}
    
    answers = {}
    
    # Project name prompt (if not provided)
    if not partial_config.get('project_name'):
        project_name = questionary.text(
            "What is your project name?",
            default="my-fullstack-app",
            validate=lambda text: validate_project_name(text)
        ).ask()
        
        if project_name is None:  # User cancelled
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(0)
        
        answers['project_name'] = project_name
    
    # Frontend framework prompt (if not provided)
    if not partial_config.get('frontend'):
        frontend = questionary.select(
            "Which frontend framework would you like to use?",
            choices=[
                questionary.Choice("Next.js (React framework with SSR)", value=FRONTEND_FRAMEWORKS['NEXT']),
                questionary.Choice("Vite + React (Fast build tool with React)", value=FRONTEND_FRAMEWORKS['VITE']),
            ],
            default=FRONTEND_FRAMEWORKS['NEXT']
        ).ask()
        
        if frontend is None:  # User cancelled
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(0)
        
        answers['frontend'] = frontend
    
    # Database prompt (if not provided)
    if partial_config.get('database') is None:
        database = questionary.select(
            "Which database would you like to use?",
            choices=[
                questionary.Choice("SQLite (Lightweight file-based database)", value=DATABASE_TYPES['SQLITE']),
                questionary.Choice("PostgreSQL (Powerful relational database)", value=DATABASE_TYPES['POSTGRES']),
                questionary.Choice("MongoDB (NoSQL document database)", value=DATABASE_TYPES['MONGO']),
            ],
            default=DATABASE_TYPES['SQLITE']
        ).ask()
        
        if database is None:  # User cancelled
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(0)
        
        answers['database'] = database
    
    # Docker support prompt (if not provided)
    if partial_config.get('docker') is None:
        docker = questionary.confirm(
            "Add Docker support?",
            default=False
        ).ask()
        
        if docker is None:  # User cancelled
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(0)
        
        answers['docker'] = docker
    
    # GitHub initialization prompt (if not provided)
    if partial_config.get('github') is None:
        github = questionary.confirm(
            "Initialize GitHub repository?",
            default=False
        ).ask()
        
        if github is None:  # User cancelled
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(0)
        
        answers['github'] = github
    
    # Merge partial config with answers
    merged_config = {**partial_config, **answers}
    
    # Build complete configuration
    config = build_config(merged_config)
    
    # Display configuration summary
    display_config_summary(config)
    
    # Confirm before proceeding
    confirmed = questionary.confirm(
        "Proceed with this configuration?",
        default=True
    ).ask()
    
    if not confirmed:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise SystemExit(0)
    
    # Validate configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        console.print("\n[red]Configuration validation failed:[/red]")
        for error in errors:
            console.print(f"  [red]- {error}[/red]")
        raise SystemExit(1)
    
    return config


def display_config_summary(config):
    """
    Display configuration summary
    
    Args:
        config: Configuration object
    """
    console.print("\n[bold cyan]📋 Configuration Summary:[/bold cyan]")
    console.print("─" * 50)
    console.print(f"  [cyan]Project Name:[/cyan]    {config.project_name}")
    console.print(f"  [cyan]Frontend:[/cyan]        {get_frontend_display_name(config.frontend)}")
    console.print(f"  [cyan]Database:[/cyan]        {get_database_display_name(config.database)}")
    console.print(f"  [cyan]Docker:[/cyan]          {'Yes' if config.docker else 'No'}")
    console.print(f"  [cyan]GitHub:[/cyan]          {'Yes' if config.github else 'No'}")
    console.print("─" * 50)
    console.print()


def get_frontend_display_name(frontend: str) -> str:
    """
    Get display name for frontend framework
    
    Args:
        frontend: Frontend framework type
        
    Returns:
        Display name
    """
    names = {
        'next': 'Next.js',
        'vite': 'Vite + React',
    }
    return names.get(frontend, frontend)


def get_database_display_name(database: str) -> str:
    """
    Get display name for database type
    
    Args:
        database: Database type
        
    Returns:
        Display name
    """
    names = {
        'sqlite': 'SQLite',
        'postgres': 'PostgreSQL',
        'mongo': 'MongoDB',
    }
    return names.get(database, database)


def validate_project_name(name: str) -> bool | str:
    """
    Validate project name
    
    Args:
        name: Project name to validate
        
    Returns:
        True if valid, error message if invalid
    """
    if not name:
        return "Project name is required"
    
    if not name.replace('-', '').replace('_', '').isalnum():
        return "Project name must contain only alphanumeric characters, hyphens, and underscores"
    
    return True

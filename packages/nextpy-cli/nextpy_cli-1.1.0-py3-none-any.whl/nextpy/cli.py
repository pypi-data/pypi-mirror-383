"""
NextPy CLI - Main entry point
"""
import os
import typer
import asyncio
from typing import Optional
from .config import build_config, FRONTEND_FRAMEWORKS, DATABASE_TYPES
from .fox import Fox
from .commands import preset_app, config_app

app = typer.Typer()
app.add_typer(preset_app, name="preset")
app.add_typer(config_app, name="config")

@app.command()
def main(
    project_name: Optional[str] = typer.Argument(
        default=None,
        help="Name of the project to create"
    ),
    frontend: Optional[str] = typer.Option(
        None,
        "--frontend",
        "-f",
        help="Frontend framework (next or vite)"
    ),
    db: Optional[str] = typer.Option(
        None,
        "--db",
        "-d",
        help="Database type (sqlite, postgres, or mongo)"
    ),
    docker: Optional[bool] = typer.Option(
        None,
        "--docker",
        help="Include Docker configuration"
    ),
    github: Optional[bool] = typer.Option(
        None,
        "--github",
        help="Initialize GitHub repository"
    ),
    fox_mode: str = typer.Option(
        "normal",
        "--fox-mode",
        help="Fox personality mode (verbose, normal, quiet, silent)"
    ),
    last: bool = typer.Option(
        False,
        "--last",
        help="Use last configuration"
    ),
    reset_preferences: bool = typer.Option(
        False,
        "--reset-preferences",
        help="Reset all preferences and start fresh"
    ),
):
    """
    Create a new full-stack application with FastAPI and Next.js/Vite
    """
    # Initialize Fox
    # Support NEXTPY_FOX_SILENT for CI/CD environments
    mode = os.environ.get('NEXTPY_FOX_MODE', fox_mode)
    if os.environ.get('NEXTPY_FOX_SILENT') in ('true', '1', 'True', 'TRUE'):
        mode = 'silent'
    fox = Fox(mode=mode)
    
    # Handle --reset-preferences flag
    if reset_preferences:
        fox.preferences.reset()
        fox.say('Preferences reset successfully! Starting fresh 🎯')
        raise typer.Exit(0)
    
    # Greet the user
    fox.greet()
    # Convert Typer ArgumentInfo/OptionInfo objects to None (when not provided by user)
    if not isinstance(project_name, str):
        project_name = None
    if not isinstance(frontend, str):
        frontend = None
    if not isinstance(db, str):
        db = None
    if not isinstance(docker, bool):
        docker = None
    if not isinstance(github, bool):
        github = None
    
    # Validate frontend option (only if provided as a string)
    if frontend is not None and frontend not in list(FRONTEND_FRAMEWORKS.values()):
        typer.echo(f"Error: --frontend must be either 'next' or 'vite'", err=True)
        raise typer.Exit(1)
    
    # Validate database option (only if provided as a string)
    if db is not None and db not in list(DATABASE_TYPES.values()):
        typer.echo(f"Error: --db must be one of 'sqlite', 'postgres', or 'mongo'", err=True)
        raise typer.Exit(1)
    
    # Build partial config
    partial_config = {
        'project_name': project_name,
        'frontend': frontend,
        'database': db,
        'docker': docker,
        'github': github,
        'interactive': project_name is None,
        'use_last': last,
    }
    
    # Handle --last flag
    if last:
        if not fox.preferences.exists():
            fox.warn('No previous configuration found. Please create a project first.')
            raise typer.Exit(1)
        
        last_config = fox.preferences.get_last_config()
        
        # Merge last config with any CLI overrides
        merged_config = {
            **last_config,
            'project_name': project_name,
            'frontend': frontend or last_config.get('frontend'),
            'database': db or last_config.get('database'),
            'docker': docker if docker is not None else last_config.get('docker'),
            'github': github if github is not None else last_config.get('github'),
        }
        
        docker_str = ' + Docker' if last_config.get('docker') else ''
        github_str = ' + GitHub' if last_config.get('github') else ''
        fox.say(f"Using last configuration: {last_config.get('frontend')} + {last_config.get('database')}{docker_str}{github_str}")
        
        # Skip prompts and use last config
        from .prompts import collect_user_input
        config = collect_user_input(merged_config, fox, None)
        
        # Import here to avoid circular imports
        from .project_generator import create_project
        
        # Create the project with Fox commentary
        create_project(config, fox)
        
        # Update preferences after successful creation
        fox.update_preferences(config)
        
        # Celebrate success
        prefs = fox.preferences.get()
        celebration = fox.messages.get_celebration(prefs['stats']['totalProjects'])
        if celebration:
            print(f'\n{celebration}\n')
        
        fox.celebrate(fox.messages.get_success(projectName=config['project_name']))
        return
    
    # Analyze project context if project name is provided
    analysis = None
    if project_name:
        analysis = asyncio.run(fox.analyze_context(project_name, partial_config))
        
        # Show high-priority recommendations
        high_priority_recs = [r for r in analysis['recommendations'] if r['priority'] == 'high']
        for rec in high_priority_recs:
            fox.warn(rec['message'])
    
    # Collect user input (will prompt for missing values or use provided ones)
    from .prompts import collect_user_input
    config = collect_user_input(partial_config, fox, analysis)
    
    # Import here to avoid circular imports
    from .project_generator import create_project
    
    # Create the project with Fox commentary
    create_project(config, fox)
    
    # Update preferences after successful creation
    fox.update_preferences(config)
    
    # Show contextual tips
    if analysis:
        tips = fox.get_contextual_tips(config, analysis['projectType'])
        # Show 2-3 most relevant tips
        for tip_key in tips[:3]:
            fox.tip(fox.messages.get_tip(tip_key))
    
    # Celebrate success
    prefs = fox.preferences.get()
    celebration = fox.messages.get_celebration(prefs['stats']['totalProjects'])
    if celebration:
        print(f'\n{celebration}\n')
    
    fox.celebrate(fox.messages.get_success(projectName=config.project_name))


def run():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    run()

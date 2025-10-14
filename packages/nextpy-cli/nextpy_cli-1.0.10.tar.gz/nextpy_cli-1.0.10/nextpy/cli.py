"""
NextPy CLI - Main entry point
"""
import typer
from typing import Optional
from .config import build_config, FRONTEND_FRAMEWORKS, DATABASE_TYPES

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
):
    """
    Create a new full-stack application with FastAPI and Next.js/Vite
    """
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
    }
    
    # Collect user input (will prompt for missing values or use provided ones)
    from .prompts import collect_user_input
    config = collect_user_input(partial_config)
    
    # Import here to avoid circular imports
    from .project_generator import create_project
    
    # Create the project
    create_project(config)


def run():
    """Entry point for the CLI"""
    typer.run(main)


if __name__ == "__main__":
    run()

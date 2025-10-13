"""
NextPy CLI - Main entry point
"""
import typer
from typing import Optional
from .config import build_config, FRONTEND_FRAMEWORKS, DATABASE_TYPES

app = typer.Typer(
    name="nextpy",
    help="CLI tool to scaffold FastAPI + Next.js full-stack applications",
    add_completion=False,
)


@app.command()
def main(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Name of the project to create"
    ),
    frontend: Optional[str] = typer.Option(
        None,
        "--frontend",
        help="Frontend framework (next or vite)"
    ),
    db: Optional[str] = typer.Option(
        None,
        "--db",
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
    # Validate frontend option (only if provided)
    if frontend is not None and frontend not in FRONTEND_FRAMEWORKS.values():
        typer.echo(f"Error: --frontend must be either 'next' or 'vite'", err=True)
        raise typer.Exit(1)
    
    # Validate database option (only if provided)
    if db is not None and db not in DATABASE_TYPES.values():
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


if __name__ == "__main__":
    app()

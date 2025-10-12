"""
Logger utilities for NextPy CLI
"""
import sys
import platform
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()


def info(message: str):
    """Log an informational message"""
    console.print(f"[blue]ℹ[/blue] {message}")


def success(message: str):
    """Log a success message"""
    console.print(f"[green]✓[/green] {message}")


def error(message: str):
    """Log an error message"""
    console.print(f"[red]✗[/red] {message}")


def warn(message: str):
    """Log a warning message"""
    console.print(f"[yellow]⚠[/yellow] {message}")


class SpinnerContext:
    """Context manager for spinner operations"""
    
    def __init__(self, message: str):
        self.message = message
        self.spinner = Spinner("dots", text=message, style="cyan")
        self.live = None
    
    def __enter__(self):
        self.live = Live(self.spinner, console=console, transient=True)
        self.live.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()
        return False
    
    def succeed(self, message: str = None):
        """Mark spinner as successful"""
        if self.live:
            self.live.stop()
        success(message or self.message)
    
    def fail(self, message: str = None):
        """Mark spinner as failed"""
        if self.live:
            self.live.stop()
        error(message or self.message)
    
    def warn(self, message: str = None):
        """Mark spinner as warning"""
        if self.live:
            self.live.stop()
        warn(message or self.message)
    
    def update(self, message: str):
        """Update spinner message"""
        self.message = message
        if self.live:
            self.spinner.update(text=message)


def spinner(message: str) -> SpinnerContext:
    """
    Create a spinner for long-running operations
    
    Args:
        message: Message to display with spinner
        
    Returns:
        SpinnerContext instance
    """
    return SpinnerContext(message)


def header(message: str):
    """Log a section header"""
    console.print(f"\n[bold cyan]{message}[/bold cyan]")
    console.print("[cyan]" + "─" * len(message) + "[/cyan]")


def new_line():
    """Log a blank line"""
    console.print()


def step(current: int, total: int, message: str):
    """
    Log a step in a process
    
    Args:
        current: Current step number
        total: Total number of steps
        message: Step message
    """
    console.print(f"[cyan][{current}/{total}][/cyan] {message}")


def box(message: str, box_type: str = "info"):
    """
    Display a box with a message
    
    Args:
        message: Message to display
        box_type: Box type: 'success', 'error', 'info', 'warn'
    """
    colors = {
        'success': 'green',
        'error': 'red',
        'info': 'blue',
        'warn': 'yellow',
    }
    
    icons = {
        'success': '✓',
        'error': '✗',
        'info': 'ℹ',
        'warn': '⚠',
    }
    
    color = colors.get(box_type, colors['info'])
    icon = icons.get(box_type, icons['info'])
    
    lines = message.split('\n')
    max_length = max(len(line) for line in lines)
    border = '─' * (max_length + 4)
    
    console.print()
    console.print(f"[{color}]┌{border}┐[/{color}]")
    console.print(f"[{color}]│ {icon} {lines[0].ljust(max_length)} │[/{color}]")
    for line in lines[1:]:
        console.print(f"[{color}]│   {line.ljust(max_length)} │[/{color}]")
    console.print(f"[{color}]└{border}┘[/{color}]")
    console.print()


def display_next_steps(config):
    """
    Display next steps after successful project creation
    
    Args:
        config: Project configuration
    """
    project_name = config.project_name
    docker = config.docker
    
    console.print()
    console.print("[bold green]🎉 Project created successfully![/bold green]")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print()
    
    if docker:
        # Docker instructions
        console.print("[cyan]  # Start with Docker[/cyan]")
        console.print(f"[white]  cd {project_name}[/white]")
        console.print("[white]  docker-compose up[/white]")
        console.print()
        console.print("[dim]  Backend will be available at: http://localhost:8000[/dim]")
        console.print("[dim]  Frontend will be available at: http://localhost:3000[/dim]")
        console.print("[dim]  API docs will be available at: http://localhost:8000/docs[/dim]")
        console.print()
        console.print("[cyan]  # Or run without Docker:[/cyan]")
    
    # Backend instructions
    console.print("[cyan]  # Start backend[/cyan]")
    console.print(f"[white]  cd {project_name}/backend[/white]")
    
    is_windows = platform.system() == 'Windows'
    activate_command = 'venv\\Scripts\\activate' if is_windows else 'source venv/bin/activate'
    
    console.print(f"[white]  {activate_command}[/white]")
    console.print("[white]  uvicorn main:app --reload[/white]")
    console.print()
    
    # Frontend instructions
    console.print("[cyan]  # Start frontend (in a new terminal)[/cyan]")
    console.print(f"[white]  cd {project_name}/frontend[/white]")
    console.print("[white]  npm run dev[/white]")
    console.print()
    
    console.print("[dim]  Backend: http://localhost:8000[/dim]")
    console.print("[dim]  Frontend: http://localhost:3000[/dim]")
    console.print("[dim]  API docs: http://localhost:8000/docs[/dim]")
    console.print()


def display_error(err: Exception, project_path: str = None):
    """
    Display error with cleanup option
    
    Args:
        err: Error object
        project_path: Path to project directory
    """
    console.print()
    error("[bold]Failed to create project[/bold]")
    console.print()
    console.print(f"[red]Error:[/red] {str(err)}")
    
    if hasattr(err, '__traceback__') and '--debug' in sys.argv:
        console.print()
        console.print_exception()
    
    if project_path:
        console.print()
        warn(f"Partial project files may exist at: {project_path}")
        console.print("[dim]You may want to remove this directory before trying again.[/dim]")
    
    console.print()

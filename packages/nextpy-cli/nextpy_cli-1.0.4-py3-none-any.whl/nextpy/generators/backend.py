"""
Backend generator for NextPy CLI
"""
import os
import subprocess
import platform
from pathlib import Path
from ..utils.filesystem import (
    create_directory,
    write_file,
    copy_template,
    render_template,
    get_template_path,
    read_file,
)
from ..utils.logger import spinner


def generate_backend(project_path: str, config):
    """
    Generate FastAPI backend structure
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    backend_path = Path(project_path) / 'backend'
    
    with spinner('Creating FastAPI backend...') as sp:
        try:
            # Create backend directory
            create_directory(str(backend_path))
            
            # Copy main.py based on database type
            copy_main_py(str(backend_path), config)
            
            # Copy requirements.txt based on database type
            copy_requirements_txt(str(backend_path), config)
            
            # Copy .env file based on database type
            copy_env_file(str(backend_path), config)
            
            # Copy .gitignore
            copy_gitignore(str(backend_path))
            
            sp.succeed('FastAPI backend created')
            
            # Create virtual environment
            with spinner('Creating Python virtual environment...') as sp2:
                create_virtual_env(str(backend_path))
                sp2.succeed('Virtual environment created')
            
            # Install dependencies
            with spinner('Installing Python dependencies (this may take a minute)...') as sp3:
                install_dependencies(str(backend_path))
                sp3.succeed('Python dependencies installed')
                
        except Exception as e:
            sp.fail('Failed to create backend')
            raise


def copy_main_py(backend_path: str, config):
    """
    Copy main.py template with database-specific code
    
    Args:
        backend_path: Backend directory path
        config: Project configuration
    """
    database = config.database
    project_name = config.project_name
    template_name = f'fastapi/main-{database}.py'
    template_path = get_template_path(template_name)
    
    if not template_path.exists():
        raise Exception(f'Template not found: {template_name}')
    
    template = read_file(str(template_path))
    content = render_template(template, {
        'projectName': project_name,
        'databaseType': get_database_display_name(database),
    })
    
    dest_path = Path(backend_path) / 'main.py'
    write_file(str(dest_path), content)


def copy_requirements_txt(backend_path: str, config):
    """
    Copy requirements.txt based on database choice
    
    Args:
        backend_path: Backend directory path
        config: Project configuration
    """
    database = config.database
    template_name = f'fastapi/requirements-{database}.txt'
    dest_path = Path(backend_path) / 'requirements.txt'
    
    copy_template(template_name, str(dest_path))


def copy_env_file(backend_path: str, config):
    """
    Copy .env file based on database choice
    
    Args:
        backend_path: Backend directory path
        config: Project configuration
    """
    database = config.database
    project_name = config.project_name
    template_name = f'fastapi/.env-{database}'
    template_path = get_template_path(template_name)
    
    if not template_path.exists():
        raise Exception(f'Template not found: {template_name}')
    
    template = read_file(str(template_path))
    content = render_template(template, {
        'projectName': project_name,
    })
    
    dest_path = Path(backend_path) / '.env'
    write_file(str(dest_path), content)


def copy_gitignore(backend_path: str):
    """
    Copy .gitignore template
    
    Args:
        backend_path: Backend directory path
    """
    template_name = 'fastapi/.gitignore'
    dest_path = Path(backend_path) / '.gitignore'
    
    copy_template(template_name, str(dest_path))


def create_virtual_env(backend_path: str):
    """
    Create Python virtual environment
    
    Args:
        backend_path: Backend directory path
    """
    try:
        # Create virtual environment using python -m venv
        subprocess.run(
            ['python', '-m', 'venv', 'venv'],
            cwd=backend_path,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError:
        # Try python3 if python fails
        try:
            subprocess.run(
                ['python3', '-m', 'venv', 'venv'],
                cwd=backend_path,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f'Failed to create virtual environment: {e.stderr}')


def install_dependencies(backend_path: str):
    """
    Install Python dependencies in virtual environment
    
    Args:
        backend_path: Backend directory path
    """
    is_windows = platform.system() == 'Windows'
    venv_path = Path(backend_path) / 'venv'
    
    # Determine pip path based on platform
    if is_windows:
        pip_path = venv_path / 'Scripts' / 'pip.exe'
    else:
        pip_path = venv_path / 'bin' / 'pip'
    
    # Check if pip exists
    if not pip_path.exists():
        raise Exception('Virtual environment pip not found')
    
    try:
        # Install dependencies from requirements.txt
        requirements_path = Path(backend_path) / 'requirements.txt'
        subprocess.run(
            [str(pip_path), 'install', '-r', str(requirements_path)],
            cwd=backend_path,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f'Failed to install dependencies: {e.stderr}')


def get_database_display_name(db_type: str) -> str:
    """
    Get display name for database type
    
    Args:
        db_type: Database type
        
    Returns:
        Display name
    """
    names = {
        'sqlite': 'SQLite',
        'postgres': 'PostgreSQL',
        'mongo': 'MongoDB',
    }
    return names.get(db_type, db_type)

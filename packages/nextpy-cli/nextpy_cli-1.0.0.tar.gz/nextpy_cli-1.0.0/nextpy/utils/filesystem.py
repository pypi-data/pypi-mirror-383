"""
File system utilities for NextPy CLI
"""
import os
import shutil
from pathlib import Path
from typing import Dict


def create_directory(dir_path: str):
    """
    Create a directory recursively
    
    Args:
        dir_path: Path to directory to create
        
    Raises:
        Exception: If directory creation fails
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise Exception(f'Failed to create directory "{dir_path}": {str(e)}')


def write_file(file_path: str, content: str):
    """
    Write content to a file
    
    Args:
        file_path: Path to file
        content: Content to write
        
    Raises:
        Exception: If file write fails
    """
    try:
        # Ensure parent directory exists
        parent_dir = Path(file_path).parent
        create_directory(str(parent_dir))
        
        Path(file_path).write_text(content, encoding='utf-8')
    except Exception as e:
        raise Exception(f'Failed to write file "{file_path}": {str(e)}')


def copy_template(template_name: str, destination: str):
    """
    Copy a template file to destination
    
    Args:
        template_name: Name of template file (relative to templates directory)
        destination: Destination path
        
    Raises:
        Exception: If copy fails
    """
    try:
        # Get the templates directory (go up from utils to nextpy to python-cli to root)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        template_path = project_root / 'templates' / template_name
        
        if not template_path.exists():
            raise Exception(f'Template "{template_name}" not found at {template_path}')
        
        # Ensure destination directory exists
        dest_path = Path(destination)
        create_directory(str(dest_path.parent))
        
        # Read template and write to destination
        content = template_path.read_text(encoding='utf-8')
        dest_path.write_text(content, encoding='utf-8')
    except Exception as e:
        raise Exception(f'Failed to copy template "{template_name}": {str(e)}')


def copy_directory(source: str, destination: str):
    """
    Copy a directory recursively
    
    Args:
        source: Source directory path
        destination: Destination directory path
        
    Raises:
        Exception: If copy fails
    """
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
    except Exception as e:
        raise Exception(f'Failed to copy directory "{source}": {str(e)}')


def read_file(file_path: str) -> str:
    """
    Read a file and return its content
    
    Args:
        file_path: Path to file
        
    Returns:
        File content
        
    Raises:
        Exception: If file read fails
    """
    try:
        return Path(file_path).read_text(encoding='utf-8')
    except Exception as e:
        raise Exception(f'Failed to read file "{file_path}": {str(e)}')


def path_exists(target_path: str) -> bool:
    """
    Check if a path exists
    
    Args:
        target_path: Path to check
        
    Returns:
        True if path exists
    """
    return Path(target_path).exists()


def remove_directory(dir_path: str):
    """
    Remove a directory recursively
    
    Args:
        dir_path: Path to directory to remove
        
    Raises:
        Exception: If removal fails
    """
    try:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
    except Exception as e:
        raise Exception(f'Failed to remove directory "{dir_path}": {str(e)}')


def cleanup_on_error(project_path: str) -> bool:
    """
    Clean up project directory on error
    
    Args:
        project_path: Path to project directory
        
    Returns:
        True if cleanup was successful
    """
    try:
        if Path(project_path).exists():
            print(f"\nCleaning up partial project at: {project_path}")
            remove_directory(project_path)
            print("Cleanup completed.")
            return True
        return False
    except Exception as e:
        print(f"Warning: Failed to cleanup directory: {str(e)}")
        print(f"You may need to manually remove: {project_path}")
        return False


def get_templates_path() -> Path:
    """
    Get the templates directory path
    
    Returns:
        Path to templates directory
    """
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    return project_root / 'templates'


def get_template_path(template_name: str) -> Path:
    """
    Get template file path
    
    Args:
        template_name: Name of template file
        
    Returns:
        Full path to template file
    """
    return get_templates_path() / template_name


def render_template(template: str, variables: Dict[str, str]) -> str:
    """
    Render a template with variables
    
    Args:
        template: Template string
        variables: Variables to replace in template
        
    Returns:
        Rendered template
    """
    result = template
    
    for key, value in variables.items():
        placeholder = '{{ ' + key + ' }}'
        result = result.replace(placeholder, str(value))
        # Also handle without spaces
        placeholder_no_space = '{{' + key + '}}'
        result = result.replace(placeholder_no_space, str(value))
    
    return result


def write_from_template(template_name: str, destination: str, variables: Dict[str, str] = None):
    """
    Write a file from template with variable substitution
    
    Args:
        template_name: Name of template file
        destination: Destination path
        variables: Variables to replace in template
        
    Raises:
        Exception: If operation fails
    """
    if variables is None:
        variables = {}
    
    try:
        template_path = get_template_path(template_name)
        
        if not template_path.exists():
            raise Exception(f'Template "{template_name}" not found')
        
        template = template_path.read_text(encoding='utf-8')
        content = render_template(template, variables)
        
        write_file(destination, content)
    except Exception as e:
        raise Exception(f'Failed to write from template "{template_name}": {str(e)}')


def list_files(dir_path: str) -> list:
    """
    Get list of files in a directory
    
    Args:
        dir_path: Directory path
        
    Returns:
        Array of file names
    """
    try:
        path = Path(dir_path)
        if not path.exists():
            return []
        return [f.name for f in path.iterdir()]
    except Exception as e:
        raise Exception(f'Failed to list files in "{dir_path}": {str(e)}')

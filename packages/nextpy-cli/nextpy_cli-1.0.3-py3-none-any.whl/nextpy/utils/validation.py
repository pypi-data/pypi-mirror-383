"""
Validation utilities for NextPy CLI
"""
import subprocess
import os
import shutil
from pathlib import Path
from typing import Tuple, List, Dict


def validate_project_name(name: str) -> Tuple[bool, str | None]:
    """
    Validate project name
    
    Args:
        name: Project name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return (False, 'Project name is required')
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not name.replace('-', '').replace('_', '').isalnum():
        return (False, 'Project name must contain only alphanumeric characters, hyphens, and underscores')
    
    # Check for reserved names
    reserved_names = [
        'node_modules',
        'package',
        'npm',
        'python',
        'pip',
        'test',
        'src',
        'dist',
        'build',
    ]
    
    if name.lower() in reserved_names:
        return (False, f'"{name}" is a reserved name and cannot be used')
    
    return (True, None)


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system
    
    Args:
        command: Command name to check
        
    Returns:
        True if command exists, False otherwise
    """
    return shutil.which(command) is not None


def check_path_exists(target_path: str) -> bool:
    """
    Check if a path exists
    
    Args:
        target_path: Path to check
        
    Returns:
        True if path exists, False otherwise
    """
    return Path(target_path).exists()


def validate_disk_space(target_path: str = None, required_space_mb: int = 500) -> Tuple[bool, str | None]:
    """
    Validate that sufficient disk space is available
    
    Args:
        target_path: Path where project will be created (default: current directory)
        required_space_mb: Required space in megabytes (default: 500MB)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if target_path is None:
        target_path = os.getcwd()
    
    try:
        stat = shutil.disk_usage(target_path)
        available_mb = stat.free / (1024 * 1024)
        
        if available_mb < required_space_mb:
            return (
                False,
                f'Insufficient disk space. Required: {required_space_mb}MB, Available: {int(available_mb)}MB'
            )
        
        return (True, None)
    except Exception:
        # If we can't determine disk space, assume it's okay
        return (True, None)


def validate_system_requirements() -> Tuple[bool, List[Dict[str, str]], str | None]:
    """
    Validate system requirements
    
    Returns:
        Tuple of (is_valid, missing_commands, error_message)
    """
    required_commands = {
        'python': 'Python 3.11+',
        'node': 'Node.js 18+',
        'npm': 'npm',
        'git': 'Git',
    }
    
    missing_commands = []
    
    for command, display_name in required_commands.items():
        if not check_command_exists(command):
            missing_commands.append({'command': command, 'display_name': display_name})
    
    if missing_commands:
        command_list = '\n'.join([f"  - {cmd['display_name']} ({cmd['command']})" for cmd in missing_commands])
        error_message = f"Missing required commands:\n{command_list}\n\nPlease install the missing dependencies and try again."
        return (False, missing_commands, error_message)
    
    return (True, [], None)


def validate_project_path(project_path: str) -> Tuple[bool, str | None]:
    """
    Validate that project directory doesn't already exist
    
    Args:
        project_path: Full path to project directory
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if check_path_exists(project_path):
        project_name = Path(project_path).name
        return (
            False,
            f'Directory "{project_name}" already exists. Please choose a different project name or remove the existing directory.'
        )
    
    return (True, None)


def validate_all(config, target_path: str) -> Tuple[bool, List[str]]:
    """
    Validate all requirements before project creation
    
    Args:
        config: Project configuration
        target_path: Target directory path
        
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Validate project name
    is_valid, error = validate_project_name(config.project_name)
    if not is_valid:
        errors.append(error)
    
    # Validate system requirements
    is_valid, missing_commands, error = validate_system_requirements()
    if not is_valid:
        errors.append(error)
    
    # Validate project path
    is_valid, error = validate_project_path(target_path)
    if not is_valid:
        errors.append(error)
    
    # Validate disk space
    is_valid, error = validate_disk_space(os.getcwd())
    if not is_valid:
        errors.append(error)
    
    return (len(errors) == 0, errors)

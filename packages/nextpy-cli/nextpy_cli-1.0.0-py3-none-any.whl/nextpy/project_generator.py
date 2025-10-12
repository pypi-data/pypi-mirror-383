"""
Main project generator
"""
import os
from pathlib import Path
from .utils.validation import validate_all
from .utils.filesystem import create_directory, cleanup_on_error
from .utils.logger import header, display_next_steps, display_error
from .generators.backend import generate_backend
from .generators.frontend import generate_frontend
from .generators.docker import generate_docker_files
from .generators.git import initialize_git, create_github_repo
from .generators.readme import generate_readme


def create_project(config):
    """
    Main project generator function
    
    Args:
        config: Project configuration
    """
    project_path = Path(os.getcwd()) / config.project_name
    
    try:
        # Display header
        header(f"Creating {config.project_name}")
        
        # Validate all requirements before starting
        is_valid, errors = validate_all(config, str(project_path))
        if not is_valid:
            print('\n❌ Validation failed:\n')
            for error in errors:
                print(error)
            raise SystemExit(1)
        
        # Create project root directory
        create_directory(str(project_path))
        
        # Generate backend
        generate_backend(str(project_path), config)
        
        # Generate frontend
        generate_frontend(str(project_path), config)
        
        # Generate Docker files if enabled
        if config.docker:
            generate_docker_files(str(project_path), config)
        
        # Initialize Git
        initialize_git(str(project_path))
        
        # Create GitHub repository if enabled
        if config.github:
            create_github_repo(config.project_name, str(project_path))
        
        # Generate README
        generate_readme(str(project_path), config)
        
        # Display success message and next steps
        display_next_steps(config)
        
    except Exception as error:
        # Display error
        display_error(error, str(project_path))
        
        # Ask user if they want to clean up
        try:
            answer = input('\nWould you like to remove the partial project files? (y/N): ')
            if answer.lower() in ['y', 'yes']:
                cleanup_on_error(str(project_path))
        except KeyboardInterrupt:
            print()
        
        raise SystemExit(1)

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


def create_project(config, fox=None):
    """
    Main project generator function
    
    Args:
        config: Project configuration
        fox: Fox instance for commentary
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
        
        # Generate backend with Fox commentary
        if fox:
            fox.say(fox.messages.get_progress('backend'))
        generate_backend(str(project_path), config)
        
        # Generate frontend with Fox commentary
        if fox:
            frontend_name = 'Next.js' if config.frontend == 'next' else 'Vite'
            fox.say(fox.messages.get_progress('frontend', frontend=frontend_name))
        generate_frontend(str(project_path), config)
        
        # Generate Docker files if enabled
        if config.docker:
            if fox:
                fox.say(fox.messages.get_progress('docker'))
                fox.tip(fox.messages.get_tip('docker_benefits'))
            generate_docker_files(str(project_path), config)
        
        # Initialize Git
        initialize_git(str(project_path))
        
        # Create GitHub repository if enabled
        if config.github:
            if fox:
                fox.say('Initializing GitHub repository...')
            create_github_repo(config.project_name, str(project_path))
        
        # Generate README
        generate_readme(str(project_path), config)
        
        # Show tips based on configuration
        if fox:
            # Tip about environment variables
            fox.tip(fox.messages.get_tip('env_variables'))
            
            # Database-specific tips
            if config.database == 'sqlite':
                fox.tip(fox.messages.get_tip('sqlite_dev'))
            elif config.database == 'postgres':
                fox.tip(fox.messages.get_tip('postgres_production'))
            
            # Docker tip if enabled
            if config.docker:
                fox.tip(fox.messages.get_tip('next_steps'))
        
        # Display success message and next steps
        display_next_steps(config)
        
    except Exception as error:
        # Use Fox for error messages if available
        if fox:
            fox.error(error)
        
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

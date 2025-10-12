"""
Docker generator for NextPy CLI
"""
from pathlib import Path
from ..utils.filesystem import (
    copy_template,
    write_file,
    render_template,
    get_template_path,
    read_file,
    path_exists,
)
from ..utils.logger import spinner


def generate_docker_files(project_path: str, config):
    """
    Generate Docker configuration files
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    with spinner('Creating Docker configuration...') as sp:
        try:
            # Copy backend Dockerfile
            copy_backend_dockerfile(project_path)
            
            # Copy frontend Dockerfile based on framework
            copy_frontend_dockerfile(project_path, config)
            
            # Generate docker-compose.yml based on database
            generate_docker_compose(project_path, config)
            
            sp.succeed('Docker configuration created')
            
        except Exception as e:
            sp.fail('Failed to create Docker configuration')
            raise


def copy_backend_dockerfile(project_path: str):
    """
    Copy backend Dockerfile
    
    Args:
        project_path: Root project path
    """
    template_name = 'docker/Dockerfile.backend'
    dest_path = Path(project_path) / 'backend' / 'Dockerfile'
    
    copy_template(template_name, str(dest_path))


def copy_frontend_dockerfile(project_path: str, config):
    """
    Copy frontend Dockerfile based on framework
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    frontend = config.frontend
    template_name = 'docker/Dockerfile.next' if frontend == 'next' else 'docker/Dockerfile.vite'
    dest_path = Path(project_path) / 'frontend' / 'Dockerfile'
    
    copy_template(template_name, str(dest_path))


def generate_docker_compose(project_path: str, config):
    """
    Generate docker-compose.yml based on database configuration
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    database = config.database
    project_name = config.project_name
    frontend = config.frontend
    
    # Select template based on database type
    template_name = f'docker/docker-compose-{database}.yml'
    template_path = get_template_path(template_name)
    
    if not template_path.exists():
        raise Exception(f'Docker compose template not found: {template_name}')
    
    # Read and render template
    template = read_file(str(template_path))
    
    # Determine frontend environment variable key
    frontend_env_key = 'NEXT_PUBLIC_API_URL' if frontend == 'next' else 'VITE_API_URL'
    
    content = render_template(template, {
        'projectName': project_name,
        'frontendEnvKey': frontend_env_key,
    })
    
    # Write docker-compose.yml to project root
    dest_path = Path(project_path) / 'docker-compose.yml'
    write_file(str(dest_path), content)

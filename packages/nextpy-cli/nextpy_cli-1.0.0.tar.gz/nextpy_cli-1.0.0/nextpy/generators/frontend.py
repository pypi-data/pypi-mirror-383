"""
Frontend generator for NextPy CLI
"""
import subprocess
from pathlib import Path
from ..utils.filesystem import (
    write_file,
    render_template,
    get_template_path,
    read_file,
    copy_template,
    path_exists,
)
from ..utils.logger import spinner


def generate_frontend(project_path: str, config):
    """
    Generate frontend structure
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    frontend = config.frontend
    
    if frontend == 'next':
        generate_next_js(project_path, config)
    elif frontend == 'vite':
        generate_vite(project_path, config)
    else:
        raise Exception(f'Unknown frontend framework: {frontend}')


def generate_next_js(project_path: str, config):
    """
    Generate Next.js frontend
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    frontend_path = Path(project_path) / 'frontend'
    
    with spinner('Creating Next.js frontend...') as sp:
        try:
            # Create Next.js app using create-next-app
            subprocess.run(
                [
                    'npx',
                    'create-next-app@latest',
                    'frontend',
                    '--typescript',
                    '--tailwind',
                    '--app',
                    '--no-src-dir',
                    '--import-alias',
                    '@/*',
                    '--no-git',
                    '--yes',
                    '--use-npm'
                ],
                cwd=project_path,
                check=True,
                capture_output=False,
                text=True
            )
            
            sp.update('Configuring Next.js environment...')
            
            # Copy .env.local file
            copy_env_file(str(frontend_path), config, 'next')
            
            # Ensure .gitignore has proper patterns
            ensure_gitignore(str(frontend_path))
            
            sp.succeed('Next.js frontend created')
            
        except subprocess.CalledProcessError as e:
            sp.fail('Failed to create Next.js frontend')
            raise Exception(f'Next.js generation failed: {e.stderr}')


def generate_vite(project_path: str, config):
    """
    Generate Vite + React frontend
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    frontend_path = Path(project_path) / 'frontend'
    
    with spinner('Creating Vite + React frontend...') as sp:
        try:
            # Create Vite app using create-vite
            subprocess.run(
                ['npm', 'create', 'vite@latest', 'frontend', '--', '--template', 'react-ts'],
                cwd=project_path,
                check=True,
                capture_output=False,
                text=True
            )
            
            sp.update('Installing Vite dependencies...')
            
            # Install dependencies
            subprocess.run(
                ['npm', 'install'],
                cwd=str(frontend_path),
                check=True,
                capture_output=False,
                text=True
            )
            
            sp.update('Configuring Vite environment...')
            
            # Copy .env file
            copy_env_file(str(frontend_path), config, 'vite')
            
            # Ensure .gitignore has proper patterns
            ensure_gitignore(str(frontend_path))
            
            sp.succeed('Vite + React frontend created')
            
        except subprocess.CalledProcessError as e:
            sp.fail('Failed to create Vite frontend')
            raise Exception(f'Vite generation failed: {e.stderr}')


def copy_env_file(frontend_path: str, config, framework: str):
    """
    Copy .env file for frontend
    
    Args:
        frontend_path: Frontend directory path
        config: Project configuration
        framework: Frontend framework (next or vite)
    """
    project_name = config.project_name
    template_name = 'next/.env.local' if framework == 'next' else 'vite/.env'
    template_path = get_template_path(template_name)
    
    if not template_path.exists():
        raise Exception(f'Template not found: {template_name}')
    
    template = read_file(str(template_path))
    content = render_template(template, {
        'projectName': project_name,
    })
    
    dest_file_name = '.env.local' if framework == 'next' else '.env'
    dest_path = Path(frontend_path) / dest_file_name
    write_file(str(dest_path), content)


def ensure_gitignore(frontend_path: str):
    """
    Ensure .gitignore exists with proper patterns
    
    Args:
        frontend_path: Frontend directory path
    """
    gitignore_path = Path(frontend_path) / '.gitignore'
    
    # If .gitignore doesn't exist, copy our template
    if not path_exists(str(gitignore_path)):
        copy_template('next/.gitignore', str(gitignore_path))
    else:
        # If it exists, ensure it has .env patterns
        content = read_file(str(gitignore_path))
        
        # Add .env patterns if not present
        if '.env' not in content:
            content += '\n# Environment variables\n.env\n.env*.local\n.env.local\n'
            write_file(str(gitignore_path), content)

"""
Git initializer for NextPy CLI
"""
import subprocess
from pathlib import Path
from ..utils.filesystem import copy_template
from ..utils.logger import spinner, warn, console
from ..utils.validation import check_command_exists


def initialize_git(project_path: str):
    """
    Initialize Git repository
    
    Args:
        project_path: Root project path
    """
    with spinner('Initializing Git repository...') as sp:
        try:
            # Initialize git repository
            subprocess.run(
                ['git', 'init'],
                cwd=project_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Create .gitignore
            create_gitignore(project_path)
            
            # Create initial commit
            create_initial_commit(project_path)
            
            sp.succeed('Git repository initialized')
            
        except subprocess.CalledProcessError as e:
            sp.fail('Failed to initialize Git repository')
            raise Exception(f'Git initialization failed: {e.stderr}')


def create_gitignore(project_path: str):
    """
    Create .gitignore file in project root
    
    Args:
        project_path: Root project path
    """
    template_name = 'git/.gitignore'
    dest_path = Path(project_path) / '.gitignore'
    
    copy_template(template_name, str(dest_path))


def create_initial_commit(project_path: str):
    """
    Create initial commit
    
    Args:
        project_path: Root project path
    """
    try:
        # Add all files
        subprocess.run(
            ['git', 'add', '.'],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Create initial commit
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit from NextPy'],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError:
        # If commit fails, it's not critical - might be due to git config
        # Just log and continue
        warn('Could not create initial commit. You may need to configure git user.name and user.email')


def create_github_repo(project_name: str, project_path: str):
    """
    Create GitHub repository
    
    Args:
        project_name: Project name
        project_path: Root project path
    """
    with spinner('Creating GitHub repository...') as sp:
        try:
            # Check if gh CLI is installed
            if not check_command_exists('gh'):
                sp.warn('GitHub CLI (gh) not found')
                console.print('\n[yellow]To create a GitHub repository manually:[/yellow]')
                console.print('1. Go to https://github.com/new')
                console.print(f'2. Create a repository named "{project_name}"')
                console.print('3. Run the following commands in your project directory:')
                console.print(f'   git remote add origin https://github.com/YOUR_USERNAME/{project_name}.git')
                console.print('   git branch -M main')
                console.print('   git push -u origin main')
                return
            
            # Check if user is authenticated
            try:
                subprocess.run(
                    ['gh', 'auth', 'status'],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError:
                sp.warn('Not authenticated with GitHub CLI')
                console.print('\n[yellow]To authenticate with GitHub CLI, run:[/yellow]')
                console.print('  gh auth login')
                console.print('\n[yellow]Then create your repository with:[/yellow]')
                console.print(f'  gh repo create {project_name} --private --source=. --remote=origin --push')
                return
            
            # Create GitHub repository
            subprocess.run(
                ['gh', 'repo', 'create', project_name, '--private', '--source=.', '--remote=origin', '--push'],
                cwd=project_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            sp.succeed('GitHub repository created')
            
        except subprocess.CalledProcessError as e:
            sp.fail('Failed to create GitHub repository')
            console.print('\n[yellow]You can create the repository manually later with:[/yellow]')
            console.print(f'  gh repo create {project_name} --private --source=. --remote=origin --push')

"""
Configuration constants and defaults for NextPy CLI
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

# Default values
DEFAULTS = {
    'frontend': 'next',
    'database': 'sqlite',
    'docker': False,
    'github': False,
}

# Port configurations
PORTS = {
    'backend': 8000,
    'frontend': 3000,
    'postgres': 5432,
    'mongo': 27017,
}

# Frontend framework options
FRONTEND_FRAMEWORKS = {
    'NEXT': 'next',
    'VITE': 'vite',
}

# Database type options
DATABASE_TYPES = {
    'SQLITE': 'sqlite',
    'POSTGRES': 'postgres',
    'MONGO': 'mongo',
}

# Database configurations
DATABASE_CONFIG = {
    'sqlite': {
        'url': 'sqlite:///./app.db',
        'dependencies': [],
        'requires_service': False,
    },
    'postgres': {
        'url': 'postgresql://user:password@localhost:5432/dbname',
        'dependencies': ['psycopg2-binary', 'sqlalchemy'],
        'requires_service': True,
        'docker_image': 'postgres:15',
        'env_vars': {
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'password',
            'POSTGRES_DB': 'dbname',
        },
    },
    'mongo': {
        'url': 'mongodb://localhost:27017/dbname',
        'dependencies': ['pymongo', 'motor'],
        'requires_service': True,
        'docker_image': 'mongo:latest',
        'env_vars': {
            'MONGO_INITDB_ROOT_USERNAME': 'user',
            'MONGO_INITDB_ROOT_PASSWORD': 'password',
        },
    },
}

# FastAPI base dependencies
FASTAPI_DEPENDENCIES = [
    'fastapi',
    'uvicorn[standard]',
    'python-dotenv',
    'pydantic',
]

# Frontend environment variable keys
FRONTEND_ENV_KEYS = {
    'next': 'NEXT_PUBLIC_API_URL',
    'vite': 'VITE_API_URL',
}


@dataclass
class ProjectConfig:
    """Project configuration"""
    project_name: Optional[str]
    frontend: str
    database: str
    docker: bool
    github: bool
    interactive: bool
    database_config: Dict[str, Any]
    api_url: str
    frontend_env_key: str
    ports: Dict[str, int]


def build_config(partial_config: Dict[str, Any]) -> ProjectConfig:
    """
    Build a complete configuration object with defaults
    
    Args:
        partial_config: Partial configuration from CLI or prompts
        
    Returns:
        Complete ProjectConfig object
    """
    config_dict = {
        'project_name': partial_config.get('project_name'),
        'frontend': partial_config.get('frontend', DEFAULTS['frontend']),
        'database': partial_config.get('database', DEFAULTS['database']),
        'docker': partial_config.get('docker', DEFAULTS['docker']),
        'github': partial_config.get('github', DEFAULTS['github']),
        'interactive': partial_config.get('interactive', False),
    }
    
    # Add derived properties
    config_dict['database_config'] = DATABASE_CONFIG[config_dict['database']]
    config_dict['api_url'] = f"http://localhost:{PORTS['backend']}"
    config_dict['frontend_env_key'] = FRONTEND_ENV_KEYS[config_dict['frontend']]
    config_dict['ports'] = PORTS
    
    return ProjectConfig(**config_dict)


def validate_config(config: ProjectConfig) -> tuple[bool, list[str]]:
    """
    Validate configuration object
    
    Args:
        config: Configuration to validate
        
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Validate project name
    if not config.project_name:
        errors.append('Project name is required')
    elif not config.project_name.replace('-', '').replace('_', '').isalnum():
        errors.append('Project name must contain only alphanumeric characters, hyphens, and underscores')
    
    # Validate frontend
    if config.frontend not in FRONTEND_FRAMEWORKS.values():
        errors.append(f"Frontend must be one of: {', '.join(FRONTEND_FRAMEWORKS.values())}")
    
    # Validate database
    if config.database not in DATABASE_TYPES.values():
        errors.append(f"Database must be one of: {', '.join(DATABASE_TYPES.values())}")
    
    return (len(errors) == 0, errors)

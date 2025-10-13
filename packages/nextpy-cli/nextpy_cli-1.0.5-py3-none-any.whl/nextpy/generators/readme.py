"""
README generator for NextPy CLI
"""
import platform
from pathlib import Path
from ..utils.filesystem import write_file
from ..utils.logger import spinner


def generate_readme(project_path: str, config):
    """
    Generate README.md file
    
    Args:
        project_path: Root project path
        config: Project configuration
    """
    with spinner('Creating README.md...') as sp:
        try:
            content = create_readme_content(config)
            dest_path = Path(project_path) / 'README.md'
            write_file(str(dest_path), content)
            
            sp.succeed('README.md created')
            
        except Exception as e:
            sp.fail('Failed to create README.md')
            raise


def create_readme_content(config) -> str:
    """
    Create README content based on configuration
    
    Args:
        config: Project configuration
        
    Returns:
        README content
    """
    project_name = config.project_name
    frontend = config.frontend
    database = config.database
    docker = config.docker
    
    frontend_name = 'Next.js' if frontend == 'next' else 'Vite + React'
    database_name = get_database_display_name(database)
    is_windows = platform.system() == 'Windows'
    activate_command = 'venv\\Scripts\\activate' if is_windows else 'source venv/bin/activate'
    
    content = f"""# {project_name}

Full-stack application built with FastAPI and {frontend_name}.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: {frontend_name}
- **Database**: {database_name}
"""
    
    if docker:
        content += "- **Containerization**: Docker & Docker Compose\n"
    
    content += f"""
## Project Structure

```
{project_name}/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Backend environment variables
│   └── venv/                # Python virtual environment
├── frontend/
│   ├── {'app/' if frontend == 'next' else 'src/'}                  # Application code
│   ├── package.json         # Node.js dependencies
│   └── .env{'.local' if frontend == 'next' else ''}                # Frontend environment variables
"""
    
    if docker:
        content += "├── docker-compose.yml      # Docker Compose configuration\n"
    
    content += """└── README.md              # This file
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
"""
    
    if docker:
        content += "- Docker and Docker Compose (optional)\n"
    
    content += f"""
### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd {project_name}
```
"""
    
    if docker:
        content += f"""
### Running with Docker (Recommended)

The easiest way to run the entire stack:

```bash
docker-compose up
```

This will start:
- Backend API at http://localhost:8000
- Frontend at http://localhost:3000
"""
        
        if database != 'sqlite':
            content += f"- {database_name} database\n"
        
        content += """
To stop the services:

```bash
docker-compose down
```

### Running without Docker
"""
    
    content += f"""
#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Activate the virtual environment:
```bash
{activate_command}
```

3. Run the FastAPI server:
```bash
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000

#### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL={get_database_url(database, project_name)}
SECRET_KEY=your-secret-key-here
DEBUG=True
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env{'.local' if frontend == 'next' else ''}`)

```env
{'NEXT_PUBLIC_API_URL' if frontend == 'next' else 'VITE_API_URL'}=http://localhost:8000
```

## API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Backend Development

The FastAPI server runs with auto-reload enabled. Any changes to Python files will automatically restart the server.

### Frontend Development

The {frontend_name} development server supports hot module replacement (HMR). Changes will be reflected immediately in the browser.

## Database

This project uses **{database_name}**.

{get_database_instructions(database, project_name)}

## Project Features

- ✅ FastAPI backend with automatic API documentation
- ✅ {frontend_name} frontend with TypeScript
- ✅ {database_name} database integration
- ✅ CORS configuration for local development
- ✅ Environment-based configuration
"""
    
    if docker:
        content += "- ✅ Docker support for easy deployment\n"
    
    content += """- ✅ Hot reload for both frontend and backend

## Available Scripts

### Backend

- `uvicorn main:app --reload` - Start development server with auto-reload
- `uvicorn main:app` - Start production server

### Frontend

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server (Next.js only)
- `npm run lint` - Run linter

"""
    
    if docker:
        content += """### Docker

- `docker-compose up` - Start all services
- `docker-compose up -d` - Start all services in detached mode
- `docker-compose down` - Stop all services
- `docker-compose logs` - View logs
- `docker-compose ps` - List running services

"""
    
    content += """## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
"""
    
    return content


def get_database_display_name(db_type: str) -> str:
    """Get display name for database type"""
    names = {
        'sqlite': 'SQLite',
        'postgres': 'PostgreSQL',
        'mongo': 'MongoDB',
    }
    return names.get(db_type, db_type)


def get_database_url(db_type: str, project_name: str) -> str:
    """Get database URL example"""
    urls = {
        'sqlite': 'sqlite:///./app.db',
        'postgres': f'postgresql://user:password@localhost:5432/{project_name}',
        'mongo': f'mongodb://localhost:27017/{project_name}',
    }
    return urls.get(db_type, '')


def get_database_instructions(db_type: str, project_name: str) -> str:
    """Get database-specific instructions"""
    instructions = {
        'sqlite': "SQLite is a file-based database that requires no additional setup. The database file (`app.db`) will be created automatically when you first run the backend.",
        
        'postgres': f"""### PostgreSQL Setup

1. Install PostgreSQL on your system
2. Create a database:
```bash
createdb {project_name}
```

3. Update the `DATABASE_URL` in `backend/.env` with your credentials

Or use Docker:
```bash
docker run -d \\
  --name postgres \\
  -e POSTGRES_USER=user \\
  -e POSTGRES_PASSWORD=password \\
  -e POSTGRES_DB={project_name} \\
  -p 5432:5432 \\
  postgres:15
```""",
        
        'mongo': f"""### MongoDB Setup

1. Install MongoDB on your system
2. Start MongoDB service

Or use Docker:
```bash
docker run -d \\
  --name mongodb \\
  -e MONGO_INITDB_ROOT_USERNAME=user \\
  -e MONGO_INITDB_ROOT_PASSWORD=password \\
  -p 27017:27017 \\
  mongo:latest
```

3. Update the `DATABASE_URL` in `backend/.env` with your credentials""",
    }
    
    return instructions.get(db_type, '')

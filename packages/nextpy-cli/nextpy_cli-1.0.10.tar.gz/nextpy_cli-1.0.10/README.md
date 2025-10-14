# NextPy CLI

<div align="center">

<img src="https://raw.githubusercontent.com/VesperAkshay/nextpy/main/logo.png" alt="NextPy Logo" width="150" style="border-radius: 20px;" />

> Scaffold full-stack FastAPI + Next.js applications in seconds

[![PyPI version](https://img.shields.io/pypi/v/nextpy-cli.svg)](https://pypi.org/project/nextpy-cli/)
[![Python](https://img.shields.io/pypi/pyversions/nextpy-cli.svg)](https://pypi.org/project/nextpy-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

NextPy is a powerful CLI tool that helps you quickly scaffold modern full-stack applications with FastAPI backend and Next.js frontend, complete with Docker support and multiple database options.

## 🚀 Quick Start

### Recommended: Using uvx (Fastest)

No installation required! Run directly:

```bash
uvx nextpy-cli my-awesome-app
```

### Alternative Methods

```bash
# Using pip
pip install nextpy-cli
nextpy my-awesome-app

# Using uv (faster pip)
uv pip install nextpy-cli
nextpy my-awesome-app

# Using pipx (isolated environment)
pipx install nextpy-cli
nextpy my-awesome-app
```

## ✨ Features

- **FastAPI Backend** - Modern, fast Python web framework
- **Next.js Frontend** - React framework with TypeScript support
- **Multiple Database Options** - PostgreSQL, MongoDB, or SQLite
- **Docker Ready** - Complete Docker and Docker Compose setup
- **TypeScript** - Full TypeScript support for type safety
- **Vite** - Lightning-fast development with Vite
- **Interactive CLI** - Beautiful, user-friendly prompts powered by Rich and Questionary
- **Best Practices** - Production-ready project structure

## 📦 What You Get

### Backend (FastAPI)
- RESTful API structure
- Database integration (PostgreSQL/MongoDB/SQLite)
- Environment configuration
- CORS setup
- Health check endpoints
- Docker configuration

### Frontend (Next.js)
- TypeScript configuration
- Vite for fast development
- API client setup
- Modern React patterns
- Responsive design ready
- Docker configuration

### DevOps
- Docker Compose for local development
- Separate Dockerfiles for frontend and backend
- Environment variable management
- Production-ready configurations

## 🎯 Usage

### Create a New Project

```bash
# Quick start with uvx (recommended)
uvx nextpy-cli my-project

# Or if installed
nextpy my-project
```

The CLI will guide you through:
1. Project name
2. Frontend framework (Next.js or Vite + React)
3. Database choice (SQLite, PostgreSQL, or MongoDB)
4. Docker support (yes/no)
5. GitHub repository initialization (yes/no)
6. Automatic setup and installation

### Start Development

```bash
cd my-project

# Start with Docker Compose (recommended)
docker-compose up

# Or start services individually:

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Requirements

- **Python** 3.11 or higher
- **Node.js** 18+ (for the generated frontend)
- **Docker** (optional, but recommended)

## 🛠️ Project Structure

```
my-project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/          # Next.js pages
│   │   ├── components/     # React components
│   │   └── lib/            # Utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Docker orchestration
└── README.md               # Project documentation
```

## 🔧 Installation

### Using uvx (Recommended - No Installation)

Run directly without installing:

```bash
uvx nextpy-cli my-project
```

**Advantages:**
- ⚡ 10-100x faster than pip
- ✅ No installation needed
- ✅ Isolated environment
- ✅ Always latest version

### From PyPI

```bash
# Using pip
pip install nextpy-cli

# Using uv (faster)
uv pip install nextpy-cli

# Using pipx (isolated)
pipx install nextpy-cli
```

### From Source

```bash
git clone https://github.com/VesperAkshay/nextpy.git
cd nextpy/python-cli
pip install -e .
```

### Installing uv/uvx

If you don't have `uv` installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see the [LICENSE](https://github.com/VesperAkshay/nextpy/blob/main/LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/VesperAkshay/nextpy)
- [Report Issues](https://github.com/VesperAkshay/nextpy/issues)
- [PyPI Package](https://pypi.org/project/nextpy-cli/)
- [npm Package](https://www.npmjs.com/package/nextpy)

## 💡 Why NextPy?

- **Save Time**: Skip the boilerplate and start building features immediately
- **Best Practices**: Pre-configured with industry standards
- **Flexible**: Choose your database and customize as needed
- **Modern Stack**: Use the latest and greatest technologies
- **Docker Ready**: Deploy anywhere with confidence
- **Python-First**: Built by Python developers, for Python developers

## 🐛 Troubleshooting

### Command not found after installation

Make sure your Python scripts directory is in your PATH:

```bash
# On Linux/Mac
export PATH="$HOME/.local/bin:$PATH"

# On Windows
# Add %APPDATA%\Python\Python311\Scripts to your PATH
```

### Permission errors on Linux/Mac

```bash
pip install --user nextpy-cli
```

## 📚 Documentation

For more detailed documentation, visit our [GitHub repository](https://github.com/VesperAkshay/nextpy).

---

Made with ❤️ by [VesperAkshay](https://github.com/VesperAkshay)

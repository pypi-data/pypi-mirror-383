from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="{{ projectName }} API",
    description="Backend API for {{ projectName }}",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

# SQLAlchemy setup for PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - returns welcome message"""
    return {
        "message": "Welcome to {{ projectName }} API",
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": "PostgreSQL",
        "database_status": db_status
    }

# Example API endpoint
@app.get("/api/items")
async def get_items():
    """Get all items - example endpoint"""
    return {
        "items": [
            {"id": 1, "name": "Item 1", "description": "First item"},
            {"id": 2, "name": "Item 2", "description": "Second item"},
        ]
    }

@app.post("/api/items")
async def create_item(name: str, description: str = ""):
    """Create a new item - example endpoint"""
    return {
        "id": 3,
        "name": name,
        "description": description,
        "message": "Item created successfully"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 FastAPI application starting...")
    print("📊 Database: PostgreSQL")
    print(f"🔗 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Not configured'}")
    
    # Create tables if they don't exist
    # Base.metadata.create_all(bind=engine)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 FastAPI application shutting down...")
    engine.dispose()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient

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

# Database configuration (MongoDB)
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "{{ projectName }}")

# MongoDB client
mongodb_client: AsyncIOMotorClient = None
database = None

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
        await mongodb_client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": "MongoDB",
        "database_status": db_status
    }

# Example API endpoint
@app.get("/api/items")
async def get_items():
    """Get all items - example endpoint"""
    try:
        items_collection = database.items
        items = await items_collection.find().to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        for item in items:
            item["_id"] = str(item["_id"])
        
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}

@app.post("/api/items")
async def create_item(name: str, description: str = ""):
    """Create a new item - example endpoint"""
    try:
        items_collection = database.items
        new_item = {
            "name": name,
            "description": description
        }
        result = await items_collection.insert_one(new_item)
        
        return {
            "id": str(result.inserted_id),
            "name": name,
            "description": description,
            "message": "Item created successfully"
        }
    except Exception as e:
        return {"error": str(e)}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    global mongodb_client, database
    
    print("🚀 FastAPI application starting...")
    print("📊 Database: MongoDB")
    
    try:
        mongodb_client = AsyncIOMotorClient(DATABASE_URL)
        database = mongodb_client[DB_NAME]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 FastAPI application shutting down...")
    if mongodb_client:
        mongodb_client.close()

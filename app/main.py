"""
Integration of Posts service into the main application structure.
This file shows how to connect the Posts service with the existing ideas application.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from services.ideas.router import router as ideas_router
from services.posts.router import router as posts_router

# Create app
app = FastAPI(title="Artur's B.Log Platform API", description="API for everything")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATA_DIR = "data"
IDEAS_DATA_FILE = os.path.join(DATA_DIR, "ideas.json")
POSTS_DATA_FILE = os.path.join(DATA_DIR, "posts.json")

# Include routers
app.include_router(ideas_router, prefix="/api/ideas", tags=["ideas"])
app.include_router(posts_router, prefix="/api/posts", tags=["posts"])

# Add health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize the data files.
    """
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize Ideas storage
    from services.ideas.storage import IdeasFileStorage
    ideas_storage = IdeasFileStorage(file_path=IDEAS_DATA_FILE)
    ideas_storage.initialize_file()
    
    # Initialize Posts storage
    from services.posts.storage import PostsFileStorage
    posts_storage = PostsFileStorage(file_path=POSTS_DATA_FILE)
    posts_storage.initialize_file()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
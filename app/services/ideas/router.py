"""
Ideas router - API endpoints for managing ideas with file storage.
This module provides FastAPI routes for all idea-related operations without authentication.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
import uuid
from datetime import datetime

from services.ideas.schemas import (
    Idea, IdeaDetail, IdeaCreate, IdeaUpdate, 
    Comment, CommentCreate
)
from services.ideas.storage import IdeasFileStorage

router = APIRouter()
storage = IdeasFileStorage()

@router.get("/", response_model=List[Idea])
async def get_ideas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = Query("latest", regex="^(latest|popular)$")
):
    """
    Get a list of ideas with optional filtering and pagination.
    """
    return storage.get_ideas(
        skip=skip,
        limit=limit,
        search=search,
        tag=tag,
        sort=sort
    )

@router.get("/{idea_id}", response_model=IdeaDetail)
async def get_idea(
    idea_id: str = Path(..., description="The ID of the idea to retrieve")
):
    """
    Get a specific idea by ID.
    """
    idea = storage.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return idea

@router.post("/", response_model=Idea, status_code=201)
async def create_idea(idea: IdeaCreate):
    """
    Create a new idea.
    """
    idea_id = str(uuid.uuid4())
    now = datetime.utcnow().strftime("%B %d, %Y")
    
    # Create new idea
    new_idea = {
        "id": idea_id,
        "title": idea.title,
        "description": idea.description,
        "author": idea.author,
        "date": now,
        "likes": 0,
        "tags": idea.tags,
        "userLiked": False
    }
    
    created_idea = storage.create_idea(new_idea)
    return created_idea

@router.put("/{idea_id}", response_model=Idea)
async def update_idea(
    idea_id: str,
    idea_update: IdeaUpdate
):
    """
    Update an existing idea.
    """
    # Get the existing idea
    idea = storage.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Prepare updates
    updates = {}
    
    if idea_update.title is not None:
        updates["title"] = idea_update.title
    
    if idea_update.description is not None:
        updates["description"] = idea_update.description
    
    if idea_update.tags is not None:
        updates["tags"] = idea_update.tags
    
    # Update the idea
    updated_idea = storage.update_idea(idea_id, updates)
    if not updated_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return updated_idea

@router.delete("/{idea_id}", status_code=204)
async def delete_idea(idea_id: str):
    """
    Delete an idea.
    """
    # Check if idea exists
    idea = storage.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Delete the idea
    result = storage.delete_idea(idea_id)
    if not result:
        raise HTTPException(status_code=404, detail="Idea not found")

@router.put("/{idea_id}/like", response_model=Idea)
async def toggle_like(
    idea_id: str,
    user_id: str = "anonymous"  # Simple string to identify the user
):
    """
    Toggle like on an idea.
    """
    # Check if idea exists
    idea = storage.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Toggle like
    updated_idea = storage.toggle_like(idea_id, user_id)
    if not updated_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return updated_idea

@router.post("/{idea_id}/comments", response_model=Comment, status_code=201)
async def add_comment(
    idea_id: str,
    comment: CommentCreate
):
    """
    Add a comment to an idea.
    """
    # Check if idea exists
    idea = storage.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Create new comment
    comment_id = str(uuid.uuid4())
    now = datetime.utcnow().strftime("%B %d, %Y")
    
    new_comment = {
        "id": comment_id,
        "content": comment.content,
        "author": comment.author,
        "idea_id": idea_id,
        "date": now
    }
    
    # Add the comment
    comment = storage.add_comment(idea_id, new_comment)
    if not comment:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return comment

@router.get("/tags/all", response_model=List[str])
async def get_all_tags():
    """
    Get all unique tags from ideas.
    """
    return storage.get_all_tags()
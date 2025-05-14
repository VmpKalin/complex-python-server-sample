"""
Posts router - API endpoints for managing blog posts with file storage.
This module provides FastAPI routes for all post-related operations without authentication.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
import uuid
from datetime import datetime

from services.posts.schemas import (
    Post, PostDetail, PostCreate, PostUpdate, 
    PostComment, PostCommentCreate
)
from services.posts.storage import PostsFileStorage

router = APIRouter()
storage = PostsFileStorage()

@router.get("/", response_model=List[Post])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    tag: Optional[str] = None,
    published_only: bool = Query(True, description="Show only published posts")
):
    """
    Get a list of posts with optional filtering and pagination.
    """
    return storage.get_posts(
        skip=skip,
        limit=limit,
        search=search,
        tag=tag,
        published_only=published_only
    )

@router.get("/{post_id}", response_model=PostDetail)
async def get_post(
    post_id: str = Path(..., description="The ID of the post to retrieve")
):
    """
    Get a specific post by ID.
    """
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Only show published posts
    if not post.get("is_published"):
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post

@router.post("/", response_model=Post, status_code=201)
async def create_post(post_create: PostCreate):
    """
    Create a new post.
    """
    post_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Create excerpt if not provided
    excerpt = post_create.excerpt
    if not excerpt and post_create.content:
        # Create excerpt from content (first 150 characters)
        excerpt = post_create.content[:150]
        if len(post_create.content) > 150:
            excerpt += "..."
    
    # Set published_at date if post is published
    published_at = now if post_create.is_published else None
    
    # Create new post
    new_post = {
        "id": post_id,
        "title": post_create.title,
        "content": post_create.content,
        "excerpt": excerpt,
        "author": post_create.author,
        "created_at": now,
        "updated_at": now,
        "published_at": published_at,
        "is_published": post_create.is_published,
        "tags": post_create.tags
    }
    
    created_post = storage.create_post(new_post)
    return created_post

@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_id: str,
    post_update: PostUpdate
):
    """
    Update an existing post.
    """
    # Get the existing post
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Prepare updates
    updates = {}
    
    if post_update.title is not None:
        updates["title"] = post_update.title
    
    if post_update.content is not None:
        updates["content"] = post_update.content
        # Update excerpt if content changed and excerpt not explicitly set
        if post_update.excerpt is None:
            excerpt = post_update.content[:150]
            if len(post_update.content) > 150:
                excerpt += "..."
            updates["excerpt"] = excerpt
    
    if post_update.excerpt is not None:
        updates["excerpt"] = post_update.excerpt
    
    if post_update.tags is not None:
        updates["tags"] = post_update.tags
    
    if post_update.is_published is not None:
        # If publishing for the first time, set published_at date
        if post_update.is_published and not post.get("is_published"):
            updates["published_at"] = datetime.utcnow().isoformat()
        updates["is_published"] = post_update.is_published
    
    updates["updated_at"] = datetime.utcnow().isoformat()
    
    # Update the post
    updated_post = storage.update_post(post_id, updates)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return updated_post

@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: str):
    """
    Delete a post.
    """
    # Check if post exists
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Delete the post
    result = storage.delete_post(post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

@router.post("/{post_id}/comments", response_model=PostComment, status_code=201)
async def add_comment(
    post_id: str,
    comment_create: PostCommentCreate
):
    """
    Add a comment to a post.
    """
    # Check if post exists and is published
    post = storage.get_post(post_id)
    if not post or not post.get("is_published"):
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create new comment
    comment_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    new_comment = {
        "id": comment_id,
        "content": comment_create.content,
        "author": comment_create.author,
        "post_id": post_id,
        "created_at": now
    }
    
    # Add the comment
    comment = storage.add_comment(post_id, new_comment)
    if not comment:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return comment

@router.get("/tags/all", response_model=List[str])
async def get_all_tags():
    """
    Get all unique tags from posts.
    """
    return storage.get_all_tags()
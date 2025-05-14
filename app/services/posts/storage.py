"""
Posts service file storage implementation, simplified without user authentication.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PostsFileStorage:
    """
    File storage handler for Posts service.
    """
    
    def __init__(self, file_path: str = "data/posts.json"):
        """
        Initialize the file storage with the given file path.
        
        Args:
            file_path: Path to the JSON file for posts data storage
        """
        self.file_path = file_path
        self.data_dir = os.path.dirname(file_path)
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not os.path.exists(file_path):
            self.initialize_file()
    
    def initialize_file(self):
        """Initialize the data file with empty collections."""
        initial_data = {
            "posts": [],
            "post_comments": [],
            "tags": []
        }
        
        with open(self.file_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all data from the file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading posts data: {e}")
            # If there's an error, reinitialize the file
            self.initialize_file()
            return {
                "posts": [],
                "post_comments": [],
                "tags": []
            }
    
    def save_data(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save all data to the file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_posts(self, 
                  skip: int = 0, 
                  limit: int = 10, 
                  search: Optional[str] = None,
                  tag: Optional[str] = None,
                  published_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get posts with optional filtering and pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            search: Optional search term
            tag: Optional tag to filter by
            published_only: Whether to return only published posts
            
        Returns:
            List of posts matching the criteria
        """
        data = self.load_data()
        posts = data.get("posts", [])
        post_comments = data.get("post_comments", [])
        
        # Group comments by post
        comments_by_post = {}
        for comment in post_comments:
            post_id = comment.get("post_id")
            if post_id not in comments_by_post:
                comments_by_post[post_id] = []
            comments_by_post[post_id].append(comment)
        
        # Filter posts
        filtered_posts = []
        for post in posts:
            # Skip unpublished posts unless explicitly requested
            if published_only and not post.get("is_published", False):
                continue
                
            # Apply search filter
            if search:
                search_term = search.lower()
                if (search_term not in post.get("title", "").lower() and 
                    search_term not in post.get("content", "").lower() and
                    (post.get("excerpt") is None or search_term not in post.get("excerpt").lower())):
                    continue
            
            # Apply tag filter
            if tag and tag not in post.get("tags", []):
                continue
            
            # Add comments count
            post_with_details = {
                **post,
                "comments_count": len(comments_by_post.get(post.get("id"), []))
            }
            
            filtered_posts.append(post_with_details)
        
        # Sort posts by published date (newest first)
        filtered_posts.sort(
            key=lambda x: datetime.fromisoformat(x.get("published_at", x.get("created_at", "2000-01-01T00:00:00"))), 
            reverse=True
        )
        
        # Apply pagination
        paginated_posts = filtered_posts[skip:skip + limit]
        
        return paginated_posts
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific post by ID.
        
        Args:
            post_id: ID of the post to retrieve
            
        Returns:
            The post if found, None otherwise
        """
        data = self.load_data()
        posts = data.get("posts", [])
        post_comments = data.get("post_comments", [])
        
        # Find the post
        post = next((p for p in posts if p.get("id") == post_id), None)
        if not post:
            return None
        
        # Get comments for this post
        comments = [comment for comment in post_comments if comment.get("post_id") == post_id]
        
        # Format post with comments
        post_with_comments = {
            **post,
            "comments": comments,
            "comments_count": len(comments)
        }
        
        return post_with_comments
    
    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new post.
        
        Args:
            post_data: Post data including title, content, author, etc.
            
        Returns:
            The created post
        """
        data = self.load_data()
        posts = data.get("posts", [])
        
        # Add the post to the collection
        posts.append(post_data)
        
        # Save to file
        data["posts"] = posts
        self.save_data(data)
        
        # Return with comments count
        return {
            **post_data,
            "comments_count": 0
        }
    
    def update_post(self, post_id: str, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing post.
        
        Args:
            post_id: ID of the post to update
            post_data: New post data
            
        Returns:
            The updated post if found, None otherwise
        """
        data = self.load_data()
        posts = data.get("posts", [])
        post_comments = data.get("post_comments", [])
        
        # Find the post
        post_index = next((i for i, p in enumerate(posts) if p.get("id") == post_id), None)
        if post_index is None:
            return None
        
        # Update the post
        posts[post_index] = {**posts[post_index], **post_data}
        
        # Save to file
        data["posts"] = posts
        self.save_data(data)
        
        # Get comments count
        comments_count = sum(1 for comment in post_comments if comment.get("post_id") == post_id)
        
        # Return the updated post
        return {
            **posts[post_index],
            "comments_count": comments_count
        }
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post and its comments.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            True if the post was found and deleted, False otherwise
        """
        data = self.load_data()
        posts = data.get("posts", [])
        post_comments = data.get("post_comments", [])
        
        # Find the post
        post_index = next((i for i, p in enumerate(posts) if p.get("id") == post_id), None)
        if post_index is None:
            return False
        
        # Remove the post
        posts.pop(post_index)
        
        # Remove associated comments
        post_comments = [c for c in post_comments if c.get("post_id") != post_id]
        
        # Save to file
        data["posts"] = posts
        data["post_comments"] = post_comments
        self.save_data(data)
        
        return True
    
    def add_comment(self, post_id: str, comment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a comment to a post.
        
        Args:
            post_id: ID of the post to comment on
            comment_data: Comment data
            
        Returns:
            The created comment if post found, None otherwise
        """
        data = self.load_data()
        posts = data.get("posts", [])
        post_comments = data.get("post_comments", [])
        
        # Check if post exists
        post = next((p for p in posts if p.get("id") == post_id), None)
        if not post:
            return None
        
        # Add the comment
        post_comments.append(comment_data)
        
        # Save to file
        data["post_comments"] = post_comments
        self.save_data(data)
        
        return comment_data
    
    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags from all posts.
        
        Returns:
            List of unique tags
        """
        data = self.load_data()
        posts = data.get("posts", [])
        
        # Collect all tags
        all_tags = []
        for post in posts:
            all_tags.extend(post.get("tags", []))
        
        # Remove duplicates and sort
        unique_tags = sorted(list(set(all_tags)))
        
        return unique_tags
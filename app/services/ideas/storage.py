"""
Ideas service file storage implementation.
This module handles file storage operations for the ideas service.
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class IdeasFileStorage:
    """
    File storage handler for Ideas service.
    """
    
    def __init__(self, file_path: str = "data/ideas.json"):
        """
        Initialize the file storage with the given file path.
        
        Args:
            file_path: Path to the JSON file for ideas data storage
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
            "ideas": [],
            "comments": [],
            "likes": [],
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
            logger.error(f"Error loading ideas data: {e}")
            # If there's an error, reinitialize the file
            self.initialize_file()
            return {
                "ideas": [],
                "comments": [],
                "likes": [],
                "tags": []
            }
    
    def save_data(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save all data to the file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_ideas(self, 
                 skip: int = 0, 
                 limit: int = 100, 
                 search: Optional[str] = None,
                 tag: Optional[str] = None,
                 sort: str = "latest",
                 current_user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ideas with optional filtering and pagination.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            search: Optional search term
            tag: Optional tag to filter by
            sort: Sort order ('latest' or 'popular')
            current_user_id: Optional user ID to check likes
            
        Returns:
            List of ideas matching the criteria
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        likes = data.get("likes", [])
        comments = data.get("comments", [])
        
        # Group comments by idea
        comments_by_idea = {}
        for comment in comments:
            idea_id = comment.get("idea_id")
            if idea_id not in comments_by_idea:
                comments_by_idea[idea_id] = []
            comments_by_idea[idea_id].append(comment)
        
        # Filter ideas
        filtered_ideas = []
        for idea in ideas:
            # Apply search filter
            if search:
                search_term = search.lower()
                if (search_term not in idea.get("title", "").lower() and 
                    search_term not in idea.get("description", "").lower()):
                    continue
            
            # Apply tag filter
            if tag and tag not in idea.get("tags", []):
                continue
            
            # Check if user liked this idea
            user_liked = False
            if current_user_id:
                for like in likes:
                    if like.get("idea_id") == idea.get("id") and like.get("user_id") == current_user_id:
                        user_liked = True
                        break
            
            # Add liked status and comments count
            idea_with_details = {
                **idea,
                "userLiked": user_liked,
                "comments": len(comments_by_idea.get(idea.get("id"), []))
            }
            
            filtered_ideas.append(idea_with_details)
        
        # Apply sorting
        if sort == "latest":
            # Convert string dates to datetime objects for sorting
            try:
                filtered_ideas.sort(
                    key=lambda x: datetime.strptime(x.get("date", "January 1, 2000"), "%B %d, %Y"), 
                    reverse=True
                )
            except ValueError as e:
                logger.error(f"Error sorting by date: {e}")
                # Fallback to unsorted
        elif sort == "popular":
            filtered_ideas.sort(key=lambda x: x.get("likes", 0), reverse=True)
        
        # Apply pagination
        paginated_ideas = filtered_ideas[skip:skip + limit]
        
        return paginated_ideas
    
    def get_idea(self, idea_id: str, current_user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific idea by ID.
        
        Args:
            idea_id: ID of the idea to retrieve
            current_user_id: Optional user ID to check likes
            
        Returns:
            The idea if found, None otherwise
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        likes = data.get("likes", [])
        comments = data.get("comments", [])
        
        # Find the idea
        idea = next((i for i in ideas if i.get("id") == idea_id), None)
        if not idea:
            return None
        
        # Check if user liked this idea
        user_liked = False
        if current_user_id:
            for like in likes:
                if like.get("idea_id") == idea_id and like.get("user_id") == current_user_id:
                    user_liked = True
                    break
        
        # Get comments for this idea
        idea_comments = [comment for comment in comments if comment.get("idea_id") == idea_id]
        
        # Format idea with comments and liked status
        idea_with_details = {
            **idea,
            "userLiked": user_liked,
            "comments_list": idea_comments,
            "comments": len(idea_comments)
        }
        
        return idea_with_details
    
    def create_idea(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new idea.
        
        Args:
            idea_data: Idea data including title, description, author, etc.
            
        Returns:
            The created idea
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        
        # Ensure idea has an ID
        if "id" not in idea_data:
            idea_data["id"] = str(uuid.uuid4())
            
        # Ensure other required fields
        if "date" not in idea_data:
            idea_data["date"] = datetime.now().strftime("%B %d, %Y")
        if "likes" not in idea_data:
            idea_data["likes"] = 0
        if "tags" not in idea_data:
            idea_data["tags"] = []
        
        # Add the idea to the collection
        ideas.append(idea_data)
        
        # Save to file
        data["ideas"] = ideas
        self.save_data(data)
        
        # Return the created idea with additional fields
        return {
            **idea_data,
            "userLiked": False,
            "comments": 0
        }
    
    def update_idea(self, idea_id: str, idea_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing idea.
        
        Args:
            idea_id: ID of the idea to update
            idea_data: New idea data
            
        Returns:
            The updated idea if found, None otherwise
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        comments = data.get("comments", [])
        
        # Find the idea
        idea_index = next((i for i, idea in enumerate(ideas) if idea.get("id") == idea_id), None)
        if idea_index is None:
            return None
        
        # Update the idea, preserving fields not in idea_data
        current_idea = ideas[idea_index]
        updated_idea = {**current_idea, **idea_data}
        ideas[idea_index] = updated_idea
        
        # Save to file
        data["ideas"] = ideas
        self.save_data(data)
        
        # Get comments count
        idea_comments = sum(1 for comment in comments if comment.get("idea_id") == idea_id)
        
        # Return the updated idea with additional fields
        return {
            **updated_idea,
            "comments": idea_comments
        }
    
    def delete_idea(self, idea_id: str) -> bool:
        """
        Delete an idea and its comments and likes.
        
        Args:
            idea_id: ID of the idea to delete
            
        Returns:
            True if the idea was found and deleted, False otherwise
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        comments = data.get("comments", [])
        likes = data.get("likes", [])
        
        # Find the idea
        idea_index = next((i for i, idea in enumerate(ideas) if idea.get("id") == idea_id), None)
        if idea_index is None:
            return False
        
        # Remove the idea
        ideas.pop(idea_index)
        
        # Remove associated comments and likes
        comments = [c for c in comments if c.get("idea_id") != idea_id]
        likes = [l for l in likes if l.get("idea_id") != idea_id]
        
        # Save to file
        data["ideas"] = ideas
        data["comments"] = comments
        data["likes"] = likes
        self.save_data(data)
        
        return True
    
    def toggle_like(self, idea_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Toggle like status for an idea.
        
        Args:
            idea_id: ID of the idea to like/unlike
            user_id: ID of the user performing the action
            
        Returns:
            The updated idea if found, None otherwise
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        likes = data.get("likes", [])
        comments = data.get("comments", [])
        
        # Find the idea
        idea_index = next((i for i, idea in enumerate(ideas) if idea.get("id") == idea_id), None)
        if idea_index is None:
            return None
        
        idea = ideas[idea_index]
        
        # Check if user already liked this idea
        like_index = next((
            i for i, like in enumerate(likes)
            if like.get("idea_id") == idea_id and like.get("user_id") == user_id
        ), None)
        
        if like_index is not None:
            # Unlike
            likes.pop(like_index)
            idea["likes"] = max(0, idea.get("likes", 0) - 1)
            user_liked = False
        else:
            # Like
            new_like = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "idea_id": idea_id,
                "created_at": datetime.now().isoformat()
            }
            likes.append(new_like)
            idea["likes"] = idea.get("likes", 0) + 1
            user_liked = True
        
        # Update idea in collection
        ideas[idea_index] = idea
        
        # Save to file
        data["ideas"] = ideas
        data["likes"] = likes
        self.save_data(data)
        
        # Get comments count
        idea_comments = sum(1 for comment in comments if comment.get("idea_id") == idea_id)
        
        # Return updated idea
        return {
            **idea,
            "userLiked": user_liked,
            "comments": idea_comments
        }
    
    def add_comment(self, idea_id: str, comment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a comment to an idea.
        
        Args:
            idea_id: ID of the idea to comment on
            comment_data: Comment data
            
        Returns:
            The created comment if idea found, None otherwise
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        comments = data.get("comments", [])
        
        # Check if idea exists
        idea = next((i for i in ideas if i.get("id") == idea_id), None)
        if not idea:
            return None
        
        # Ensure comment has required fields
        comment_data["idea_id"] = idea_id
        if "id" not in comment_data:
            comment_data["id"] = str(uuid.uuid4())
        if "date" not in comment_data:
            comment_data["date"] = datetime.now().strftime("%B %d, %Y")
        
        # Add the comment
        comments.append(comment_data)
        
        # Save to file
        data["comments"] = comments
        self.save_data(data)
        
        return comment_data
    
    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags from all ideas.
        
        Returns:
            List of unique tags
        """
        data = self.load_data()
        ideas = data.get("ideas", [])
        
        # Collect all tags
        all_tags = []
        for idea in ideas:
            all_tags.extend(idea.get("tags", []))
        
        # Remove duplicates and sort
        unique_tags = sorted(list(set(all_tags)))
        
        return unique_tags
"""
Entity Schemas and Data Generators

Defines the data model for benchmarking: User, Post, Comment, Relationship.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 12, 2025
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any


@dataclass
class User:
    """Level 1: User entity"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    bio: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    follower_count: int = 0
    following_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Post:
    """Level 2: Post entity (belongs to User)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    likes_count: int = 0
    comment_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Comment:
    """Level 3: Comment entity (belongs to Post)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str = ""
    user_id: str = ""
    content: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_deleted: bool = False  # For soft delete
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Relationship:
    """Relationship entity for edge-based databases (User follows User)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_user_id: str = ""
    target_user_id: str = ""
    relationship_type: str = "follows"  # "follows" or "likes"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create from dictionary"""
        return cls(**data)


# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_user(index: int) -> User:
    """Generate a sample user"""
    return User(
        username=f"user{index}",
        email=f"user{index}@example.com",
        bio=f"Bio for user {index}",
        follower_count=index % 100,
        following_count=index % 50
    )


def generate_post(index: int, user_id: str) -> Post:
    """Generate a sample post"""
    return Post(
        user_id=user_id,
        title=f"Post {index} Title",
        content=f"Content for post {index}",
        likes_count=index % 50,
        comment_count=index % 20
    )


def generate_comment(index: int, post_id: str, user_id: str) -> Comment:
    """Generate a sample comment"""
    return Comment(
        post_id=post_id,
        user_id=user_id,
        content=f"Comment {index} text",
        is_deleted=False
    )


def generate_relationship(source_id: str, target_id: str, rel_type: str = "follows") -> Relationship:
    """Generate a sample relationship"""
    return Relationship(
        source_user_id=source_id,
        target_user_id=target_id,
        relationship_type=rel_type
    )


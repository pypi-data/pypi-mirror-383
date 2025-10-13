#!/usr/bin/env python3
"""
Base Database Class

Abstract base class for all database implementations.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

# Add xwnode src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from exonware.xwnode import XWNode, XWEdge
from exonware.xwnode.defs import NodeMode, EdgeMode, GraphOptimization

from shared_schema import User, Post, Comment, Relationship


class BaseDatabase(ABC):
    """Abstract base class for all database types"""
    
    def __init__(self, name: str, node_mode: NodeMode, edge_mode: Optional[EdgeMode] = None,
                 graph_optimization: GraphOptimization = GraphOptimization.OFF):
        """
        Initialize the database.
        
        Args:
            name: Database type name
            node_mode: NodeMode strategy to use
            edge_mode: Optional EdgeMode strategy for graph operations
            graph_optimization: Graph optimization level (OFF, INDEX_ONLY, CACHE_ONLY, FULL)
        """
        self.name = name
        self.node_mode = node_mode
        self.edge_mode = edge_mode
        self.graph_optimization = graph_optimization
        
        # Initialize storage nodes
        self.users_node = XWNode.from_native({})
        self.posts_node = XWNode.from_native({})
        self.comments_node = XWNode.from_native({})
        
        # In-memory indexes for fast lookups
        self.users: Dict[str, Dict[str, Any]] = {}
        self.posts: Dict[str, Dict[str, Any]] = {}
        self.comments: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}
        
        # Secondary indexes for search
        self.users_by_username: Dict[str, str] = {}
        self.posts_by_user: Dict[str, List[str]] = {}
        self.comments_by_post: Dict[str, List[str]] = {}
        
        # Optional Graph Manager for O(1) relationship queries
        self.graph_manager = None
        if graph_optimization != GraphOptimization.OFF and edge_mode is not None:
            from exonware.xwnode.common.graph import XWGraphManager
            
            # Determine optimization settings
            enable_indexing = graph_optimization in (GraphOptimization.INDEX_ONLY, GraphOptimization.FULL)
            enable_caching = graph_optimization in (GraphOptimization.CACHE_ONLY, GraphOptimization.FULL)
            
            self.graph_manager = XWGraphManager(
                edge_mode=edge_mode,
                enable_caching=enable_caching,
                enable_indexing=enable_indexing,
                cache_size=1000
            )
    
    # ============================================================================
    # USER OPERATIONS
    # ============================================================================
    
    def insert_user(self, user: User) -> str:
        """Insert a new user"""
        user_dict = user.to_dict()
        user_id = user_dict['id']
        
        self.users[user_id] = user_dict
        self.users_by_username[user_dict['username']] = user_id
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user fields"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].update(updates)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Hard delete user"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        self.users_by_username.pop(user['username'], None)
        self.users.pop(user_id)
        return True
    
    def search_users(self, username_contains: str) -> List[Dict[str, Any]]:
        """Search users by username"""
        return [
            user for user in self.users.values()
            if username_contains.lower() in user['username'].lower()
        ]
    
    def list_all_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        return list(self.users.values())
    
    # ============================================================================
    # POST OPERATIONS
    # ============================================================================
    
    def insert_post(self, post: Post) -> str:
        """Insert a new post"""
        post_dict = post.to_dict()
        post_id = post_dict['id']
        
        self.posts[post_id] = post_dict
        
        # Update user index
        user_id = post_dict['user_id']
        if user_id not in self.posts_by_user:
            self.posts_by_user[user_id] = []
        self.posts_by_user[user_id].append(post_id)
        
        return post_id
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get post by ID"""
        return self.posts.get(post_id)
    
    def update_post(self, post_id: str, updates: Dict[str, Any]) -> bool:
        """Update post fields"""
        if post_id not in self.posts:
            return False
        
        self.posts[post_id].update(updates)
        return True
    
    def delete_post(self, post_id: str) -> bool:
        """Hard delete post"""
        if post_id not in self.posts:
            return False
        
        post = self.posts[post_id]
        user_id = post['user_id']
        
        if user_id in self.posts_by_user:
            self.posts_by_user[user_id].remove(post_id)
        
        self.posts.pop(post_id)
        return True
    
    def list_posts_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """List all posts by a specific user"""
        post_ids = self.posts_by_user.get(user_id, [])
        return [self.posts[pid] for pid in post_ids if pid in self.posts]
    
    # ============================================================================
    # COMMENT OPERATIONS
    # ============================================================================
    
    def insert_comment(self, comment: Comment) -> str:
        """Insert a new comment"""
        comment_dict = comment.to_dict()
        comment_id = comment_dict['id']
        
        self.comments[comment_id] = comment_dict
        
        # Update post index
        post_id = comment_dict['post_id']
        if post_id not in self.comments_by_post:
            self.comments_by_post[post_id] = []
        self.comments_by_post[post_id].append(comment_id)
        
        return comment_id
    
    def get_comment(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """Get comment by ID"""
        return self.comments.get(comment_id)
    
    def update_comment(self, comment_id: str, updates: Dict[str, Any]) -> bool:
        """Update comment fields"""
        if comment_id not in self.comments:
            return False
        
        self.comments[comment_id].update(updates)
        return True
    
    def soft_delete_comment(self, comment_id: str) -> bool:
        """Soft delete comment (set is_deleted flag)"""
        if comment_id not in self.comments:
            return False
        
        self.comments[comment_id]['is_deleted'] = True
        return True
    
    def delete_comment(self, comment_id: str) -> bool:
        """Hard delete comment"""
        if comment_id not in self.comments:
            return False
        
        comment = self.comments[comment_id]
        post_id = comment['post_id']
        
        if post_id in self.comments_by_post:
            self.comments_by_post[post_id].remove(comment_id)
        
        self.comments.pop(comment_id)
        return True
    
    def list_comments_by_post(self, post_id: str) -> List[Dict[str, Any]]:
        """List all comments for a specific post"""
        comment_ids = self.comments_by_post.get(post_id, [])
        return [self.comments[cid] for cid in comment_ids if cid in self.comments]
    
    # ============================================================================
    # RELATIONSHIP OPERATIONS (for edge-based databases)
    # ============================================================================
    
    def add_relationship(self, relationship: Relationship) -> str:
        """Add a relationship (user follows user)"""
        rel_dict = relationship.to_dict()
        rel_id = rel_dict['id']
        
        # Store in dict (backward compatibility)
        self.relationships[rel_id] = rel_dict
        
        # Use graph manager if enabled (O(1) indexed)
        if self.graph_manager:
            self.graph_manager.add_relationship(
                source=rel_dict['source_user_id'],
                target=rel_dict['target_user_id'],
                relationship_type=rel_dict['relationship_type'],
                **rel_dict
            )
        
        return rel_id
    
    def get_followers(self, user_id: str) -> List[str]:
        """Get all users who follow this user"""
        # Use graph manager if enabled (O(1) indexed lookup)
        if self.graph_manager:
            relationships = self.graph_manager.get_incoming(
                entity_id=user_id,
                relationship_type='follows'
            )
            return [r['source'] for r in relationships]
        
        # Fallback: O(n) dict iteration
        return [
            r['source_user_id'] for r in self.relationships.values()
            if r['target_user_id'] == user_id and r['relationship_type'] == 'follows'
        ]
    
    def get_following(self, user_id: str) -> List[str]:
        """Get all users that this user follows"""
        # Use graph manager if enabled (O(1) indexed lookup)
        if self.graph_manager:
            relationships = self.graph_manager.get_outgoing(
                entity_id=user_id,
                relationship_type='follows'
            )
            return [r['target'] for r in relationships]
        
        # Fallback: O(n) dict iteration
        return [
            r['target_user_id'] for r in self.relationships.values()
            if r['source_user_id'] == user_id and r['relationship_type'] == 'follows'
        ]
    
    # ============================================================================
    # STATISTICS
    # ============================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'name': self.name,
            'node_mode': self.node_mode.name if hasattr(self.node_mode, 'name') else str(self.node_mode),
            'edge_mode': self.edge_mode.name if self.edge_mode and hasattr(self.edge_mode, 'name') else str(self.edge_mode),
            'graph_optimization': self.graph_optimization.name if hasattr(self.graph_optimization, 'name') else str(self.graph_optimization),
            'total_users': len(self.users),
            'total_posts': len(self.posts),
            'total_comments': len(self.comments),
            'total_relationships': len(self.relationships)
        }
        
        # Add graph manager stats if enabled
        if self.graph_manager:
            stats['graph_manager'] = self.graph_manager.get_stats()
        
        return stats


"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/kd_tree.py

k-d Tree Node Strategy Implementation

This module implements the KD_TREE strategy for multi-dimensional point
queries and nearest neighbor search.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.23
Generation Date: 12-Oct-2025
"""

import math
from typing import Any, Iterator, List, Dict, Optional, Tuple, Callable
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeError, XWNodeValueError


class KdNode:
    """
    Node in k-d tree.
    
    WHY dimension cycling:
    - Ensures balanced partitioning across all dimensions
    - Enables efficient multi-dimensional search
    - Logarithmic depth for n points
    """
    
    def __init__(self, point: Tuple[float, ...], value: Any, axis: int):
        """
        Initialize k-d tree node.
        
        Args:
            point: k-dimensional point coordinates
            value: Associated data
            axis: Splitting dimension at this level
        """
        self.point = point
        self.value = value
        self.axis = axis
        self.left: Optional['KdNode'] = None
        self.right: Optional['KdNode'] = None


class KdTreeStrategy(ANodeTreeStrategy):
    """
    k-d Tree strategy for multi-dimensional point queries.
    
    WHY k-d Tree:
    - Efficient multi-dimensional point queries: O(log n) average
    - Near-optimal nearest neighbor search in low dimensions
    - Natural partitioning for spatial data
    - Excellent for machine learning (k-NN, clustering)
    - Widely used in computer graphics and GIS
    
    WHY this implementation:
    - Median-based splitting ensures balanced trees
    - Cycles through dimensions for uniform partitioning
    - Supports arbitrary dimensions (k >= 1)
    - Distance metrics customizable (Euclidean, Manhattan, etc.)
    - Bounding box pruning for efficient range queries
    
    Time Complexity:
    - Insert: O(log n) average, O(n) worst (unbalanced)
    - Search: O(log n) average
    - Nearest neighbor: O(log n) average, O(n) worst
    - Range query: O(n^(1-1/k) + m) where m is result size
    - Build from n points: O(n log n) with median finding
    
    Space Complexity: O(n) for n points
    
    Trade-offs:
    - Advantage: Efficient for low dimensions (k ≤ 20)
    - Advantage: Simple structure, easy to understand
    - Advantage: Good cache locality for small k
    - Limitation: Performance degrades for high dimensions (curse of dimensionality)
    - Limitation: Requires rebalancing for optimal performance
    - Limitation: Nearest neighbor becomes O(n) for k > 20
    - Compared to R-tree: Simpler, better for points, worse for rectangles
    - Compared to Ball tree: Better for low k, worse for high k
    
    Best for:
    - 2D/3D point clouds (graphics, GIS, robotics)
    - Machine learning k-NN classification
    - Nearest neighbor search (k ≤ 20 dimensions)
    - Spatial indexing for games
    - Computer vision applications
    - Low-dimensional scientific data
    
    Not recommended for:
    - High-dimensional data (k > 20) - use LSH, HNSW instead
    - Dynamic frequent updates (use R-tree)
    - Rectangle/region queries (use R-tree)
    - Very large datasets in high dimensions
    - String or categorical data
    
    Following eXonware Priorities:
    1. Security: Validates dimensions, prevents malformed points
    2. Usability: Natural point API, clear dimension handling
    3. Maintainability: Clean recursive structure, dimension cycling
    4. Performance: O(log n) queries for low dimensions
    5. Extensibility: Easy to add metrics, balancing strategies
    
    Industry Best Practices:
    - Follows Bentley's original k-d tree paper (1975)
    - Implements median-based splitting for balance
    - Supports customizable distance metrics
    - Provides bounding box pruning
    - Compatible with k-NN algorithms
    """
    
    # Tree node type for classification
    STRATEGY_TYPE: NodeType = NodeType.TREE
    
    def __init__(self, mode: NodeMode = NodeMode.KD_TREE,
                 traits: NodeTrait = NodeTrait.NONE,
                 dimensions: int = 2, **options):
        """
        Initialize k-d tree strategy.
        
        Args:
            mode: Node mode
            traits: Node traits
            dimensions: Number of dimensions (k)
            **options: Additional options
            
        Raises:
            XWNodeValueError: If dimensions < 1
        """
        if dimensions < 1:
            raise XWNodeValueError(f"Dimensions must be >= 1, got {dimensions}")
        
        super().__init__(mode, traits, **options)
        
        self.dimensions = dimensions
        self._root: Optional[KdNode] = None
        self._size = 0
        self._points: Dict[Tuple[float, ...], Any] = {}  # Point -> value mapping
    
    def get_supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return NodeTrait.SPATIAL | NodeTrait.INDEXED | NodeTrait.HIERARCHICAL
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _validate_point(self, point: Any) -> Tuple[float, ...]:
        """
        Validate and normalize point to tuple.
        
        Args:
            point: Point coordinates
            
        Returns:
            Normalized point tuple
            
        Raises:
            XWNodeValueError: If point is invalid
        """
        if isinstance(point, (tuple, list)):
            if len(point) != self.dimensions:
                raise XWNodeValueError(
                    f"Point must have {self.dimensions} dimensions, got {len(point)}"
                )
            return tuple(float(x) for x in point)
        else:
            raise XWNodeValueError(
                f"Point must be tuple or list, got {type(point).__name__}"
            )
    
    def _euclidean_distance(self, p1: Tuple[float, ...], p2: Tuple[float, ...]) -> float:
        """Calculate Euclidean distance between points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))
    
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================
    
    def put(self, key: Any, value: Any = None) -> None:
        """
        Insert point into k-d tree.
        
        Args:
            key: Point coordinates (tuple or list)
            value: Associated value
            
        Raises:
            XWNodeValueError: If key is invalid point
        """
        # Security: Validate point
        point = self._validate_point(key)
        
        # Insert into tree
        if self._root is None:
            self._root = KdNode(point, value, 0)
            self._points[point] = value
            self._size += 1
        else:
            # Check if point already exists
            if point in self._points:
                # Update existing value
                self._update_value(self._root, point, value, 0)
                self._points[point] = value
            else:
                # Insert new point
                self._insert_recursive(self._root, point, value, 0)
                self._points[point] = value
                self._size += 1
    
    def _insert_recursive(self, node: KdNode, point: Tuple[float, ...], 
                         value: Any, depth: int) -> KdNode:
        """
        Recursively insert point.
        
        Args:
            node: Current node
            point: Point to insert
            value: Associated value
            depth: Current depth
            
        Returns:
            Node (for tree structure building)
        """
        axis = depth % self.dimensions
        
        if point[axis] < node.point[axis]:
            if node.left is None:
                node.left = KdNode(point, value, axis)
            else:
                self._insert_recursive(node.left, point, value, depth + 1)
        else:
            if node.right is None:
                node.right = KdNode(point, value, axis)
            else:
                self._insert_recursive(node.right, point, value, depth + 1)
        
        return node
    
    def _update_value(self, node: Optional[KdNode], point: Tuple[float, ...],
                     value: Any, depth: int) -> bool:
        """Update value for existing point."""
        if node is None:
            return False
        
        if node.point == point:
            node.value = value
            return True
        
        axis = depth % self.dimensions
        
        if point[axis] < node.point[axis]:
            return self._update_value(node.left, point, value, depth + 1)
        else:
            return self._update_value(node.right, point, value, depth + 1)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve value by point.
        
        Args:
            key: Point coordinates
            default: Default value
            
        Returns:
            Value or default
        """
        try:
            point = self._validate_point(key)
        except XWNodeValueError:
            return default
        
        return self._points.get(point, default)
    
    def has(self, key: Any) -> bool:
        """Check if point exists."""
        try:
            point = self._validate_point(key)
            return point in self._points
        except XWNodeValueError:
            return False
    
    def delete(self, key: Any) -> bool:
        """
        Delete point.
        
        Args:
            key: Point coordinates
            
        Returns:
            True if deleted, False if not found
            
        Note: Simplified deletion. Full implementation would rebalance.
        """
        try:
            point = self._validate_point(key)
        except XWNodeValueError:
            return False
        
        if point not in self._points:
            return False
        
        del self._points[point]
        self._size -= 1
        
        # For simplicity, rebuild tree (O(n log n))
        # Full implementation would do node removal with rebalancing
        points_list = list(self._points.items())
        self._root = None
        self._size = 0
        self._points.clear()
        
        for pt, val in points_list:
            if pt != point:
                self.put(pt, val)
        
        return True
    
    # ============================================================================
    # K-D TREE SPECIFIC OPERATIONS
    # ============================================================================
    
    def nearest_neighbor(self, query_point: Tuple[float, ...], 
                        distance_fn: Optional[Callable] = None) -> Optional[Tuple[Tuple[float, ...], Any]]:
        """
        Find nearest neighbor to query point.
        
        Args:
            query_point: Query coordinates
            distance_fn: Distance function (default: Euclidean)
            
        Returns:
            (point, value) tuple of nearest neighbor or None
            
        Raises:
            XWNodeValueError: If query_point is invalid
        """
        # Security: Validate query
        query = self._validate_point(query_point)
        
        if self._root is None:
            return None
        
        if distance_fn is None:
            distance_fn = self._euclidean_distance
        
        best = [None, float('inf')]  # [node, distance]
        
        def search_nn(node: Optional[KdNode], depth: int) -> None:
            """Recursive nearest neighbor search."""
            if node is None:
                return
            
            # Calculate distance to current node
            dist = distance_fn(query, node.point)
            
            if dist < best[1]:
                best[0] = node
                best[1] = dist
            
            # Determine which subtree to search first
            axis = depth % self.dimensions
            
            if query[axis] < node.point[axis]:
                near, far = node.left, node.right
            else:
                near, far = node.right, node.left
            
            # Search near subtree
            search_nn(near, depth + 1)
            
            # Search far subtree if necessary
            axis_dist = abs(query[axis] - node.point[axis])
            if axis_dist < best[1]:
                search_nn(far, depth + 1)
        
        search_nn(self._root, 0)
        
        if best[0] is None:
            return None
        
        return (best[0].point, best[0].value)
    
    def range_search(self, min_bounds: Tuple[float, ...], 
                    max_bounds: Tuple[float, ...]) -> List[Tuple[Tuple[float, ...], Any]]:
        """
        Find all points within hyperrectangle.
        
        Args:
            min_bounds: Minimum bounds for each dimension
            max_bounds: Maximum bounds for each dimension
            
        Returns:
            List of (point, value) tuples in range
            
        Raises:
            XWNodeValueError: If bounds are invalid
        """
        # Security: Validate bounds
        min_b = self._validate_point(min_bounds)
        max_b = self._validate_point(max_bounds)
        
        for i in range(self.dimensions):
            if min_b[i] > max_b[i]:
                raise XWNodeValueError(
                    f"Invalid range: min[{i}]={min_b[i]} > max[{i}]={max_b[i]}"
                )
        
        result = []
        
        def search_range(node: Optional[KdNode], depth: int) -> None:
            """Recursive range search."""
            if node is None:
                return
            
            # Check if point is in range
            in_range = all(
                min_b[i] <= node.point[i] <= max_b[i]
                for i in range(self.dimensions)
            )
            
            if in_range:
                result.append((node.point, node.value))
            
            # Determine which subtrees to search
            axis = depth % self.dimensions
            
            # Search left if range overlaps left subtree
            if min_b[axis] <= node.point[axis]:
                search_range(node.left, depth + 1)
            
            # Search right if range overlaps right subtree
            if max_b[axis] >= node.point[axis]:
                search_range(node.right, depth + 1)
        
        search_range(self._root, 0)
        return result
    
    def k_nearest_neighbors(self, query_point: Tuple[float, ...], k: int,
                           distance_fn: Optional[Callable] = None) -> List[Tuple[Tuple[float, ...], Any, float]]:
        """
        Find k nearest neighbors.
        
        Args:
            query_point: Query coordinates
            k: Number of neighbors
            distance_fn: Distance function
            
        Returns:
            List of (point, value, distance) tuples
            
        Raises:
            XWNodeValueError: If query_point invalid or k < 1
        """
        if k < 1:
            raise XWNodeValueError(f"k must be >= 1, got {k}")
        
        query = self._validate_point(query_point)
        
        if distance_fn is None:
            distance_fn = self._euclidean_distance
        
        # Priority queue of k nearest (max heap by distance)
        nearest: List[Tuple[float, KdNode]] = []
        
        def search_knn(node: Optional[KdNode], depth: int) -> None:
            """Recursive k-NN search."""
            if node is None:
                return
            
            dist = distance_fn(query, node.point)
            
            # Add to nearest if:
            # 1. We have < k neighbors, or
            # 2. This is closer than farthest current neighbor
            if len(nearest) < k:
                nearest.append((dist, node))
                nearest.sort(reverse=True)  # Max heap
            elif dist < nearest[0][0]:
                nearest[0] = (dist, node)
                nearest.sort(reverse=True)
            
            # Determine search order
            axis = depth % self.dimensions
            
            if query[axis] < node.point[axis]:
                near, far = node.left, node.right
            else:
                near, far = node.right, node.left
            
            # Search near subtree
            search_knn(near, depth + 1)
            
            # Search far if necessary
            axis_dist = abs(query[axis] - node.point[axis])
            if len(nearest) < k or axis_dist < nearest[0][0]:
                search_knn(far, depth + 1)
        
        search_knn(self._root, 0)
        
        # Convert to result format
        return [(node.point, node.value, dist) for dist, node in reversed(nearest)]
    
    # ============================================================================
    # STANDARD OPERATIONS
    # ============================================================================
    
    def keys(self) -> Iterator[Any]:
        """Get iterator over all points."""
        yield from self._inorder_traversal(self._root)
    
    def _inorder_traversal(self, node: Optional[KdNode]) -> Iterator[Tuple[float, ...]]:
        """Inorder traversal."""
        if node is None:
            return
        
        yield from self._inorder_traversal(node.left)
        yield node.point
        yield from self._inorder_traversal(node.right)
    
    def values(self) -> Iterator[Any]:
        """Get iterator over all values."""
        for point in self.keys():
            yield self._points[point]
    
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get iterator over point-value pairs."""
        for point in self.keys():
            yield (point, self._points[point])
    
    def __len__(self) -> int:
        """Get number of points."""
        return self._size
    
    def to_native(self) -> Any:
        """Convert to native dict."""
        return {point: value for point, value in self.items()}
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def clear(self) -> None:
        """Clear all points."""
        self._root = None
        self._size = 0
        self._points.clear()
    
    def is_empty(self) -> bool:
        """Check if empty."""
        return self._size == 0
    
    def size(self) -> int:
        """Get number of points."""
        return self._size
    
    def get_mode(self) -> NodeMode:
        """Get strategy mode."""
        return self.mode
    
    def get_traits(self) -> NodeTrait:
        """Get strategy traits."""
        return self.traits
    
    def get_height(self) -> int:
        """Get tree height."""
        def height(node: Optional[KdNode]) -> int:
            if node is None:
                return 0
            return 1 + max(height(node.left), height(node.right))
        
        return height(self._root)
    
    # ============================================================================
    # STATISTICS
    # ============================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get k-d tree statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'size': self._size,
            'dimensions': self.dimensions,
            'height': self.get_height(),
            'optimal_height': math.ceil(math.log2(self._size + 1)) if self._size > 0 else 0,
            'balance_factor': self.get_height() / max(math.log2(self._size + 1), 1) if self._size > 0 else 1.0
        }
    
    # ============================================================================
    # COMPATIBILITY METHODS
    # ============================================================================
    
    def find(self, key: Any) -> Optional[Any]:
        """Find value by point."""
        return self.get(key)
    
    def insert(self, key: Any, value: Any = None) -> None:
        """Insert point."""
        self.put(key, value)
    
    def __str__(self) -> str:
        """String representation."""
        return f"KdTreeStrategy(k={self.dimensions}, size={self._size}, height={self.get_height()})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"KdTreeStrategy(mode={self.mode.name}, k={self.dimensions}, size={self._size}, traits={self.traits})"
    
    # ============================================================================
    # FACTORY METHOD
    # ============================================================================
    
    @classmethod
    def create_from_data(cls, data: Any, dimensions: int = 2) -> 'KdTreeStrategy':
        """
        Create k-d tree from data.
        
        Args:
            data: Dict with point tuples as keys or list of points
            dimensions: Number of dimensions
            
        Returns:
            New KdTreeStrategy instance
        """
        instance = cls(dimensions=dimensions)
        
        if isinstance(data, dict):
            for key, value in data.items():
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, (tuple, list)):
                    if len(item) == dimensions + 1:
                        # Point with value
                        instance.put(tuple(item[:dimensions]), item[dimensions])
                    else:
                        # Just point
                        instance.put(tuple(item), None)
                else:
                    raise XWNodeValueError(
                        "List items must be point tuples or point+value tuples"
                    )
        else:
            raise XWNodeValueError(
                "Data must be dict with point keys or list of point tuples"
            )
        
        return instance
    
    # ============================================================================
    # BULK CONSTRUCTION (OPTIMAL)
    # ============================================================================
    
    def build_balanced(self, points: List[Tuple[Tuple[float, ...], Any]]) -> None:
        """
        Build balanced k-d tree from points using median splitting.
        
        Args:
            points: List of (point, value) tuples
            
        WHY median splitting:
        - Ensures balanced tree construction
        - O(n log n) build time
        - Optimal for static datasets
        """
        self.clear()
        
        def build_recursive(point_list: List[Tuple[Tuple[float, ...], Any]], 
                          depth: int) -> Optional[KdNode]:
            """Recursively build balanced tree."""
            if not point_list:
                return None
            
            axis = depth % self.dimensions
            
            # Sort by current axis and find median
            point_list.sort(key=lambda x: x[0][axis])
            median = len(point_list) // 2
            
            point, value = point_list[median]
            node = KdNode(point, value, axis)
            
            # Recursively build subtrees
            node.left = build_recursive(point_list[:median], depth + 1)
            node.right = build_recursive(point_list[median + 1:], depth + 1)
            
            # Track in points dict
            self._points[point] = value
            self._size += 1
            
            return node
        
        self._root = build_recursive(points, 0)


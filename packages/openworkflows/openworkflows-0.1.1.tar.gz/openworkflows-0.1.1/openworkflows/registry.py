"""Node registry for registering and retrieving node types."""

from typing import Dict, Type, Optional, Any, Callable
from openworkflows.node import Node


class NodeRegistry:
    """Registry for workflow node types."""

    def __init__(self):
        """Initialize the registry."""
        self._nodes: Dict[str, Type[Node] | Callable] = {}

    def register(self, name: str, node_class: Type[Node] | Callable) -> None:
        """Register a node type.

        Args:
            name: The name to register the node under
            node_class: The node class or factory function

        Raises:
            ValueError: If a node with this name is already registered
        """
        if name in self._nodes:
            raise ValueError(f"Node type '{name}' is already registered")
        self._nodes[name] = node_class

    def get(self, name: str) -> Optional[Type[Node] | Callable]:
        """Get a node type by name.

        Args:
            name: The node type name

        Returns:
            The node class or factory function, or None if not found
        """
        return self._nodes.get(name)

    def create(self, name: str, config: Optional[Dict[str, Any]] = None) -> Node:
        """Create a node instance by type name.

        Args:
            name: The node type name
            config: Optional configuration for the node

        Returns:
            A node instance

        Raises:
            ValueError: If the node type is not registered
        """
        node_class = self.get(name)
        if node_class is None:
            raise ValueError(f"Unknown node type: {name}")

        # Check if it's a factory function (from @node decorator)
        if callable(node_class) and not isinstance(node_class, type):
            return node_class(config)

        # It's a class, instantiate it
        return node_class(config)

    def list_nodes(self) -> list[str]:
        """Get a list of all registered node type names.

        Returns:
            List of node type names
        """
        return list(self._nodes.keys())

    def unregister(self, name: str) -> None:
        """Unregister a node type.

        Args:
            name: The node type name
        """
        if name in self._nodes:
            del self._nodes[name]


# Global registry instance
_global_registry = NodeRegistry()


def register_node(name: Optional[str] = None):
    """Decorator to register a node class.

    Args:
        name: Optional name for the node (defaults to class name)

    Returns:
        Decorator function

    Example:
        >>> @register_node("my_node")
        >>> class MyNode(Node):
        ...     async def execute(self, ctx):
        ...         return {"result": "done"}
    """

    def decorator(node_class: Type[Node] | Callable):
        node_name = name or getattr(node_class, "node_name", node_class.__name__)
        _global_registry.register(node_name, node_class)
        return node_class

    return decorator


def get_node(name: str) -> Optional[Type[Node] | Callable]:
    """Get a node type from the global registry.

    Args:
        name: The node type name

    Returns:
        The node class or None if not found
    """
    return _global_registry.get(name)


def create_node(name: str, config: Optional[Dict[str, Any]] = None) -> Node:
    """Create a node instance from the global registry.

    Args:
        name: The node type name
        config: Optional configuration

    Returns:
        A node instance
    """
    return _global_registry.create(name, config)


def list_nodes() -> list[str]:
    """Get a list of all registered node types.

    Returns:
        List of node type names
    """
    return _global_registry.list_nodes()


def get_node_info(name: str) -> Optional[Dict[str, Any]]:
    """Get node info including schema for frontend.

    Returns dict with inputs, outputs, parameters, tags, and optional schema.

    Args:
        name: The node type name

    Returns:
        Dictionary with node metadata or None if not found
    """
    node_class = _global_registry.get(name)
    if not node_class:
        return None

    return {
        "type": name,
        "inputs": getattr(node_class, "inputs", {}),
        "outputs": getattr(node_class, "outputs", {}),
        "parameters": getattr(node_class, "parameters", {}),
        "tags": getattr(node_class, "tags", []),
        "schema": getattr(node_class, "schema", None),
    }

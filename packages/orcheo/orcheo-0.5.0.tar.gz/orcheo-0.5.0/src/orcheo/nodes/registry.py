"""Registry implementation for Orcheo nodes."""

from collections.abc import Callable
from pydantic import BaseModel


class NodeMetadata(BaseModel):
    """Metadata for a node in the flow.

    Attributes:
        name: Unique identifier for the node
        description: Human-readable description of the node's purpose
        category: Node category, defaults to "general"
    """

    name: str
    """Unique identifier for the node."""
    description: str
    """Human-readable description of the node's purpose."""
    category: str = "general"
    """Node category, defaults to "general"."""


class NodeRegistry:
    """Registry for managing flow nodes and their metadata."""

    def __init__(self) -> None:
        """Initialize an empty node registry."""
        self._nodes: dict[str, Callable] = {}
        self._metadata: dict[str, NodeMetadata] = {}

    def register(self, metadata: NodeMetadata) -> Callable[[Callable], Callable]:
        """Register a new node with its metadata.

        Args:
            metadata: Node metadata including name and schemas

        Returns:
            Decorator function that registers the node implementation
        """

        def decorator(func: Callable) -> Callable:
            self._nodes[metadata.name] = func
            self._metadata[metadata.name] = metadata
            return func

        return decorator

    def get_node(self, name: str) -> Callable | None:
        """Get a node implementation by name.

        Args:
            name: Name of the node to retrieve

        Returns:
            Node implementation function or None if not found
        """
        return self._nodes.get(name)


# Global registry instance
registry = NodeRegistry()

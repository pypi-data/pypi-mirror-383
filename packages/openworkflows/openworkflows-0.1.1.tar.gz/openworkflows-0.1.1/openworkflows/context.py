"""Execution context for workflow nodes."""

from typing import Any, Dict, Optional, Callable, List, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    pass


@dataclass
class ExecutionContext:
    """Context passed to nodes during execution.

    Attributes:
        node_id: ID of the current node
        get_input: Function to retrieve input values by handle name
        node_results: Results from all previously executed nodes
        workflow_inputs: Initial inputs provided to the workflow
        metadata: Additional metadata (user_id, request_id, etc.)
        services: Additional services (database, cache, etc.)
        _connected_inputs: Set of input handle names that have connections
    """

    node_id: str
    get_input: Callable[[str], Any]
    node_results: Dict[str, Any]
    workflow_inputs: Dict[str, Any]
    metadata: Dict[str, Any]
    services: Optional[Dict[str, Any]] = None
    _connected_inputs: List[str] = field(default_factory=list)

    def input(self, handle: str, default: Any = None) -> Any:
        """Get input value for a handle with optional default.

        Args:
            handle: The input handle name
            default: Default value if input is not found

        Returns:
            The input value or default
        """
        value = self.get_input(handle)
        return value if value is not None else default

    def has_input(self, handle: str) -> bool:
        """Check if an input handle has a value.

        Args:
            handle: The input handle name

        Returns:
            True if the handle has a value
        """
        return self.get_input(handle) is not None

    def service(self, name: str) -> Any:
        """Get a service by name.

        Args:
            name: The service name

        Returns:
            The service instance

        Raises:
            KeyError: If service not found
        """
        if self.services is None:
            raise KeyError("No services configured")
        return self.services[name]

    def list_connected_inputs(self) -> List[str]:
        """Return list of input handle names that have connections.

        Returns:
            List of input handle names that are connected to this node
        """
        return list(self._connected_inputs)

    def get_input_or_none(self, handle: str) -> Any:
        """Get input value or None if not connected (no exception).

        Args:
            handle: The input handle name

        Returns:
            The input value or None if not connected
        """
        return self.get_input(handle)

    def all_inputs(self) -> Dict[str, Any]:
        """Get all connected inputs as a dictionary.

        Returns:
            Dictionary mapping handle names to their values for all connected inputs
        """
        result = {}
        for handle in self._connected_inputs:
            value = self.get_input(handle)
            if value is not None:
                result[handle] = value
        return result

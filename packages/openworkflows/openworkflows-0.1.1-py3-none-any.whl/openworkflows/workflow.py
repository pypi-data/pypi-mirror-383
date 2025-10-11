"""Workflow execution engine."""

from typing import Any, Dict, List, Optional, Set
import logging
from dataclasses import dataclass, asdict
import json

from openworkflows.node import Node
from openworkflows.context import ExecutionContext
from openworkflows.registry import create_node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowNode:
    """Internal representation of a node in the workflow."""

    id: str
    type: str
    config: Dict[str, Any]
    instance: Optional[Node] = None


@dataclass
class WorkflowEdge:
    """Represents a connection between two nodes."""

    source: str
    target: str
    source_handle: str = "result"
    target_handle: str = "input"


class Workflow:
    """Workflow execution engine."""

    def __init__(self, name: Optional[str] = None):
        """Initialize a new workflow.

        Args:
            name: Optional name for the workflow
        """
        self.name = name or "Workflow"
        self._nodes: Dict[str, WorkflowNode] = {}
        self._edges: List[WorkflowEdge] = []
        self._llm_provider = None
        self._services: Dict[str, Any] = {}

    def add_node(
        self, node_id: str, node_type: str, config: Optional[Dict[str, Any]] = None
    ) -> "Workflow":
        """Add a node to the workflow.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node (must be registered)
            config: Optional configuration for the node

        Returns:
            Self for method chaining

        Raises:
            ValueError: If node_id already exists or parameter validation fails
        """
        if node_id in self._nodes:
            raise ValueError(f"Node with id '{node_id}' already exists")

        # Validate parameters by creating a temporary instance
        # This ensures parameter validation happens at graph construction time
        try:
            create_node(node_type, config or {})
        except Exception as e:
            raise ValueError(
                f"Failed to create node '{node_id}' of type '{node_type}': {str(e)}"
            ) from e

        self._nodes[node_id] = WorkflowNode(id=node_id, type=node_type, config=config or {})
        return self

    def connect(
        self,
        source: str,
        target: str,
        source_handle: str = "result",
        target_handle: str = "input",
    ) -> "Workflow":
        """Connect two nodes.

        Args:
            source: Source node ID or "source_id.handle" format
            target: Target node ID or "target_id.handle" format
            source_handle: Source output handle name (if not in source string)
            target_handle: Target input handle name (if not in target string)

        Returns:
            Self for method chaining

        Example:
            >>> workflow.connect("node1", "node2")
            >>> workflow.connect("node1.output", "node2.input")
        """
        # Parse source and target handles from dot notation
        if "." in source:
            source_id, source_handle = source.split(".", 1)
        else:
            source_id = source

        if "." in target:
            target_id, target_handle = target.split(".", 1)
        else:
            target_id = target

        self._edges.append(
            WorkflowEdge(
                source=source_id,
                target=target_id,
                source_handle=source_handle,
                target_handle=target_handle,
            )
        )
        return self

    def add_service(self, name: str, service: Any) -> "Workflow":
        """Add a service to the workflow context.

        Args:
            name: Service name
            service: Service instance

        Returns:
            Self for method chaining
        """
        self._services[name] = service
        return self

    async def run(
        self, inputs: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the workflow.

        Args:
            inputs: Input values for the workflow
            metadata: Additional metadata to pass to nodes

        Returns:
            Dictionary of outputs from all nodes

        Raises:
            ValueError: If workflow validation fails
            Exception: If execution fails
        """
        inputs = inputs or {}
        metadata = metadata or {}

        logger.info(f"Starting workflow '{self.name}' with {len(self._nodes)} nodes")

        # Build execution order
        execution_order = self._build_execution_order()
        logger.info(f"Execution order: {execution_order}")

        # Initialize node instances
        for node_id, workflow_node in self._nodes.items():
            workflow_node.instance = create_node(workflow_node.type, workflow_node.config)

        # Execute nodes in order
        node_results: Dict[str, Any] = {}

        for node_id in execution_order:
            logger.info(f"Executing node '{node_id}'")
            workflow_node = self._nodes[node_id]

            # Create input resolver for this node
            def make_resolver(nid: str):
                def resolve_input(handle: str) -> Any:
                    return self._resolve_input(nid, handle, node_results)

                return resolve_input

            # Get list of connected input handles for this node
            connected_inputs = list(set(
                edge.target_handle
                for edge in self._edges
                if edge.target == node_id
            ))

            # Create execution context
            ctx = ExecutionContext(
                node_id=node_id,
                get_input=make_resolver(node_id),
                node_results=node_results,
                workflow_inputs=inputs,
                metadata=metadata,
                services=self._services if self._services else None,
                _connected_inputs=connected_inputs,
            )

            try:
                result = await workflow_node.instance.run(ctx)
                node_results[node_id] = result
                logger.info(f"Node '{node_id}' completed successfully")
            except Exception as e:
                logger.error(f"Node '{node_id}' failed: {str(e)}")
                raise Exception(f"Node '{node_id}' execution failed: {str(e)}") from e

        logger.info(f"Workflow '{self.name}' completed successfully")
        return node_results

    def _build_execution_order(self) -> List[str]:
        """Build execution order using topological sort.

        Returns:
            List of node IDs in execution order

        Raises:
            ValueError: If circular dependency detected
        """
        # Build dependency graph
        dependencies: Dict[str, List[str]] = {node_id: [] for node_id in self._nodes}

        for edge in self._edges:
            if edge.target not in dependencies:
                dependencies[edge.target] = []
            dependencies[edge.target].append(edge.source)

        # Topological sort using DFS
        visited: Set[str] = set()
        temp_visited: Set[str] = set()
        execution_order: List[str] = []

        def dfs(node_id: str):
            if node_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving node '{node_id}'")
            if node_id in visited:
                return

            temp_visited.add(node_id)

            for dep in dependencies[node_id]:
                dfs(dep)

            temp_visited.remove(node_id)
            visited.add(node_id)
            execution_order.append(node_id)

        for node_id in self._nodes:
            if node_id not in visited:
                dfs(node_id)

        return execution_order

    def _resolve_input(self, node_id: str, handle: str, node_results: Dict[str, Any]) -> Any:
        """Resolve input value for a node's handle.

        Args:
            node_id: The target node ID
            handle: The target handle name
            node_results: Results from executed nodes

        Returns:
            The resolved input value or None
        """
        # Find edges that connect to this node's handle
        connected_edges = [
            edge for edge in self._edges if edge.target == node_id and edge.target_handle == handle
        ]

        if not connected_edges:
            logger.debug(f"No input found for {node_id}.{handle}")
            return None

        # Take the first edge (could support multiple in the future)
        edge = connected_edges[0]
        source_id = edge.source
        source_handle = edge.source_handle

        if source_id not in node_results:
            logger.warning(f"Source node '{source_id}' has not been executed yet")
            return None

        source_result = node_results[source_id]

        # Extract value from source result
        if isinstance(source_result, dict) and source_handle in source_result:
            return source_result[source_handle]

        # Fallback to "result" if specific handle not found
        if isinstance(source_result, dict) and "result" in source_result:
            return source_result["result"]

        logger.warning(f"Could not resolve {source_id}.{source_handle} for {node_id}.{handle}")
        return None

    def print_graph(self) -> None:
        """Print a visual representation of the workflow graph to the terminal."""
        print(f"\n{'='*80}")
        print(f"  🔀 Workflow: {self.name}")
        print(f"{'='*80}\n")

        # Build dependency map
        incoming_edges: Dict[str, List[WorkflowEdge]] = {node_id: [] for node_id in self._nodes}
        outgoing_edges: Dict[str, List[WorkflowEdge]] = {node_id: [] for node_id in self._nodes}

        for edge in self._edges:
            if edge.target in incoming_edges:
                incoming_edges[edge.target].append(edge)
            if edge.source in outgoing_edges:
                outgoing_edges[edge.source].append(edge)

        # Get execution order
        try:
            execution_order = self._build_execution_order()
        except ValueError as e:
            print(f"❌ ERROR: {str(e)}\n")
            execution_order = list(self._nodes.keys())

        # Print nodes in execution order with visual flow
        for i, node_id in enumerate(execution_order):
            node = self._nodes[node_id]

            # Print incoming edges
            if incoming_edges[node_id]:
                for edge in incoming_edges[node_id]:
                    handle_info = ""
                    if edge.source_handle != "result" or edge.target_handle != "input":
                        handle_info = f" ({edge.source_handle} → {edge.target_handle})"
                    print(f"       ↓ from {edge.source}{handle_info}")
            elif i > 0:
                print("       │")

            # Print node box
            config_str = ""
            if node.config:
                # Format config compactly
                config_items = [f"{k}={v}" for k, v in node.config.items()]
                config_str = f" [{', '.join(config_items)}]"

            box_content = f"{node_id} ({node.type}){config_str}"
            box_width = len(box_content) + 4

            print(f"    ┌{'─' * (box_width - 2)}┐")
            print(f"    │ {box_content} │")
            print(f"    └{'─' * (box_width - 2)}┘")

            # Print outgoing edges preview
            if outgoing_edges[node_id]:
                out_count = len(outgoing_edges[node_id])
                targets = [e.target for e in outgoing_edges[node_id]]
                if out_count == 1:
                    print(f"       ↓")
                else:
                    print(f"       ↓ (to {out_count} nodes: {', '.join(targets)})")
            elif i < len(execution_order) - 1:
                print("       ↓")

            print()

        # Print summary
        print(f"{'─'*80}")
        print(f"  📊 Summary: {len(self._nodes)} nodes, {len(self._edges)} connections")
        print(f"{'='*80}\n")

    def to_json(self, indent: Optional[int] = 2) -> str:
        """Export workflow to JSON string.

        Args:
            indent: JSON indentation level (None for compact output)

        Returns:
            JSON string representation of the workflow
        """
        workflow_dict = {
            "name": self.name,
            "nodes": [
                {"id": node.id, "type": node.type, "config": node.config}
                for node in self._nodes.values()
            ],
            "edges": [asdict(edge) for edge in self._edges],
        }
        return json.dumps(workflow_dict, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "Workflow":
        """Import workflow from JSON string.

        Args:
            json_str: JSON string representation of a workflow

        Returns:
            New Workflow instance

        Raises:
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}") from e

        if not isinstance(data, dict):
            raise ValueError("JSON must be an object")

        # Extract workflow data
        name = data.get("name", "Workflow")
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        # Create new workflow
        workflow = cls(name=name)

        # Add nodes
        for node_data in nodes:
            if not isinstance(node_data, dict):
                raise ValueError(f"Invalid node data: {node_data}")

            node_id = node_data.get("id")
            node_type = node_data.get("type")
            node_config = node_data.get("config", {})

            if not node_id or not node_type:
                raise ValueError(f"Node missing 'id' or 'type': {node_data}")

            workflow.add_node(node_id, node_type, node_config)

        # Add edges
        for edge_data in edges:
            if not isinstance(edge_data, dict):
                raise ValueError(f"Invalid edge data: {edge_data}")

            source = edge_data.get("source")
            target = edge_data.get("target")
            source_handle = edge_data.get("source_handle", "result")
            target_handle = edge_data.get("target_handle", "input")

            if not source or not target:
                raise ValueError(f"Edge missing 'source' or 'target': {edge_data}")

            workflow.connect(source, target, source_handle, target_handle)

        return workflow

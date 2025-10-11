"""Base node class and decorator for creating workflow nodes."""

from typing import Any, Dict, Optional, Callable, Type, Union
from abc import ABC, abstractmethod
import inspect

from openworkflows.context import ExecutionContext
from openworkflows.handles import HandleSpec
from openworkflows.parameters import Parameter, ParameterSpec


class Node(ABC):
    """Base class for all workflow nodes.

    Subclasses should define:
    - inputs: Dict of input handle names to types
    - outputs: Dict of output handle names to types
    - parameters: Dict of parameter names to types or Parameter objects
    - tags: List of tags for categorizing the node (e.g., ["llm", "text"])
    - schema: Optional dict with multilingual metadata for frontend rendering
    - execute(): The node's execution logic
    """

    inputs: Dict[str, Type[Any]] = {}
    outputs: Dict[str, Type[Any]] = {}
    parameters: Dict[str, Union[Type[Any], Parameter]] = {}
    tags: list[str] = []
    schema: Optional[Dict[str, Any]] = None

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the node with optional configuration.

        Args:
            config: Configuration dictionary for the node
        """
        self._handle_spec = HandleSpec(inputs=self.inputs, outputs=self.outputs)
        self._param_spec = ParameterSpec.from_dict(self.parameters)

        # Validate config and apply defaults
        self.config = self._param_spec.validate_and_set_defaults(config or {})

    @abstractmethod
    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Execute the node's logic.

        Args:
            ctx: Execution context

        Returns:
            Dictionary of output handle names to values
        """
        pass

    async def run(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Run the node with validation.

        Args:
            ctx: Execution context

        Returns:
            Dictionary of output handle names to values

        Raises:
            TypeError: If input/output validation fails
        """
        # Collect inputs
        inputs = {}
        for handle_name in self.inputs.keys():
            value = ctx.get_input(handle_name)
            if value is not None:
                inputs[handle_name] = value

        # Validate inputs
        self._handle_spec.validate_inputs(inputs)

        # Execute
        outputs = await self.execute(ctx)

        # Validate outputs
        if outputs is not None:
            self._handle_spec.validate_outputs(outputs)

        return outputs or {}

    def param(self, name: str, default: Any = None) -> Any:
        """Get a parameter value with optional default.

        Args:
            name: The parameter name
            default: Default value if parameter not found

        Returns:
            The parameter value or default
        """
        return self.config.get(name, default)

    @classmethod
    def get_type_name(cls) -> str:
        """Get the type name for this node (used for registration)."""
        return cls.__name__


class FunctionNode(Node):
    """A node created from a function using the @node decorator."""

    def __init__(
        self,
        func: Callable,
        inputs: Dict[str, Type[Any]],
        outputs: Dict[str, Type[Any]],
        parameters: Dict[str, Union[Type[Any], Parameter]] = None,
        tags: list[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a function-based node.

        Args:
            func: The function to execute
            inputs: Input handle specifications
            outputs: Output handle specifications
            parameters: Parameter specifications
            tags: List of tags for categorizing the node
            config: Optional configuration
        """
        self.func = func
        self.inputs = inputs
        self.outputs = outputs
        self.parameters = parameters or {}
        self.tags = tags or []
        super().__init__(config)

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Execute the wrapped function.

        Args:
            ctx: Execution context

        Returns:
            Dictionary of outputs
        """
        # Collect inputs based on function signature
        sig = inspect.signature(self.func)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "ctx":
                kwargs["ctx"] = ctx
            elif param_name in self.inputs:
                value = ctx.get_input(param_name)
                if value is not None:
                    kwargs[param_name] = value
                elif param.default is not inspect.Parameter.empty:
                    kwargs[param_name] = param.default

        # Execute function
        if inspect.iscoroutinefunction(self.func):
            result = await self.func(**kwargs)
        else:
            result = self.func(**kwargs)

        # Convert result to output dictionary
        if isinstance(result, dict):
            return result
        elif len(self.outputs) == 1:
            output_name = list(self.outputs.keys())[0]
            return {output_name: result}
        else:
            return {"result": result}

    @classmethod
    def get_type_name(cls) -> str:
        """Get type name from the wrapped function."""
        return getattr(cls, "_node_name", cls.__name__)


def node(
    inputs: Optional[Dict[str, Type[Any]]] = None,
    outputs: Optional[Dict[str, Type[Any]]] = None,
    parameters: Optional[Dict[str, Union[Type[Any], Parameter]]] = None,
    tags: Optional[list[str]] = None,
    name: Optional[str] = None,
) -> Callable:
    """Decorator to create a node from a function.

    Args:
        inputs: Dictionary of input handle names to types
        outputs: Dictionary of output handle names to types
        parameters: Dictionary of parameter names to types or Parameter objects
        tags: List of tags for categorizing the node (e.g., ["llm", "text"])
        name: Optional name for the node type

    Returns:
        Decorator function

    Example:
        >>> @node(
        ...     inputs={"text": str},
        ...     outputs={"length": int},
        ...     parameters={"multiplier": int},
        ...     tags=["transform", "text"]
        ... )
        >>> async def count_chars(ctx: ExecutionContext, node) -> int:
        ...     text = ctx.input("text")
        ...     multiplier = node.param("multiplier", 1)
        ...     return len(text) * multiplier
    """

    def decorator(func: Callable) -> Type[FunctionNode]:
        # Infer inputs/outputs from function signature if not provided
        sig = inspect.signature(func)
        inferred_inputs = inputs or {}
        inferred_outputs = outputs or {}

        # If inputs not specified, infer from parameters (excluding 'ctx')
        if not inferred_inputs:
            for param_name, param in sig.parameters.items():
                if param_name != "ctx" and param.annotation != inspect.Parameter.empty:
                    inferred_inputs[param_name] = param.annotation

        # If outputs not specified, infer from return type
        if not inferred_outputs:
            return_type = sig.return_annotation
            if return_type != inspect.Parameter.empty:
                if return_type == Dict[str, Any] or str(return_type).startswith("typing.Dict"):
                    # Function returns a dictionary of outputs
                    inferred_outputs = {"result": Any}
                else:
                    # Function returns a single value
                    inferred_outputs = {"result": return_type}
            else:
                inferred_outputs = {"result": Any}

        # Create a new class that inherits from FunctionNode
        node_name = name or func.__name__
        node_class = type(
            node_name,
            (FunctionNode,),
            {
                "__doc__": func.__doc__,
                "_node_name": node_name,
                "_wrapped_func": func,
            },
        )

        # Create a factory function that returns instances
        def node_factory(config: Optional[Dict[str, Any]] = None) -> FunctionNode:
            return FunctionNode(
                func=func,
                inputs=inferred_inputs,
                outputs=inferred_outputs,
                parameters=parameters or {},
                tags=tags or [],
                config=config,
            )

        # Attach metadata to the factory
        node_factory.node_class = node_class
        node_factory.node_name = node_name
        node_factory.inputs = inferred_inputs
        node_factory.outputs = inferred_outputs
        node_factory.parameters = parameters or {}
        node_factory.tags = tags or []

        return node_factory

    return decorator

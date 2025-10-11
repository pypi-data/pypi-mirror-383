"""Input and output handle definitions for nodes."""

from typing import Any, Dict, Type, Optional, get_origin, get_args, Union
from dataclasses import dataclass


@dataclass
class Handle:
    """Defines an input or output handle for a node.

    Attributes:
        name: Handle name
        type: Expected Python type
        required: Whether this handle is required
        description: Human-readable description
    """

    name: str
    type: Type[Any]
    required: bool = True
    description: str = ""

    def __post_init__(self):
        """Automatically detect if type is Optional and mark as not required."""
        origin = get_origin(self.type)
        if origin is Union:
            args = get_args(self.type)
            # Check if it's Optional (Union with None)
            if type(None) in args:
                self.required = False

    def validate(self, value: Any) -> None:
        """Validate that a value matches the handle's type.

        Args:
            value: The value to validate

        Raises:
            TypeError: If the value doesn't match the expected type
        """
        if value is None:
            if self.required:
                raise TypeError(f"Required handle '{self.name}' cannot be None")
            return

        # Get the origin type for generics (e.g., List[str] -> list)
        origin = get_origin(self.type)

        # Handle Union types (including Optional)
        if origin is Union:
            args = get_args(self.type)
            # Filter out None type
            non_none_args = [arg for arg in args if arg is not type(None)]

            # Try to validate against each possible type
            for arg in non_none_args:
                try:
                    # Recursively create a handle with this type and validate
                    temp_handle = Handle(name=self.name, type=arg, required=False)
                    temp_handle.validate(value)
                    return  # If validation succeeds, we're done
                except TypeError:
                    continue  # Try next type

            # If we get here, none of the types matched
            type_names = [
                arg.__name__ if hasattr(arg, "__name__") else str(arg) for arg in non_none_args
            ]
            raise TypeError(
                f"Handle '{self.name}' expects one of {type_names}, got {type(value).__name__}"
            )

        expected_type = origin or self.type

        # Skip validation for Any type
        if expected_type is Any:
            return

        # Allow int for float (automatic coercion)
        if expected_type is float and isinstance(value, int):
            return

        # Allow numeric types for each other
        if expected_type in (int, float) and isinstance(value, (int, float)):
            return

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Handle '{self.name}' expects {expected_type.__name__}, got {type(value).__name__}"
            )


class HandleSpec:
    """Specification for a node's input and output handles."""

    def __init__(
        self,
        inputs: Optional[Dict[str, Type[Any]]] = None,
        outputs: Optional[Dict[str, Type[Any]]] = None,
    ):
        """Initialize handle specification.

        Args:
            inputs: Dictionary of input handle names to types (use "*" for wildcard)
            outputs: Dictionary of output handle names to types (use "*" for wildcard)
        """
        inputs = inputs or {}
        outputs = outputs or {}

        # Extract wildcard pattern if present
        self.wildcard_input: Optional[Handle] = None
        if "*" in inputs:
            wildcard_type = inputs["*"]
            self.wildcard_input = Handle(name="*", type=wildcard_type)
            # Remove wildcard from regular inputs
            inputs = {k: v for k, v in inputs.items() if k != "*"}

        self.wildcard_output: Optional[Handle] = None
        if "*" in outputs:
            wildcard_type = outputs["*"]
            self.wildcard_output = Handle(name="*", type=wildcard_type)
            # Remove wildcard from regular outputs
            outputs = {k: v for k, v in outputs.items() if k != "*"}

        self.inputs = {
            name: Handle(name=name, type=type_) for name, type_ in inputs.items()
        }
        self.outputs = {
            name: Handle(name=name, type=type_) for name, type_ in outputs.items()
        }

    def validate_inputs(self, inputs: Dict[str, Any]) -> None:
        """Validate input values against the spec.

        Args:
            inputs: Dictionary of input values

        Raises:
            TypeError: If validation fails
        """
        # Check required inputs are present
        for handle_name, handle in self.inputs.items():
            if handle.required and handle_name not in inputs:
                raise TypeError(f"Required input '{handle_name}' is missing")

        # Validate each input
        for handle_name, value in inputs.items():
            if handle_name in self.inputs:
                # Validate against named handle
                self.inputs[handle_name].validate(value)
            elif self.wildcard_input:
                # Validate against wildcard pattern
                wildcard_handle = Handle(name=handle_name, type=self.wildcard_input.type)
                wildcard_handle.validate(value)
            # If no wildcard and no named handle, skip validation (allow unknown inputs)

    def validate_outputs(self, outputs: Dict[str, Any]) -> None:
        """Validate output values against the spec.

        Args:
            outputs: Dictionary of output values

        Raises:
            TypeError: If validation fails
        """
        for handle_name, handle in self.outputs.items():
            if handle.required and handle_name not in outputs:
                raise TypeError(f"Required output '{handle_name}' is missing")

        for handle_name, value in outputs.items():
            if handle_name in self.outputs:
                # Validate against named handle
                self.outputs[handle_name].validate(value)
            elif self.wildcard_output:
                # Validate against wildcard pattern
                wildcard_handle = Handle(name=handle_name, type=self.wildcard_output.type)
                wildcard_handle.validate(value)
            # If no wildcard and no named handle, skip validation (allow unknown outputs)

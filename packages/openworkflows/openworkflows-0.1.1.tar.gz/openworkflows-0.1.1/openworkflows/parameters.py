"""Parameter definitions for node configuration."""

from typing import Any, Type, Optional, Callable, List, Union, get_origin
from dataclasses import dataclass


@dataclass
class Parameter:
    """Defines a configurable parameter for a node.

    Parameters are set at node instantiation time and remain constant
    during execution, unlike inputs which vary per execution.

    Attributes:
        name: Parameter name
        type: Expected Python type
        default: Default value (if None and required=True, parameter is required)
        required: Whether this parameter must be provided
        description: Human-readable description
        choices: Optional list of allowed values
        validator: Optional custom validation function
    """

    name: str
    type: Type[Any]
    default: Any = None
    required: bool = False
    description: str = ""
    choices: Optional[List[Any]] = None
    validator: Optional[Callable[[Any], bool]] = None

    def validate(self, value: Any) -> Any:
        """Validate and coerce a parameter value.

        Args:
            value: The value to validate

        Returns:
            The validated/coerced value

        Raises:
            ValueError: If validation fails
        """
        # Handle None values
        if value is None:
            if self.required:
                raise ValueError(f"Required parameter '{self.name}' cannot be None")
            return self.default

        # Type validation with coercion
        if self.type is not Any:
            # Check if type is a Literal - skip isinstance check for Literal types
            origin = get_origin(self.type)
            is_literal = str(origin) == "typing.Literal"

            if not is_literal:
                try:
                    # Special handling for common types
                    if self.type is bool:
                        # Don't coerce for bool - be strict
                        if not isinstance(value, bool):
                            raise TypeError(f"Expected bool, got {type(value).__name__}")
                    elif self.type is str:
                        value = str(value)
                    elif self.type in (int, float):
                        # Allow numeric coercion
                        if isinstance(value, (int, float)):
                            value = self.type(value)
                        else:
                            raise TypeError(
                                f"Expected {self.type.__name__}, got {type(value).__name__}"
                            )
                    else:
                        # For all other types, check if we can do isinstance
                        # Skip generic types that can't be used with isinstance
                        try:
                            if not isinstance(value, self.type):
                                raise TypeError(
                                    f"Expected {self.type.__name__}, got {type(value).__name__}"
                                )
                        except TypeError:
                            # Can't use isinstance with this type (e.g., generic), skip type check
                            pass
                except (TypeError, ValueError) as e:
                    raise ValueError(f"Parameter '{self.name}' validation failed: {str(e)}") from e

        # Choices validation
        if self.choices is not None and value not in self.choices:
            raise ValueError(f"Parameter '{self.name}' must be one of {self.choices}, got {value}")

        # Custom validator
        if self.validator is not None:
            try:
                if not self.validator(value):
                    raise ValueError(f"Custom validation failed for parameter '{self.name}'")
            except Exception as e:
                raise ValueError(
                    f"Parameter '{self.name}' custom validation error: {str(e)}"
                ) from e

        return value


class ParameterSpec:
    """Specification for a node's parameters."""

    def __init__(self, parameters: Optional[dict[str, Parameter]] = None):
        """Initialize parameter specification.

        Args:
            parameters: Dictionary of parameter name to Parameter objects
        """
        self.parameters = parameters or {}

    def validate_and_set_defaults(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate config values and apply defaults.

        Args:
            config: User-provided configuration dictionary

        Returns:
            Validated config with defaults applied

        Raises:
            ValueError: If validation fails
        """
        result = {}

        # Validate provided values
        for key, value in config.items():
            if key not in self.parameters:
                # Allow extra config values (for backwards compatibility)
                result[key] = value
            else:
                param = self.parameters[key]
                result[key] = param.validate(value)

        # Add defaults for missing parameters
        for name, param in self.parameters.items():
            if name not in result:
                if param.required and param.default is None:
                    raise ValueError(f"Required parameter '{name}' is missing")
                result[name] = param.default

        return result

    @classmethod
    def from_dict(cls, params_dict: dict[str, Union[Type, Parameter]]) -> "ParameterSpec":
        """Create ParameterSpec from a simple dict of types.

        Args:
            params_dict: Dict of parameter names to types or Parameter objects

        Returns:
            ParameterSpec instance

        Example:
            >>> spec = ParameterSpec.from_dict({
            ...     "model": str,
            ...     "temperature": Parameter("temperature", float, default=0.7)
            ... })
        """
        parameters = {}
        for name, type_or_param in params_dict.items():
            if isinstance(type_or_param, Parameter):
                parameters[name] = type_or_param
            else:
                # Simple type - create parameter with no default (optional)
                parameters[name] = Parameter(name=name, type=type_or_param, required=False)

        return cls(parameters)

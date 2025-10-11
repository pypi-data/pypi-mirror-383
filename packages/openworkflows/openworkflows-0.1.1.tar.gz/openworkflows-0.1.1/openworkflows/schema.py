"""Schema generation for frontend node rendering."""

from typing import Any, Type, Dict, List, Union, get_origin, get_args, Literal
from openworkflows.parameters import Parameter
from openworkflows.registry import get_node, list_nodes


def _get_ui_type(python_type: Type) -> Dict[str, Any]:
    """Convert Python type to UI component specification.

    Args:
        python_type: Python type annotation

    Returns:
        Dictionary with 'component' type and optional 'options'
    """
    origin = get_origin(python_type)

    # Handle Literal types -> dropdown
    if origin is type(Literal) or str(origin) == "typing.Literal":
        choices = get_args(python_type)
        return {
            "component": "dropdown",
            "options": list(choices),
        }

    # Handle Optional types -> extract inner type and mark as optional
    if origin is Union:
        args = get_args(python_type)
        # Check if it's Optional (Union with None)
        if type(None) in args:
            non_none_types = [t for t in args if t is not type(None)]
            if len(non_none_types) == 1:
                result = _get_ui_type(non_none_types[0])
                result["optional"] = True
                return result

    # Handle Dict types
    if origin is dict or python_type is dict:
        return {
            "component": "json",
            "description": "JSON object",
        }

    # Handle List types
    if origin is list or python_type is list:
        return {
            "component": "json",
            "description": "JSON array",
        }

    # Handle basic types
    if python_type is str:
        return {"component": "text"}
    elif python_type is int:
        return {"component": "number", "inputType": "integer"}
    elif python_type is float:
        return {"component": "number", "inputType": "float"}
    elif python_type is bool:
        return {"component": "checkbox"}
    elif python_type is Any:
        return {"component": "text", "description": "Any type"}

    # Default fallback
    return {"component": "text", "description": str(python_type)}


def get_node_schema(node_type: str) -> Dict[str, Any]:
    """Generate JSON schema for a node type.

    Args:
        node_type: Registered node type name

    Returns:
        Dictionary containing node schema for frontend rendering

    Raises:
        ValueError: If node type not found

    Example:
        >>> schema = get_node_schema("transform")
        >>> print(schema)
        {
            "type": "transform",
            "name": "Transform",
            "description": "Node that applies a transformation...",
            "inputs": [
                {"name": "input", "type": "text", "component": "text"}
            ],
            "outputs": [
                {"name": "output", "type": "text"}
            ],
            "parameters": [
                {
                    "name": "transform",
                    "type": "dropdown",
                    "component": "dropdown",
                    "options": ["identity", "upper", "lower", ...],
                    "default": "identity",
                    "required": false,
                    "description": "Transformation to apply"
                }
            ]
        }
    """
    # Get node class or factory
    node_factory = get_node(node_type)

    if node_factory is None:
        raise ValueError(f"Node type '{node_type}' not found in registry")

    # Handle function nodes differently
    if hasattr(node_factory, "inputs"):
        # Function node created with @node decorator
        inputs = node_factory.inputs
        outputs = node_factory.outputs
        parameters = node_factory.parameters
        node_class = getattr(node_factory, "node_class", node_factory)
    else:
        # Regular node class
        node_class = node_factory
        inputs = getattr(node_class, "inputs", {})
        outputs = getattr(node_class, "outputs", {})
        parameters = getattr(node_class, "parameters", {})

    # Extract inputs
    input_schemas = []
    for handle_name, handle_type in inputs.items():
        ui_spec = _get_ui_type(handle_type)
        input_schemas.append({"name": handle_name, "type": str(handle_type), **ui_spec})

    # Extract outputs
    output_schemas = []
    for handle_name, handle_type in outputs.items():
        output_schemas.append(
            {
                "name": handle_name,
                "type": str(handle_type),
            }
        )

    # Extract parameters
    param_schemas = []
    for param_name, param_def in parameters.items():
        if isinstance(param_def, Parameter):
            # Full Parameter object
            ui_spec = _get_ui_type(param_def.type)

            # Override with choices if provided
            if param_def.choices:
                ui_spec = {
                    "component": "dropdown",
                    "options": param_def.choices,
                }

            param_schema = {
                "name": param_def.name,
                "type": str(param_def.type),
                **ui_spec,
                "default": param_def.default,
                "required": param_def.required,
                "description": param_def.description,
            }
        else:
            # Simple type
            ui_spec = _get_ui_type(param_def)
            param_schema = {
                "name": param_name,
                "type": str(param_def),
                **ui_spec,
                "required": False,
            }

        param_schemas.append(param_schema)

    # Build final schema
    schema = {
        "type": node_type,
        "name": node_type.replace("_", " ").title(),
        "description": node_class.__doc__ or "",
        "inputs": input_schemas,
        "outputs": output_schemas,
        "parameters": param_schemas,
    }

    return schema


def get_all_node_schemas() -> List[Dict[str, Any]]:
    """Get schemas for all registered nodes.

    Returns:
        List of node schemas

    Example:
        >>> schemas = get_all_node_schemas()
        >>> for schema in schemas:
        ...     print(f"{schema['type']}: {len(schema['parameters'])} parameters")
    """
    schemas = []
    for node_type in list_nodes():
        try:
            schema = get_node_schema(node_type)
            schemas.append(schema)
        except Exception as e:
            # Skip nodes that can't be schematized
            print(f"Warning: Could not generate schema for '{node_type}': {e}")

    return schemas

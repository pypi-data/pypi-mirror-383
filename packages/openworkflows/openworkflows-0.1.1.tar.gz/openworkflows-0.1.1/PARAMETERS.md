# OpenWorkflows Parameter System

The parameter system allows nodes to have configurable values that are set at node instantiation time, separate from runtime inputs.

## Overview

**Parameters vs Inputs:**
- **Inputs**: Runtime data that flows between nodes during execution
- **Parameters**: Configuration values set when the node is added to the workflow

## Features

- ✅ **Type validation** with automatic int/float coercion
- ✅ **Default values** for optional parameters
- ✅ **Required parameters** with validation at workflow construction time
- ✅ **Choices validation** for enum-like parameters
- ✅ **Custom validators** for complex validation logic
- ✅ **Built-in parameter support** in all core nodes

## Basic Usage

### Using Parameters in Built-in Nodes

```python
from openworkflows import Workflow, MockLLMProvider

workflow = Workflow("Example")
workflow.set_llm_provider(MockLLMProvider())

# GenerateTextNode with parameters
workflow.add_node("gen", "generate_text", {
    "model": "gpt-4",           # Model name
    "temperature": 0.8,         # Sampling temperature
    "max_tokens": 500,          # Max output length
    "top_p": 0.9,              # Nucleus sampling
})

# TemplateNode with parameters
workflow.add_node("template", "template", {
    "template": "Hello, {name}!",  # Template string (required)
    "strict": True,                 # Fail on missing variables
})

# TransformNode with parameters
workflow.add_node("transform", "transform", {
    "transform": "upper"  # Must be one of valid choices
})

# MergeNode with parameters
workflow.add_node("merge", "merge", {
    "mode": "list",      # "dict" or "list"
    "max_inputs": 20,    # Maximum inputs to collect
})
```

## Creating Nodes with Parameters

### Method 1: Class-Based Node

```python
from openworkflows import Node, ExecutionContext, register_node
from openworkflows.parameters import Parameter
from typing import Dict, Any

@register_node("multiplier")
class MultiplierNode(Node):
    inputs = {"value": float}
    outputs = {"result": float}
    parameters = {
        "factor": Parameter(
            name="factor",
            type=float,
            default=2.0,
            required=False,
            description="Multiplication factor",
            validator=lambda x: x > 0,  # Must be positive
        ),
        "round_result": Parameter(
            name="round_result",
            type=bool,
            default=False,
            description="Round to nearest integer",
        ),
    }

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        value = ctx.input("value")
        factor = self.param("factor")  # Access parameter
        result = value * factor

        if self.param("round_result"):
            result = round(result)

        return {"result": result}

# Use in workflow
workflow.add_node("mult", "multiplier", {
    "factor": 3.5,
    "round_result": True
})
```

### Method 2: Function-Based Node

```python
from openworkflows import node, register_node
from openworkflows.parameters import Parameter

@node(
    inputs={"x": float, "y": float},
    outputs={"result": float},
    parameters={
        "operation": Parameter(
            name="operation",
            type=str,
            default="add",
            choices=["add", "subtract", "multiply", "divide"],
        ),
    }
)
async def math_op(ctx, node):
    x = ctx.input("x")
    y = ctx.input("y")
    op = node.param("operation")

    if op == "add":
        return {"result": x + y}
    elif op == "subtract":
        return {"result": x - y}
    elif op == "multiply":
        return {"result": x * y}
    elif op == "divide":
        return {"result": x / y}

register_node("math_op")(math_op)

# Use in workflow
workflow.add_node("calc", "math_op", {"operation": "multiply"})
```

## Parameter Types

### Required Parameters

```python
parameters = {
    "name": Parameter(
        name="name",
        type=str,
        required=True,  # Must be provided
        description="User name",
    ),
}

# This will raise ValueError at add_node time:
workflow.add_node("node1", "my_node", {})  # Missing 'name'

# This will work:
workflow.add_node("node1", "my_node", {"name": "Alice"})
```

### Optional Parameters with Defaults

```python
parameters = {
    "timeout": Parameter(
        name="timeout",
        type=int,
        default=30,  # Default value
        required=False,
        description="Timeout in seconds",
    ),
}

# Uses default value of 30
workflow.add_node("node1", "my_node", {})

# Overrides default
workflow.add_node("node2", "my_node", {"timeout": 60})
```

### Parameters with Choices

```python
parameters = {
    "level": Parameter(
        name="level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        description="Log level",
    ),
}

# This works
workflow.add_node("node1", "my_node", {"level": "debug"})

# This raises ValueError at add_node time
workflow.add_node("node2", "my_node", {"level": "invalid"})
```

### Parameters with Custom Validators

```python
parameters = {
    "percentage": Parameter(
        name="percentage",
        type=float,
        default=50.0,
        validator=lambda x: 0 <= x <= 100,  # Must be 0-100
        description="Percentage value",
    ),
    "port": Parameter(
        name="port",
        type=int,
        validator=lambda x: 1024 <= x <= 65535,  # Valid port range
        description="Network port",
    ),
}
```

## Parameter Validation

Parameters are validated when nodes are added to the workflow:

```python
workflow = Workflow("Example")

# Validation happens here, not at runtime
try:
    workflow.add_node("test", "my_node", {
        "invalid_param": "bad_value"
    })
except ValueError as e:
    print(f"Validation failed: {e}")
```

This provides **early error detection** before workflow execution.

## Type Coercion

Parameters support automatic type coercion:

```python
parameters = {
    "value": Parameter(name="value", type=float, default=1.0),
}

# Integer is automatically coerced to float
workflow.add_node("node1", "my_node", {"value": 42})  # OK, becomes 42.0

# String conversion works where appropriate
parameters = {
    "text": Parameter(name="text", type=str),
}
workflow.add_node("node2", "my_node", {"text": 123})  # OK, becomes "123"
```

## Built-in Node Parameters

### GenerateTextNode

```python
workflow.add_node("gen", "generate_text", {
    "model": "gpt-4",                  # Model name (optional)
    "temperature": 0.7,                # 0.0-2.0 (default: 0.7)
    "max_tokens": 500,                 # Max tokens (optional)
    "top_p": 0.9,                      # Nucleus sampling (optional)
    "frequency_penalty": 0.5,          # -2.0 to 2.0 (optional)
    "presence_penalty": 0.5,           # -2.0 to 2.0 (optional)
})
```

### EmbedTextNode

```python
workflow.add_node("embed", "embed_text", {
    "model": "text-embedding-ada-002", # Embedding model (optional)
    "dimensions": 1536,                # Embedding dimensions (optional)
})
```

### TemplateNode

```python
workflow.add_node("template", "template", {
    "template": "Hello, {name}!",      # Template string (required)
    "strict": True,                     # Fail on missing variables (default: True)
})
```

### TransformNode

```python
workflow.add_node("transform", "transform", {
    "transform": "upper",  # One of: identity, upper, lower, strip,
                           #         length, str, int, float (default: identity)
})
```

### MergeNode

```python
workflow.add_node("merge", "merge", {
    "mode": "list",      # "dict" or "list" (default: "dict")
    "max_inputs": 20,    # Max inputs to collect (default: 10)
})
```

## Best Practices

1. **Use Required Parameters** for essential configuration that has no sensible default
2. **Provide Defaults** for optional parameters to make nodes easy to use
3. **Add Descriptions** to help users understand what parameters do
4. **Use Validators** for complex validation logic beyond type checking
5. **Use Choices** for enum-like parameters to prevent typos
6. **Validate Early** - parameters are checked at workflow construction time

## Advanced: ParameterSpec

For complex scenarios, you can use `ParameterSpec` directly:

```python
from openworkflows.parameters import Parameter, ParameterSpec

class MyNode(Node):
    def __init__(self, config=None):
        # Create custom parameter spec
        param_spec = ParameterSpec({
            "mode": Parameter(name="mode", type=str, default="fast"),
            "quality": Parameter(name="quality", type=int, default=80),
        })

        # Validate and set defaults
        validated_config = param_spec.validate_and_set_defaults(config or {})

        # Call parent with validated config
        super().__init__(validated_config)
```

## Migration from Config Dict

Old approach (using raw config dict):

```python
class OldNode(Node):
    async def execute(self, ctx):
        timeout = self.config.get("timeout", 30)  # No validation
        return {"result": "done"}
```

New approach (using parameters):

```python
class NewNode(Node):
    parameters = {
        "timeout": Parameter(
            name="timeout",
            type=int,
            default=30,
            validator=lambda x: x > 0,
        ),
    }

    async def execute(self, ctx):
        timeout = self.param("timeout")  # Validated!
        return {"result": "done"}
```

Benefits:
- ✅ Type safety
- ✅ Validation at workflow construction time
- ✅ Clear documentation of what parameters are supported
- ✅ Better error messages
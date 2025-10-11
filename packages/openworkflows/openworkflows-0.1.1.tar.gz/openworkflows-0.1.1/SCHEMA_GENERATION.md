# Node Schema Generation for Frontend Integration

## Overview

OpenWorkflows provides automatic schema generation to support visual workflow editors and frontends. The schema system introspects registered nodes and generates JSON schemas describing their inputs, outputs, and parameters with appropriate UI component mappings.

## Quick Start

```python
from openworkflows import get_node_schema, get_all_node_schemas

# Get schema for a specific node
schema = get_node_schema("transform")

# Get all registered node schemas
all_schemas = get_all_node_schemas()

# Export to JSON for frontend
import json
with open("node_schemas.json", "w") as f:
    json.dump(all_schemas, f, indent=2)
```

## Type to UI Component Mapping

| Python Type | UI Component | Schema Output |
|------------|--------------|---------------|
| `str` | Text input | `{"component": "text"}` |
| `int` | Number input (integer) | `{"component": "number", "inputType": "integer"}` |
| `float` | Number input (float) | `{"component": "number", "inputType": "float"}` |
| `bool` | Checkbox | `{"component": "checkbox"}` |
| `dict` / `Dict[str, Any]` | JSON editor | `{"component": "json"}` |
| `list` / `List[T]` | JSON array editor | `{"component": "json"}` |
| `Literal["a", "b", "c"]` | Dropdown | `{"component": "dropdown", "options": ["a", "b", "c"]}` |
| `Optional[T]` | Same as T + optional flag | `{"component": "text", "optional": true}` |
| `Any` | Text input with note | `{"component": "text", "description": "Any type"}` |

## Schema Structure

Each node schema includes:

```typescript
{
  type: string;              // Node type identifier (e.g., "transform")
  name: string;              // Display name (e.g., "Transform")
  description: string;       // Node description from docstring
  inputs: Array<{            // Input handles
    name: string;            // Handle name
    type: string;            // Python type as string
    component: string;       // UI component type
    optional?: boolean;      // If Optional type
    description?: string;    // Additional info
  }>;
  outputs: Array<{           // Output handles
    name: string;            // Handle name
    type: string;            // Python type as string
  }>;
  parameters: Array<{        // Configuration parameters
    name: string;            // Parameter name
    type: string;            // Python type as string
    component: string;       // UI component type
    default: any;            // Default value
    required: boolean;       // Is required
    description: string;     // Parameter description
    options?: any[];         // For dropdown/choices
    optional?: boolean;      // If Optional type
  }>;
}
```

## Example Schemas

### Transform Node

```json
{
  "type": "transform",
  "name": "Transform",
  "description": "Node that applies a transformation function to input.",
  "inputs": [
    {
      "name": "input",
      "type": "typing.Any",
      "component": "text",
      "description": "Any type"
    }
  ],
  "outputs": [
    {
      "name": "output",
      "type": "typing.Any"
    }
  ],
  "parameters": [
    {
      "name": "transform",
      "type": "<class 'str'>",
      "component": "dropdown",
      "options": ["identity", "upper", "lower", "strip", "length", "str", "int", "float"],
      "default": "identity",
      "required": false,
      "description": "Transformation to apply"
    }
  ]
}
```

### HTTP Request Node

```json
{
  "type": "http_request",
  "name": "Http Request",
  "description": "Node that makes HTTP requests with templated URL and body.",
  "inputs": [
    {
      "name": "variables",
      "type": "typing.Optional[typing.Dict[str, typing.Any]]",
      "component": "json",
      "description": "JSON object",
      "optional": true
    }
  ],
  "outputs": [
    {
      "name": "response",
      "type": "typing.Dict[str, typing.Any]"
    },
    {
      "name": "status_code",
      "type": "<class 'int'>"
    },
    {
      "name": "body",
      "type": "typing.Any"
    },
    {
      "name": "headers",
      "type": "typing.Dict[str, str]"
    }
  ],
  "parameters": [
    {
      "name": "method",
      "type": "<class 'str'>",
      "component": "dropdown",
      "options": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
      "default": null,
      "required": true,
      "description": "HTTP method"
    },
    {
      "name": "url_template",
      "type": "<class 'str'>",
      "component": "text",
      "default": null,
      "required": true,
      "description": "URL template with {variable} placeholders"
    },
    {
      "name": "timeout",
      "type": "<class 'int'>",
      "component": "number",
      "inputType": "integer",
      "default": 30,
      "required": false,
      "description": "Request timeout in seconds"
    }
  ]
}
```

## Frontend Integration

### React/TypeScript Example

```typescript
import { useEffect, useState } from 'react';

interface NodeSchema {
  type: string;
  name: string;
  description: string;
  inputs: Array<{
    name: string;
    type: string;
    component: string;
    optional?: boolean;
  }>;
  outputs: Array<{
    name: string;
    type: string;
  }>;
  parameters: Array<{
    name: string;
    component: string;
    default: any;
    required: boolean;
    description: string;
    options?: any[];
  }>;
}

function NodeConfigForm({ nodeType }: { nodeType: string }) {
  const [schema, setSchema] = useState<NodeSchema | null>(null);

  useEffect(() => {
    // Fetch schema from backend
    fetch(`/api/nodes/${nodeType}/schema`)
      .then(r => r.json())
      .then(setSchema);
  }, [nodeType]);

  if (!schema) return <div>Loading...</div>;

  return (
    <form>
      <h3>{schema.name}</h3>
      <p>{schema.description}</p>

      {schema.parameters.map(param => (
        <div key={param.name}>
          <label>{param.name}</label>
          {param.component === 'dropdown' && (
            <select defaultValue={param.default}>
              {param.options?.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          )}
          {param.component === 'text' && (
            <input type="text" defaultValue={param.default} />
          )}
          {param.component === 'number' && (
            <input type="number" defaultValue={param.default} />
          )}
          {param.component === 'checkbox' && (
            <input type="checkbox" defaultChecked={param.default} />
          )}
          {param.component === 'json' && (
            <textarea defaultValue={JSON.stringify(param.default, null, 2)} />
          )}
          <small>{param.description}</small>
        </div>
      ))}
    </form>
  );
}
```

### Backend API Example (FastAPI)

```python
from fastapi import FastAPI
from openworkflows import get_node_schema, get_all_node_schemas

app = FastAPI()

@app.get("/api/nodes")
async def list_node_schemas():
    """Get all registered node schemas."""
    return get_all_node_schemas()

@app.get("/api/nodes/{node_type}/schema")
async def get_node_type_schema(node_type: str):
    """Get schema for a specific node type."""
    try:
        return get_node_schema(node_type)
    except ValueError:
        return {"error": f"Node type '{node_type}' not found"}, 404
```

## Custom Node Schemas

Custom nodes automatically get schemas:

```python
from openworkflows import Node, register_node
from openworkflows.parameters import Parameter
from typing import Literal

@register_node("my_custom_node")
class MyCustomNode(Node):
    """My custom processing node."""

    inputs = {"data": str, "format": Optional[str]}
    outputs = {"result": str}
    parameters = {
        "mode": Parameter(
            name="mode",
            type=str,
            default="process",
            choices=["process", "transform", "validate"],
            description="Processing mode"
        ),
        "threshold": Parameter(
            name="threshold",
            type=float,
            default=0.5,
            description="Threshold value"
        ),
        "count": Parameter(
            name="count",
            type=Literal[1, 5, 10, 20],
            default=5,
            description="Item count"
        )
    }

    async def execute(self, ctx):
        # Implementation
        pass

# Schema is automatically available
schema = get_node_schema("my_custom_node")
# {
#   "parameters": [
#     {"name": "mode", "component": "dropdown", "options": ["process", "transform", "validate"]},
#     {"name": "threshold", "component": "number", "inputType": "float"},
#     {"name": "count", "component": "dropdown", "options": [1, 5, 10, 20]}
#   ]
# }
```

## Known Limitations

1. **Dynamic Inputs**: Nodes with dynamic inputs (like `MergeNode`) don't have explicit input definitions in their schema. Frontend should handle these as special cases.

2. **Complex Generic Types**: Some complex generic types may not be fully introspected. The system falls back to text input with type description.

3. **Validator Functions**: Custom validator functions are detected but not exposed in the schema. Validation happens server-side.

## Testing

Comprehensive tests are available in `tests/test_schema.py`:

```bash
uv run pytest tests/test_schema.py -v
```

Tests cover:
- Type to UI component mapping
- Built-in node schemas
- Custom node schemas
- Schema structure validation
- Edge cases (Optional, Literal, Dict, List, etc.)

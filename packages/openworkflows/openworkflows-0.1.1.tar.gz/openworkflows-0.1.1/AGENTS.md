# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenWorkflows is a node-based DAG workflow engine for building AI pipelines. It uses async Python and provides a type-safe, declarative API for connecting nodes into complex workflows.

## Development Commands

This project uses `uv` for package management.

### Setup
```bash
uv sync                    # Install all dependencies
```

### Testing
```bash
uv run pytest tests/                           # Run all tests
uv run pytest tests/test_nonlinear_workflows.py -v  # Run specific test file
uv run pytest tests/ -k "test_diamond_pattern" -v   # Run specific test by name
uv run pytest tests/ --tb=short                     # Show short tracebacks
```

### Code Quality
```bash
uv run black openworkflows tests     # Format code
uv run ruff check openworkflows      # Lint code
uv run mypy openworkflows            # Type check
```

### Running Examples
```bash
uv run python examples/basic_workflow.py
uv run python examples/llm_workflow.py
uv run python examples/custom_node.py
```

## Core Architecture

### Workflow Execution Model

OpenWorkflows uses a **DAG-based execution engine** with topological sorting:

1. **Workflow** (`openworkflows/workflow.py`): Orchestrator that builds execution order via DFS-based topological sort, then executes nodes sequentially in dependency order
2. **Node** (`openworkflows/node.py`): Base class for computation units with typed inputs/outputs. Nodes can be created via class inheritance or the `@node` decorator
3. **Registry** (`openworkflows/registry.py`): Global registry mapping node type names to node classes/factories
4. **Context** (`openworkflows/context.py`): Execution context passed to each node containing input resolver, node results, workflow inputs, metadata, services, and LLM provider

### Handle-Based I/O System

Nodes communicate through **named handles** (not just generic "input"/"output"):

- Each node defines `inputs = {"handle_name": Type}` and `outputs = {"handle_name": Type}`
- Edges connect specific handles: `workflow.connect("source_node.output_handle", "target_node.input_handle")`
- The workflow's `_resolve_input()` method finds edges targeting a specific handle and extracts values from source node results
- Type validation in `openworkflows/handles.py` supports int/float coercion and Optional types

### Node Resolution Strategy

When a node requests input via `ctx.input("handle_name")`:

1. Workflow finds edges where `edge.target == node_id` and `edge.target_handle == handle_name`
2. Takes first matching edge (first-edge-wins for duplicate connections)
3. Looks up source node in `node_results` dict
4. Extracts value from `source_result[edge.source_handle]` or falls back to `source_result["result"]`

### Key Design Patterns

**Fan-out (1-to-many)**: One node output can connect to multiple downstream nodes via multiple edges from same source handle

**Fan-in (many-to-1)**: Multiple nodes can feed one node via edges to different target handles (e.g., `merge_sum` node has `input1`, `input2`, `input3` handles)

**Conditional Routing**: Nodes like `ConditionalNode` output to multiple handles (`high`, `low`, `result`) where downstream nodes only receive values on the taken path

## Creating Custom Nodes

### Method 1: Class-based (for complex nodes)
```python
from openworkflows import Node, ExecutionContext, register_node

@register_node("my_node")
class MyNode(Node):
    inputs = {"text": str, "count": int}
    outputs = {"result": str}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        text = ctx.input("text")
        count = ctx.input("count", 1)  # with default
        return {"result": text * count}
```

### Method 2: Function-based (for simple nodes)
```python
from openworkflows import node, register_node

@node(inputs={"x": int, "y": int}, outputs={"sum": int})
async def add(ctx: ExecutionContext) -> int:
    return ctx.input("x") + ctx.input("y")

register_node("add")(add)
```

## Test Architecture

Tests are organized by workflow pattern (29 tests total):

- `test_nonlinear_workflows.py`: Diamond patterns, complex branching, parallel paths
- `test_one_to_many.py`: Fan-out patterns (1 source → N consumers)
- `test_many_to_one.py`: Fan-in patterns (N sources → 1 aggregator)
- `test_conditional_routing.py`: Runtime path selection based on values
- `test_complex_dags.py`: Real-world patterns (ETL, scatter-gather, layered pipelines)

Test fixtures in `conftest.py` define helper nodes (AddNode, MultiplyNode, ConditionalNode, etc.).

## Important Implementation Details

### Topological Sort
`Workflow._build_execution_order()` uses DFS to detect circular dependencies and build execution order. All nodes in the workflow are visited even if disconnected (independent subgraphs execute in arbitrary order relative to each other).

### Node Instantiation
Nodes are instantiated **per workflow run** in `Workflow.run()`. Each execution creates fresh node instances from the registry, allowing stateless execution.

### Type Validation
`handles.py` validates types but allows numeric coercion (int→float). Validation happens in `Node.run()` wrapper before calling `Node.execute()`.

### Input Resolution Closure
The workflow creates a closure `make_resolver(node_id)` for each node to capture the correct node_id, preventing late-binding issues in the input resolution function.

## Built-in Node Types

Registered in `openworkflows/__init__.py`:
- `input`: Reads from workflow inputs dict
- `output`: Pass-through for collecting outputs
- `template`: String formatting with `{variable}` placeholders
- `transform`: Built-in transformations (upper, lower, strip, length, type conversions)
- `merge`: Combines multiple inputs into dict/list
- `generate_text`: LLM text generation (requires `workflow.set_llm_provider()`)
- `embed_text`: Generate embeddings (requires LLM provider)

## Common Pitfalls

1. **Forgetting to register nodes**: Custom nodes must be registered via `register_node("name")` decorator or explicit `_global_registry.register()` call
2. **Handle name mismatches**: Edge connections must use exact handle names from node's `inputs`/`outputs` dicts
3. **Circular dependencies**: Workflow will raise exception during topological sort if edges form a cycle
4. **Type validation errors**: Remember int/float are interchangeable, but other types must match exactly (or use `Any` type)
5. **Node state**: Nodes are instantiated per-run, so instance variables reset each execution (use `ctx.services` for persistent state)

## Extension Points

- **Custom LLM Providers**: Subclass `LLMProvider` (base class in `openworkflows/providers/base.py`) and implement `generate()`, `stream()`, `embed()`
- **Custom Services**: Inject via `workflow.add_service("name", service)` and access with `ctx.service("name")` in nodes
- **Metadata**: Pass per-execution metadata via `workflow.run(metadata={...})` for tracing, user IDs, etc.

## Package Structure

```
openworkflows/
├── __init__.py          # Public API, built-in node registration
├── workflow.py          # Workflow orchestration, topological sort
├── node.py              # Base Node class, @node decorator, FunctionNode
├── registry.py          # Global node registry
├── context.py           # ExecutionContext
├── handles.py           # Handle type validation
├── nodes/               # Built-in node implementations
│   ├── input.py
│   ├── output.py
│   ├── transform.py
│   └── llm.py
└── providers/           # LLM provider abstractions
    ├── base.py
    └── mock.py
```
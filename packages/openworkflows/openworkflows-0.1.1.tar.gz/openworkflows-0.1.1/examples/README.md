# OpenWorkflows Examples

This directory contains example workflows demonstrating various features of OpenWorkflows.

## Examples

### 1. Basic Workflow (`basic_workflow.py`)

A simple workflow that demonstrates:
- Creating a workflow
- Adding nodes (input, transform, output)
- Connecting nodes
- Running the workflow

```bash
python examples/basic_workflow.py
```

### 2. LLM Workflow (`llm_workflow.py`)

An LLM-based workflow that demonstrates:
- Using template nodes for prompt engineering
- Text generation with LLM nodes
- Working with mock LLM providers

```bash
python examples/llm_workflow.py
```

### 3. Custom Nodes (`custom_node.py`)

Creating custom nodes using different approaches:
- Using the `@node` decorator for simple functions
- Creating `Node` subclasses for complex logic
- Configurable nodes with parameters

```bash
python examples/custom_node.py
```

## Running Examples

Make sure you have OpenWorkflows installed:

```bash
uv pip install -e .
```

Then run any example:

```bash
python examples/basic_workflow.py
```

## Creating Your Own Workflows

Use these examples as templates for your own workflows. Key patterns:

1. **Simple transformations**: Use built-in transform nodes
2. **LLM operations**: Use template + generate_text nodes
3. **Complex logic**: Create custom nodes with the `@node` decorator or `Node` class
4. **Error handling**: Wrap workflow execution in try-except blocks
5. **Services**: Inject databases, caches, or other services via `workflow.add_service()`
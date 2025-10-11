"""Test wildcard input matching functionality."""

import pytest
from typing import Dict, Any, Optional

from openworkflows import Workflow, Node, ExecutionContext, register_node


@register_node("wildcard_test_node")
class WildcardTestNode(Node):
    """Test node that accepts any input via wildcard."""

    inputs = {"*": Optional[str]}  # Accept any input name
    outputs = {"result": dict}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Collect all inputs."""
        all_inputs = ctx.all_inputs()
        connected = ctx.list_connected_inputs()

        return {
            "result": {
                "inputs": all_inputs,
                "connected_handles": connected,
                "count": len(all_inputs),
            }
        }


@register_node("wildcard_any_type")
class WildcardAnyTypeNode(Node):
    """Test node that accepts any input with any type."""

    inputs = {"*": Any}  # Accept any input name, any type
    outputs = {"result": dict}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Collect all inputs."""
        return {"result": ctx.all_inputs()}


@register_node("mixed_handles")
class MixedHandlesNode(Node):
    """Test node with both named and wildcard inputs."""

    inputs = {
        "required_input": str,  # Named required input
        "*": Optional[int],  # Wildcard for additional inputs
    }
    outputs = {"result": dict}

    async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
        """Collect all inputs."""
        return {"result": ctx.all_inputs()}


@pytest.mark.asyncio
async def test_template_node_with_wildcard_inputs():
    """Test TemplateNode using wildcard inputs."""
    workflow = Workflow("Template Wildcard Test")

    # Add input nodes
    workflow.add_node("name_input", "input", {"name": "name"})
    workflow.add_node("age_input", "input", {"name": "age"})

    # Add template node
    workflow.add_node(
        "template",
        "template",
        {"template": "Hello {name}, you are {age} years old!"},
    )

    # Connect to template with specific handle names
    workflow.connect("name_input.value", "template.name")
    workflow.connect("age_input.value", "template.age")

    # Run workflow
    result = await workflow.run(inputs={"name": "Alice", "age": 30})

    assert result["template"]["text"] == "Hello Alice, you are 30 years old!"


@pytest.mark.asyncio
async def test_merge_node_with_wildcard_inputs():
    """Test MergeNode using wildcard inputs."""
    workflow = Workflow("Merge Wildcard Test")

    # Add input nodes
    workflow.add_node("input1", "input", {"name": "val1"})
    workflow.add_node("input2", "input", {"name": "val2"})
    workflow.add_node("input3", "input", {"name": "val3"})

    # Add merge node
    workflow.add_node("merge", "merge", {"mode": "dict"})

    # Connect with different handle names
    workflow.connect("input1.value", "merge.first")
    workflow.connect("input2.value", "merge.second")
    workflow.connect("input3.value", "merge.third")

    # Run workflow
    result = await workflow.run(inputs={"val1": "A", "val2": "B", "val3": "C"})

    assert result["merge"]["result"] == {"first": "A", "second": "B", "third": "C"}


@pytest.mark.asyncio
async def test_merge_node_list_mode():
    """Test MergeNode in list mode."""
    workflow = Workflow("Merge List Test")

    # Add input nodes
    workflow.add_node("input1", "input", {"name": "val1"})
    workflow.add_node("input2", "input", {"name": "val2"})

    # Add merge node in list mode
    workflow.add_node("merge", "merge", {"mode": "list"})

    # Connect
    workflow.connect("input1.value", "merge.x")
    workflow.connect("input2.value", "merge.y")

    # Run workflow
    result = await workflow.run(inputs={"val1": 10, "val2": 20})

    # Result should be a list (order may vary based on dict ordering)
    assert set(result["merge"]["result"]) == {10, 20}


@pytest.mark.asyncio
async def test_wildcard_with_custom_node():
    """Test custom node with wildcard inputs."""
    workflow = Workflow("Custom Wildcard Test")

    # Add input nodes
    workflow.add_node("source1", "input", {"name": "text1"})
    workflow.add_node("source2", "input", {"name": "text2"})
    workflow.add_node("source3", "input", {"name": "text3"})

    # Add custom wildcard node
    workflow.add_node("collector", "wildcard_test_node")

    # Connect with arbitrary handle names
    workflow.connect("source1.value", "collector.alpha")
    workflow.connect("source2.value", "collector.beta")
    workflow.connect("source3.value", "collector.gamma")

    # Run workflow
    result = await workflow.run(inputs={"text1": "A", "text2": "B", "text3": "C"})

    collector_result = result["collector"]["result"]
    assert collector_result["count"] == 3
    assert set(collector_result["connected_handles"]) == {"alpha", "beta", "gamma"}
    assert collector_result["inputs"] == {"alpha": "A", "beta": "B", "gamma": "C"}


@pytest.mark.asyncio
async def test_wildcard_any_type():
    """Test wildcard with Any type accepts different types."""
    workflow = Workflow("Wildcard Any Type Test")

    # Add input nodes with different types
    workflow.add_node("str_input", "input", {"name": "str_val"})
    workflow.add_node("int_input", "input", {"name": "int_val"})

    # Add wildcard node that accepts Any
    workflow.add_node("collector", "wildcard_any_type")

    # Connect
    workflow.connect("str_input.value", "collector.text")
    workflow.connect("int_input.value", "collector.number")

    # Run workflow
    result = await workflow.run(inputs={"str_val": "hello", "int_val": 42})

    assert result["collector"]["result"] == {"text": "hello", "number": 42}


@pytest.mark.asyncio
async def test_mixed_named_and_wildcard_handles():
    """Test node with both named and wildcard handles."""
    workflow = Workflow("Mixed Handles Test")

    # Add input nodes
    workflow.add_node("required", "input", {"name": "req"})
    workflow.add_node("extra1", "input", {"name": "ex1"})
    workflow.add_node("extra2", "input", {"name": "ex2"})

    # Add mixed handles node
    workflow.add_node("mixed", "mixed_handles")

    # Connect required input and wildcard inputs
    workflow.connect("required.value", "mixed.required_input")
    workflow.connect("extra1.value", "mixed.optional1")
    workflow.connect("extra2.value", "mixed.optional2")

    # Run workflow
    result = await workflow.run(inputs={"req": "required_value", "ex1": 10, "ex2": 20})

    assert result["mixed"]["result"] == {
        "required_input": "required_value",
        "optional1": 10,
        "optional2": 20,
    }


@pytest.mark.asyncio
async def test_wildcard_with_no_connections():
    """Test wildcard node with no connected inputs."""
    workflow = Workflow("No Connections Test")

    # Add wildcard node with no connections
    workflow.add_node("collector", "wildcard_test_node")

    # Run workflow
    result = await workflow.run(inputs={})

    collector_result = result["collector"]["result"]
    assert collector_result["count"] == 0
    assert collector_result["connected_handles"] == []
    assert collector_result["inputs"] == {}


@pytest.mark.asyncio
async def test_template_fallback_to_workflow_inputs():
    """Test TemplateNode falls back to workflow inputs when no connections."""
    workflow = Workflow("Template Fallback Test")

    # Add template node with NO connections
    workflow.add_node(
        "template",
        "template",
        {"template": "Name: {name}, Age: {age}"},
    )

    # Run workflow with inputs (should use workflow_inputs)
    result = await workflow.run(inputs={"name": "Bob", "age": 25})

    assert result["template"]["text"] == "Name: Bob, Age: 25"


@pytest.mark.asyncio
async def test_wildcard_type_validation():
    """Test that wildcard inputs validate types correctly."""
    workflow = Workflow("Wildcard Type Validation Test")

    # Create a node that outputs a string
    workflow.add_node("source", "input", {"name": "value"})

    # Connect to wildcard node expecting Optional[str]
    workflow.add_node("collector", "wildcard_test_node")
    workflow.connect("source.value", "collector.input1")

    # Should succeed with string input
    result = await workflow.run(inputs={"value": "test_string"})
    assert result["collector"]["result"]["inputs"]["input1"] == "test_string"


@pytest.mark.asyncio
async def test_list_connected_inputs_with_wildcard():
    """Test list_connected_inputs() works with wildcard nodes."""
    workflow = Workflow("List Connected Test")

    # Add sources
    workflow.add_node("s1", "input", {"name": "v1"})
    workflow.add_node("s2", "input", {"name": "v2"})

    # Add wildcard node
    workflow.add_node("collector", "wildcard_test_node")

    # Connect with specific names
    workflow.connect("s1.value", "collector.handle_a")
    workflow.connect("s2.value", "collector.handle_b")

    # Run workflow
    result = await workflow.run(inputs={"v1": "A", "v2": "B"})

    connected = result["collector"]["result"]["connected_handles"]
    assert set(connected) == {"handle_a", "handle_b"}

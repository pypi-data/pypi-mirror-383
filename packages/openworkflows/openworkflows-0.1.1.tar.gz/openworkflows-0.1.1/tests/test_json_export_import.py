"""Tests for workflow JSON export and import functionality."""

import pytest
import json
from openworkflows import Workflow


@pytest.mark.asyncio
async def test_export_to_json():
    """Test exporting workflow to JSON string."""
    workflow = Workflow("Test Workflow")
    workflow.add_node("input1", "input", {"name": "x"})
    workflow.add_node("output1", "output")
    workflow.connect("input1.value", "output1.value")

    json_str = workflow.to_json()

    # Verify it's valid JSON
    data = json.loads(json_str)
    assert data["name"] == "Test Workflow"
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1


@pytest.mark.asyncio
async def test_import_from_json():
    """Test importing workflow from JSON string."""
    json_data = {
        "name": "Imported Workflow",
        "nodes": [
            {"id": "node1", "type": "input", "config": {"name": "value"}},
            {"id": "node2", "type": "output", "config": {}},
        ],
        "edges": [
            {
                "source": "node1",
                "target": "node2",
                "source_handle": "value",
                "target_handle": "value",
            }
        ],
    }

    json_str = json.dumps(json_data)
    workflow = Workflow.from_json(json_str)

    assert workflow.name == "Imported Workflow"
    assert len(workflow._nodes) == 2
    assert len(workflow._edges) == 1


@pytest.mark.asyncio
async def test_roundtrip_export_import():
    """Test that export->import preserves workflow functionality."""
    # Create original workflow
    original = Workflow("Math Pipeline")
    original.add_node("x", "input", {"name": "x"})
    original.add_node("y", "input", {"name": "y"})
    original.add_node("adder", "add", {})
    original.add_node("result", "output")

    original.connect("x.value", "adder.a")
    original.connect("y.value", "adder.b")
    original.connect("adder.result", "result.value")

    # Run original
    result1 = await original.run(inputs={"x": 5, "y": 10})

    # Export and import
    json_str = original.to_json()
    imported = Workflow.from_json(json_str)

    # Run imported
    result2 = await imported.run(inputs={"x": 5, "y": 10})

    # Verify same results
    assert result1["result"]["result"] == result2["result"]["result"]


@pytest.mark.asyncio
async def test_export_complex_workflow():
    """Test exporting a complex workflow with multiple nodes and edges."""
    workflow = Workflow("Complex Workflow")

    # Create diamond pattern
    workflow.add_node("input", "input", {"name": "value"})
    workflow.add_node("branch1", "add", {})
    workflow.add_node("branch2", "multiply", {})
    workflow.add_node("merge", "add", {})
    workflow.add_node("output", "output")

    workflow.connect("input.value", "branch1.a")
    workflow.connect("input.value", "branch2.a")
    workflow.connect("branch1.result", "merge.a")
    workflow.connect("branch2.result", "merge.b")
    workflow.connect("merge.result", "output.value")

    json_str = workflow.to_json()
    data = json.loads(json_str)

    assert len(data["nodes"]) == 5
    assert len(data["edges"]) == 5


@pytest.mark.asyncio
async def test_import_with_node_config():
    """Test importing workflow with node configurations."""
    json_data = {
        "name": "Config Test",
        "nodes": [
            {"id": "input1", "type": "input", "config": {"name": "x", "default": 10}},
            {"id": "transform1", "type": "transform", "config": {"operation": "upper"}},
            {"id": "output1", "type": "output", "config": {}},
        ],
        "edges": [
            {
                "source": "input1",
                "target": "transform1",
                "source_handle": "value",
                "target_handle": "input",
            },
            {
                "source": "transform1",
                "target": "output1",
                "source_handle": "result",
                "target_handle": "value",
            },
        ],
    }

    workflow = Workflow.from_json(json.dumps(json_data))
    assert workflow._nodes["input1"].config["name"] == "x"
    assert workflow._nodes["input1"].config["default"] == 10
    assert workflow._nodes["transform1"].config["operation"] == "upper"


@pytest.mark.asyncio
async def test_import_invalid_json():
    """Test that invalid JSON raises appropriate error."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        Workflow.from_json("not valid json")


@pytest.mark.asyncio
async def test_import_missing_required_fields():
    """Test that missing required fields raise appropriate errors."""
    # Missing node type
    json_data = {"name": "Test", "nodes": [{"id": "node1", "config": {}}], "edges": []}

    with pytest.raises(ValueError, match="missing 'id' or 'type'"):
        Workflow.from_json(json.dumps(json_data))

    # Missing edge source
    json_data = {
        "name": "Test",
        "nodes": [{"id": "n1", "type": "input", "config": {}}],
        "edges": [{"target": "n1", "source_handle": "result"}],
    }

    with pytest.raises(ValueError, match="missing 'source' or 'target'"):
        Workflow.from_json(json.dumps(json_data))


@pytest.mark.asyncio
async def test_export_compact_json():
    """Test exporting workflow with compact JSON (no indentation)."""
    workflow = Workflow("Compact Test")
    workflow.add_node("n1", "input", {"name": "x"})

    json_str = workflow.to_json(indent=None)

    # Verify no newlines in compact format
    assert "\n" not in json_str
    # Verify it's still valid
    data = json.loads(json_str)
    assert data["name"] == "Compact Test"


@pytest.mark.asyncio
async def test_import_preserves_edge_handles():
    """Test that custom handle names are preserved during import."""
    workflow = Workflow("Handle Test")
    workflow.add_node("source", "input", {"name": "data"})
    workflow.add_node("target", "output")
    workflow.connect("source.value", "target.value")

    # Export and import
    json_str = workflow.to_json()
    imported = Workflow.from_json(json_str)

    # Check edge handles preserved
    assert len(imported._edges) == 1
    edge = imported._edges[0]
    assert edge.source == "source"
    assert edge.target == "target"
    assert edge.source_handle == "value"
    assert edge.target_handle == "value"


@pytest.mark.asyncio
async def test_import_empty_workflow():
    """Test importing a minimal empty workflow."""
    json_data = {"name": "Empty", "nodes": [], "edges": []}

    workflow = Workflow.from_json(json.dumps(json_data))

    assert workflow.name == "Empty"
    assert len(workflow._nodes) == 0
    assert len(workflow._edges) == 0


@pytest.mark.asyncio
async def test_roundtrip_with_template_node():
    """Test export/import with template nodes."""
    workflow = Workflow("Template Test")
    workflow.add_node("name_input", "input", {"name": "name"})
    workflow.add_node("template", "template", {"template": "Hello, {name}!"})
    workflow.add_node("output", "output")

    workflow.connect("name_input.value", "template.name")
    workflow.connect("template.text", "output.value")

    # Export and import
    json_str = workflow.to_json()
    imported = Workflow.from_json(json_str)

    # Run both
    result1 = await workflow.run(inputs={"name": "World"})
    result2 = await imported.run(inputs={"name": "World"})

    assert result1["output"]["result"] == result2["output"]["result"]


@pytest.mark.asyncio
async def test_complex_workflow_with_parameters():
    """Test export/import with complex workflows and nodes with parameters."""
    # Create a complex workflow with multiple node types and parameters
    workflow = Workflow("Complex Parameter Test")

    # Add input node
    workflow.add_node("text_input", "input", {"name": "text", "default": "hello world"})

    # Add template node with parameters - use workflow inputs instead of connecting
    workflow.add_node(
        "template1",
        "template",
        {"template": "The text is: {text}", "strict": False},
    )

    # Add transform nodes with different operations
    workflow.add_node("upper_transform", "transform", {"transform": "upper"})
    workflow.add_node("length_transform", "transform", {"transform": "length"})

    # Add merge node with parameters
    workflow.add_node("merge", "merge", {"mode": "dict", "max_inputs": 5})

    # Add output nodes
    workflow.add_node("text_output", "output")
    workflow.add_node("length_output", "output")

    # Connect nodes - template reads from workflow inputs
    workflow.connect("template1.text", "upper_transform.input")
    workflow.connect("upper_transform.output", "text_output.value")
    workflow.connect("upper_transform.output", "length_transform.input")
    workflow.connect("length_transform.output", "length_output.value")

    # Export to JSON
    json_str = workflow.to_json()

    # Verify JSON structure
    data = json.loads(json_str)
    assert data["name"] == "Complex Parameter Test"
    assert len(data["nodes"]) == 7  # 1 input + 1 template + 2 transforms + 1 merge + 2 outputs

    # Verify parameter preservation in JSON
    template_node = next(n for n in data["nodes"] if n["id"] == "template1")
    assert template_node["config"]["template"] == "The text is: {text}"
    assert template_node["config"]["strict"] is False

    transform_node = next(n for n in data["nodes"] if n["id"] == "upper_transform")
    assert transform_node["config"]["transform"] == "upper"

    merge_node = next(n for n in data["nodes"] if n["id"] == "merge")
    assert merge_node["config"]["mode"] == "dict"
    assert merge_node["config"]["max_inputs"] == 5

    # Import from JSON
    imported = Workflow.from_json(json_str)

    # Run both workflows
    inputs = {"text": "hello world"}
    result1 = await workflow.run(inputs=inputs)
    result2 = await imported.run(inputs=inputs)

    # Verify results match
    assert result1["text_output"]["result"] == result2["text_output"]["result"]
    assert result1["length_output"]["result"] == result2["length_output"]["result"]
    assert result2["text_output"]["result"] == "THE TEXT IS: HELLO WORLD"


@pytest.mark.asyncio
async def test_generate_text_node_export_import():
    """Test export/import with GenerateTextNode with parameters."""
    workflow = Workflow("LLM Workflow")

    # Add nodes with LLM parameters
    workflow.add_node("prompt_input", "input", {"name": "prompt"})
    workflow.add_node(
        "generate",
        "generate_text",
        {"provider": "openrouter", "model": "anthropic/claude-3-haiku"},
    )
    workflow.add_node("output", "output")

    # Connect nodes
    workflow.connect("prompt_input.value", "generate.prompt")
    workflow.connect("generate.text", "output.value")

    # Export to JSON
    json_str = workflow.to_json()

    # Verify JSON contains LLM parameters
    data = json.loads(json_str)
    generate_node = next(n for n in data["nodes"] if n["id"] == "generate")
    assert generate_node["config"]["provider"] == "openrouter"
    assert generate_node["config"]["model"] == "anthropic/claude-3-haiku"

    # Import from JSON
    imported = Workflow.from_json(json_str)

    # Verify the imported workflow has correct configuration
    imported_node = imported._nodes["generate"]
    assert imported_node.config["provider"] == "openrouter"
    assert imported_node.config["model"] == "anthropic/claude-3-haiku"


@pytest.mark.asyncio
async def test_complex_branching_workflow_export():
    """Test export/import of a complex branching workflow with parameters."""
    workflow = Workflow("Complex Branching")

    # Create a diamond pattern with transforms
    workflow.add_node("input", "input", {"name": "text", "default": "test"})
    workflow.add_node("upper", "transform", {"transform": "upper"})
    workflow.add_node("lower", "transform", {"transform": "lower"})
    workflow.add_node("len_upper", "transform", {"transform": "length"})
    workflow.add_node("len_lower", "transform", {"transform": "length"})
    workflow.add_node("merge", "merge", {"mode": "dict", "max_inputs": 10})
    workflow.add_node("output", "output")

    # Connect in diamond pattern
    workflow.connect("input.value", "upper.input")
    workflow.connect("input.value", "lower.input")
    workflow.connect("upper.output", "len_upper.input")
    workflow.connect("lower.output", "len_lower.input")
    workflow.connect("len_upper.output", "merge.input1")
    workflow.connect("len_lower.output", "merge.input2")
    workflow.connect("merge.result", "output.value")

    # Export and import
    json_str = workflow.to_json()
    imported = Workflow.from_json(json_str)

    # Run both
    result1 = await workflow.run(inputs={"text": "Hello"})
    result2 = await imported.run(inputs={"text": "Hello"})

    # Both branches should produce length 5
    assert result1["output"]["result"] == result2["output"]["result"]


@pytest.mark.asyncio
async def test_multiple_parameters_preservation():
    """Test that all parameter types are preserved during export/import."""
    workflow = Workflow("Parameter Types")

    # Node with string parameter
    workflow.add_node("template", "template", {"template": "Test {var}", "strict": False})

    # Node with int parameter
    workflow.add_node("merge1", "merge", {"mode": "list", "max_inputs": 20})

    # Node with choice parameter
    workflow.add_node("transform1", "transform", {"transform": "strip"})

    # Export
    json_str = workflow.to_json()
    data = json.loads(json_str)

    # Verify each parameter type
    template_config = next(n for n in data["nodes"] if n["id"] == "template")["config"]
    assert template_config["template"] == "Test {var}"
    assert template_config["strict"] is False  # boolean

    merge_config = next(n for n in data["nodes"] if n["id"] == "merge1")["config"]
    assert merge_config["mode"] == "list"  # string choice
    assert merge_config["max_inputs"] == 20  # integer

    transform_config = next(n for n in data["nodes"] if n["id"] == "transform1")["config"]
    assert transform_config["transform"] == "strip"  # string from choices

    # Import and verify node configs match
    imported = Workflow.from_json(json_str)
    assert imported._nodes["template"].config == template_config
    assert imported._nodes["merge1"].config == merge_config
    assert imported._nodes["transform1"].config == transform_config

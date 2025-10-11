"""Tests for the parameter system."""

import pytest
from openworkflows import Workflow, Node, ExecutionContext, register_node
from openworkflows.parameters import Parameter
from typing import Dict, Any


@pytest.mark.asyncio
async def test_template_node_parameters():
    """Test TemplateNode with parameters."""
    workflow = Workflow("Test Template Parameters")

    # Don't connect anything - template will use workflow_inputs
    workflow.add_node(
        "template",
        "template",
        {"template": "Hello, {name}! Welcome to {place}.", "strict": False},
    )

    result = await workflow.run(inputs={"name": "Alice", "place": "Wonderland"})

    assert result["template"]["text"] == "Hello, Alice! Welcome to Wonderland."


@pytest.mark.asyncio
async def test_template_node_strict_validation():
    """Test TemplateNode strict parameter."""
    workflow = Workflow("Test Template Strict")

    workflow.add_node(
        "template", "template", {"template": "Hello, {name}! {missing}", "strict": True}
    )

    with pytest.raises(Exception, match="Missing template variable"):
        await workflow.run(inputs={"name": "Alice"})


@pytest.mark.asyncio
async def test_transform_node_parameters():
    """Test TransformNode with transform parameter."""
    workflow = Workflow("Test Transform Parameters")

    workflow.add_node("input", "input", {"name": "text"})
    workflow.add_node("transform", "transform", {"transform": "upper"})

    workflow.connect("input.value", "transform.input")

    result = await workflow.run(inputs={"text": "hello world"})

    assert result["transform"]["output"] == "HELLO WORLD"


@pytest.mark.asyncio
async def test_transform_node_choices_validation():
    """Test TransformNode validates choices."""
    with pytest.raises(ValueError, match="must be one of"):
        workflow = Workflow("Test Choices")
        workflow.add_node("transform", "transform", {"transform": "invalid_transform"})


@pytest.mark.asyncio
async def test_merge_node_parameters():
    """Test MergeNode with mode parameter."""
    workflow = Workflow("Test Merge Parameters")

    workflow.add_node("input1", "input", {"name": "a"})
    workflow.add_node("input2", "input", {"name": "b"})
    workflow.add_node("merge", "merge", {"mode": "list"})

    workflow.connect("input1.value", "merge.input")
    workflow.connect("input2.value", "merge.input1")

    result = await workflow.run(inputs={"a": 10, "b": 20})

    assert result["merge"]["result"] == [10, 20]


@pytest.mark.asyncio
async def test_custom_node_with_parameters():
    """Test custom node with parameters."""

    @register_node("custom_multiplier")
    class MultiplierNode(Node):
        inputs = {"value": float}
        outputs = {"result": float}
        parameters = {
            "multiplier": Parameter(
                name="multiplier",
                type=float,
                default=2.0,
                required=False,
                description="Multiplication factor",
            ),
            "add_offset": Parameter(
                name="add_offset",
                type=bool,
                default=False,
                required=False,
                description="Add 10 to result",
            ),
        }

        async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
            value = ctx.input("value")
            multiplier = self.param("multiplier")
            add_offset = self.param("add_offset")

            result = value * multiplier
            if add_offset:
                result += 10

            return {"result": result}

    workflow = Workflow("Test Custom Parameters")
    workflow.add_node("input", "input", {"name": "x"})
    workflow.add_node("mult", "custom_multiplier", {"multiplier": 3.0, "add_offset": True})

    workflow.connect("input.value", "mult.value")

    result = await workflow.run(inputs={"x": 5})

    assert result["mult"]["result"] == 25.0  # 5 * 3 + 10


@pytest.mark.asyncio
async def test_parameter_validation():
    """Test parameter type validation."""

    @register_node("validated_node")
    class ValidatedNode(Node):
        outputs = {"result": str}
        parameters = {
            "count": Parameter(
                name="count",
                type=int,
                required=True,
                description="Must be positive",
                validator=lambda x: x > 0,
            ),
        }

        async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
            return {"result": "ok"}

    # Should work with valid value
    workflow = Workflow("Valid")
    workflow.add_node("test", "validated_node", {"count": 5})

    # Should fail with invalid value
    with pytest.raises(ValueError, match="Custom validation failed"):
        workflow2 = Workflow("Invalid")
        workflow2.add_node("test", "validated_node", {"count": -1})


@pytest.mark.asyncio
async def test_required_parameter():
    """Test required parameter validation."""

    @register_node("required_param_node")
    class RequiredParamNode(Node):
        outputs = {"result": str}
        parameters = {
            "name": Parameter(name="name", type=str, required=True, description="Required name"),
        }

        async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
            return {"result": self.param("name")}

    # Should fail without required parameter
    with pytest.raises(ValueError, match="Required parameter 'name' is missing"):
        workflow = Workflow("Missing Required")
        workflow.add_node("test", "required_param_node", {})


@pytest.mark.asyncio
async def test_parameter_type_coercion():
    """Test parameter type coercion."""

    @register_node("coercion_node")
    class CoercionNode(Node):
        outputs = {"result": float}
        parameters = {
            "value": Parameter(name="value", type=float, default=1.0),
        }

        async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
            return {"result": self.param("value")}

    # Should coerce int to float
    workflow = Workflow("Coercion")
    workflow.add_node("test", "coercion_node", {"value": 42})  # int

    result = await workflow.run()
    assert result["test"]["result"] == 42.0  # coerced to float


@pytest.mark.asyncio
async def test_parameter_defaults():
    """Test parameter default values."""

    @register_node("default_node")
    class DefaultNode(Node):
        outputs = {"result": str}
        parameters = {
            "prefix": Parameter(name="prefix", type=str, default="Hello"),
            "suffix": Parameter(name="suffix", type=str, default="World"),
        }

        async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
            return {"result": f"{self.param('prefix')} {self.param('suffix')}"}

    # Use all defaults
    workflow1 = Workflow("All Defaults")
    workflow1.add_node("test", "default_node", {})
    result1 = await workflow1.run()
    assert result1["test"]["result"] == "Hello World"

    # Override one default
    workflow2 = Workflow("Override One")
    workflow2.add_node("test", "default_node", {"prefix": "Goodbye"})
    result2 = await workflow2.run()
    assert result2["test"]["result"] == "Goodbye World"

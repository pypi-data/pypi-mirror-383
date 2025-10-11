"""Tests for node schema generation."""

import pytest
from typing import Literal, Optional, Dict, Any
from openworkflows.schema import get_node_schema, get_all_node_schemas, _get_ui_type
from openworkflows import register_node, Node, node
from openworkflows.context import ExecutionContext
from openworkflows.parameters import Parameter


class TestUITypeMapping:
    """Test UI type conversion from Python types."""

    def test_basic_types(self):
        """Test basic type mappings."""
        assert _get_ui_type(str) == {"component": "text"}
        assert _get_ui_type(int) == {"component": "number", "inputType": "integer"}
        assert _get_ui_type(float) == {"component": "number", "inputType": "float"}
        assert _get_ui_type(bool) == {"component": "checkbox"}

    def test_literal_type(self):
        """Test Literal type maps to dropdown."""
        ui_spec = _get_ui_type(Literal["a", "b", "c"])
        assert ui_spec["component"] == "dropdown"
        assert ui_spec["options"] == ["a", "b", "c"]

    def test_optional_type(self):
        """Test Optional type unwraps and marks optional."""
        ui_spec = _get_ui_type(Optional[str])
        assert ui_spec["component"] == "text"
        assert ui_spec["optional"] is True

    def test_dict_type(self):
        """Test dict type maps to JSON editor."""
        ui_spec = _get_ui_type(dict)
        assert ui_spec["component"] == "json"

        ui_spec = _get_ui_type(Dict[str, Any])
        assert ui_spec["component"] == "json"

    def test_list_type(self):
        """Test list type maps to JSON editor."""
        ui_spec = _get_ui_type(list)
        assert ui_spec["component"] == "json"

    def test_any_type(self):
        """Test Any type."""
        ui_spec = _get_ui_type(Any)
        assert ui_spec["component"] == "text"
        assert "description" in ui_spec


class TestBuiltInNodeSchemas:
    """Test schema generation for built-in nodes."""

    def test_input_node_schema(self):
        """Test InputNode schema."""
        schema = get_node_schema("input")

        assert schema["type"] == "input"
        assert len(schema["inputs"]) == 0
        assert len(schema["outputs"]) == 1
        assert schema["outputs"][0]["name"] == "value"

    def test_output_node_schema(self):
        """Test OutputNode schema."""
        schema = get_node_schema("output")

        assert schema["type"] == "output"
        assert len(schema["inputs"]) == 1
        assert schema["inputs"][0]["name"] == "value"
        assert len(schema["outputs"]) == 1

    def test_template_node_schema(self):
        """Test TemplateNode schema with parameters."""
        schema = get_node_schema("template")

        assert schema["type"] == "template"
        assert len(schema["parameters"]) == 2

        # Check template parameter
        template_param = next(p for p in schema["parameters"] if p["name"] == "template")
        assert template_param["component"] == "text"
        assert template_param["required"] is True

        # Check strict parameter
        strict_param = next(p for p in schema["parameters"] if p["name"] == "strict")
        assert strict_param["component"] == "checkbox"
        assert strict_param["default"] is True

    def test_transform_node_schema(self):
        """Test TransformNode schema with choices."""
        schema = get_node_schema("transform")

        assert schema["type"] == "transform"
        assert len(schema["parameters"]) == 1

        transform_param = schema["parameters"][0]
        assert transform_param["name"] == "transform"
        assert transform_param["component"] == "dropdown"
        assert "identity" in transform_param["options"]
        assert "upper" in transform_param["options"]
        assert transform_param["default"] == "identity"

    def test_merge_node_schema(self):
        """Test MergeNode schema with wildcard inputs."""
        schema = get_node_schema("merge")

        assert schema["type"] == "merge"

        # Check mode parameter (choices)
        mode_param = next(p for p in schema["parameters"] if p["name"] == "mode")
        assert mode_param["component"] == "dropdown"
        assert mode_param["options"] == ["dict", "list"]

        # MergeNode now uses wildcard inputs, so it should only have the mode parameter
        assert len(schema["parameters"]) == 1

    def test_generate_text_node_schema(self):
        """Test GenerateTextNode schema."""
        schema = get_node_schema("generate_text")

        assert schema["type"] == "generate_text"
        assert len(schema["inputs"]) == 2

        # Check prompt input
        prompt_input = next(i for i in schema["inputs"] if i["name"] == "prompt")
        assert prompt_input["component"] == "text"

        # Check system input (Optional)
        system_input = next(i for i in schema["inputs"] if i["name"] == "system")
        assert system_input["component"] == "text"
        assert system_input.get("optional") is True

    def test_http_request_node_schema(self):
        """Test HTTPRequestNode schema."""
        schema = get_node_schema("http_request")

        assert schema["type"] == "http_request"

        # Check method parameter (dropdown)
        method_param = next(p for p in schema["parameters"] if p["name"] == "method")
        assert method_param["component"] == "dropdown"
        assert "GET" in method_param["options"]
        assert "POST" in method_param["options"]

        # Check headers parameter (dict/JSON)
        headers_param = next(p for p in schema["parameters"] if p["name"] == "headers")
        assert headers_param["component"] == "json"

        # Check timeout parameter (number)
        timeout_param = next(p for p in schema["parameters"] if p["name"] == "timeout")
        assert timeout_param["component"] == "number"
        assert timeout_param["inputType"] == "integer"


class TestCustomNodeSchemas:
    """Test schema generation for custom nodes."""

    def test_class_based_node_schema(self):
        """Test schema for class-based custom node."""

        @register_node("test_class_node")
        class TestClassNode(Node):
            """A test node."""

            inputs = {"x": int, "y": float}
            outputs = {"result": float}
            parameters = {
                "operation": Parameter(
                    name="operation",
                    type=str,
                    default="add",
                    choices=["add", "multiply"],
                    description="Math operation",
                )
            }

            async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
                return {"result": 0.0}

        schema = get_node_schema("test_class_node")

        assert schema["type"] == "test_class_node"
        assert len(schema["inputs"]) == 2
        assert len(schema["outputs"]) == 1

        # Check inputs
        x_input = next(i for i in schema["inputs"] if i["name"] == "x")
        assert x_input["component"] == "number"
        assert x_input["inputType"] == "integer"

        y_input = next(i for i in schema["inputs"] if i["name"] == "y")
        assert y_input["component"] == "number"
        assert y_input["inputType"] == "float"

        # Check parameter
        param = schema["parameters"][0]
        assert param["name"] == "operation"
        assert param["component"] == "dropdown"
        assert param["options"] == ["add", "multiply"]

    def test_function_based_node_schema(self):
        """Test schema for function-based node."""

        @node(
            inputs={"text": str},
            outputs={"length": int},
            parameters={"multiplier": Parameter(name="multiplier", type=int, default=1)},
        )
        async def test_func_node(ctx: ExecutionContext) -> int:
            """Count characters."""
            return 0

        register_node("test_func_node")(test_func_node)

        schema = get_node_schema("test_func_node")

        assert schema["type"] == "test_func_node"
        assert len(schema["inputs"]) == 1
        assert len(schema["outputs"]) == 1

        # Check input
        assert schema["inputs"][0]["name"] == "text"
        assert schema["inputs"][0]["component"] == "text"

        # Check output
        assert schema["outputs"][0]["name"] == "length"

        # Check parameter
        param = schema["parameters"][0]
        assert param["name"] == "multiplier"
        assert param["component"] == "number"
        assert param["default"] == 1

    def test_optional_inputs_schema(self):
        """Test schema with Optional input types."""

        @register_node("test_optional_node")
        class TestOptionalNode(Node):
            inputs = {"required": str, "optional": Optional[int]}
            outputs = {"result": str}

            async def execute(self, ctx: ExecutionContext) -> Dict[str, Any]:
                return {"result": ""}

        schema = get_node_schema("test_optional_node")

        required_input = next(i for i in schema["inputs"] if i["name"] == "required")
        assert required_input["component"] == "text"
        assert "optional" not in required_input

        optional_input = next(i for i in schema["inputs"] if i["name"] == "optional")
        assert optional_input["component"] == "number"
        assert optional_input["optional"] is True


class TestAllNodeSchemas:
    """Test bulk schema generation."""

    def test_get_all_node_schemas(self):
        """Test getting all registered node schemas."""
        schemas = get_all_node_schemas()

        # Should have at least the built-in nodes
        assert len(schemas) >= 9

        # Check all schemas have required fields
        for schema in schemas:
            assert "type" in schema
            assert "name" in schema
            assert "description" in schema
            assert "inputs" in schema
            assert "outputs" in schema
            assert "parameters" in schema
            assert isinstance(schema["inputs"], list)
            assert isinstance(schema["outputs"], list)
            assert isinstance(schema["parameters"], list)

    def test_schema_completeness(self):
        """Test that all built-in nodes have complete schemas."""
        required_nodes = [
            "input",
            "output",
            "template",
            "transform",
            "merge",
            "generate_text",
            "http_request",
            "http_get",
            "http_post",
        ]

        schemas = get_all_node_schemas()
        schema_types = [s["type"] for s in schemas]

        for node_type in required_nodes:
            assert node_type in schema_types, f"Missing schema for {node_type}"

    def test_invalid_node_type(self):
        """Test error handling for invalid node type."""
        with pytest.raises(ValueError, match="not found in registry"):
            get_node_schema("nonexistent_node")


class TestSchemaStructure:
    """Test the structure of generated schemas."""

    def test_input_schema_structure(self):
        """Test input schema structure."""
        schema = get_node_schema("template")

        for input_schema in schema["inputs"]:
            assert "name" in input_schema
            assert "type" in input_schema
            assert "component" in input_schema

    def test_output_schema_structure(self):
        """Test output schema structure."""
        schema = get_node_schema("transform")

        for output_schema in schema["outputs"]:
            assert "name" in output_schema
            assert "type" in output_schema

    def test_parameter_schema_structure(self):
        """Test parameter schema structure."""
        schema = get_node_schema("http_request")

        for param_schema in schema["parameters"]:
            assert "name" in param_schema
            assert "type" in param_schema
            assert "component" in param_schema
            assert "required" in param_schema

            # Parameters should have description
            if "description" in param_schema:
                assert isinstance(param_schema["description"], str)

    def test_dropdown_parameter_has_options(self):
        """Test dropdown parameters include options."""
        schema = get_node_schema("transform")

        transform_param = schema["parameters"][0]
        assert transform_param["component"] == "dropdown"
        assert "options" in transform_param
        assert isinstance(transform_param["options"], list)
        assert len(transform_param["options"]) > 0
